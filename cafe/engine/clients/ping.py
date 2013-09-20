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

import platform
import re
import subprocess


class PingClient(object):
    """
    @summary: Client to ping windows or linux servers
    """

    PING_IPV4_COMMAND_LINUX = 'ping -c 3'
    PING_IPV6_COMMAND_LINUX = 'ping6 -c 3'
    PING_IPV4_COMMAND_WINDOWS = 'ping'
    PING_IPV6_COMMAND_WINDOWS = 'ping -6'
    PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'

    @classmethod
    def ping(cls, ip, ip_address_version):
        """
        @summary: Ping a server with a IP
        @param ip: IP address to ping
        @type ip: string
        @return: True if the server was reachable, False otherwise
        @rtype: bool
        """

        os_type = platform.system().lower()
        ping_ipv4 = (cls.PING_IPV4_COMMAND_WINDOWS if os_type == 'windows'
                     else cls.PING_IPV4_COMMAND_LINUX)
        ping_ipv6 = (cls.PING_IPV6_COMMAND_WINDOWS if os_type == 'windows'
                     else cls.PING_IPV6_COMMAND_LINUX)
        ping_command = ping_ipv6 if ip_address_version == 6 else ping_ipv4
        command = '{command} {address}'.format(
            command=ping_command, address=ip)
        process = subprocess.Popen(command, shell=True,
                                   stdout=subprocess.PIPE)
        process.wait()
        try:
            packet_loss_percent = re.search(
                cls.PING_PACKET_LOSS_REGEX,
                process.stdout.read()).group(1)
        except Exception:
            # If there is no match, fail
            return False
        return packet_loss_percent != '100'
