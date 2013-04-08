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
import socket
import exceptions
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from paramiko.resource import ResourceManager
    from paramiko.client import SSHClient
    import paramiko

from cafe.common.reporting import cclogging
from cafe.engine.clients.base import BaseClient


class SSHBaseClient(BaseClient):

    _log = cclogging.getLogger(__name__)

    def __init__(self, host, username, password, timeout=20, port=22):
        super(SSHBaseClient, self).__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = int(timeout)
        self._chan = None

    def _get_ssh_connection(self):
        """Returns an ssh connection to the specified host"""
        _timeout = True
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        _start_time = time.time()
        saved_exception = exceptions.StandardError()
        #doing this because the log file fills up with these messages
        #this way it only logs it once
        log_attempted = False
        socket_error_logged = False
        auth_error_logged = False
        ssh_error_logged = False
        while not self._is_timed_out(self.timeout, _start_time):
            try:
                if not log_attempted:
                    self._log.debug('Attempting to SSH connect to: ')
                    self._log.debug('host: %s, username: %s, password: %s' %
                                    (self.host, self.username, self.password))
                    log_attempted = True
                ssh.connect(hostname=self.host,
                            username=self.username,
                            password=self.password,
                            timeout=20,
                            key_filename=[],
                            look_for_keys=False,
                            allow_agent=False)
                _timeout = False
                break
            except socket.error as e:
                if not socket_error_logged:
                    self._log.error('Socket Error: %s' % str(e))
                    socket_error_logged = True
                saved_exception = e
                continue
            except paramiko.AuthenticationException as e:
                if not auth_error_logged:
                    self._log.error('Auth Exception: %s' % str(e))
                    auth_error_logged = True
                saved_exception = e
                time.sleep(2)
                continue
            except paramiko.SSHException as e:
                if not ssh_error_logged:
                    self._log.error('SSH Exception: %s' % str(e))
                    ssh_error_logged = True
                saved_exception = e
                time.sleep(2)
                continue
                #Wait 2 seconds otherwise
            time.sleep(2)
        if _timeout:
            self._log.error('SSHConnector timed out while trying to establish a connection')
            raise saved_exception

        #This MUST be done because the transport gets garbage collected if it
        #is not done here, which causes the connection to close on invoke_shell
        #which is needed for exec_shell_command
        ResourceManager.register(self, ssh.get_transport())
        return ssh

    def _is_timed_out(self, timeout, start_time):
        return (time.time() - timeout) > start_time

    def connect_until_closed(self):
        """Connect to the server and wait until connection is lost"""
        try:
            ssh = self._get_ssh_connection()
            _transport = ssh.get_transport()
            _start_time = time.time()
            _timed_out = self._is_timed_out(self.timeout, _start_time)
            while _transport.is_active() and not _timed_out:
                time.sleep(5)
                _timed_out = self._is_timed_out(self.timeout, _start_time)
            ssh.close()
        except (EOFError, paramiko.AuthenticationException, socket.error):
            return

    def exec_command(self, cmd):
        """Execute the specified command on the server.

        :returns: data read from standard output of the command

        """
        self._log.debug('EXECing: %s' % str(cmd))
        ssh = self._get_ssh_connection()
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read()
        ssh.close()
        self._log.debug('EXEC-OUTPUT: %s' % str(output))
        return output

    def test_connection_auth(self):
        """ Returns true if ssh can connect to server"""
        try:
            connection = self._get_ssh_connection()
            connection.close()
        except paramiko.AuthenticationException:
            return False

        return True

    def start_shell(self):
        """Starts a shell instance of SSH to use with multiple commands."""
        #large width and height because of need to parse output of commands
        #in exec_shell_command
        self._chan = self._get_ssh_connection().invoke_shell(width=9999999,
                                                             height=9999999)
        #wait until buffer has data
        while not self._chan.recv_ready():
            time.sleep(1)
            #clearing initial buffer, usually login information
        while self._chan.recv_ready():
            self._chan.recv(1024)

    def exec_shell_command(self, cmd, stop_after_send=False):
        """
        Executes a command in shell mode and receives all of the response.
        Parses the response and returns the output of the command and the
        prompt.
        """
        if not cmd.endswith('\n'):
            cmd = '%s\n' % cmd
        self._log.debug('EXEC-SHELLing: %s' % cmd)
        if self._chan is None or self._chan.closed:
            self.start_shell()
        while not self._chan.send_ready():
            time.sleep(1)
        self._chan.send(cmd)
        if stop_after_send:
            self._chan.get_transport().set_keepalive(1000)
            return None
        while not self._chan.recv_ready():
            time.sleep(1)
        output = ''
        while self._chan.recv_ready():
            output += self._chan.recv(1024)
        self._log.debug('SHELL-COMMAND-RETURN: \n%s' % output)
        prompt = output[output.rfind('\r\n') + 2:]
        output = output[output.find('\r\n') + 2:output.rfind('\r\n')]
        self._chan.get_transport().set_keepalive(1000)
        return output, prompt

    def exec_shell_command_wait_for_prompt(self, cmd, prompt='#', timeout=300):
        """
        Executes a command in shell mode and receives all of the response.
        Parses the response and returns the output of the command and the
        prompt.
        """
        if not cmd.endswith('\n'):
            cmd = '%s\n' % cmd
        self._log.debug('EXEC-SHELLing: %s' % cmd)
        if self._chan is None or self._chan.closed:
            self.start_shell()
        while not self._chan.send_ready():
            time.sleep(1)
        self._chan.send(cmd)
        while not self._chan.recv_ready():
            time.sleep(1)
        output = ''
        max_time = time.time() + timeout
        while time.time() < max_time:
            current = self._chan.recv(1024)
            output += current
            if current.find(prompt) != -1:
                self._log.debug('SHELL-PROMPT-FOUND: %s' % prompt)
                break
            self._log.debug('Current response: %s' % current)
            self._log.debug('Looking for prompt: %s. Time remaining until timeout: %s'
                            % (prompt, max_time - time.time()))
            while not self._chan.recv_ready() and time.time() < max_time:
                time.sleep(5)
            self._chan.get_transport().set_keepalive(1000)
        self._log.debug('SHELL-COMMAND-RETURN: %s' % output)
        prompt = output[output.rfind('\r\n') + 2:]
        output = output[output.find('\r\n') + 2:output.rfind('\r\n')]
        return output, prompt

    def make_directory(self, directory_name):
        self._log.info('Making a Directory')
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.mkdir(directory_name)
        except IOError, exception:
            self._log.warning("Exception in making a directory: %s" % exception)
            return False
        else:
            sftp.close()
            transport.close()
            return True

    def browse_folder(self):
        self._log.info('Browsing a folder')
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.listdir()
        except IOError, exception:
            self._log.warning("Exception in browsing folder file: %s" % exception)
            return False
        else:
            sftp.close()
            transport.close()
            return True

    def upload_a_file(self, server_file_path, client_file_path):
        self._log.info("uploading file from %s to %s"
                                % (client_file_path, server_file_path))
        transport = paramiko.Transport((self.host, self.port))
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.put(client_file_path, server_file_path)
        except IOError, exception:
            self._log.warning("Exception in uploading file: %s" % exception)
            return False
        else:
            sftp.close()
            transport.close()
            return True

    def download_a_file(self, server_filepath, client_filepath):
        transport = paramiko.Transport(self.host)
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.get(server_filepath, client_filepath)
        except IOError:
            return False
        else:
            sftp.close()
            transport.close()
            return True

    def end_shell(self):
        if not self._chan.closed:
            self._chan.close()
        self._chan = None
