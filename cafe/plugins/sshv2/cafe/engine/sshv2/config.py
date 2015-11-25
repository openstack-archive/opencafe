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

from cafe.engine.models.data_interfaces import ConfigSectionInterface
from cafe.engine.sshv2.common import DEFAULT_TIMEOUT


class SSHClientConfig(ConfigSectionInterface):
    SECTION_NAME = "ssh_client"

    @property
    def hostname(self):
        return self.get("hostname", None)

    @property
    def port(self):
        return self.get("port", 22)

    @property
    def username(self):
        return self.get("username", None)

    @property
    def password(self):
        return self.get_raw("password")

    @property
    def accept_missing_host_key(self):
        return self.get_boolean("accept_missing_host_key", True)

    @property
    def timeout(self):
        return self.get("timeout", DEFAULT_TIMEOUT)

    @property
    def compress(self):
        return self.get_boolean("compress", True)

    @property
    def pkey(self):
        return self.get("pkey", None)

    @property
    def look_for_keys(self):
        return self.get_boolean("look_for_keys", False)

    @property
    def allow_agent(self):
        return self.get_boolean("allow_agent", False)

    @property
    def key_filename(self):
        return self.get("key_filename")

    @property
    def proxy_type(self):
        return self.get("proxy_type")

    @property
    def proxy_ip(self):
        return self.get("proxy_ip")

    @property
    def proxy_port(self):
        return self.get("proxy_port")


class ProxyConfig(ConfigSectionInterface):
    SECTION_NAME = "proxy"

    @property
    def hostname(self):
        return self.get("hostname", None)

    @property
    def port(self):
        return self.get("port", 22)

    @property
    def username(self):
        return self.get("username", None)

    @property
    def compress(self):
        return self.get_boolean("compress", True)

    @property
    def look_for_keys(self):
        return self.get_boolean("look_for_keys", False)

    @property
    def key_filename(self):
        return self.get("key_filename")


class ProxyForward(ConfigSectionInterface):
    SECTION_NAME = "port_forward"

    @property
    def bind_port(self):
        return self.get("bind_port", None)

    @property
    def forward_hostname(self):
        return self.get("forward_hostname", None)

    @property
    def forward_port(self):
        return self.get("forward_port", None)

    @property
    def bind_address(self):
        return self.get("bind_address", None)
