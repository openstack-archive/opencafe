"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import json
import os
import ConfigParser

from cafe.common.reporting import cclogging

data_sources = []


class DataSourceType(type):
    def __new__(cls, clsname, bases, attrs):
        data_source = super(DataSourceType, cls).__new__(
            cls, clsname, bases, attrs)
        if data_source.__strategy_name__:
            data_sources.append(data_source)
        return data_source


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
        print ("Unexpected exception when attempting to access '{1}'"
               " environment variable.".format(os_env_var))
        raise exception

# Standard format to for flat key/value data sources
CONFIG_KEY = 'CAFE_{section_name}_{key}'


class DataSource(object):

    __metaclass__ = DataSourceType
    __strategy_name__ = None

    def get(self, item_name, default=None):
        raise NotImplementedError

    def get_raw(self, item_name, default=None):
        raise NotImplementedError

    def get_boolean(self, item_name, default=None):
        raise NotImplementedError


class EnvironmentVariableDataSource(DataSource):

    __strategy_name__ = 'env_variable'

    def __init__(self, section_name):
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

        self._section_name = section_name

    def get(self, item_name, default=None):
        return os.environ.get(CONFIG_KEY.format(
            section_name=self._section_name, key=item_name), default)

    def get_raw(self, item_name, default=None):
        return self.get(item_name, default)

    def get_boolean(self, item_name, default=None):
        item_value = self.get(item_name, default)
        return bool(item_value) if item_value is not None else item_value


class ConfigParserDataSource(DataSource):

    __strategy_name__ = 'config_parser'

    def __init__(self, config_file_path, section_name):
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

        self._data_source = ConfigParser.SafeConfigParser()
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
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
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
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
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
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            if default is None:
                self._log.error(str(e))
            else:
                msg = "{0}.  Using default value '{1}' instead".format(
                    str(e), default)
                self._log.warning(msg)
            return default


class DictionaryDataSource(DataSource):

    # This is a building block for other data sources. Setting it's name
    # to None will cause it to skip registration
    __strategy_name__ = None

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

        item_value = section.get(item_name, default)
        return bool(item_value) if item_value is not None else item_value


class JSONDataSource(DictionaryDataSource):

    __strategy_name__ = 'json'

    def __init__(self, config_file_path, section_name):
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

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


class BaseConfigSectionInterface(object):
    """Base class for building an interface for the data contained in a
    SafeConfigParser object, as loaded from the config file as defined
    by the engine's config file.
    """

    def __init__(self, data_source, override, section_name):

        self._override = data_source
        self._data_source = override
        self._section_name = section_name

    def get(self, item_name, default=None):
        return self._override.get(item_name, None) or \
            self._data_source.get(item_name, default)

    def get_raw(self, item_name, default=None):
        return self._override.get_raw(item_name, None) or \
            self._data_source.get(item_name, default)

    def get_boolean(self, item_name, default=None):
        return self._override.get_boolean(item_name, None) or \
            self._data_source.get_boolean(item_name, default)


class ConfigSectionInterface(BaseConfigSectionInterface):
    def __init__(self, config_file_path=None, section_name=None,
                 config_strategy=None):
        section_name = (section_name or
                        getattr(self, 'SECTION_NAME', None) or
                        getattr(self, 'CONFIG_SECTION_NAME', None))
        config_file_path = config_file_path or _get_path_from_env(
            'CAFE_CONFIG_FILE_PATH')

        # Determine if the configuration strategy is valid
        strategy = config_strategy or os.environ.get("CAFE_CONFIG_STRATEGY")
        strategy = strategy.lower()
        config_strategies = {data_source.__strategy_name__: data_source
                             for data_source in data_sources}
        if strategy not in config_strategies.keys():
            raise KeyError(
                "{strategy} is an unregistered configuration strategy. "
                "Known strategies are {strategies}.".format(
                    strategy=strategy, strategies=config_strategies.keys()))

        if strategy in [ConfigParserDataSource.__strategy_name__,
                        JSONDataSource.__strategy_name__]:
            data_source = config_strategies[strategy](
                config_file_path, section_name)
        else:
            data_source = config_strategies[strategy](section_name)
        override = EnvironmentVariableDataSource(
            section_name)

        super(ConfigSectionInterface, self).__init__(
            data_source=data_source,
            override=override,
            section_name=section_name)
