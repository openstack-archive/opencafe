import os
from cafe.common.reporting.cclogging import \
    get_object_namespace, getLogger, setup_new_cchandler, log_info_block
from cafe.common.reporting.metrics import \
    TestRunMetrics, TestResultTypes, PBStatisticsLog


class _FixtureLogger(object):
    """Provides logging for any test fixture"""
    def __init__(self, parent_object):
        self.log = getLogger('')
        self.log_handler = setup_new_cchandler(
            get_object_namespace(parent_object))
        self._is_logging = False

    def start(self):
        """Adds handler to log to start logging"""
        if self._is_logging is False:
            self.log.addHandler(self.log_handler)
            self._is_logging = True

    def stop(self):
        """Removes handler from log to stop logging"""
        self.log.removeHandler(self.log_handler)
        self._is_logging = False


class FixtureReporter(object):
    """Provides logging and metrics reporting for any test fixture"""
    SEPERATOR = "{0}".format('=' * 56)

    def __init__(self, parent_object):
        self.logger = _FixtureLogger(parent_object)
        self.metrics = TestRunMetrics()
        self.report_name = str(get_object_namespace(parent_object))

    def start(self):
        """Starts logging and metrics reporting for the fixture"""
        self.logger.start()
        self.metrics.timer.start()

        log_info_block(
            self.logger.log,
            [('Fixture', self.report_name),
             ('Created At', self.metrics.timer.start_time)])

    def stop(self):
        """Logs all collected metrics and stats, then stops logging and metrics
        reporting for the fixture.
        """

        self.metrics.timer.stop()
        if (self.metrics.total_passed == self.metrics.total_tests):
            self.metrics.result = TestResultTypes.PASSED
        else:
            self.metrics.result = TestResultTypes.FAILED

        log_info_block(
            self.logger.log,
            [('Fixture', self.report_name),
             ('Result', self.metrics.result),
             ('Start Time', self.metrics.timer.start_time),
             ('Elapsed Time', self.metrics.timer.get_elapsed_time()),
             ('Total Tests', self.metrics.total_tests),
             ('Total Passed', self.metrics.total_passed),
             ('Total Failed', self.metrics.total_failed),
             ('Total Errored', self.metrics.total_errored)])
        self.logger.stop()

    def start_test_metrics(self, class_name, test_name, test_description=None):
        """Creates a new Metrics object and starts reporting to it.  Useful
        for creating metrics for individual tests.
        """

        test_description = test_description or "No Test description."
        self.metrics.total_tests += 1
        self.test_metrics = TestRunMetrics()
        self.test_metrics.timer.start()
        root_log_dir = os.environ['CAFE_ROOT_LOG_PATH']
        self.stats_log = PBStatisticsLog(
            "{0}.{1}.statistics.csv".format(class_name, test_name),
            "{0}/statistics/".format(root_log_dir))

        log_info_block(
            self.logger.log,
            [('Test Case', test_name),
             ('Created At', self.metrics.timer.start_time),
             (test_description, '')])

    def stop_test_metrics(self, test_name, test_result):
        """Stops reporting on the Metrics object created in start_test_metrics.
        Logs all collected metrics.
        Useful for logging metrics for individual test at the test's conclusion
        """

        self.test_metrics.timer.stop()

        if test_result == TestResultTypes.PASSED:
            self.metrics.total_passed += 1

        if test_result == TestResultTypes.ERRORED:
            self.metrics.total_errored += 1

        if test_result == TestResultTypes.FAILED:
            self.metrics.total_failed += 1

        self.test_metrics.result = test_result

        log_info_block(
            self.logger.log,
            [('Test Case', test_name),
             ('Result', self.test_metrics.result),
             ('Start Time', self.test_metrics.timer.start_time),
             ('Elapsed Time', self.test_metrics.timer.get_elapsed_time())])
        self.stats_log.report(self.test_metrics)
