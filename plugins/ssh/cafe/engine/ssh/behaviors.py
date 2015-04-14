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

import os
from Crypto.PublicKey import RSA
import datetime
import re

from cafe.engine.behaviors import BaseBehavior, behavior
from cafe.engine.ssh.client import BaseSSHClient
from cafe.engine.config import EngineConfig
from cafe.engine.ssh.models.ssh_response import SSHKeyResponse
from cafe.common.reporting import cclogging


class SSHBehavior(BaseBehavior):
    PING_IPV4_COMMAND_LINUX = 'ping -c'
    PING_PACKET_LOSS_REGEX = r'(?P<ping_loss>\d{1,3}\.?\d*)% packet loss'

    def __init__(self, ssh_client=None):
        super(SSHBehavior, self).__init__()
        self.client = ssh_client

    @classmethod
    def generate_rsa_ssh_keys(cls,
                              keyfile_name=None,
                              keyfile_path=None,
                              key_size=1024,
                              pass_phrase=""):
        """
        Generates rsa keys
        """
        engine_config = EngineConfig()
        _log = cclogging.getLogger(__name__)
        _log.debug(
            "Creating RSA keys with name: {0} inside folder: {1}".format(
                keyfile_name, keyfile_path))

        # Build the key file names and path
        if keyfile_name is None:
            keyfile_name = "test_ssh_key_{0}".format(
                str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
        if keyfile_path is None:
            keyfile_path = engine_config.temp_directory

        pub_keyfile_path = os.path.join(keyfile_path,
                                        "{0}.pub".format(keyfile_name))
        private_key_file_path = os.path.join(keyfile_path, keyfile_name)

        # If the key files already exist, remove them
        if os.path.isfile(private_key_file_path):
            os.remove(private_key_file_path)
        if os.path.isfile(pub_keyfile_path):
            os.remove(pub_keyfile_path)
        try:
            # Generate the keys
            private_key = RSA.generate(key_size)
            public_key = private_key.publickey()
        except ValueError as msg:
            _log.error("Key Generate exception: \n {0}".format(msg))
            return SSHKeyResponse(error=msg)

        try:
            # Create the key files and write the keys onto them
            with open(pub_keyfile_path, "w") as public_key_file:
                public_key_file.write(
                    public_key.exportKey(passphrase=pass_phrase))

            if not os.path.isfile(pub_keyfile_path):
                return SSHKeyResponse(error="No public key file created")

            with open(private_key_file_path, "w") as private_key_file:
                private_key_file.write(
                    private_key.exportKey(passphrase=pass_phrase))

            if not os.path.isfile(private_key_file_path):
                return SSHKeyResponse(error="No private key file created")
            else:
                os.chmod(private_key_file_path, 0o700)
            return SSHKeyResponse(
                public_key=pub_keyfile_path,
                private_key=private_key_file_path)
        except IOError as err:
            try:
                errno, strerror = err
                _log.error("I/O error({0}): {1}".format(
                    errno, strerror))
                return SSHKeyResponse(error=strerror)
            except:
                return SSHKeyResponse(error=str(err))

    @behavior(BaseSSHClient)
    def ping_using_remote_machine(self, ping_ip_address, count=3):
        _log = cclogging.getLogger(__name__)
        # packet count value of 3 comes with the constants
        command = "{0} {1}".format(SSHBehavior.PING_IPV4_COMMAND_LINUX,
                                   count)
        ping_response = self.client.execute_shell_command(
            "{0} {1}".format(command, ping_ip_address),
            prompt="$").stdout
        packet_loss_regex_result = re.search(
            SSHBehavior.PING_PACKET_LOSS_REGEX, ping_response)
        if packet_loss_regex_result is None:
            _log.error(
                "regex did not match ping response: {0}".format(
                    ping_response))
            return False
        packet_loss_percent = packet_loss_regex_result.group("ping_loss")
        return int(packet_loss_percent) != 100
