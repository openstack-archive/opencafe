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

import argparse
import mock
import os
import sys
import unittest

from contextlib import contextmanager
from six import StringIO

from cafe.drivers.unittest import runner_parallel


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


class TestUnittestRunner(runner_parallel.UnittestRunner):
    def __init__(self):
        self.test_env = mock.Mock(test_log_dir='test_dir')


class ParallelRunnerTests(unittest.TestCase):
    """Metatests for the Parrallel Runner."""
    def setUp(self):
        self.runner = TestUnittestRunner()
        self.run_time = 10.5
        self.datagen_time = 180.4

    def test_skipped_results_show_when_present(self):
        """Check that skipped test count prints in results if present."""

        with capture(self.runner.print_results, tests=200, errors=0,
                     failures=0, skipped=4, run_time=self.run_time,
                     datagen_time=self.datagen_time) as output:
            expected_text = "FAILED (skipped=4)\n"

            assert expected_text in output

    def test_error_results_show_when_present(self):
        """Check that errored test count prints in results if present."""

        with capture(self.runner.print_results, tests=200, errors=5,
                     failures=0, skipped=0, run_time=self.run_time,
                     datagen_time=self.datagen_time) as output:
            expected_text = "FAILED (errors=5)\n"

            assert expected_text in output

    def test_failures_results_show_when_present(self):
        """Check that errored test count prints in results if present."""

        with capture(self.runner.print_results, tests=200, errors=0,
                     failures=6, skipped=0, run_time=self.run_time,
                     datagen_time=self.datagen_time) as output:
            expected_text = "FAILED (failures=6)\n"

            assert expected_text in output

    def test_all_failed_results_show_when_present(self):
        """Check that errored test count prints in results if present."""

        with capture(self.runner.print_results, tests=200, errors=9,
                     failures=7, skipped=8, run_time=self.run_time,
                     datagen_time=self.datagen_time) as output:
            expected_text = "FAILED (failures=7, skipped=8, errors=9)\n"

            assert expected_text in output
