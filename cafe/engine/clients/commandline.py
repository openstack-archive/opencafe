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
import sys
from subprocess import Popen, PIPE, CalledProcessError

from cafe.common.reporting.cclogging import log_info_block, logsafe_str
from logging import DEBUG
from cafe.engine.clients.base import BaseClient
from cafe.engine.models.commandline_response import CommandLineResponse


class BaseCommandLineClient(BaseClient):
    """
    Provides low level connectivity to the commandline via popen()

    Primarily intended to serve as base classes for a specific command line
    client Class. This class is dependent on a local installation of the
    wrapped client process. The thing you run has to be there!
    """

    def __init__(self, base_command=None, env_var_dict=None):
        """
        :param base_command: This shell command to execute, e.g. 'ls' or 'pwd'
        :param dict env_var_dict: Environment variables to inject into env
                                  before execution.
        """

        super(BaseCommandLineClient, self).__init__()
        self.base_command = base_command
        self.env_var_dict = env_var_dict or {}
        self.set_environment_variables(self.env_var_dict)

    def set_environment_variables(self, env_var_dict=None):
        """Sets all os environment variables provided in env_var_dict"""

        self.env_var_dict = env_var_dict
        for key, value in list(self.env_var_dict.items()):
            self._log.debug('setting {0}={1}'.format(key, value))
            os.environ[str(key)] = str(value)

    def update_environment_variables(self, env_var_dict=None):
        """Sets all os environment variables provided in env_var_dict"""

        self.env_var_dict = self.env_var_dict.update(env_var_dict or {})
        for key, value in list(self.env_var_dict.items()):
            self._log.debug('setting {0}={1}'.format(key, value))
            os.environ[str(key)] = str(value)

    def unset_environment_variables(self, env_var_list=None):
        """Unsets all os environment variables provided in env_var_dict
        by default.
        If env_var_list is passed, attempts to unset all environment vars in
        list"""

        env_var_list = env_var_list or list(self.env_var_dict.keys()) or []
        for key, _ in env_var_list:
            self._log.debug('unsetting {0}'.format(key))
            os.unsetenv(str(key))

    def _build_command(self, cmd, *args):
        # Process command we received
        command = "{0} {1}".format(
            self.base_command, cmd) if self.base_command else cmd
        if args and args[0]:
            for arg in args[0]:
                command += "{0} {1}".format(command, arg)

        keys = set(os.environ).intersection(self.env_var_dict)
        set_env_vars = dict([(k, os.environ[k]) for k in keys])

        info = [
            ("command", logsafe_str(command)),
            ("args", logsafe_str(args)),
            ("set env vars", logsafe_str(set_env_vars))]

        log_info_block(
            self._log, info, heading='COMMAND LINE REQUEST',
            log_level=DEBUG, one_line=True)

        return command

    def _execute_command(self, command):
        # Run the command
        process = None
        try:
            process = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)
        except CalledProcessError as exception:
            self._log.exception(
                "Exception running commandline command {0}\n{1}".format(
                    str(command), str(exception)))
        return process

    def run_command_async(self, cmd, *args):
        """Running a command asynchronously returns a CommandLineResponse
        objecct with a running subprocess.Process object in it.  This process
        needs to be closed or killed manually after execution."""

        os_response = CommandLineResponse()
        os_response.command = self._build_command(cmd, *args)
        os_response.process = self._execute_command(os_response.command)
        return os_response

    def run_command(self, cmd, *args):
        """Sends a command directly to this instance's command line
        @param cmd: Command to sent to command line
        @type cmd: C{str}
        @param args: Optional list of args to be passed with the command
        @type args: C{list}
        @raise exception: If unable to close process after running the command
        @return: The full response details from the command line
        @rtype: L{CommandLineResponse}
        @note: PRIVATE. Can be over-ridden in a child class
        """

        # Wait for the process to complete and then read the output
        os_response = self.run_command_async(cmd, *args)
        std_out, std_err = os_response.process.communicate()
        os_response.standard_out = str(std_out).splitlines()
        os_response.standard_error = str(std_err).splitlines()
        os_response.return_code = os_response.process.returncode

        info = [
            ("return code", logsafe_str(os_response.return_code)),
            ("standard out", logsafe_str("\n{0}".format(
                "\n".join(os_response.standard_out)))),
            ("standard error", logsafe_str("\n{0}".format(
                "\n".join(os_response.standard_error))))]
        log_info_block(
            self._log, info, heading='COMMAND LINE RESPONSE',
            log_level=DEBUG, one_line=True)

        # Clean up the process to avoid any leakage/wonkiness with
        # stdout/stderr
        try:
            os_response.process.kill()
        except OSError:
            # An OS Error is valid if the process has exited. We only
            # need to be concerned about other exceptions
            sys.exc_clear()

        os_response.process = None
        return os_response
