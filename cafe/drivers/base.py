import os
from cafe.common.reporting.cclogging import get_object_namespace, EasyLogger
from cafe.common.reporting.metrics import (
    TestRunMetrics, TestResultTypes, PBStatisticsLog)


class FixtureReporter(object):
    """Provides logging and metrics reporting for any test fixture"""

    def __init__(self, parent_object):
        self.logger = EasyLogger(parent_object)
        self.metrics = TestRunMetrics()
        self.report_name = str(get_object_namespace(parent_object))

    def start(self):
        self.logger.start()
        self.metrics.timer.start()

        self.logger.log.info("{0}".format('=' * 56))
        self.logger.log.info("Fixture...: {0}".format(self.report_name))
        self.logger.log.info("Created At: {0}".format(
            self.metrics.timer.start_time))
        self.logger.log.info("{0}".format('=' * 56))

    def stop(self):
        self.metrics.timer.stop()
        if (self.metrics.total_passed == self.metrics.total_tests):
            self.metrics.result = TestResultTypes.PASSED
        else:
            self.metrics.result = TestResultTypes.FAILED

        self.logger.log.info("{0}".format('=' * 56))
        self.logger.log.info("Fixture.....: {0}".format(str(self.report_name)))
        self.logger.log.info("Result......: {0}".format(self.metrics.result))
        self.logger.log.info(
            "Start Time..: {0}".format(self.metrics.timer.start_time))
        self.logger.log.info(
            "Elapsed Time: {0}".format(self.metrics.timer.get_elapsed_time()))
        self.logger.log.info(
            "Total Tests.: {0}".format(self.metrics.total_tests))
        self.logger.log.info(
            "Total Passed: {0}".format(self.metrics.total_passed))
        self.logger.log.info(
            "Total Failed: {0}".format(self.metrics.total_failed))
        self.logger.log.info("{0}".format('=' * 56))
        self.logger.stop()

    def start_test_metrics(self, test_name, test_description=None):
        test_description = test_description or "No Test description."
        self.metrics.total_tests += 1
        self.test_metrics = TestRunMetrics()
        self.test_metrics.timer.start()
        root_log_dir = os.environ['CAFE_ROOT_LOG_PATH']
        self.stats_log = PBStatisticsLog(
            "{0}.statistics.csv".format(test_name),
            "{0}/statistics/".format(root_log_dir))

        self.logger.log.info("{0}".format('=' * 56))
        self.logger.log.info("Test Case.: {0}".format(test_name))
        self.logger.log.info("Created.At: {0}".format(
            self.test_metrics.timer.start_time))
        self.logger.log.info("{0}".format(test_description))
        self.logger.log.info("{0}".format('=' * 56))

    def stop_test_metrics(self, test_name, test_result):
        self.test_metrics.timer.stop()

        if test_result == TestResultTypes.PASSED:
            self.metrics.total_passed += 1

        if test_result == TestResultTypes.ERRORED:
            self.metrics.total_errored += 1

        if test_result == TestResultTypes.FAILED:
            self.metrics.total_failed += 1

        self.test_metrics.result = test_result

        self.logger.log.info("{0}".format('=' * 56))
        self.logger.log.info("Test Case...: {0}".format(test_name))
        self.logger.log.info("Result......: {0}".format(
            self.test_metrics.result))
        self.logger.log.info("Start Time...: {0}".format(
            self.test_metrics.timer.start_time))
        self.logger.log.info("Elapsed Time: {0}".format(
            self.test_metrics.timer.get_elapsed_time()))
        self.logger.log.info("{0}".format('=' * 56))
        self.stats_log.report(self.test_metrics)
