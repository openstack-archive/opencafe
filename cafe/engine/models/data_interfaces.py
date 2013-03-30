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

import os
import ConfigParser
from cafe.common.reporting import cclogging


class ConfigDataException(Exception):
    pass


class NonExistentConfigPathError(Exception):
    pass


class ConfigEnvironmentVariableError(Exception):
    pass


#Decorator
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


class BaseConfigSectionInterface(object):
    """
    Base class for building an interface for the data contained in a
    SafeConfigParser object, as loaded from the config file as defined
    by the engine's config file.

    This is meant to be a generic interface so that in the future
    get() and getboolean() can be reimplemented to provide data from a
    database
    """

    def __init__(self, config_file_path, section_name):
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

        self._datasource = ConfigParser.SafeConfigParser()
        self._section_name = section_name

        #Check the path
        if not os.path.exists(config_file_path):
            msg = 'Could not verify the existence of config file at {0}'\
                  .format(config_file_path)
            raise NonExistentConfigPathError(msg)

        #Read the file in and turn it into a SafeConfigParser instance
        try:
            self._datasource.read(config_file_path)
        except Exception as exception:
            self._log.exception(exception)
            raise exception

    def get(self, item_name, default=None):

        try:
            return self._datasource.get(self._section_name, item_name)
        except ConfigParser.NoOptionError as e:
            self._log.error(str(e))
            return default
        except ConfigParser.NoSectionError as e:
            self._log.error(str(e))
            pass

    def get_raw(self, item_name, default=None):
        '''Performs a get() on SafeConfigParser object without interopolation
        '''

        try:
            return self._datasource.get(self._section_name, item_name,
                                        raw=True)
        except ConfigParser.NoOptionError as e:
            self._log.error(str(e))
            return default
        except ConfigParser.NoSectionError as e:
            self._log.error(str(e))
            pass

    def get_boolean(self, item_name, default=None):

        try:
            return self._datasource.getboolean(self._section_name,
                                               item_name)
        except ConfigParser.NoOptionError as e:
            self._log.error(str(e))
            return default
        except ConfigParser.NoSectionError as e:
            self._log.error(str(e))
            pass
