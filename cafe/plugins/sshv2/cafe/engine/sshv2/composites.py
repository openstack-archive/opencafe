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

from cafe.engine.sshv2.behaviors import SSHBehavior
from cafe.engine.sshv2.client import SSHClient
from cafe.engine.sshv2.common import BaseSSHClass
from cafe.engine.sshv2.config import ProxyConfig, SSHClientConfig
from cafe.engine.sshv2.proxy import SSHProxy


class SSHComposite(BaseSSHClass):
    def __init__(self, ssh_config=None, proxy_config=None):
        self.proxy_config = proxy_config or ProxyConfig()
        self.ssh_config = ssh_config or SSHClientConfig()

        self.proxy_client = SSHProxy(
            hostname=self.proxy_config.hostname,
            port=self.proxy_config.port,
            username=self.proxy_config.username,
            compress=self.proxy_config.compress,
            look_for_keys=self.proxy_config.look_for_keys,
            key_filename=self.proxy_config.key_filename)

        self.client = SSHClient(
            hostname=self.ssh_config.hostname,
            port=self.ssh_config.port,
            username=self.ssh_config.username,
            password=self.ssh_config.password,
            accept_missing_host_key=self.ssh_config.accept_missing_host_key,
            timeout=self.ssh_config.timeout,
            compress=self.ssh_config.compress,
            pkey=self.ssh_config.pkey,
            look_for_keys=self.ssh_config.look_for_keys,
            allow_agent=self.ssh_config.allow_agent,
            key_filename=self.ssh_config.key_filename,
            proxy_type=self.ssh_config.proxy_type,
            proxy_ip=self.ssh_config.proxy_ip,
            proxy_port=self.ssh_config.proxy_port)

        self.behavior = SSHBehavior
