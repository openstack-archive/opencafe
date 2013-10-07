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

import os
from Crypto.PublicKey import RSA

from cafe.common.reporting import cclogging


def generate_rsa_ssh_keys(keyfilename,
                          keyfilepath,
                          key_size=1024,
                          pass_phrase=""):
    """
    Generates rsa keys
    """
    _log = cclogging.getLogger(__name__)
    _log.debug(
        "Creating RSA keys with name: {0} inside folder: {1}".format(
            keyfilename,
            keyfilepath
        ))
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
    try:
        public_key_file = open("{0}/{1}.pub".format(keyfilepath, keyfilename), "w")
        private_key_file = open("{0}/{1}".format(keyfilepath, keyfilename), "w")
        public_key_file.write(public_key.exportKey(passphrase=pass_phrase))
        private_key_file.write(private_key.exportKey(passphrase=pass_phrase))
        public_key_file.close()
        private_key_file.close()
        if not os.path.isfile("{0}/{1}".format(keyfilepath, keyfilename)):
            return False, "No private key file found"
        if not os.path.isfile("{0}/{1}.pub".format(keyfilepath, keyfilename)):
            return False, "No public key file found"
        return True, ""
    except IOError as (errno, strerror):
        _log.error("I/O error({0}): {1}".format(
            errno, strerror))
