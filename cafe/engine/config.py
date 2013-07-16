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


_ENGINE_CONFIG_FILE_ENV_VAR = 'OPENCAFE_ENGINE_CONFIG_FILE'


class NonExistentConfigPathError(Exception):
    pass


class ConfigEnvironmentVariableError(Exception):
    pass


class EngineConfig(object):
    '''
    Config interface for the global engine configuration
    '''

    SECTION_NAME = 'OPENCAFE_ENGINE'

    def __init__(self, config_file_path=None, section_name=None):
        #Support for setting the section name as a class or instance
        #constant, as both 'SECTION_NAME' and 'CONFIG_SECTION_NAME'
        self._section_name = (section_name or
                              getattr(self, 'SECTION_NAME', None) or
                              getattr(self, 'CONFIG_SECTION_NAME', None))

        self._datasource = None
        if not config_file_path:
            config_file_path = os.environ[_ENGINE_CONFIG_FILE_ENV_VAR]
        #Check the path
        if not os.path.exists(config_file_path):
            msg = 'Could not verify the existence of config file at {0}'\
                  .format(config_file_path)
            raise NonExistentConfigPathError(msg)

        #Read the file in and turn it into a SafeConfigParser instance
        try:
            self._datasource = ConfigParser.SafeConfigParser()
            self._datasource.read(config_file_path)
        except Exception as e:
            raise e

    def get(self, item_name, default=None):

        try:
            return self._datasource.get(self._section_name, item_name)
        except ConfigParser.NoOptionError as no_option_err:
            if not default:
                raise no_option_err
            return default

    def get_raw(self, item_name, default=None):
        '''
        Performs a get() on SafeConfigParser object without interpolation
        '''

        try:
            return self._datasource.get(self._section_name, item_name,
                                        raw=True)
        except ConfigParser.NoOptionError as no_option_err:
            if not default:
                raise no_option_err
            return default

    def get_boolean(self, item_name, default=None):

        try:
            return self._datasource.getboolean(self._section_name,
                                               item_name)
        except ConfigParser.NoOptionError as no_option_err:
            if not default:
                raise no_option_err
            return default

    #Provided for implementations of cafe, unused by the engine itself
    @property
    def data_directory(self):
        return self.get_raw("data_directory")

    #Provided for implementations of cafe, unused by the engine itself
    @property
    def temp_directory(self):
        return self.get_raw("temp_directory")

    #Used by the engine for the output of engine and implementation logs
    @property
    def config_directory(self):
        return self.get_raw("config_directory")

    #Used by the engine for the output of engine and implementation logs
    @property
    def master_log_file_name(self):
        return self.get_raw("master_log_file_name", default="engine-master")

    #Used by the engine for the output of engine and implementation logs
    @property
    def logging_verbosity(self):
        return self.get_boolean("logging_verbosity", False)

    #Used by the engine to facilitate using multiple test repositories.
    @property
    def default_test_repo(self):
        return self.get_raw("default_test_repo")

