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

'''
@summary: Base Classes for Test Fixtures
@note: Corresponds DIRECTLY TO A unittest.TestCase
@see: http://docs.python.org/library/unittest.html#unittest.TestCase
'''
import unittest2 as unittest
from datetime import datetime

from cafe.engine.config import EngineConfig
from cafe.common.reporting import cclogging
from cafe.common.reporting.metrics import TestRunMetrics
from cafe.common.reporting.metrics import TestResultTypes
from cafe.common.reporting.metrics import PBStatisticsLog

engine_config = EngineConfig()


class BaseTestFixture(unittest.TestCase):
    '''
    @summary: Foundation for TestRepo Test Fixture.
    @note: This is the base class for ALL test cases in TestRepo. Add new
           functionality carefully.
    @see: http://docs.python.org/library/unittest.html#unittest.TestCase
    '''
    @classmethod
    def assertClassSetupFailure(cls, message):
        '''
        @summary: Use this if you need to fail from a Test Fixture's
                  setUpClass() method
        '''
        cls.fixture_log.error("FATAL: %s:%s" % (cls.__name__, message))
        raise AssertionError("FATAL: %s:%s" % (cls.__name__, message))

    @classmethod
    def assertClassTeardownFailure(cls, message):
        '''
        @summary: Use this if you need to fail from a Test Fixture's
                  tearUpClass() method
        '''
        cls.fixture_log.error("FATAL: %s:%s" % (cls.__name__, message))
        raise AssertionError("FATAL: %s:%s" % (cls.__name__, message))

    def shortDescription(self):
        '''
        @summary: Returns a one-line description of the test 
        '''
        if self._testMethodDoc is not None:
            if self._testMethodDoc.startswith("\n") is True:
                self._testMethodDoc = " ".join(
                    self._testMethodDoc.splitlines()).strip()
        return unittest.TestCase.shortDescription(self)

    @classmethod
    def setUpClass(cls):
        super(BaseTestFixture, cls).setUpClass()

        #Master Config Provider

        #Setup root log handler only if the root logger doesn't already haves
        if cclogging.getLogger('').handlers == []:
            cclogging.getLogger('').addHandler(
                cclogging.setup_new_cchandler('cc.master'))

        #Setup fixture log, which is really just a copy of the master log
        #for the duration of this test fixture
        cls.fixture_log = cclogging.getLogger('')
        cls._fixture_log_handler = cclogging.setup_new_cchandler(
            cclogging.get_object_namespace(cls))
        cls.fixture_log.addHandler(cls._fixture_log_handler)
        
        '''
        @todo: Upgrade the metrics to be more unittest compatible. Currently the 
        unittest results are not available at the fixture level, only the test case
        or the test suite and runner level.
        '''
        # Setup the fixture level metrics
        cls.fixture_metrics = TestRunMetrics()
        cls.fixture_metrics.timer.start()

        # Report
        cls.fixture_log.info("{0}".format('=' * 56))
        cls.fixture_log.info("Fixture...: {0}".format(
                             str(cclogging.get_object_namespace(cls))))
        cls.fixture_log.info("Created At: {0}"
                             .format(cls.fixture_metrics.timer.start_time))
        cls.fixture_log.info("{0}".format('=' * 56))


    @classmethod
    def tearDownClass(cls):
        # Kill the timers and calculate the metrics objects
        cls.fixture_metrics.timer.stop()
        if(cls.fixture_metrics.total_passed == 
           cls.fixture_metrics.total_tests):
            cls.fixture_metrics.result = TestResultTypes.PASSED
        else:
            cls.fixture_metrics.result = TestResultTypes.FAILED
        
        # Report
        cls.fixture_log.info("{0}".format('=' * 56))
        cls.fixture_log.info("Fixture.....: {0}".format(
                             str(cclogging.get_object_namespace(cls))))
        cls.fixture_log.info("Result......: {0}"
                             .format(cls.fixture_metrics.result))
        cls.fixture_log.info("Start Time..: {0}"
                             .format(cls.fixture_metrics.timer.start_time))
        cls.fixture_log.info("Elapsed Time: {0}"
                             .format(cls.fixture_metrics.timer.get_elapsed_time()))
        cls.fixture_log.info("Total Tests.: {0}"
                             .format(cls.fixture_metrics.total_tests))
        cls.fixture_log.info("Total Passed: {0}"
                             .format(cls.fixture_metrics.total_passed))
        cls.fixture_log.info("Total Failed: {0}"
                             .format(cls.fixture_metrics.total_failed))
        cls.fixture_log.info("{0}".format('=' * 56))

        #Remove the fixture log handler from the fixture log
        cls.fixture_log.removeHandler(cls._fixture_log_handler)

        #Call super teardown after we've finished out additions to teardown
        super(BaseTestFixture, cls).tearDownClass()

    def setUp(self):
        # Setup the timer and other custom init jazz
        self.fixture_metrics.total_tests += 1
        self.test_metrics = TestRunMetrics()
        self.test_metrics.timer.start()
        
        # Log header information
        self.fixture_log.info("{0}".format('=' * 56))
        self.fixture_log.info("Test Case.: {0}".format(self._testMethodName))
        self.fixture_log.info("Created.At: {0}".format(self.test_metrics.timer.
                                                       start_time))
        if self.shortDescription():
            self.fixture_log.info("{0}".format(self.shortDescription()))
        self.fixture_log.info("{0}".format('=' * 56))
        
        ''' @todo: Get rid of this hard coded value for the statistics '''
        # set up the stats log
        self.stats_log = PBStatisticsLog("{0}.statistics.csv".format(self._testMethodName), "{0}/../statistics/".format(engine_config.log_directory))

        # Let the base handle whatever hoodoo it needs
        unittest.TestCase.setUp(self)

    def tearDown(self):
        # Kill the timer and other custom destroy jazz
        self.test_metrics.timer.stop()

        ''' 
        @todo: This MUST be upgraded this from resultForDoCleanups into a
               better pattern or working with the result object directly.
               This is related to the todo in L{TestRunMetrics}
        '''
        # Build metrics
        if self._resultForDoCleanups.wasSuccessful():
            self.fixture_metrics.total_passed += 1
            self.test_metrics.result = TestResultTypes.PASSED
        else:
            self.fixture_metrics.total_failed += 1
            self.test_metrics.result = TestResultTypes.FAILED
        
        # Report
        self.fixture_log.info("{0}".format('=' * 56))
        self.fixture_log.info("Test Case...: {0}".
                              format(self._testMethodName))
        self.fixture_log.info("Result......: {0}".
                              format(self.test_metrics.result))
        self.fixture_log.info("Start Time...: {0}".
                              format(self.test_metrics.timer.start_time))
        self.fixture_log.info("Elapsed Time: {0}".
                              format(self.test_metrics.timer.get_elapsed_time()))
        self.fixture_log.info("{0}".format('=' * 56))
        
        # Write out our statistics
        self.stats_log.report(self.test_metrics)

        # Let the base handle whatever hoodoo it needs
        super(BaseTestFixture, self).tearDown()


class BaseParameterizedTestFixture(BaseTestFixture):
    """ TestCase classes that want to be parameterized should
        inherit from this class.
    """
    def __copy__(self):
        new_copy = self.__class__(self._testMethodName)
        for key in self.__dict__.keys():
            new_copy.key = self.__dict__[key]
        return new_copy

    def setUp(self):
        self._testMethodName =  self.__dict__
        super(BaseTestFixture, self).setup()

    def __str__(self):
        if "test_record" in self.__dict__:
            return self._testMethodName + " " + str(self.test_record)
        else:
            return super(BaseParameterizedTestFixture, self).__str__()

class BaseBurnInTestFixture(BaseTestFixture):
    '''
    @summary: Base test fixture that allows for Burn-In tests
    '''
    @classmethod
    def setUpClass(cls):
        super(BaseBurnInTestFixture, cls).setUpClass()
        cls.test_list = []
        cls.iterations = 0
    
    @classmethod
    def addTest(cls, test_case):
        cls.test_list.append(test_case)

    def setUp(self):
        # Let the base handle whatever hoodoo it needs
        super(BaseBurnInTestFixture, self).setUp()
        
    def tearDown(self):
        # Let the base handle whatever hoodoo it needs
        super(BaseBurnInTestFixture, self).tearDown()
