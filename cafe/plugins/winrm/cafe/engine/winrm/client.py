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

import time

from winrm.exceptions import WinRMTransportError
from winrm.protocol import Protocol

from cafe.engine.clients.base import BaseClient
from cafe.engine.winrm.models.winrm_response \
    import WinRMResponse


class BaseWinRMClient(BaseClient):

    def __init__(self, host=None):
        """
        Initialization

        @param host: IP address or host name to connect to
        @type host: string
        """
        super(BaseWinRMClient, self).__init__()
        self.host = host
        self.connection = None
        self.shell_id = None

    def connect(self, username=None, password=None):
        """
        Attempts to connect to a remote server via WinRM.

        @param username: Username to be used for the WinRM connection
        @type username: string
        @param password: Password to be used for the WinRM connection
        @type password: string
        """

        endpoint = 'http://{host}:5985/wsman'.format(host=self.host)

        try:
            self.connection = Protocol(endpoint=endpoint,
                                       username=username,
                                       password=password)
        # Doing a wide catch as the exception handling in WinRM is not
        # very thorough or specific
        except Exception as exception:
            self._log(exception.message)
        else:
            self.shell_id = self.connection.open_shell()

    def is_connected(self):
        """
        Checks to see if a WinRM connection exists.

        @rtype: bool
        """

        return self.connection is not None and self.shell_id is not None

    def _format_response(self, std_out=None, std_err=None, status_code=None):
        """
        Converts the executed command responses into an object.

        @param std_out: The stdout result
        @type std_out: string
        @param std_err: The stderr result
        @type std_err: string
        @param status_code: The status code of the executed command
        @type status_code: int
        @rtype: WinRMResponse
        """
        response = WinRMResponse(std_out=std_out, std_err=std_err,
                                 status_code=status_code)
        return response

    def execute_command(self, command=None, args=None):
        """
        Executes a command via remote shell.

        @param command: The command to execute
        @type command: string
        @param args: A list of arguments to pass to the command
        @type args: list of strings
        @return: Result of command execution
        @rtype: WinRMResponse
        """

        if not self.is_connected():
            message = 'Not currently connected to {host}.'.format(
                host=self.host)
            self._log.error(message)
            raise Exception(message)

        if args is None:
            args = []

        self._log.debug('Executing command: {command} {args}'.format(
            command=command, args=' '.join(args)))
        command_id = self.connection.run_command(self.shell_id, command, args)
        std_out, std_err, status_code = self.connection.get_command_output(
            self.shell_id, command_id)
        response = self._format_response(
            std_out=std_out, std_err=std_err, status_code=status_code)
        self._log.debug('Stdout: {std_out}'.format(std_out=response.std_out))
        self._log.debug('Stderr: {std_err}'.format(std_err=response.std_err))
        self._log.debug('Status code: {status_code}'.format(
            status_code=response.status_code))
        return response


class WinRMClient(BaseWinRMClient):

    def __init__(self, username=None, password=None, host=None):
        """
        Initialization

        @param username: Username to be used for WinRM connection
        @type username: string
        @param password: Password to be used for WinRM connection
        @type password: string
        @param host: IP address or host name to connect to
        @type host: string
        """

        super(WinRMClient, self).__init__(host=host)
        self.username = username
        self.password = password
        self.host = host

    def connect_with_retries(self, retries=10, cooldown=10):
        """
        Attempt to connect via WinRM, retrying until a
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
            try:
                self.connect(username=self.username, password=self.password)
            except WinRMTransportError as exception:
                self._log.error(exception.message)
            if self.is_connected():
                return True
            time.sleep(cooldown)
        return False

    def connect_with_timeout(self, cooldown=10, timeout=600):
        """
        Attempt to connect via WinRM, retrying until a
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
            self.connect(username=self.username, password=self.password)
            if self.is_connected():
                return True
            time.sleep(cooldown)
        return False
