# Copyright 2016 Rackspace
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

from cafe.engine.models.data_interfaces import (
    ConfigSectionInterface, _get_path_from_env)


class HTTPPluginConfig(ConfigSectionInterface):

    SECTION_NAME = 'PLUGIN.HTTP'

    def __init__(self, config_file_path=None):
        """Initialization of the HTTP Plugin Engine config section."""
        config_file_path = config_file_path or _get_path_from_env(
            'CAFE_ENGINE_CONFIG_FILE_PATH')
        super(HTTPPluginConfig, self).__init__(
            config_file_path=config_file_path)

    @property
    def retries_on_requests_exceptions(self):
        """
        Number of retries allowed on Requests library exceptions.

        This is provided to allow retries on exceptions from the Requests
        library. Specifically this will allow retries on errors resulting
        from the following exceptions: ConnectionError, HTTPError, Timeout,
        and TooManyRedirects.
        """
        try:
            return int(self.get('retries_on_requests_exceptions', 0))
        except ValueError:
            raw_data = self.get_raw('retries_on_requests_exceptions')
            raise ValueError(
                '{} is not a valid input for the '
                '\"retries_on_requests_exceptions\" congfiguration value. '
                'Value must be an integer'.format(raw_data))
