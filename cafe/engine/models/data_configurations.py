"""
Copyright 2014 Rackspace

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

from cafe.engine.models.data_interfaces import \
    ConfigSectionInterface


class ConfigParserFileConfig(ConfigSectionInterface):

    SECTION_NAME = 'CONFIG_PARSER_CONFIG'

    @property
    def file_path(self):
        return self.get_raw("file_path")


class JsonFileConfig(ConfigSectionInterface):

    SECTION_NAME = 'JSON_CONFIG'

    @property
    def file_path(self):
        return self.get_raw("file_path")


class MongoDBConfig(ConfigSectionInterface):

    SECTION_NAME = 'MONGO_CONFIG'

    @property
    def connection_string(self):
        return self.get_raw("connection_string")

    @property
    def database_name(self):
        return self.get_raw("database_name")