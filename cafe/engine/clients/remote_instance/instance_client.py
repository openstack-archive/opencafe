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

from cafe.common.reporting import cclogging
from cafe.engine.clients.remote_instance.linux.linux_instance_client \
    import LinuxClient
from cafe.engine.clients.remote_instance.windows.windows_instance_client \
    import WindowsClient


class InstanceClientFactory(object):
    """
    @summary: Factory class which will create appropriate utility object
    based on the operating system of the server.
    """
    clientList = {'windows': 'WindowsClient', 'linux': 'LinuxClient',
                  'gentoo': 'LinuxClient', 'arch': 'LinuxClient',
                  'freebsd': 'FreeBSDClient'}

    @classmethod
    def get_instance_client(cls, ip_address=None, username=None, password=None,
                            os_distro=None, server_id=None, config=None,
                            key=None):
        """
        @summary: Returns utility class based on the OS type of server
        @param ip_address: IP Address of the server
        @type ip_address: string
        @param password: The administrator user password
        @type password: string
        @param username: The administrator user name
        @type username: string
        @return: Utility class based on the OS type of server
        @rtype: LinuxClient or WindowsClient
        """

        instanceClient = cls.clientList.get(os_distro.lower())
        if instanceClient is None:
            instanceClient = cls.clientList.get(cls.os_type.lower())

        target_str = "globals().get('" + instanceClient + "')"
        instanceClient = eval(target_str)

        return instanceClient(ip_address=ip_address, username=username,
                              password=password, os_distro=os_distro,
                              server_id=server_id, config=config, key=key)


class InstanceClient(object):
    """
    @summary: Wrapper class around different operating system utilities.
    """

    def __init__(self, ip_address=None, password=None, os_distro=None,
                 config=None, username=None, server_id=None, key=None):
        self._client = InstanceClientFactory.get_instance_client(
            ip_address=ip_address, password=password, os_distro=os_distro,
            username=username, server_id=server_id, config=config, key=key)
        self.client_log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))

    def can_authenticate(self):
        """
        @summary: Checks if you can authenticate to the server
        @return: True if you can connect, False otherwise
        @rtype: bool
        """
        return self._client.test_connection_auth()

    def get_hostname(self):
        """
        @summary: Gets the host name of the server
        @return: The host name of the server
        @rtype: string
        """
        return self._client.get_hostname()

    def get_files(self, path):
        """
        @summary: Gets the list of filenames from the path
        @param path: Path from where to get the filenames
        @type path: string
        @return: List of filenames
        @rtype: List of strings
        """
        return self._client.get_files(path)

    def get_ram_size_in_mb(self):
        """
        @summary: Returns the RAM size in MB
        @return: The RAM size in MB
        @rtype: string
        """
        return self._client.get_ram_size_in_mb()

    def get_disk_size_in_gb(self):
        """
        @summary: Returns the disk size in GB
        @return: The disk size in GB
        @rtype: int
        """
        return self._client.get_disk_size_in_gb()

    def get_number_of_vcpus(self):
        """
        @summary: Get the number of vcpus assigned to the server
        @return: The number of vcpus assigned to the server
        @rtype: int
        """
        return self._client.get_number_of_vcpus()

    def get_partitions(self):
        """
        @summary: Returns the contents of /proc/partitions
        @return: The partitions attached to the instance
        @rtype: string
        """
        return self._client.get_partitions()

    def get_uptime(self):
        """
        @summary: Get the boot time of the server
        @return: The boot time of the server
        @rtype: time.struct_time
        """
        return self._client.get_uptime()

    def create_file(self, filedetails):
        '''
        @summary: Create a new file
        @param filedetails: File details such as content, name
        @type filedetails; FileDetails
        '''
        return self._client.create_file()

    def get_file_details(self, filepath):
        """
        @summary: Get the file details
        @param filepath: Path to the file
        @type filepath: string
        @return: File details including permissions and content
        @rtype: FileDetails
        """
        return self._client.get_file_details()

    def is_file_present(self, filepath):
        """
        @summary: Check if the given file is present
        @param filepath: Path to the file
        @type filepath: string
        @return: True if File exists, False otherwise
        """
        return self._client.is_file_present()
