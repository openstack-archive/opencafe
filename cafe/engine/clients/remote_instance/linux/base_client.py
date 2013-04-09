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

import re
import os

from cafe.engine.clients.ssh import SSHBaseClient


class BasePersistentLinuxClient(object):

    def __init__(self, ip_address, username, password, ssh_timeout=600, prompt=None):
        self.ssh_client = SSHBaseClient(ip_address, username, password, ssh_timeout)
        self.prompt = prompt
        if not self.ssh_client.test_connection_auth():
            raise

    def format_disk_device(self, device, fstype):
        '''Formats entire device, does not create partitions'''
        return self.ssh_client.exec_command(
            "mkfs.%s %s\n" % (str(fstype).lower(), str(device)))

    def mount_disk_device(self, device, mountpoint, fstype, create_mountpoint=True):
        '''
        Mounts a disk at a specified mountpoint.
        Performs 'touch mountpoint' before executing
        '''
        self.ssh_client.exec_command("mkdir %s" % str(mountpoint))
        return self.ssh_client.exec_command(
            "mount -t %s %s %s\n" % (str(fstype).lower(),
                                     str(device), str(mountpoint)))

    def unmount_disk_device(self, mountpoint):
        '''
        Forces unmounts (umount -f) a disk at a specified mountpoint.
        '''
        return self.ssh_client.exec_command(
            "umount -f %s\n" % (str(mountpoint)))

    def write_random_data_to_disk(self, dir_path, filename, blocksize=1024,
                                  count=1024):
        '''Uses dd command to write blocksize*count bytes to dir_path/filename
           via ssh on remote machine.

           By default writes one mebibyte (2^20 bytes) if blocksize and count
           are not defined.
           NOTE:  1 MEBIbyte (2^20) != 1 MEGAbyte (10^6) for all contexts

           Note: dd if=/dev/urandom
        '''

        dd_of = os.path.join(dir_path, str(filename))
        return self.ssh_client.exec_command(
            "dd if=/dev/urandom of=%s bs=%s count=%s\n" %
            (str(dd_of), str(blocksize), str(count)))

    def write_zeroes_data_to_disk(self, disk_mountpoint, filename,
                                  blocksize=1024, count=1024):
        '''By default writes one mebibyte (2^20 bytes)'''

        of = '%s/%s' % (disk_mountpoint, str(filename))
        return self.ssh_client.exec_command(
            "dd if=/dev/zero of=%s bs=%s count=%s\n" %
            (str(of), str(blocksize), str(count)))

    def execute_resource_bomb(self):
        '''By default executes :(){ :|:& };:'''
        return self.ssh_client.exec_command(":(){ :|:& };:")

    def stat_file(self, filepath):
        sshresp = self.ssh_client.exec_command("stat %s\n" % str(filepath))
        return  sshresp

    def get_file_size_bytes(self, filepath):
        '''
           Performs wc -c on path provided, returning the numerical count in
           the result
        '''
        sshresp = self.ssh_client.exec_command("wc -c %s\n" % str(filepath))
        result = re.search('^(.*)\s', sshresp)
        try:
            return result.groups()[0]
        except:
            return None

    def get_file_md5hash(self, filepath):
        '''
            Performs binary mode md5sum of file and returns hash.
            (md5sum -b <file>)
        '''
        sshresp = self.ssh_client.exec_command("md5sum -b %s\n" % str(filepath))
        result = re.search('^(.*)\s', sshresp)
        try:
            return result.groups()[0]
        except:
            return None
