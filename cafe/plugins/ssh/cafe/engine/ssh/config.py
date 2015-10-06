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

import os

from cafe.configurator.managers import EngineDirectoryManager
from cafe.engine.models.data_interfaces import (
    BaseConfigSectionInterface, EnvironmentVariableDataSource,
    ConfigParserDataSource)


ENV_KEY = 'CAFE_SSH_CONFIG_FILE'
SSH_CONFIG_FILE = 'ssh.config'

SSH_CONFIG_PATH = os.path.join(EngineDirectoryManager.OPENCAFE_ROOT_DIR,
                               SSH_CONFIG_FILE)
os.environ[ENV_KEY] = SSH_CONFIG_PATH


class SSHConfig(BaseConfigSectionInterface):
    SECTION_NAME = 'ssh'

    # This configuration allows a user to set a global ssh proxy for tunneling
    # ssh connections.
    #
    # NOTE: This approach assumes that proxy has the execution host's ssh keys
    # are already copied to the proxy.
    #
    # If using the config file:
    #     +  the file is: ~/.opencafe/ssh.config
    #     +  it should have a 'ssh' section, and a 'proxy' option that defines
    #        the proxy ip address or FQDN.
    #
    # The value in the config file can be overridden by setting the environment
    # variable "CAFE_ssh_proxy"
    #    e.g - set CAFE_ssh_proxy="192.168.0.1"

    def __init__(self, config_file_path=None, section_name=None):
        section_name = section_name or self.SECTION_NAME
        config_file_path = config_file_path or SSH_CONFIG_PATH

        self._override = EnvironmentVariableDataSource(section_name)

        # If no config file exists, try to use the env var as the sole source
        if os.path.exists(config_file_path):
            self._data_source = ConfigParserDataSource(
                config_file_path, section_name)
        else:
            self._data_source = self._override
        self._section_name = section_name

    @property
    def proxy(self):
        """
        Used by the ssh plugin to build a tunnel through the proxy/bastion
        to the test environment.
        """
        return self.get('proxy', None)
