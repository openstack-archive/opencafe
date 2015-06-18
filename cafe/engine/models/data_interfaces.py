# Copyright 2015 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc
import json
import os
from six.moves import configparser
from six import add_metaclass

from cafe.common.reporting import cclogging
try:
    from cafe.engine.mongo.client import BaseMongoClient
except:
    """ We are temporarily ignoring errors due to plugin refactor.
    The mongo data-source is currently not being used. and needs to be
    abstracted out into a data-source plugin.
    """

    pass


class ConfigDataException(Exception):
    pass


class NonExistentConfigPathError(Exception):
    pass


class ConfigEnvironmentVariableError(Exception):
    pass


# This is a decorator
def expected_values(*values):
    def decorator(fn):
        def wrapped():
            class UnexpectedConfigOptionValueError(Exception):
                pass
            value = fn()
            if value not in values:
                raise UnexpectedConfigOptionValueError(value)
            return fn()
        return wrapped
    return decorator


def _get_path_from_env(os_env_var):
    try:
        return os.environ[os_env_var]
    except KeyError:
        msg = "'{0}' environment variable was not set.".format(
            os_env_var)
        raise ConfigEnvironmentVariableError(msg)
    except Exception as exception:
        print(
            "Unexpected exception when attempting to access '{1}'"
            " environment variable.".format(os_env_var))
        raise exception

# Standard format to for flat key/value data sources
CONFIG_KEY = 'CAFE_{section_name}_{key}'


@add_metaclass(abc.ABCMeta)
class DataSource(object):

    def __init__(self):
        self._log = cclogging.logging.getLogger(
            cclogging.get_object_namespace(self.__class__))

    def get(self, item_name, default=None):
        raise NotImplementedError

    def get_raw(self, item_name, default=None):
        raise NotImplementedError

    def get_boolean(self, item_name, default=None):
        raise NotImplementedError

    def get_json(self, item_name, default=None):
        raise NotImplementedError

    @staticmethod
    def _str_to_bool(value):
        """Attempts to convert a text value to a boolean.
        Returns None otherwise."""
        if value:
            return value.lower() == 'true'
        return None

    @staticmethod
    def _parse_json(value, log=None):
        """Parse the value as JSON. Returns None if value is invalid JSON."""
        if not value:
            return None

        try:
            return json.loads(value)
        except ValueError as error:
            if log is not None:
                log.warning("Invalid JSON '{0}'. ValueError: {1}"
                            .format(value, error))
            return None


class EnvironmentVariableDataSource(DataSource):

    def __init__(self, section_name):
        super(EnvironmentVariableDataSource, self).__init__()
        self._section_name = section_name

    def get(self, item_name, default=None):
        return os.environ.get(CONFIG_KEY.format(
            section_name=self._section_name, key=item_name), default)

    def get_raw(self, item_name, default=None):
        return self.get(item_name, default)

    def get_boolean(self, item_name, default=None):
        return self._str_to_bool(self.get(item_name, default))

    def get_json(self, item_name, default=None):
        return self._parse_json(self.get(item_name, default), log=self._log)


class ConfigParserDataSource(DataSource):

    def __init__(self, config_file_path, section_name):
        super(ConfigParserDataSource, self).__init__()

        cafe_env_var = {key: value for key, value in os.environ.iteritems()
                        if key.startswith('CAFE_')}

        self._data_source = configparser.SafeConfigParser(
            defaults=cafe_env_var)
        self._section_name = section_name

        # Check if the path exists
        if not os.path.exists(config_file_path):
            msg = 'Could not verify the existence of config file at {0}'\
                  .format(config_file_path)
            raise NonExistentConfigPathError(msg)

        # Read the file in and turn it into a SafeConfigParser instance
        try:
            self._data_source.read(config_file_path)
        except Exception as exception:
            self._log.exception(exception)
            raise exception

    def get(self, item_name, default=None):

        try:
            return self._data_source.get(self._section_name, item_name)
        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            if default is None:
                self._log.error(str(e))
            else:
                msg = "{0}.  Using default value '{1}' instead".format(
                    str(e), default)
                self._log.warning(msg)
            return default

    def get_raw(self, item_name, default=None):
        try:
            return self._data_source.get(
                self._section_name, item_name, raw=True)
        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            if default is None:
                self._log.error(str(e))
            else:
                msg = "{0}.  Using default value '{1}' instead".format(
                    str(e), default)
                self._log.warning(msg)
            return default

    def get_boolean(self, item_name, default=None):

        try:
            return self._data_source.getboolean(self._section_name, item_name)
        except (configparser.NoOptionError, configparser.NoSectionError) as e:
            if default is None:
                self._log.error(str(e))
            else:
                msg = "{0}.  Using default value '{1}' instead".format(
                    str(e), default)
                self._log.warning(msg)
            return default

    def get_json(self, item_name, default=None):
        value = self._parse_json(self.get(item_name, None), log=self._log)
        if value is None:
            return default
        return value


class DictionaryDataSource(DataSource):

    def get(self, item_name, default=None):
        section = self._data_source.get(self._section_name)
        if section is None:
            self._log.error("No section: '{section_name}'".format(
                section_name=self._section_name))
            return None

        if item_name not in section:
            self._log.error(
                "No option '{item_name}' in section: '{section_name}'".format(
                    section_name=self._section_name, item_name=item_name))
            return default

        return section.get(item_name, default)

    def get_raw(self, item_name, default=None):

        section = self._data_source.get(self._section_name)
        if section is None:
            self._log.error("No section: '{section_name}'".format(
                section_name=self._section_name))
            return None

        if item_name not in section:
            self._log.error(
                "No option '{item_name}' in section: '{section_name}'".format(
                    section_name=self._section_name, item_name=item_name))
            return default

        return section.get(item_name, default)

    def get_boolean(self, item_name, default=None):

        section = self._data_source.get(self._section_name)
        if section is None:
            self._log.error("No section: '{section_name}'".format(
                section_name=self._section_name))
            return None

        if item_name not in section:
            self._log.error(
                "No option '{item_name}' in section: '{section_name}'".format(
                    section_name=self._section_name, item_name=item_name))
            return default

        return self._str_to_bool(self.get(item_name, default))

    def get_json(self, item_name, default=None):
        value = self._parse_json(self.get(item_name, None), log=self._log)
        if value is None:
            return default
        return value


class JSONDataSource(DictionaryDataSource):

    def __init__(self, config_file_path, section_name):
        super(JSONDataSource, self).__init__()

        self._section_name = section_name

        # Check if file path exists
        if not os.path.exists(config_file_path):
            msg = 'Could not verify the existence of config file at {0}'\
                  .format(config_file_path)
            raise NonExistentConfigPathError(msg)

        with open(config_file_path) as config_file:
            config_data = config_file.read()
            try:
                self._data_source = json.loads(config_data)
            except Exception as exception:
                self._log.exception(exception)
                raise exception


class MongoDataSource(DictionaryDataSource):

    def __init__(
            self, hostname, db_name, username, password, config_name,
            section_name):
        super(MongoDataSource, self).__init__()
        self._section_name = section_name

        self.db = BaseMongoClient(
            hostname=hostname, db_name=db_name,
            username=username, password=password)
        self.db.connect()
        self.db.auth()
        self._data_source = self.db.find_one({'config_name': config_name})


class BaseConfigSectionInterface(object):
    """Base class for building an interface for the data contained in a
    SafeConfigParser object, as loaded from the config file as defined
    by the engine's config file.
    """

    def __init__(self, config_file_path, section_name):
        self._log = cclogging.logging.getLogger(
            cclogging.get_object_namespace(self.__class__))
        self._override = EnvironmentVariableDataSource(
            section_name)
        self._data_source = ConfigParserDataSource(
            config_file_path, section_name)
        self._section_name = section_name

    def get(self, item_name, default=None):
        return self._override.get(item_name, None) or \
            self._data_source.get(item_name, default)

    def get_raw(self, item_name, default=None):
        return self._override.get_raw(item_name, None) or \
            self._data_source.get_raw(item_name, default)

    def get_boolean(self, item_name, default=None):
        value = self._override.get_boolean(item_name, None)
        if value is None:
            value = self._data_source.get_boolean(item_name, default)
        return value

    def get_json(self, item_name, default=None):
        value = self._override.get_json(item_name, None)
        if value is None:
            value = self._data_source.get_json(item_name, default)
        return value


class ConfigSectionInterface(BaseConfigSectionInterface):
    def __init__(self, config_file_path=None, section_name=None):
        section_name = (section_name or
                        getattr(self, 'SECTION_NAME', None) or
                        getattr(self, 'CONFIG_SECTION_NAME', None))

        config_file_path = config_file_path or _get_path_from_env(
            'CAFE_CONFIG_FILE_PATH')

        super(ConfigSectionInterface, self).__init__(
            config_file_path, section_name)
