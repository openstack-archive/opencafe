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


class DriverConfig(ConfigSectionInterface):
    """
    Unittest driver configuration values.

    This config section is intended to supply values and configuration that can
    not be programatically identified to the unittest driver.
    """

    SECTION_NAME = 'drivers.unittest'

    def __init__(self, config_file_path=None):
        config_file_path = config_file_path or _get_path_from_env(
            'CAFE_ENGINE_CONFIG_FILE_PATH')
        super(DriverConfig, self).__init__(config_file_path=config_file_path)

    @property
    def ignore_empty_datasets(self):
        """
        Identify whether empty datasets should change suite results.

        A dataset provided to a suite should result in the suite failing. This
        value provides a mechanism to modify that behavior in the case of
        suites with intensionally included empty datasets. If this is set to
        'True' empty datasets will not cause suite failures. This defaults
        to 'False'.
        """
        return self.get_boolean(
            item_name="ignore_empty_datasets",
            default=False)
