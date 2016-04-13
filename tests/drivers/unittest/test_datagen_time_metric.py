# Copyright 2016 Rackspace
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

from contextlib import contextmanager
from StringIO import StringIO
import unittest
import sys

from cafe.drivers.unittest.runner_parallel import UnittestRunner


@contextmanager
def captured_output():
    """STDOUT context manager for testing prints to terminal."""
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


class ParallelRunnerTimingTests(unittest.TestCase):
    """
    Metatests for the parallel runner.
    """

    def test_compile_results(self):
        """
        Check that the parallel runner calculates new time metrics
        correctly.
        """

        runner = UnittestRunner()

        with captured_output as (out, err):
            runner.compile_results(times, times2)
        output = out

