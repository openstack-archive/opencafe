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


class WinRMResponse(object):

    def __init__(self, std_out=None,
                 std_err=None, status_code=None):
        """
        Initialization

        @param std_out: Text from the stdout stream
        @type std_out: string
        @param std_err: Text from the stderr stream
        @type std_err: string
        @param status_code: Exit status code of the command
        @type status_code: int
        """

        self.std_out = std_out
        self.std_err = std_err
        self.status_code = status_code
