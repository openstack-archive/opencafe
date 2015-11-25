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
"""SSH Behaviors for creating and writing ssh keys"""
import os
from Crypto.PublicKey import RSA

from cafe.engine.config import EngineConfig
from cafe.engine.sshv2.models import SSHKeyResponse
from cafe.engine.sshv2.common import BaseSSHClass

ENGINE_CONFIG = EngineConfig()


class SSHBehavior(BaseSSHClass):
    """SSH Behaviors"""

    @classmethod
    def generate_rsa_ssh_keys(cls, key_size=None, pass_phrase=None):
        """Generates rsa keys"""
        key_size = key_size or 2048
        pass_phrase = pass_phrase or ""

        try:
            private_key = RSA.generate(key_size)
            public_key = private_key.publickey()
        except ValueError as exception:
            cls._log.error("Key Generate exception: \n {0}".format(exception))
            raise exception

        return SSHKeyResponse(
            public_key=public_key.exportKey(passphrase=pass_phrase),
            private_key=private_key.exportKey(passphrase=pass_phrase))

    @classmethod
    def write_secure_keys_local(
            cls, private_key, public_key=None, path=None, file_name=None):
        """private_key is a string that contains the private key, normally the
        id_rsa file
        """
        if path is None:
            path = ENGINE_CONFIG.temp_directory
        if file_name is None:
            file_name = "id_rsa"

        try:
            os.makedirs(path)
        except OSError:
            pass

        key_path = os.path.join(path, file_name)
        cls.write_file_with_permissions(key_path, private_key, 0o600)
        key_path = "{0}.pub".format(key_path)
        cls.write_file_with_permissions(key_path, public_key, 0o600)

    @staticmethod
    def write_file_with_permissions(file_path, string=None, permissions=0o600):
        """Writes file from string with permissions"""
        if string is None:
            return
        with open(file_path, "w") as file_:
            file_.write(string)
        os.chmod(file_path, permissions)

    @classmethod
    def generate_and_write_files(
            cls, path=None, file_name=None, key_size=None, passphrase=None):
        """Generates rsa keys and writes them to path with filename"""
        keys = cls.generate_rsa_ssh_keys(key_size, passphrase)
        cls.write_secure_keys_local(
            private_key=keys.private_key, public_key=keys.public_key,
            path=path, file_name=file_name)
