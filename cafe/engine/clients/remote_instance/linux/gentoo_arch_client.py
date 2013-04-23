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

import time

from cafe.engine.clients.remote_instance.linux.linux_instance_client import LinuxClient
from cloudcafe.common.constants import InstanceClientConstants


class GentooArchClient(LinuxClient):
    def get_boot_time(self):
        """
        @summary: Get the boot time of the server
        @return: The boot time of the server
        @rtype: time.struct_time
        """
        boot_time_string = self.ssh_client.exec_command(
            'who -b | grep -o "[A-Za-z]* [0-9].*"').replace('\n', ' ')
        year = self.ssh_client.exec_command(
            'date | grep -o "[0-9]\{4\}$"').replace('\n', '')
        boot_time = boot_time_string + year

        return time.strptime(boot_time, InstanceClientConstants.LAST_REBOOT_TIME_FORMAT_GENTOO)
