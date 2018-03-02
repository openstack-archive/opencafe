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

from importlib import import_module
import os
import unittest

from cafe.drivers.unittest import decorators
from cafe.drivers.unittest.datasets import DatasetList


class DSLSuiteBuilderTests(unittest.TestCase):
    """Metatests for the DSL Suite Builder."""

    def test_FauxDSLFixture_raises_Exception(self):
        """Check that the _FauxDSLFixture raises an exception as expected."""

        faux_fixture = type(
            '_FauxDSLFixture',
            (object,),
            dict(decorators._FauxDSLFixture.__dict__))

        # Check that the fixture raises an exception
        with self.assertRaises(decorators.EmptyDSLError) as e:
            faux_fixture().setUpClass()

        # If it does, let's make sure the exception generates the correct
        # message.
        msg = (
            "The Dataset list used to generate this Data Driven Class was "
            "empty. No Fixtures or Tests were generated. Review the Dataset "
            "used to run this test.\n"
            "Dataset List location: None\n\n"
            "The following 0 tests were not run\n\t")

        self.assertEqual(msg, e.exception.message)

    def test_skipped_fixture_does_not_raise_EmptyDSLError(self):
        """Ensure a skipped Fixture doesn't generate _FauxDSLFixtures"""

        # Minimal setup required to instantiate a DataDrivenClass
        os.environ['CAFE_ENGINE_CONFIG_FILE_PATH'] = '/tmp'
        os.environ['CAFE_TEST_LOG_PATH'] = '/tmp/log'

        # Define a skipped TestClass with an empty DSL
        @decorators.DataDrivenClass(DatasetList())
        @unittest.skip('This test is skipped')
        class MyTestCase(unittest.TestCase):
            """A dummy test fixture"""

        # Ensure that DSL_EXCEPTION class wanted generated
        module = import_module(MyTestCase.__module__)
        self.assertFalse(
            hasattr(module, 'MyTestCase_DSL_EXCEPTION_0'),
            'EmptyDSLError should not be raised on skipped tests')
