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

from socks import socket, create_connection
from StringIO import StringIO
from uuid import uuid4
import io
import time

from paramiko import AutoAddPolicy, RSAKey
from paramiko import py3compat
from paramiko.client import SSHClient as ParamikoSSHClient

from cafe.engine.sshv2.common import (
    BaseSSHClass, _SSHLogger, DEFAULT_TIMEOUT, POLLING_RATE, CHANNEL_KEEPALIVE)
from cafe.engine.sshv2.models import ExecResponse

# this is a hack to preimport dependencies imported in a thread during connect
# which causes a deadlock. https://github.com/paramiko/paramiko/issues/104
py3compat.u("")

# dirty hack 2.0 also issue 104
# Try / Catch to prevent users using paramiko<2.0.0 from raising an ImportError
try:
    from cryptography.hazmat.backends import default_backend
    default_backend()
except ImportError:
    pass


class ProxyTypes(object):
    SOCKS5 = 2
    SOCKS4 = 1


class ExtendedParamikoSSHClient(ParamikoSSHClient):
    def execute_command(
        self, command, bufsize=-1, timeout=None, stdin_str="", stdin_file=None,
            raise_exceptions=False):
        timeout = timeout or DEFAULT_TIMEOUT
        chan = self._transport.open_session()
        chan.settimeout(POLLING_RATE)
        chan.exec_command(command)
        stdin_str = stdin_str if stdin_file is None else stdin_file.read()
        stdin = chan.makefile("wb", bufsize)
        stdout = chan.makefile("rb", bufsize)
        stderr = chan.makefile_stderr("rb", bufsize)
        stdin.write(stdin_str)
        stdin.close()
        stdout_str = stderr_str = ""
        exit_status = None
        max_time = time.time() + timeout
        while not chan.exit_status_ready():
            stderr_str += self._read_channel(stderr)
            stdout_str += self._read_channel(stdout)
            if max_time < time.time():
                raise socket.timeout(
                    "Command timed out\nSTDOUT:{0}\nSTDERR:{1}\n".format(
                        stdout_str, stderr_str))
        exit_status = chan.recv_exit_status()
        stdout_str += self._read_channel(stdout)
        stderr_str += self._read_channel(stderr)
        chan.close()
        return stdin_str, stdout_str, stderr_str, exit_status

    def _read_channel(self, chan):
        read = ""
        try:
            read += chan.read()
        except socket.timeout:
            pass
        return read


class SSHClient(BaseSSHClass):
    def __init__(
        self, hostname=None, port=22, username=None, password=None,
        accept_missing_host_key=True, timeout=None, compress=True, pkey=None,
        look_for_keys=False, allow_agent=False, key_filename=None,
            proxy_type=None, proxy_ip=None, proxy_port=None, sock=None):
        super(SSHClient, self).__init__()
        self.connect_kwargs = {}
        self.accept_missing_host_key = accept_missing_host_key
        self.proxy_port = proxy_port
        self.proxy_ip = proxy_ip
        self.proxy_type = proxy_type
        self.connect_kwargs["timeout"] = timeout or DEFAULT_TIMEOUT
        self.connect_kwargs["hostname"] = hostname
        self.connect_kwargs["port"] = int(port)
        self.connect_kwargs["username"] = username
        self.connect_kwargs["password"] = password
        self.connect_kwargs["compress"] = compress
        self.connect_kwargs["pkey"] = pkey
        self.connect_kwargs["look_for_keys"] = look_for_keys
        self.connect_kwargs["allow_agent"] = allow_agent
        self.connect_kwargs["key_filename"] = key_filename
        self.connect_kwargs["sock"] = sock

    @property
    def timeout(self):
        return self.connect_kwargs.get("timeout")

    @timeout.setter
    def timeout(self, value):
        self.connect_kwargs["timeout"] = value

    @timeout.deleter
    def timeout(self):
        if "timeout" in self.connect_kwargs:
            del self.connect_kwargs["timeout"]

    def _connect(
        self, hostname=None, port=None, username=None, password=None,
        accept_missing_host_key=None, timeout=None, compress=None, pkey=None,
        look_for_keys=None, allow_agent=None, key_filename=None,
            proxy_type=None, proxy_ip=None, proxy_port=None, sock=None):
        connect_kwargs = dict(self.connect_kwargs)
        connect_kwargs.update({
            k: locals().get(k) for k in self.connect_kwargs
            if locals().get(k) is not None})
        connect_kwargs["port"] = int(connect_kwargs.get("port"))

        ssh = ExtendedParamikoSSHClient()

        if bool(self.accept_missing_host_key or accept_missing_host_key):
            ssh.set_missing_host_key_policy(AutoAddPolicy())

        if connect_kwargs.get("pkey") is not None:
            connect_kwargs["pkey"] = RSAKey.from_private_key(
                io.StringIO(unicode(connect_kwargs["pkey"])))

        proxy_type = proxy_type or self.proxy_type
        proxy_ip = proxy_ip or self.proxy_ip
        proxy_port = proxy_port or self.proxy_port
        if connect_kwargs.get("sock") is not None:
            pass
        elif all([proxy_type, proxy_ip, proxy_port]):
            connect_kwargs["sock"] = create_connection(
                (connect_kwargs.get("hostname"), connect_kwargs.get("port")),
                proxy_type, proxy_ip, int(proxy_port))

        ssh.connect(**connect_kwargs)
        return ssh

    @_SSHLogger
    def execute_command(
        self, command, bufsize=-1, stdin_str="", stdin_file=None,
            **connect_kwargs):
        ssh_client = self._connect(**connect_kwargs)
        stdin, stdout, stderr, exit_status = ssh_client.execute_command(
            timeout=self._get_timeout(connect_kwargs.get("timeout")),
            command=command, bufsize=bufsize, stdin_str=stdin_str,
            stdin_file=stdin_file)
        ssh_client.close()
        del ssh_client
        return ExecResponse(
            stdin=stdin, stdout=stdout, stderr=stderr, exit_status=exit_status)

    def _get_timeout(self, timeout=None):
        return timeout if timeout is not None else self.timeout

    @_SSHLogger
    def create_shell(self, keepalive=None, **connect_kwargs):
        connection = self._connect(**connect_kwargs)
        return SSHShell(
            connection, self._get_timeout(connect_kwargs.get("timeout")),
            keepalive)

    @_SSHLogger
    def create_sftp(self, keepalive=None, **connect_kwargs):
        connection = self._connect(**connect_kwargs)
        return SFTPShell(connection, keepalive)


class SFTPShell(BaseSSHClass):
    def __init__(self, connection=None, keepalive=None):
        super(SFTPShell, self).__init__()
        self.connection = connection
        self.sftp = connection.open_sftp()
        self.sftp.get_channel().get_transport().set_keepalive(
            keepalive or CHANNEL_KEEPALIVE)
        self.chdir(".")

    def __getattribute__(self, name):
        if name in [
            "chdir", "chmod", "chown", "file", "get", "getcwd", "getfo",
            "listdir", "listdir_attr", "listdir_iter", "lstat", "mkdir",
            "normalize", "open", "put", "putfo", "readlink", "remove",
            "rename", "rmdir", "stat", "symlink", "truncate", "unlink",
                "utime"]:
            return self.sftp.__getattribute__(name)
        else:
            return super(SFTPShell, self).__getattribute__(name)

    def exists(self, path):
        ret_val = False
        try:
            self.sftp.stat(path)
            ret_val = True
        except IOError, e:
            if e[0] != 2:
                raise
            ret_val = False
        return ret_val

    def get_file(self, remote_path):
        ret_val = StringIO()
        self.getfo(remote_path, ret_val)
        return ret_val.getvalue()

    def write_file(self, data, remote_path):
        return self.putfo(StringIO(data), remote_path)

    def close(self):
        if hasattr(self, "sftp"):
            self.sftp.close()
            del self.sftp
        if hasattr(self, "connection"):
            self.connection.close()
            del self.connection


class SSHShell(BaseSSHClass):
    RAISE = "RAISE"
    RAISE_DISCONNECT = "RAISE_DISCONNECT"

    def __init__(self, connection, timeout, keepalive=None):
        super(SSHShell, self).__init__()
        self.connection = connection
        self.timeout = timeout
        self.channel = self._create_channel()
        self.channel.settimeout(POLLING_RATE)
        self._clear_channel()
        self.channel.get_transport().set_keepalive(
            keepalive or CHANNEL_KEEPALIVE)

    def close(self):
        if hasattr(self, "channel"):
            self.channel.close()
            del self.channel
        if hasattr(self, "connection"):
            self.connection.close()
            del self.connection

    @_SSHLogger
    def execute_shell_command(
        self, cmd, timeout=None, timeout_action=RAISE_DISCONNECT,
            exception_on_timeout=True):
        max_time = time.time() + self._get_timeout(timeout)
        uuid = str(uuid4()).replace("-", "")
        cmd = "echo {1}\n{0}\necho {1} $?\n".format(cmd.strip(), uuid)
        try:
            self._clear_channel()
            self._wait_for_active_shell(max_time)
            self.channel.send(cmd)
            response = self._read_shell_response(uuid, max_time)
        except socket.timeout as e:
            if timeout_action == self.RAISE_DISCONNECT:
                self.close()
            raise e
        return response

    def _create_channel(self):
        chan = self.connection._transport.open_session()
        chan.invoke_shell()
        return chan

    def _wait_for_active_shell(self, max_time):
        while not self.channel.send_ready():
            time.sleep(POLLING_RATE)
            if max_time < time.time():
                raise socket.timeout("Timed out waiting for active shell")

    def _read_shell_response(self, uuid, max_time):
        stdout = stderr = ""
        exit_status = None
        while max_time > time.time():
            stdout += self._read_channel(self.channel.recv)
            stderr += self._read_channel(self.channel.recv_stderr)
            if stdout.count(uuid) == 2:
                list_ = stdout.split(uuid)
                stdout = list_[1]
                try:
                    exit_status = int(list_[2])
                except (ValueError, TypeError):
                    exit_status = None
                break
        else:
            raise socket.timeout(
                "Command timed out\nSTDOUT:{0}\nSTDERR:{1}\n".format(
                    stdout, stderr))
        response = ExecResponse(
            stdin=None, stdout=stdout.strip(), stderr=stderr,
            exit_status=exit_status)
        return response

    def _read_channel(self, read_func, buffsize=1024):
        read = ""
        try:
            read += read_func(buffsize)
        except socket.timeout:
            pass
        return read

    def _clear_channel(self):
        self._read_channel(self.channel.recv)
        self._read_channel(self.channel.recv_stderr)

    def _get_timeout(self, timeout=None):
        return timeout if timeout is not None else self.timeout
