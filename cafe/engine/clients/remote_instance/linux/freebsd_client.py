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
import re

from cafe.engine.clients.remote_instance.constants import \
    InstanceClientConstants
from cafe.engine.clients.remote_instance.linux.linux_instance_client \
    import LinuxClient


class FreeBSDClient(LinuxClient):
    def get_boot_time(self):
        """
        @summary: Get the boot time of the server
        @return: The boot time of the server
        @rtype: time.struct_time
        """
        uptime_string = self.ssh_client.execute_command('uptime').stdout
        uptime = uptime_string.replace('\n', '').split(',')[0].split()[2]
        uptime_unit = uptime_string.replace('\n', '').split(',')[0].split()[3]
        if uptime_unit == 'mins':
            uptime_unit_format = 'M'
        else:
            uptime_unit_format = 'S'

        command = 'date -v -{uptime}{unit_format} "+%Y-%m-%d %H:%M"'.format(
            uptime=uptime, uptime_unit_format=uptime_unit_format)
        reboot_time = self.ssh_client.execute_command(
            command).stdout.replace('\n', '')

        return time.strptime(reboot_time,
                             InstanceClientConstants.LAST_REBOOT_TIME_FORMAT)

    def get_disk_size_in_gb(self):
        """
        @summary: Returns the disk size in GB
        @return: The disk size in GB
        @rtype: int
        """
        output = self.ssh_client.execute_command(
            'gpart show -p | grep "GPT"').stdout.replace('\n', '')
        disk_size = re.search(r'([0-9]+)G', output).group(1)
        return int(disk_size)
