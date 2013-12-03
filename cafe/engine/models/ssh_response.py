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


class ExecResponse(object):

    def __init__(self, stdin=None, stdout=None,
                 stderr=None, exit_status=None):
        """
        Initialization

        @param stdin: stdin stream resulting from a command execution
        @type stdin: stream
        @param stdout: Text from the stdout stream
        @type stdout: string
        @param stderr: Text from the stderr stream
        @type stderr: string
        @param exit_status: Exit status code of the command
        @type exit_status: int
        """
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.exit_status = exit_status


class SSHKeyResponse(object):

    def __init__(self, public_key=None, private_key=None, error=None):

        self.public_key = public_key
        self.private_key = private_key
        self.error = error
