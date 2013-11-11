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

from cafe.engine.behaviors import BaseBehavior, behavior
from cafe.common.reporting import cclogging
from cafe.engine.clients.ssh import BaseSSHClient
from cafe.engine.config import EngineConfig
from cafe.engine.models.ssh_response import SSHKeyResponse

import os
from Crypto.PublicKey import RSA
import re
import datetime

class SSHBehavior(BaseBehavior):
    PING_IPV4_COMMAND_LINUX = 'ping -c 3 '
    PING_PACKET_LOSS_REGEX = '(\d{1,3})\.?\d*\%.*loss'

    def __init__(self, ssh_client=None):
        self.client = ssh_client

    @classmethod
    def generate_rsa_ssh_keys(cls,
                              keyfilename=None,
                              keyfilepath=None,
                              key_size=1024,
                              pass_phrase=""):

        """
        Generates rsa keys
        """
        engine_config = EngineConfig()
        _log = cclogging.getLogger(__name__)
        _log.debug(
            "Creating RSA keys with name: {0} inside folder: {1}".format(
                keyfilename,
                keyfilepath
            ))
        if keyfilename is None:
            keyfilename = "test_ssh_key_{0}".format(
                str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
        if keyfilepath is None:
            keyfilepath = engine_config.temp_directory
        if os.path.isfile("{0}/{1}".format(
                          keyfilepath, keyfilename)):
            os.remove("{0}/{1}".format(keyfilepath, keyfilename))
        if os.path.isfile("{0}/{1}.pub".format(keyfilepath, keyfilename)):
            os.remove("{0}/{1}.pub".format(keyfilepath, keyfilename))
        try:
            private_key = RSA.generate(key_size)
            public_key = private_key.publickey()
        except ValueError, msg:
            _log.error(
                "Key Generate exception: \n {0}".format(msg))
            return SSHKeyResponse(
                error = msg
            )
        try:
            public_key_file = open("{0}/{1}.pub".format(keyfilepath, keyfilename), "w")
            private_key_file = open("{0}/{1}".format(keyfilepath, keyfilename), "w")
            public_key_file.write(public_key.exportKey(passphrase=pass_phrase))
            private_key_file.write(private_key.exportKey(passphrase=pass_phrase))
            public_key_file.close()
            private_key_file.close()
            if not os.path.isfile("{0}/{1}".format(keyfilepath, keyfilename)):
                return SSHKeyResponse(
                    error = "No private key file created")
            if not os.path.isfile("{0}/{1}.pub".format(keyfilepath, keyfilename)):
                return SSHKeyResponse(
                    error = "No public key file created")
            return SSHKeyResponse(
                public_key = "{0}/{1}.pub".format(
                    keyfilepath,
                    keyfilename),
                private_key = "{0}/{1}".format(
                    keyfilepath,
                    keyfilename)
            )
        except IOError as (errno, strerror):
            _log.error("I/O error({0}): {1}".format(
                errno, strerror))
            return SSHKeyResponse(
                error = strerror)

    @behavior(BaseSSHClient)
    def ping_using_remote_machine(self,
                                  ping_ip_address,
                                  count=3):
        command = SSHBehavior.PING_IPV4_COMMAND_LINUX
        # packet count value of 3 comes with the constants
        if count != 3:
            ping_items = command.split(' ')[:2]
            ping_items.append(count)
            command = '{0} {1} {2} '.format(*ping_items)
        ping_response = self.client.execute_shell_command(
                              "{0}{1}".format(
                                  command,
                                  ping_ip_address),
                              prompt="$").stdout
        try:
            packet_loss_percent = re.search(SSHBehavior.PING_PACKET_LOSS_REGEX,
                                            ping_response).group(1)
        except:
            if hasattr(self.client, 'host'):
                client_ip = getattr(self.client, 'host')
            elif hasattr(self.client, 'ip'):
                client_ip = getattr(self.client, 'ip')
            else:
                client_ip = ''
            msg = 'Failed to ping IP {0} from remote server {1}'.format(
                ping_ip_address, client_ip)
            raise Exception(msg)
        return int(packet_loss_percent) != '100'