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

from __future__ import print_function
import sys
from traceback import print_exc


def print_exception(file_=None, method=None, value=None, exception=None):
    """
        Prints exceptions in a standard format to stderr.
    """
    print("{0}".format("=" * 70), file=sys.stderr)
    if file_:
        print("{0}:".format(file_), file=sys.stderr, end=" ")
    if method:
        print("{0}:".format(method), file=sys.stderr, end=" ")
    if value:
        print("{0}:".format(value), file=sys.stderr, end=" ")
    if exception:
        print("{0}:".format(exception), file=sys.stderr, end=" ")
    print("\n{0}".format("-" * 70), file=sys.stderr)
    if exception is not None:
        print_exc(file=sys.stderr)
    print(file=sys.stderr)


def get_error(exception=None):
    """Gets errno from exception or returns one"""
    return getattr(exception, "errno", 1)
