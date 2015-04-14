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


def get_range_data(data, bytes_):
    """
    Assists with testing HTTP calls which use the Range header.
    Should emulate the behavior of the Range header (RFC 2616):
    http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html#sec14.35

    @type  data: string
    @param data: The data that you are making the range request against.
    @type  bytes_: string
    @param bytes_: The range in bytes that you want returned.  Given a
                   10,000 byte data, the following bytes_ value:
                       '0-499' returns the first 500 bytes of data
                       '500-999 returns the second 500 bytes of data
                       '-500' or '9500-' returns thet final 500 bytes of data
    @rtype:  string
    @return: a substring of data representing the range requested.
    """
    if bytes_.startswith('-') or bytes_.endswith('-'):
        end = len(data)
        if bytes_.startswith('-'):
            start = end - int(bytes_.strip('-'))
        else:
            start = int(bytes_.strip('-'))
    else:
        (start, end) = [int(x) for x in bytes_.split('-')]
    return data[start:end + 1]
