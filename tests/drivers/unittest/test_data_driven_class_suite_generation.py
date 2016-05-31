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

import unittest

from cafe.drivers.unittest import decorators
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture


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


class TestDataGenerator(DatasetList):
    def __init__(self):
        super(TestDataGenerator, self).__init__()
        self.append_new_dataset('test', {'test': 'test'})


@decorators.DataDrivenClass(TestDataGenerator(), skip=True)
class TestClassWithDecoratorSkip(BaseTestFixture):
    """Test that data generator does not run when skip is passed"""

    def test_skipped_data_generation(self):
        self.assertFalse(hasattr(self, 'test'))


@decorators.DataDrivenClass(TestDataGenerator())
class TestClassWithDecoratorNoSkip(BaseTestFixture):
    """Test that data generator still runs when skip is not passed"""

    def test_not_skipped_data_generation(self):
        self.assertEqual(self.test, 'test')
