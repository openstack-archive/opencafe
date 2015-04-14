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

from time import sleep
from cafe.drivers.unittest.decorators import (
    tags, DataDrivenFixture, data_driven_test, DataDrivenClass)
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture

DATASET = [1, 2]
SLEEP_TIME = 0


class TestDataGenerator(DatasetList):
    """Data generator"""
    def __init__(self):
        super(TestDataGenerator, self).__init__()

        for num in DATASET:
            self.append_new_dataset(
                name=str(num),
                data_dict={'num': num})


class TestFixture(BaseTestFixture):
    """Test Fixture for tests"""
    @classmethod
    def setUpClass(cls):
        super(TestFixture, cls).setUpClass()
        sleep(SLEEP_TIME)
        cls.fixture_log.error(cls.__name__)


class NoDataGenerator(TestFixture):
    """Testing Non Data Generated class/test"""
    def test_pass(self):
        """Testing pass case"""
        sleep(SLEEP_TIME)
        self.assertIn(1, DATASET)
        self.fixture_log.error("%s Pass", self.__class__.__name__)

    def test_fail(self):
        """Testing failure case"""
        sleep(SLEEP_TIME)
        self.fixture_log.error("%s Fail", self.__class__.__name__)
        self.assertIn(9, DATASET)

    def test_error(self):
        """Testing error case"""
        sleep(SLEEP_TIME)
        self.fixture_log.error("%s Error", self.__class__.__name__)
        raise Exception


@DataDrivenFixture
class DataGeneratedTests(TestFixture):
    """Testing Data Driven Tests"""
    @tags("value", "value1", key='value')
    @data_driven_test(TestDataGenerator())
    def ddtest_pass(self, num):
        """Testing pass case"""
        sleep(SLEEP_TIME)
        self.assertIn(num, DATASET)
        self.fixture_log.error("%s Pass", self.__class__.__name__)

    @tags("value", "value1", key='value')
    @data_driven_test(TestDataGenerator())
    def ddtest_fail(self, num):
        """Testing failure case"""
        sleep(SLEEP_TIME)
        self.fixture_log.error("%s Fail", self.__class__.__name__)
        self.assertNotIn(num, DATASET)

    @tags("value", "value1", key='value')
    @data_driven_test(TestDataGenerator())
    def ddtest_error(self, num):
        """Testing error case"""
        sleep(SLEEP_TIME)
        self.fixture_log.error("%s Error", self.__class__.__name__)
        raise Exception(num)


@DataDrivenClass(TestDataGenerator())
class DataGeneratedClasses(NoDataGenerator):
    """Testing Data Driven Classes"""
    pass


@DataDrivenClass(TestDataGenerator())
class DataGeneratedClassesAndTests(DataGeneratedTests):
    """Testing Data Driven Classes with Data Driven Tests"""
    pass


class SetupFailNoDataGenerator(NoDataGenerator):
    """Testing setUpClass failure for SetupFailNoDataGenerator"""
    @classmethod
    def setUpClass(cls):
        super(SetupFailNoDataGenerator, cls).setUpClass()
        raise Exception


class SetupFailDataGeneratedTests(DataGeneratedTests):
    """Testing setUpClass failure for SetupFailDataGeneratedTests"""
    @classmethod
    def setUpClass(cls):
        super(SetupFailDataGeneratedTests, cls).setUpClass()
        raise Exception


@DataDrivenClass(TestDataGenerator())
class SetupFailDataGeneratedClasses(DataGeneratedClasses):
    """Testing setUpClass failure for SetupFailDataGeneratedClasses"""
    @classmethod
    def setUpClass(cls):
        super(SetupFailDataGeneratedClasses, cls).setUpClass()
        raise Exception


@DataDrivenClass(TestDataGenerator())
class SetupFailDataGeneratedClassesAndTests(DataGeneratedClassesAndTests):
    """Testing setUpClass failure for SetupFailDataGeneratedClassesAndTests"""
    @classmethod
    def setUpClass(cls):
        super(SetupFailDataGeneratedClassesAndTests, cls).setUpClass()
        raise Exception
