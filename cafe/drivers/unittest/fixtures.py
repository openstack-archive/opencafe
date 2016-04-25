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

"""
@summary: Base Classes for Test Fixtures
@note: Corresponds DIRECTLY TO A unittest.TestCase
@see: http://docs.python.org/library/unittest.html#unittest.TestCase
"""
import os
import re
import six
import sys
import unittest

from cafe.drivers.base import FixtureReporter


class BaseTestFixture(unittest.TestCase):
    """
    @summary: This should be used as the base class for any unittest tests,
              meant to be used instead of unittest.TestCase.
    @see: http://docs.python.org/library/unittest.html#unittest.TestCase
    """

    __test__ = True

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
        """
        @summary: Returns a formatted description from the _testMethodDoc
        """
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
        cls.fixture_log.error("FATAL: %s:%s", cls.__name__, message)
        raise AssertionError("FATAL: %s:%s" % (cls.__name__, message))

    @classmethod
    def assertClassTeardownFailure(cls, message):
        """
        @summary: Use this if you need to fail from a Test Fixture's
                  tearUpClass() method
        """
        cls.fixture_log.error("FATAL: %s:%s", cls.__name__, message)
        raise AssertionError("FATAL: %s:%s" % (cls.__name__, message))

    @classmethod
    def setUpClass(cls):
        """@summary: Adds logging/reporting to Unittest setUpClass"""
        super(BaseTestFixture, cls).setUpClass()
        cls._reporter = FixtureReporter(cls)
        cls.fixture_log = cls._reporter.logger.log
        cls._reporter.start()
        cls._class_cleanup_tasks = []

    @classmethod
    def tearDownClass(cls):
        """@summary: Adds stop reporting to Unittest setUpClass"""
        cls._reporter.stop()
        # Call super teardown after to avoid tearing down the class before we
        # can run our own tear down stuff.
        super(BaseTestFixture, cls).tearDownClass()

    def setUp(self):
        """@summary: Logs test metrics"""
        self.shortDescription()
        self._reporter.start_test_metrics(
            self.__class__.__name__, self._testMethodName,
            self.logDescription())
        self._duration = 0.00
        super(BaseTestFixture, self).setUp()

    def tearDown(self):
        """
        @todo: This MUST be upgraded this from resultForDoCleanups into a
               better pattern or working with the result object directly.
               This is related to the todo in L{TestRunMetrics}
        """
        if sys.version_info < (3, 4):
            if six.PY2:
                report = self._resultForDoCleanups
            else:
                report = self._outcomeForDoCleanups

            if any(r for r in report.failures
                   if self._test_name_matches_result(self._testMethodName, r)):
                self._reporter.stop_test_metrics(self._testMethodName,
                                                 'Failed')
            elif any(r for r in report.errors
                     if self._test_name_matches_result(self._testMethodName,
                                                       r)):
                self._reporter.stop_test_metrics(self._testMethodName,
                                                 'ERRORED')
            else:
                self._reporter.stop_test_metrics(self._testMethodName,
                                                 'Passed')
            try:
                self._duration = \
                    self._reporter.test_metrics.timer.get_elapsed_time()
            except AttributeError:
                # If the reporter was not appropriately called at test start
                # or end tests will fail unless we catch this. This is common
                # in the case where test writers did not appropriately call
                # 'super' in the setUp or setUpClass of their fixture or
                # test class.
                self._duration = float('nan')
        else:
            for method, _ in self._outcome.errors:
                if self._test_name_matches_result(self._testMethodName,
                                                  method):
                    self._reporter.stop_test_metrics(self._testMethodName,
                                                     'Failed')
                else:
                    self._reporter.stop_test_metrics(self._testMethodName,
                                                     'Passed')
                self._duration = \
                    self._reporter.test_metrics.timer.get_elapsed_time()

        # Continue inherited tearDown()
        super(BaseTestFixture, self).tearDown()

    @staticmethod
    def _test_name_matches_result(name, test_result):
        """@summary: Checks if a test result matches a specific test name."""
        if sys.version_info < (3, 4):
            # Try to get the result portion of the tuple
            try:
                result = test_result[0]
            except IndexError:
                return False
        else:
            result = test_result

        # Verify the object has the correct property
        if hasattr(result, '_testMethodName'):
            return result._testMethodName == name
        else:
            return False

    @classmethod
    def _do_class_cleanup_tasks(cls):
        """@summary: Runs class cleanup tasks added during testing"""
        for func, args, kwargs in reversed(cls._class_cleanup_tasks):
            cls.fixture_log.debug(
                "Running class cleanup task: %s(%s, %s)",
                func.__name__,
                ", ".join([str(arg) for arg in args]),
                ", ".join(["{0}={1}".format(
                    str(k), str(kwargs[k])) for k in kwargs]))
            try:
                func(*args, **kwargs)
            except Exception as exception:
                # Pretty prints method signature in the following format:
                # "classTearDown failure: Unable to execute FnName(a, b, c=42)"
                cls.fixture_log.exception(exception)
                cls.fixture_log.error(
                    "classTearDown failure: Exception occured while trying to"
                    " execute class teardown task: %s(%s, %s)",
                    func.__name__,
                    ", ".join([str(arg) for arg in args]),
                    ", ".join(["{0}={1}".format(
                        str(k), str(kwargs[k])) for k in kwargs]))

    @classmethod
    def addClassCleanup(cls, function, *args, **kwargs):
        """@summary: Named to match unittest's addCleanup.
        ClassCleanup tasks run if setUpClass fails, or after tearDownClass.
        (They don't depend on tearDownClass running)
        """

        cls._class_cleanup_tasks.append((function, args or [], kwargs or {}))


class BaseBurnInTestFixture(BaseTestFixture):
    """
    @summary: Base test fixture that allows for Burn-In tests
    """
    @classmethod
    def setUpClass(cls):
        """@summary: inits burning testing variables"""
        super(BaseBurnInTestFixture, cls).setUpClass()
        cls.test_list = []
        cls.iterations = 0

    @classmethod
    def addTest(cls, test_case):
        """@summary: Adds a test case"""
        cls.test_list.append(test_case)
