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

"""
@summary: Base Classes for Test Fixtures
@note: Corresponds DIRECTLY TO A unittest.TestCase
@see: http://docs.python.org/library/unittest.html#unittest.TestCase
"""
import os
import re
import unittest2 as unittest

from cafe.drivers.base import FixtureReporter
from cafe.common.reporting.cclogging import init_root_log_handler


class BaseTestFixture(unittest.TestCase):
    """
    @summary: This should be used as the base class for any unittest tests,
              meant to be used instead of unittest.TestCase.
    @see: http://docs.python.org/library/unittest.html#unittest.TestCase
    """
    def shortDescription(self):
        """
        @summary: Returns a formatted description of the test
        """
        short_desc = None

        if os.environ.get("VERBOSE", None) == "true" and self._testMethodDoc:
            temp = self._testMethodDoc.strip("\n")
            short_desc = re.sub(r"[ ]{2,}", "", temp).strip("\n")
        return short_desc

    def logDescription(self):
        log_desc = None
        if self._testMethodDoc:
            log_desc = "\n{0}".format(
                re.sub(r"[ ]{2,}", "", self._testMethodDoc).strip("\n"))
        return log_desc

    @classmethod
    def assertClassSetupFailure(cls, message):
        """
        @summary: Use this if you need to fail from a Test Fixture's
                  setUpClass() method
        """
        cls.fixture_log.error("FATAL: %s:%s" % (cls.__name__, message))
        raise AssertionError("FATAL: %s:%s" % (cls.__name__, message))

    @classmethod
    def assertClassTeardownFailure(cls, message):
        """
        @summary: Use this if you need to fail from a Test Fixture's
                  tearUpClass() method
        """
        cls.fixture_log.error("FATAL: %s:%s" % (cls.__name__, message))
        raise AssertionError("FATAL: %s:%s" % (cls.__name__, message))

    @classmethod
    def setUpClass(cls):
        super(BaseTestFixture, cls).setUpClass()
        #Move root log handler initialization to the runner!
        init_root_log_handler()
        cls._reporter = FixtureReporter(cls)
        cls.fixture_log = cls._reporter.logger.log
        cls._reporter.start()

    @classmethod
    def tearDownClass(cls):
        cls._reporter.stop()
        # Call super teardown after to avoid tearing down the class before we
        # can run our own tear down stuff.
        super(BaseTestFixture, cls).tearDownClass()

    def setUp(self):
        self.shortDescription()
        self._reporter.start_test_metrics(
            self.__class__.__name__, self._testMethodName,
            self.logDescription())
        super(BaseTestFixture, self).setUp()

    def tearDown(self):
        """
        @todo: This MUST be upgraded this from resultForDoCleanups into a
               better pattern or working with the result object directly.
               This is related to the todo in L{TestRunMetrics}
        """
        if any(r for r in self._resultForDoCleanups.failures
               if self._test_name_matches_result(self._testMethodName, r)):
            self._reporter.stop_test_metrics(self._testMethodName, 'Failed')
        elif any(r for r in self._resultForDoCleanups.errors
                 if self._test_name_matches_result(self._testMethodName, r)):
            self._reporter.stop_test_metrics(self._testMethodName, 'ERRORED')
        else:
            self._reporter.stop_test_metrics(self._testMethodName, 'Passed')

        # Let the base handle whatever hoodoo it needs
        super(BaseTestFixture, self).tearDown()

    def _test_name_matches_result(self, name, test_result):
        """Checks if a test result matches a specific test name."""
        # Try to get the result portion of the tuple
        try:
            result = test_result[0]
        except IndexError:
            return False

        # Verify the object has the correct property
        if hasattr(result, '_testMethodName'):
            return result._testMethodName == name
        else:
            return False


class BaseBurnInTestFixture(BaseTestFixture):
    """
    @summary: Base test fixture that allows for Burn-In tests
    """
    @classmethod
    def setUpClass(cls):
        super(BaseBurnInTestFixture, cls).setUpClass()
        cls.test_list = []
        cls.iterations = 0

    @classmethod
    def addTest(cls, test_case):
        cls.test_list.append(test_case)
