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

from cafe.engine.clients.ssh import SSHBaseClient
from cafe.common.reporting import cclogging
from cafe.engine.clients.ping import PingClient
from cloudcafe.compute.common.models.file_details import FileDetails
from cloudcafe.compute.common.models.partition import Partition, DiskSize
from cafe.engine.clients.remote_instance.linux.base_client import BasePersistentLinuxClient
from cloudcafe.compute.common.exceptions import FileNotFoundException, ServerUnreachable, SshConnectionException


class LinuxClient(BasePersistentLinuxClient):

    def __init__(self, ip_address=None, server_id=None, username=None,
                 password=None, config=None, os_distro=None):
        self.client_log = cclogging.getLogger \
                (cclogging.get_object_namespace(self.__class__))
        ssh_timeout = config.connection_timeout
        if ip_address is None:
            raise ServerUnreachable("None")
        self.ip_address = ip_address
        self.username = username
        if self.username is None:
            self.username = 'root'
        self.password = password
        self.server_id = server_id

        start = int(time.time())
        reachable = False
        while not reachable:
            reachable = PingClient.ping(ip_address,
                                        config.ip_address_version_for_ssh)
            time.sleep(config.connection_retry_interval)
            if int(time.time()) - start >= config.connection_timeout:
                raise ServerUnreachable(ip_address)

        self.ssh_client = SSHBaseClient(self.ip_address,
                                        self.username,
                                        self.password,
                                        timeout=ssh_timeout)
        if not self.ssh_client.test_connection_auth():
            self.client_log.error("Ssh connection failed for: IP:{0} \
                    Username:{1} Password: {2}".format(self.ip_address,
                                                       self.username, self.password))
            raise SshConnectionException("ssh connection failed")

    def can_connect_to_public_ip(self):
        """
        @summary: Checks if you can connect to server using public ip
        @return: True if you can connect, False otherwise
        @rtype: bool
        """
        # This returns true since the connection has already been tested in the
        # init method

        return self.ssh_client is not None

    def can_ping_public_ip(self, public_addresses, ip_address_version_for_ssh):
        """
        @summary: Checks if you can ping a public ip
        @param addresses: List of public addresses
        @type addresses: Address List
        @return: True if you can ping, False otherwise
        @rtype: bool
        """
        for public_address in public_addresses:
            if public_address.version == 4 and not PingClient.ping(public_address.addr, ip_address_version_for_ssh):
                return False
        return True

    def can_authenticate(self):
        """
        @summary: Checks if you can authenticate to the server
        @return: True if you can connect, False otherwise
        @rtype: bool
        """
        return self.ssh_client.test_connection_auth()

    def reboot(self, timeout=100):
        '''
        @timeout: max timeout for the machine to reboot
        '''
        ssh_connector = SSHConnector(self.ip_address, self.username,
                                     self.password)
        response, prompt = ssh_connector.exec_shell_command("sudo reboot")
        response, prompt = ssh_connector.exec_shell_command(self.password)
        self.client_log.info("Reboot response for %s: %s" % (self.ip_address,
                                                             response))
        max_time = time.time() + timeout
        while time.time() < max_time:
            time.sleep(5)
            if self.ssh_client.test_connection_auth():
                self.client_log.info("Reboot successful for %s"
                                     % (self.ip_address))
                return True

    def get_hostname(self):
        """
        @summary: Gets the host name of the server
        @return: The host name of the server
        @rtype: string
        """
        return self.ssh_client.exec_command("hostname").rstrip()

    def can_remote_ping_private_ip(self, private_addresses):
        """
        @summary: Checks if you can ping a private ip from this server.
        @param private_addresses: List of private addresses
        @type private_addresses: Address List
        @return: True if you can ping, False otherwise
        @rtype: bool
        """
        for private_address in private_addresses:
            if private_address.version == 4 and not PingClient.ping_using_remote_machine(self.ssh_client, private_address.addr):
                return False
        return True

    def get_files(self, path):
        """
        @summary: Gets the list of filenames from the path
        @param path: Path from where to get the filenames
        @type path: string
        @return: List of filenames
        @rtype: List of strings
        """
        command = "ls -m " + path
        return self.ssh_client.exec_command(command).rstrip('\n').split(', ')

    def get_ram_size_in_mb(self):
        """
        @summary: Returns the RAM size in MB
        @return: The RAM size in MB
        @rtype: string
        """
        output = self.ssh_client.exec_command('free -m | grep Mem')
        # TODO (dwalleck): We should handle the failure case here
        if output:
            return output.split()[1]

    def get_swap_size_in_mb(self):
        """
        @summary: Returns the Swap size in MB
        @return: The Swap size in MB
        @rtype: int
        """
        output = self.ssh_client.exec_command(
            'fdisk -l /dev/xvdc1 2>/dev/null | grep "Disk.*bytes"').rstrip('\n')
        if output:
            return int(output.split()[2])

    def get_disk_size_in_gb(self, disk_path):
        """
        @summary: Returns the disk size in GB
        @return: The disk size in GB
        @rtype: int
        """
        command = "df -h | grep '{0}'".format(disk_path)
        output = self.ssh_client.exec_command(command)
        size = output.split()[1]

        def is_decimal(char):
            return str.isdigit(char) or char == "."
        size = filter(is_decimal, size)
        return float(size)

    def get_number_of_vcpus(self):
        """
        @summary: Get the number of vcpus assigned to the server
        @return: The number of vcpus assigned to the server
        @rtype: int
        """
        command = 'cat /proc/cpuinfo | grep processor | wc -l'
        output = self.ssh_client.exec_command(command)
        return int(output)

    def get_partitions(self):
        """
        @summary: Returns the contents of /proc/partitions
        @return: The partitions attached to the instance
        @rtype: string
        """
        command = 'cat /proc/partitions'
        output = self.ssh_client.exec_command(command)
        return output

    def get_uptime(self):
        """
        @summary: Get the uptime time of the server
        @return: The uptime of the server
        """
        result = self.ssh_client.exec_command('cat /proc/uptime')
        uptime = float(result.split(' ')[0])
        return uptime

    def create_file(self, file_name, file_content, file_path=None):
        '''
        @summary: Create a new file
        @param file_name: File Name
        @type file_name: String
        @param file_content: File Content
        @type file_content: String
        @return filedetails: File details such as content, name and path
        @rtype filedetails; FileDetails
        '''
        if file_path is None:
            file_path = "/root/" + file_name
        self.ssh_client.exec_command(
            'echo -n ' + file_content + '>>' + file_path)
        return FileDetails("644", file_content, file_path)

    def get_file_details(self, filepath):
        """
        @summary: Get the file details
        @param filepath: Path to the file
        @type filepath: string
        @return: File details including permissions and content
        @rtype: FileDetails
        """
        output = self.ssh_client.exec_command(
            '[ -f ' + filepath + ' ] && echo "File exists" || echo "File does not exist"')
        if not output.rstrip('\n') == 'File exists':
            raise FileNotFoundException(
                "File:" + filepath + " not found on instance.")

        file_permissions = self.ssh_client.exec_command(
            'stat -c %a ' + filepath).rstrip("\n")
        file_contents = self.ssh_client.exec_command('cat ' + filepath)
        return FileDetails(file_permissions, file_contents, filepath)

    def is_file_present(self, filepath):
        """
        @summary: Check if the given file is present
        @param filepath: Path to the file
        @type filepath: string
        @return: True if File exists, False otherwise
        """
        output = self.ssh_client.exec_command(
            '[ -f ' + filepath + ' ] && echo "File exists" || echo "File does not exist"')
        return output.rstrip('\n') == 'File exists'

    def get_partition_types(self):
        """
        @summary: Return the partition types for all partitions
        @return: The partition types for all partitions
        @rtype: Dictionary
        """
        partitions_list = self.ssh_client.exec_command(
            'blkid').rstrip('\n').split('\n')
        partition_types = {}
        for row in partitions_list:
            partition_name = row.split()[0].rstrip(':')
            partition_types[partition_name] = re.findall(
                r'TYPE="([^"]+)"', row)[0]
        return partition_types

    def get_partition_details(self):
        """
        @summary: Return the partition details
        @return: The partition details
        @rtype: Partition List
        """
        # Return a list of partition objects that each contains the name and
        # size of the partition in bytes and the type of the partition
        partition_types = self.get_partition_types()
        partition_names = ' '.join(partition_types.keys())

        partition_size_output = self.ssh_client.exec_command(
            'fdisk -l %s 2>/dev/null | grep "Disk.*bytes"' % (partition_names)).rstrip('\n').split('\n')
        partitions = []
        for row in partition_size_output:
            row_details = row.split()
            partition_name = row_details[1].rstrip(':')
            partition_type = partition_types[partition_name]
            if partition_type == 'swap':
                partition_size = DiskSize(
                    float(row_details[2]), row_details[3].rstrip(','))
            else:
                partition_size = DiskSize(
                    int(row_details[4]) / 1073741824, 'GB')
            partitions.append(
                Partition(partition_name, partition_size, partition_type))
        return partitions

    def verify_partitions(self, expected_disk_size, expected_swap_size, server_status, actual_partitions):
        """
        @summary: Verify the partition details of the server
        @param expected_disk_size: The expected value of the Disk size in GB
        @type expected_disk_size: string
        @param expected_swap_size: The expected value of the Swap size in GB
        @type expected_swap_size: string
        @param server_status: The status of the server
        @type server_status: string
        @param actual_partitions: The actual partition details of the server
        @type actual_partitions: Partition List
        @return: The result of verification and the message to be displayed
        @rtype: Tuple (bool,string)
        """
        expected_partitions = self._get_expected_partitions(
            expected_disk_size, expected_swap_size, server_status)
        if actual_partitions is None:
            actual_partitions = self.get_partition_details()

        for partition in expected_partitions:
            if partition not in actual_partitions:
                return False, self._construct_partition_mismatch_message(expected_partitions, actual_partitions)
        return True, "Partitions Matched"

    def _get_expected_partitions(self, expected_disk_size, expected_swap_size, server_status):
        """
        @summary: Returns the expected partitions for a server based on server status
        @param expected_disk_size: The Expected disk size of the server in GB
        @type expected_disk_size: string
        @param expected_swap_size: The Expected swap size of the server in MB
        @type expected_swap_size: string
        @param server_status: Status of the server (ACTIVE or RESCUE)
        @type server_status: string
        @return: The expected partitions
        @rtype: Partition List
        """
        # ignoring swap untill the rescue functionality is clarified

        expected_partitions = [Partition(
            '/dev/xvda1', DiskSize(expected_disk_size, 'GB'), 'ext3'),
                               Partition('/dev/xvdc1', DiskSize(expected_swap_size, 'MB'), 'swap')]
        if str.upper(server_status) == 'RESCUE':
            expected_partitions = [Partition(
                '/dev/xvdb1', DiskSize(expected_disk_size, 'GB'), 'ext3')]
            # expected_partitions.append(Partition('/dev/xvdd1',
            # DiskSize(expected_swap_size, 'MB'), 'swap'))
        return expected_partitions

    def _construct_partition_mismatch_message(self, expected_partitions, actual_partitions):
        """
        @summary: Constructs the partition mismatch message based on expected_partitions and actual_partitions
        @param expected_partitions: Expected partitions of the server
        @type expected_partitions: Partition List
        @param actual_partitions: Actual Partitions of the server
        @type actual_partitions: Partition List
        @return: The partition mismatch message
        @rtype: string
        """
        message = 'Partitions Mismatch \n Expected Partitions:\n'
        for partition in expected_partitions:
            message += str(partition) + '\n'
        message += ' Actual Partitions:\n'
        for partition in actual_partitions:
            message += str(partition) + '\n'
        return message

    def mount_file_to_destination_directory(self, source_path, destination_path):
        '''
        @summary: Mounts the file to destination directory
        @param source_path: Path to file source
        @type source_path: String
        @param destination_path: Path to mount destination
        @type destination_path: String
        '''
        self.ssh_client.exec_command(
            'mount ' + source_path + ' ' + destination_path)
