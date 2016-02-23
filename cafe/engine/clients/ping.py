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

import platform
import re
import subprocess


class PingClient(object):
    """
    @summary: Client to ping windows or linux servers
    """

    DEFAULT_NUM_PINGS = 3
    PING_IPV4_COMMAND_LINUX = 'ping -c {num_pings}'
    PING_IPV6_COMMAND_LINUX = 'ping6 -c {num_pings}'
    PING_IPV4_COMMAND_WINDOWS = 'ping -c {num_pings}'
    PING_IPV6_COMMAND_WINDOWS = 'ping -6 -c {num_pings}'
    PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'

    @classmethod
    def ping(cls, ip, ip_address_version, num_pings=DEFAULT_NUM_PINGS):
        """
        @summary: Ping an IP address, return if replies were received or not.
        @param ip: IP address to ping
        @type ip: string
        @param ip_address_version: IP Address version (4 or 6)
        @type ip_address_version: int
        @param num_pings: Number of pings to attempt
        @type num_pings: int
        @return: True if the server was reachable, False otherwise
        @rtype: bool
        """
        packet_loss_percent = cls._ping(
            ip=ip, ip_address_version=ip_address_version, num_pings=num_pings)
        return packet_loss_percent != '100'

    @classmethod
    def ping_percent_success(cls, ip, ip_address_version,
                             num_pings=DEFAULT_NUM_PINGS):
        """
        @summary: Ping an IP address, return the percent of replies received
        @param ip: IP address to ping
        @type ip: string
        @param ip_address_version: IP Address version (4 or 6)
        @type ip_address_version: int
        @param num_pings: Number of pings to attempt
        @type num_pings: int
        @return: Percent of responses received, based on number of requests
        @rtype: int
        """
        packet_loss_percent = cls._ping(
            ip=ip, ip_address_version=ip_address_version, num_pings=num_pings)
        return 100 - int(packet_loss_percent)

    @classmethod
    def ping_percent_loss(cls, ip, ip_address_version,
                          num_pings=DEFAULT_NUM_PINGS):
        """
        @summary: Ping an IP address, return the percent of replies not
             returned
        @param ip: IP address to ping
        @type ip: string
        @param ip_address_version: IP Address version (4 or 6)
        @type ip_address_version: int
        @param num_pings: Number of pings to attempt
        @type num_pings: int
        @return: Percent of responses not received, based on number of requests
        @rtype: int
        """
        return int(cls._ping(
            ip=ip, ip_address_version=ip_address_version, num_pings=num_pings))

    @classmethod
    def _ping(cls, ip, ip_address_version, num_pings):
        """
        @summary: Ping an IP address
        @param ip: IP address to ping
        @type ip: string
        @param ip_address_version: IP Address version (4 or 6)
        @type ip_address_version: int
        @param num_pings: Number of pings to attempt
        @type num_pings: int
        @return: Percent of ping replies received
        @rtype: int
        """

        windows = 'windows'

        os_type = platform.system().lower()
        ping_ipv4 = (cls.PING_IPV4_COMMAND_WINDOWS if windows in os_type
                     else cls.PING_IPV4_COMMAND_LINUX)
        ping_ipv6 = (cls.PING_IPV6_COMMAND_WINDOWS if windows in os_type
                     else cls.PING_IPV6_COMMAND_LINUX)

        ping_cmd = ping_ipv6 if ip_address_version == 6 else ping_ipv4
        ping_cmd = ping_cmd.format(num_pings=num_pings)
        cmd = '{command} {address}'.format(command=ping_cmd, address=ip)

        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        process.wait()

        try:
            packet_loss_percent = re.search(
                cls.PING_PACKET_LOSS_REGEX,
                process.stdout.read()).group(1)
        except Exception:
            # When there is no match, 100% ping loss is the best response
            # (for now). There has to be a better way, since the regex not
            # matching does not guarantee that the target IP is not online.
            # e.g. - The ping utility was not available/located in the path or
            # the expected ping output changed.
            packet_loss_percent = 100

        return packet_loss_percent
