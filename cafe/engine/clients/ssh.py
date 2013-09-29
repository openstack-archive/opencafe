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

import paramiko
import socket
import StringIO
import time
from paramiko.client import SSHClient as ParamikoSSHClient
from paramiko.resource import ResourceManager

from cafe.engine.clients.base import BaseClient
from cafe.common.reporting import cclogging


class SSHAuthStrategy:
    PASSWORD = 'password'
    LOCAL_KEY = 'local_key'
    KEY_STRING = 'key_string'
    KEY_FILE_LIST = 'key_file_list'


class ExecResponse(object):

    def __init__(self, stdin=None, stdout=None, stderr=None, exit_status=None):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.exit_status = exit_status


class SSHClient(ParamikoSSHClient):

    def exec_command(self, command, bufsize=-1, timeout=None, get_pty=False,
                         return_exit_status=False):
        """Re-implements exec_command to optionally return an
        exit status code."""
        chan = self._transport.open_session()
        if(get_pty):
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
        return {stdin: stdin, stdout: stdout, stderr: stderr}


class BaseSSHClient(BaseClient):

    _log = cclogging.getLogger(__name__)

    def __init__(self, host):
        self.ssh_connection = None
        self.host = host

    def connect(self, username=None, password=None, accept_missing_host_key=True,
                tcp_timeout=None, auth_strategy=None, port=22, key=None,
                allow_agent=None, key_filename=None):

        ssh = SSHClient()
        if accept_missing_host_key:
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_args = {'hostname': self.host, 'username': username,
                        'timeout': tcp_timeout, 'port': port,
                        'allow_agent': allow_agent}

        self._log.debug('Attempting to SSH connect to {host} with user {user}.'.format(host=self.host, user=username))
        if auth_strategy == SSHAuthStrategy.PASSWORD:
            connect_args['password'] = password
        if auth_strategy == SSHAuthStrategy.LOCAL_KEY:
            connect_args['look_for_keys'] = True
        if auth_strategy == SSHAuthStrategy.KEY_STRING:
            key_file = StringIO.StringIO(key)
            key = paramiko.RSAKey.from_private_key(key_file)
            connect_args['pkey'] = key
        if auth_strategy == SSHAuthStrategy.KEY_FILE_LIST:
            connect_args['key_filename'] = key_filename

        try:
            ssh.connect(**connect_args)
        except socket.error as e:
            self._log.error('Socket Error: %s' % str(e))
        except paramiko.AuthenticationException as e:
            self._log.error('Authentication Exception: %s' % str(e))
        except paramiko.SSHException as e:
            self._log.error('SSH Exception: %s' % str(e))

        ResourceManager.register(self, ssh.get_transport())
        self.ssh_connection = ssh

    def _format_response(self, resp_dict):
        stdout = resp_dict.get('stdout').read()
        stderr = resp_dict.get('stderr').read()
        response = ExecResponse(stdin=resp_dict.get('stdin'), stdout=stdout,
                                stderr=stderr, exit_status=resp_dict.get('exit_status'))
        return response

    def is_connected(self):
        return self.ssh_connection is not None

    def execute_command(self, command):
        if not self.is_connected():
            message = 'Not currently connected to {host}.'.format(host=self.host)
            self._log.error(message)
            raise Exception(message)
        self._log.debug('Executing command: {command}'.format(command=command))
        response = self.ssh_connection.exec_command(command=command,
                                                    return_exit_status=True)
        response = self._format_response(response)
        self._log.debug('Stdout: {stdout}'.format(stdout=response.stdout))
        self._log.debug('Stderr: {stderr}'.format(stderr=response.stderr))
        return response


class SSHBehaviors(BaseSSHClient):

    def __init__(self, username=None, password=None, host=None,
                 tcp_timeout=None, auth_strategy=None, port=22,
                 look_for_keys=None, key=None, key_filename=None,
                 allow_agent=None, accept_missing_host_key=True):

        super(SSHBehaviors, self).__init__(host=host)
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
        for iteration in range(1, retries + 1):
            self._log.debug('Attempting connection {iteration} of {retries} to {host}'.format(
                iteration=iteration, retries=retries, host=self.host))
            try:
                self.connect(username=self.username, password=self.password,
                             accept_missing_host_key=self.accept_missing_host_key,
                             tcp_timeout=self.tcp_timeout, auth_strategy=self.auth_strategy,
                             port=self.port, key=self.key, allow_agent=self.allow_agent,
                             key_filename=self.key_filename)
                return True
            except Exception:
                time.sleep(cooldown)
        return False

    def connect_with_timeout(self, timeout):
        # Still need to implement
        pass

    def transfer_file_to(self, local_path, remote_path):
        sftp_conn = self.ssh_connection.open_sftp()
        try:
            sftp_conn.put(local_path, remote_path)
        except IOError, exception:
            self._log.warning("Error during file transfer: {error}".format(exception))
            return False
        else:
            sftp_conn.close()
        return True

    def retrieve_file_from(self, local_path, remote_path):
        sftp_conn = self.ssh_connection.open_sftp()
        try:
            sftp_conn.get(remote_path, local_path)
        except IOError, exception:
            self._log.warning("Error during file transfer: {error}".format(exception))
            return False
        else:
            sftp_conn.close()
        return True
