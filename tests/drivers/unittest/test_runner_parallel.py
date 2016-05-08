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
import glob
import os
import sys
import unittest

from contextlib import contextmanager
from StringIO import StringIO

from cafe.drivers.unittest import runner_parallel
from cafe.drivers.unittest.arguments import ArgumentParser


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


class ParallelRunnerTests(unittest.TestCase):
    """Metatests for the Parrallel Runner."""

    def test_skipped_results_show_when_present(self):
        """Check that skipped test count prints in results if present."""

        virtual_env = os.environ.get('VIRTUAL_ENV', None)
        if virtual_env is None:
            unittest.skip(
                "Can't run this test outside of a Python virtual env")

        config_files = glob.glob(
            "{}/.opencafe/configs/*.config".format(virtual_env))
        if not config_files:
            unittest.skip(
                "Can't run this test without a config file in an "
                "initiated cafe foler (.opencafe/configs)")

        a_config_file = os.path.basename(config_files[0])

        parser = ArgumentParser()
        args = parser.parse_args([a_config_file, 'os'])
        runner = runner_parallel.UnittestRunner(args)
        run_time = 10.5
        datagen_time = 180.4
        with capture(runner.print_results, tests=200, errors=5,
                     failures=10, skipped=4, run_time=run_time,
                     datagen_time=datagen_time) as output:
            expected_text = "FAILED (failures=10, skipped=4, errors=5)\n"

            assert expected_text in output
