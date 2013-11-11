import os
from cafe.common.reporting import cclogging
from cafe.common.reporting.metrics import (
    TestRunMetrics, TestResultTypes, PBStatisticsLog)


class LoggingFixtureMixin(object):
    """ Mixin adds methods for managing cafe logging in a test class."""

    @staticmethod
    def init_master_log():
        #Setup root log handler if the root logger doesn't already have one
        if not cclogging.getLogger('').handlers:
            master_log_file_name = os.getenv('CAFE_MASTER_LOG_FILE_NAME')
            cclogging.getLogger('').addHandler(
                cclogging.setup_new_cchandler(master_log_file_name))

    @classmethod
    def start_fixture_log(cls):
        #Setup test log, which is really just a copy of the master log
        #for the duration of this test fixture
        cls.fixture_log = cclogging.getLogger('')
        cls._class_log_handler = cclogging.setup_new_cchandler(
            cclogging.get_object_namespace(cls))
        cls.fixture_log.addHandler(cls._class_log_handler)

    @classmethod
    def end_fixture_log(cls):
        #Remove the fixture log handler from the fixture log
        cls.fixture_log.removeHandler(cls._class_log_handler)


class ReportingFixtureMixin(LoggingFixtureMixin):
    """Extends the LoggingFixtureMixin with methods to run at the start and end
    of test fixtures and methods to log timing and other metrics."""

    @classmethod
    def start_fixture_metrics_logging(cls):
        cls.start_fixture_log()
        cls.fixture_metrics = TestRunMetrics()
        cls.fixture_metrics.timer.start()
        #Fixture Log Header
        cls.fixture_log.info("{0}".format('=' * 56))
        cls.fixture_log.info(
            "Fixture...: {0}".format(str(cclogging.get_object_namespace(cls))))
        cls.fixture_log.info(
            "Created At: {0}".format(cls.fixture_metrics.timer.start_time))
        cls.fixture_log.info("{0}".format('=' * 56))

    @classmethod
    def end_fixture_metrics_logging(cls):
        cls.fixture_metrics.timer.stop()
        if (cls.fixture_metrics.total_passed ==
                cls.fixture_metrics.total_tests):
            cls.fixture_metrics.result = TestResultTypes.PASSED
        else:
            cls.fixture_metrics.result = TestResultTypes.FAILED

        cls.fixture_log.info("{0}".format('=' * 56))
        cls.fixture_log.info("Fixture.....: {0}".format(
            str(cclogging.get_object_namespace(cls))))
        cls.fixture_log.info("Result......: {0}".format(
            cls.fixture_metrics.result))
        cls.fixture_log.info("Start Time..: {0}".format(
            cls.fixture_metrics.timer.start_time))
        cls.fixture_log.info("Elapsed Time: {0}".format(
            cls.fixture_metrics.timer.get_elapsed_time()))
        cls.fixture_log.info("Total Tests.: {0}".format(
            cls.fixture_metrics.total_tests))
        cls.fixture_log.info("Total Passed: {0}".format(
            cls.fixture_metrics.total_passed))
        cls.fixture_log.info("Total Failed: {0}".format(
            cls.fixture_metrics.total_failed))
        cls.fixture_log.info("{0}".format('=' * 56))

        cls.end_fixture_log()

    def start_test_metrics(self, test_name, test_description=None):
        test_description = test_description or "No Test description."
        self.fixture_metrics.total_tests += 1
        self.test_metrics = TestRunMetrics()
        self.test_metrics.timer.start()
        root_log_dir = os.environ['CAFE_ROOT_LOG_PATH']
        self.stats_log = PBStatisticsLog(
            "{0}.statistics.csv".format(test_name),
            "{0}/statistics/".format(root_log_dir))

        self.fixture_log.info("{0}".format('=' * 56))
        self.fixture_log.info("Test Case.: {0}".format(test_name))
        self.fixture_log.info("Created.At: {0}".format(
            self.test_metrics.timer.start_time))
        self.fixture_log.info("{0}".format(test_description ))
        self.fixture_log.info("{0}".format('=' * 56))

    def end_test_metrics(self, test_name, test_result):
        self.test_metrics.timer.stop()

        if test_result == TestResultTypes.PASSED:
            self.fixture_metrics.total_passed += 1

        if test_result == TestResultTypes.ERRORED:
            self.fixture_metrics.total_errored += 1

        if test_result == TestResultTypes.FAILED:
            self.fixture_metrics.total_failed += 1

        self.test_metrics.result = test_result

        self.fixture_log.info("{0}".format('=' * 56))
        self.fixture_log.info("Test Case...: {0}".format(test_name))
        self.fixture_log.info("Result......: {0}".format(
            self.test_metrics.result))
        self.fixture_log.info("Start Time...: {0}".format(
            self.test_metrics.timer.start_time))
        self.fixture_log.info("Elapsed Time: {0}".format(
            self.test_metrics.timer.get_elapsed_time()))
        self.fixture_log.info("{0}".format('=' * 56))
        self.stats_log.report(self.test_metrics)
