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
import signal
import subprocess

from cafe.engine.sshv2.common import BaseSSHClass


class SSHProxy(BaseSSHClass):
    def __init__(
        self, hostname=None, port=22, username=None, compress=True,
            look_for_keys=False, key_filename=None):
        super(SSHProxy, self).__init__()
        for k, v in locals().items():
            if k != "self":
                setattr(self, k, v)

    def _get_args(
        self, hostname=None, port=None, username=None, compress=None,
            look_for_keys=None, key_filename=None):
        args = [
            "ssh", "-oUserKnownHostsFile=/dev/null",
            "-oStrictHostKeyChecking=no", "-oExitOnForwardFailure=yes", "-N"]
        hostname = hostname or self.hostname
        username = username or self.username
        compress = compress if compress is not None else self.compress
        key_filename = key_filename or self.key_filename
        look_for_keys = (
            look_for_keys if look_for_keys is not None
            else self.look_for_keys)

        args.append("-P{0}".format(port or self.port))
        if compress:
            args.append("-C")

        if look_for_keys is False:
            args.append("-i{0}".format(key_filename))

        if username:
            args.append("{0}@{1}".format(username, hostname))
        else:
            args.append(hostname)
        return args

    def create_forward_port(
        self, bind_port, forward_hostname, forward_port, bind_address=None,
            **connect_kwargs):
        args = self._get_args(**connect_kwargs)
        if bind_address:
            args.append("-L{0}:{1}:{2}:{3}".format(
                bind_address, bind_port, forward_hostname, forward_port))
        else:
            args.append("-L{0}:{1}:{2}".format(
                bind_port, forward_hostname, forward_port))
        return PortForward(
            subprocess.Popen(args).pid, "forward", bind_address or "localhost",
            bind_port)

    def create_socks_proxy(
            self, bind_port, bind_address=None, **connect_kwargs):
        args = self._get_args(**connect_kwargs)
        if bind_address:
            args.append("-D{0}:{1}".format(bind_address, bind_port))
        else:
            args.append("-D{0}:{1}:{2}".format(bind_port))
        return SocksProxy(
            subprocess.Popen(args).pid, "forward", bind_address or "localhost",
            bind_port)


class PortForward(BaseSSHClass):
    def __init__(self, pid, type_, bind_address, bind_port):
        for k, v in locals().items():
            if k != "self":
                setattr(self, k, v)
        self.name = None

    def set_name(self, name):
        self.name = name

    def close(self):
        try:
            os.kill(self.pid, signal.SIGKILL)
        except OSError as e:
            self._log.warning(
                "Close called more than once or process ended unexpectedly")
            self._log.warning(e)


class SocksProxy(PortForward):
    pass
