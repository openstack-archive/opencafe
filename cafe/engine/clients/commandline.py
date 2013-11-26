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

'''Provides low level connectivity to the commandline via popen()
@note: Primarily intended to serve as base classes for a specific
       command line client Class
'''
import os
import sys
import subprocess

from cafe.engine.models.commandline_response import CommandLineResponse
from cafe.engine.clients.base import BaseClient


class BaseCommandLineClient(BaseClient):
    '''Wrapper for driving/parsing a command line program
    @ivar base_command: This processes base command string. (I.E. 'ls', 'pwd')
    @type base_command: C{str}
    @note: This class is dependent on a local installation of the wrapped
           client process.  The thing you run has to be there!
    '''
    def __init__(self, base_command=None, env_var_dict=None):
        '''
        @param base_command: This processes base command string.
                             (I.E. 'ls', 'pwd')
        @type base_command: C{str}
        '''
        super(BaseCommandLineClient, self).__init__()
        self.base_command = base_command
        self.env_var_dict = env_var_dict or {}
        self.set_environment_variables(self.env_var_dict)

    def set_environment_variables(self, env_var_dict=None):
        '''Sets all os environment variables provided in env_var_dict'''
        for key, value in env_var_dict.items():
            self._log.debug('setting {0}={1}'.format(key, value))
            os.putenv(str(key), str(value))

    def unset_environment_variables(self, env_var_list=None):
        '''Unsets all os environment variables provided in env_var_dict
        by default.
        If env_var_list is passed, attempts to unset all environment vars in
        list'''
        env_var_list = env_var_list or self.env_var_dict.keys() or []
        for key, _ in env_var_list:
            self._log.debug('unsetting {0}'.format(key))
            os.unsetenv(str(key))

    def run_command(self, cmd, *args):
        '''Sends a command directly to this instance's command line
        @param cmd: Command to sent to command line
        @type cmd: C{str}
        @param args: Optional list of args to be passed with the command
        @type args: C{list}
        @raise exception: If unable to close process after running the command
        @return: The full response details from the command line
        @rtype: L{CommandLineResponse}
        @note: PRIVATE. Can be over-ridden in a child class
        '''
        os_process = None
        os_response = CommandLineResponse()

        #Process command we received
        os_response.command = "{0} {1}".format(
            self.base_command, cmd) if self.base_command else cmd
        if args and args[0]:
            for arg in args[0]:
                os_response.command += "{0} {1}".format(
                    os_response.command, arg)

        """@TODO: Turn this into a decorator like the rest client"""
        try:
            logline = ''.join([
                '\n{0}\nCOMMAND LINE REQUEST\n{0}\n'.format('-' * 4),
                "args..........: {0}".format(args),
                "command.......: {0}".format(os_response.command)])
        except Exception as exception:
            self._log.exception(exception)

        try:
            self._log.debug(logline.decode('utf-8', 'replace'))
        except Exception as exception:
            #Ignore all exceptions that happen in logging, then log them
            self._log.debug('\n{0}\nCOMMAND LINE REQUEST INFO\n{0}\n'.format(
                '-' * 12))
            self._log.exception(exception)

        #Run the command
        try:
            os_process = subprocess.Popen(os_response.command,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE,
                                          shell=True)
        except subprocess.CalledProcessError() as cpe:
            self._log.exception(
                "Exception running commandline command {0}\n{1}".format(
                    str(os_response.command), str(cpe)))

        #Wait for the process to complete and then read the lines.
        #for some reason if you read each line as the process is running
        #and use os_process.Poll() you don't always get all output
        std_out, std_err = os_process.communicate()
        os_response.return_code = os_process.returncode

        #Pass the full output of the process_command back. It is important to
        #not parse, strip or otherwise massage this output in the private send
        #since a child class could override and contain actual command
        #processing logic.
        os_response.standard_out = str(std_out).splitlines()
        if std_err is not None:
            os_response.standard_error = str(std_err).splitlines()

        """@TODO: Turn this into a decorator like in the rest client"""
        try:
            logline = ''.join([
                '\n{0}\nCOMMAND LINE RESPONSE\n{0}\n'.format('-' * 4),
                "standard out...: {0}".format(os_response.standard_out),
                "standard error.: {0}".format(os_response.standard_error),
                "return code....: {0}".format(os_response.return_code)])
        except Exception as exception:
            self._log.exception(exception)

        try:
            self._log.debug(logline.decode('utf-8', 'replace'))
        except Exception as exception:
            #Ignore all exceptions that happen in logging, then log them
            self._log.debug('\n{0}\nCOMMAND LINE RESPONSE INFO\n{0}\n'.format(
                '-' * 12))
            self._log.exception(exception)

        #Clean up the process to avoid any leakage/wonkiness with stdout/stderr
        try:
            os_process.kill()
        except OSError:
            #An OS Error is valid if the process has exited. We only
            #need to be concerned about other exceptions
            sys.exc_clear()
        except Exception, kill_exception:
            raise Exception(
                "Exception forcing %s Process to close: {0}".format(
                    self.base_command, kill_exception))
        finally:
            del os_process

        return os_response
