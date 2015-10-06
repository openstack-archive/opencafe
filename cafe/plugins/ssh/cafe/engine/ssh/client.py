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

import socket
import io
import time

from paramiko import AutoAddPolicy, RSAKey, ProxyCommand
from paramiko import AuthenticationException, SSHException
from paramiko.client import SSHClient as ParamikoSSHClient
from paramiko.resource import ResourceManager

from cafe.engine.clients.base import BaseClient
from cafe.engine.ssh.models.ssh_response import ExecResponse
from cafe.engine.ssh.config import SSHConfig


class SSHAuthStrategy:
    PASSWORD = 'password'
    LOCAL_KEY = 'local_key'
    KEY_STRING = 'key_string'
    KEY_FILE_LIST = 'key_file_list'


class ExtendedParamikoSSHClient(ParamikoSSHClient):

    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False,
                     return_exit_status=False):
        """
        Re-implements exec_command to optionally return an
        exit status code.
        """
        chan = self._transport.open_session()
        if get_pty:
            chan.get_pty()
        chan.settimeout(timeout)
        chan.exec_command(command)
        stdin = chan.makefile('wb', bufsize)
        stdout = chan.makefile('rb', bufsize)
        stderr = chan.makefile_stderr('rb', bufsize)
        if return_exit_status:
            exit_status = chan.recv_exit_status()
            return {'stdin': stdin, 'stdout': stdout,
                    'stderr': stderr, 'exit_status': exit_status}
        return {'stdin': stdin, 'stdout': stdout, 'stderr': stderr}


class BaseSSHClient(BaseClient):

    def __init__(self, host):
        """
        Initialization

        @param host: IP address or host name to connect to
        @type host: string
        """
        super(BaseSSHClient, self).__init__()
        self.ssh_connection = None
        self.host = host
        self._chan = None
        self.proxy = None
        self.proxy_set = False

    def connect(self, username=None, password=None,
                accept_missing_host_key=True, tcp_timeout=30,
                auth_strategy=SSHAuthStrategy.PASSWORD,
                port=22, key=None, allow_agent=True, key_filename=None):
        """
        Attempts to connect to a remote server via SSH

        @param username: Username to be used for SSH connection
        @type username: string
        @param password: Password to be used for SSH connection
        @type password: string
        @param auth_strategy: Authentication strategy to use to connect
        @type auth_strategy: string
        @param port: Port to use for the SSH connection
        @type port: int
        @param key: Text of an SSH key to be used to connect
        @type key: string
        @param key_filename: Name of a file that contains a SSH key
        @type key_filename: string
        @param allow_agent: Set to False to disable connecting to
                            the SSH agent
        @type allow_agent: bool
        @param accept_missing_host_key: Sets if a SSH connection can
                                        be made to remote server if
                                        the server does not have a
                                        host key in the local system
        @type accept_missing_host_key: bool
        @return: None
        """

        ssh = ExtendedParamikoSSHClient()
        if accept_missing_host_key:
            ssh.set_missing_host_key_policy(AutoAddPolicy())

        connect_args = {'hostname': self.host, 'username': username,
                        'timeout': tcp_timeout, 'port': port,
                        'allow_agent': allow_agent}

        self._log.debug('Attempting to SSH connect to {host} '
                        'with user {user} and strategy {strategy}.'.format(
                            host=self.host, user=username,
                            strategy=auth_strategy))

        if auth_strategy == SSHAuthStrategy.PASSWORD:
            connect_args['password'] = password

        if auth_strategy == SSHAuthStrategy.LOCAL_KEY:
            connect_args['look_for_keys'] = True

        if auth_strategy == SSHAuthStrategy.KEY_STRING:
            key_file = io.StringIO(key)
            key = RSAKey.from_private_key(key_file)
            connect_args['pkey'] = key

        if auth_strategy == SSHAuthStrategy.KEY_FILE_LIST:
            connect_args['key_filename'] = key_filename

        # Add sock proxy if ssh tunnel through proxy/bastion is required
        if self.is_proxy_needed():
            self._log.info("Using a proxy: {proxy}".format(proxy=self.proxy))
            proxy_str = 'ssh -q -a -x {proxy} nc {host} {port}'
            proxy_cmd = proxy_str.format(proxy=self.proxy,
                                         host=self.host, port=port)
            connect_args['sock'] = ProxyCommand(proxy_cmd)

        try:
            ssh.connect(**connect_args)
        except (AuthenticationException, SSHException,
                socket.error, EOFError) as exception:
            # Log the failure
            self._log.error(exception.message)
        else:
            # Complete setup of the client
            ResourceManager.register(self, ssh.get_transport())
            self.ssh_connection = ssh

    def is_proxy_needed(self):
        """
        @return: Boolean - True=proxy specified, False=proxy not specified
        """

        # Should only check once and then use the result for the duration of
        # the connection.
        if not self.proxy_set:
            if self.proxy is None:
                cafe_config = SSHConfig()
                self.proxy = cafe_config.proxy

                # If the option is in the config file, but no value is set,
                # the proxy is not set.
                if self.proxy == '':
                    self.proxy = None
            self.proxy_set = True
        return self.proxy is not None

    def _format_response(self, resp_dict):
        """
        Converts the exec_command response streams into an object.

        @param resp_dict: A dictionary containing the result
                          of an executed command
        @type resp_dict: dict
        @return: response
        @rtype: ExecResponse
        """

        stdout = (resp_dict.get('stdout').read()
                  if resp_dict.get('stdout') else None)
        stderr = (resp_dict.get('stderr').read()
                  if resp_dict.get('stderr') else None)
        response = ExecResponse(stdin=resp_dict.get('stdin'), stdout=stdout,
                                stderr=stderr,
                                exit_status=resp_dict.get('exit_status'))
        return response

    def is_connected(self):
        """Checks to see if an SSH connection exists."""
        return self.ssh_connection is not None

    def start_shell(self, retries=5):
        """
        @summary: Starts a shell instance of SSH to use with multiple commands.

        """
        # large width and height because of need to parse output of commands
        # in exec_shell_command
        retry_count = 0
        while retry_count < retries:
            try:
                self._chan = self.ssh_connection.invoke_shell(width=9999999,
                                                              height=9999999)
                if self._chan is not None:
                    break
            except SSHException as msg:
                retry_count = retry_count + 1
                self._log.error("Channel attempt {0} failed \n {1}".format(
                    retry_count,
                    msg))

        # wait until buffer has data
        while not self._chan.recv_ready():
            time.sleep(1)

        # clearing initial buffer, usually login information
        while self._chan.recv_ready():
            self._chan.recv(1024)

    def end_shell(self):
        """
        @summary: Kills the pseudo terminal if not already closed.
        """
        if not self._chan.closed:
            self._chan.close()
        self._chan = None

    def wait_for_active_shell(self, max_time):
        """
        Opens a chanel and waits until max_time for the chanel
        to be ready for data transmission
        """
        if not self.is_connected():
            message = 'Not currently connected to {host}.'.format(
                host=self.host)
            self._log.error(message)
            raise Exception(message)
        if self._chan is None or self._chan.closed:
            self.start_shell()
        while not self._chan.send_ready() and time.time() < max_time:
            time.sleep(1)

    def read_shell_response(self, prompt, max_time):
        """
        Reads the data from the pseudo terminal until it finds the prompt
        or until max_time.
        """
        output = ''
        while time.time() < max_time:
            while not self._chan.recv_ready() and time.time() < max_time:
                time.sleep(1)
            if not self._chan.recv_ready():
                break
            current = self._chan.recv(1024)
            output += current
            if not prompt:
                break
            if current.find(prompt) != -1:
                self._log.debug('SHELL-PROMPT-FOUND: %s' % prompt)
                break
            self._log.debug('Current response: {0}'.format(current))
            self._log.debug(
                "Looking for prompt: {0}.Time remaining: {1}".format(
                    prompt, max_time - time.time()))
            self._chan.get_transport().set_keepalive(1000)
        self._log.debug('SHELL-COMMAND-RETURN: {0}'.format(output))
        return output

    def execute_shell_command(self,
                              cmd,
                              prompt=None,
                              timeout=100):
        """
        @summary: Executes a command in shell mode and receives all of
            the response.  Parses the response and returns the output
            of the command and the prompt.
        @return: Returns the output of the command and the prompt.

        """

        max_time = time.time() + timeout
        if not cmd.endswith("\n"):
            cmd = "{0}\n".format(cmd)
        self._log.debug('EXEC-SHELLing: {0}'.format(cmd))
        self.wait_for_active_shell(max_time)
        if not self._chan.send_ready():
            self._log.error("Channel timed out for send ready")
            return ExecResponse(
                stdin=None,
                stdout=None,
                stderr=None)
        self._chan.send(cmd)
        output = self.read_shell_response(prompt,
                                          max_time)
        if self._chan.recv_stderr_ready():
            stderr = self._chan.recv_stderr(1024)
        else:
            stderr = None
        return ExecResponse(
            stdin=self._chan.makefile('wb'),
            stdout=output,
            stderr=stderr)

    def execute_command(self, command, return_exit_status=False):
        """
        Executes a command and returns the results.

        @param command: Command to execute
        @type command: string
        @param return_exit_status: Decides if the exit code is included
                                   with the response. If this is set to True,
                                   the function will block until the
                                   response code is determined
        @type return_exit_status: bool
        @return: response
        @rtype: ExecResponse
        """
        if not self.is_connected():
            message = 'Not currently connected to {host}.'.format(
                host=self.host)
            self._log.error(message)
            raise Exception(message)
        try:
            self._log.debug('Executing command: {command}'.format(
                            command=str(command).decode(
                                encoding='UTF-8', errors='ignore')))
        except Exception as exception:
            self._log.debug(exception)
        response = self.ssh_connection.exec_command(
            command=command, return_exit_status=return_exit_status)
        response = self._format_response(response)
        try:
            self._log.debug('Stdout: {stdout}'.format(
                            stdout=str(response.stdout).decode(
                                encoding='UTF-8', errors='ignore')))
        except Exception as exception:
            self._log.debug(exception)
        try:
            self._log.debug('Stderr: {stderr}'.format(
                            stderr=str(response.stderr).decode(
                                encoding='UTF-8', errors='ignore')))
        except Exception as exception:
            self._log.debug(exception)
        try:
            self._log.debug('Exit status: {status}'.format(
                            status=str(response.exit_status).decode(
                                encoding='UTF-8', errors='ignore')))
        except Exception as exception:
            self._log.debug(exception)
        return response


class SSHClient(BaseSSHClient):

    def __init__(self, username=None, password=None, host=None,
                 tcp_timeout=None, auth_strategy=None, port=22,
                 look_for_keys=None, key=None, key_filename=None,
                 allow_agent=True, accept_missing_host_key=True):
        """
        Initialization
        @param username: Username to be used for SSH connection
        @type username: string
        @param password: Password to be used for SSH connection
        @type password: string
        @param host: IP address or host name to connect to
        @type host: string
        @param auth_strategy: Authentication strategy to use to connect
        @type auth_strategy: string
        @param port: Port to use for the SSH connection
        @type port: int
        @param look_for_keys: Whether the client should look for
               local look_for_keys
        @type look_for_keys: bool
        @param key: Text of an SSH key to be used to connect
        @type key: string
        @param key_filename: Name of a file that contains a SSH key
        @type key_filename: string
        @param allow_agent: Set to False to disable connecting to
                            the SSH agent
        @type allow_agent: bool
        @param accept_missing_host_key: Sets if a SSH connection can
                                        be made to remote server if
                                        the server does not have a
                                        host key in the local system
        @type accept_missing_host_key: bool
        """
        super(SSHClient, self).__init__(host=host)
        self.username = username
        self.password = password
        self.host = host
        self.tcp_timeout = tcp_timeout
        self.auth_strategy = auth_strategy
        self.look_for_keys = look_for_keys
        self.key = key
        self.key_filename = key_filename
        self.allow_agent = allow_agent
        self.port = port
        self.accept_missing_host_key = accept_missing_host_key

    def connect_with_retries(self, retries=10, cooldown=10):
        """
        Attempt to connect via SSH, retrying until a
        time limit has been exceeded.

        @param cooldown: Amount of time to wait between connection attempts
        @type cooldown: int
        @param retries: Number of times to retry connecting
        @type retries: int
        @rtype: bool
        """

        for iteration in range(1, retries + 1):
            self._log.debug('Attempting connection {iteration} of '
                            '{retries} to {host}.'.format(
                                iteration=iteration, retries=retries,
                                host=self.host))
            self.connect(
                username=self.username, password=self.password,
                accept_missing_host_key=self.accept_missing_host_key,
                tcp_timeout=self.tcp_timeout,
                auth_strategy=self.auth_strategy,
                port=self.port, key=self.key,
                allow_agent=self.allow_agent,
                key_filename=self.key_filename)
            if self.is_connected():
                return True
            time.sleep(cooldown)
        return False

    def connect_with_timeout(self, cooldown=10, timeout=600):
        """
        Attempt to connect via SSH, retrying until a
        time limit has been exceeded.

        @param cooldown: Amount of time to wait between connection attempts
        @type cooldown: int
        @param timeout: Amount of time to wait before giving up on connecting
        @type timeout: int
        @rtype: bool
        """

        end_time = time.time() + timeout

        while time.time() < end_time:
            self._log.debug('Attempting connection to {host}.'.format(
                host=self.host))
            self.connect(
                username=self.username, password=self.password,
                accept_missing_host_key=self.accept_missing_host_key,
                tcp_timeout=self.tcp_timeout,
                auth_strategy=self.auth_strategy,
                port=self.port, key=self.key,
                allow_agent=self.allow_agent,
                key_filename=self.key_filename)
            if self.is_connected():
                return True
            time.sleep(cooldown)
        return False

    def transfer_file_to(self, local_path, remote_path):
        """
        Transfers a file from the local machine to the remote
        machine via SFTP.

        @param local_path: Path to transfer file from.
        @type local_path: string
        @param remote_path: Path to transfer file to.
        @param remote_path: string
        @rtype: bool
        """

        sftp_conn = self.ssh_connection.open_sftp()
        try:
            sftp_conn.put(local_path, remote_path)
        except IOError as exception:
            self._log.warning("Error during file transfer: {error}".format(
                error=exception))
            return False
        else:
            sftp_conn.close()
        return True

    def retrieve_file_from(self, local_path, remote_path):
        """
        Transfers a file from the remote machine to the
        local machine via SFTP.

        @param local_path: Path to transfer file to.
        @type local_path: string
        @param remote_path: Path to transfer file from.
        @param remote_path: string
        @rtype: bool
        """

        sftp_conn = self.ssh_connection.open_sftp()
        try:
            sftp_conn.get(remote_path, local_path)
        except IOError as exception:
            self._log.warning("Error during file transfer: {error}".format(
                error=exception))
            return False
        else:
            sftp_conn.close()
        return True
