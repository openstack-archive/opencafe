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

from __future__ import print_function
from traceback import print_exc
from warnings import warn
import argparse
import os
import sys

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
        self.log_handler.close()
        self.log.removeHandler(self.log_handler)
        self._is_logging = False


class FixtureReporter(object):
    """Provides logging and metrics reporting for any test fixture"""

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
        try:
            self.test_metrics.timer.stop()
        except AttributeError:
            warn(
                "\nTest metrics not being logged! "
                "stop_test_metrics is being called without "
                "start_test_metrics having been previously called.\n\n")
            log_info_block(
                self.logger.log,
                [('Test Case', test_name),
                 ('Result', test_result),
                 ('Start Time', "Unknown, start_test_metrics was not called"),
                 ('Elapsed Time', "Unknown, start_test_metrics was not called")
                 ])
            return

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


def parse_runner_args(arg_parser):
    """ Generic CAFE args for external runners"""

    arg_parser.add_argument(
        "product",
        nargs=1,
        metavar="<product>",
        help="Product name")

    arg_parser.add_argument(
        "config",
        nargs=1,
        metavar="<config_file>",
        help="Product test config")

    arg_parser.add_argument(
        dest='cmd_opts',
        nargs=argparse.REMAINDER,
        metavar="<cmd_opts>",
        help="Options to pass to the test runner")

    return arg_parser.parse_args()


def print_mug(name, brewing_from):
    """ Generic CAFE mug """
    border = '-' * 40
    mug = """
    Brewing from {path}
              ( (
               ) )
            .........
            |       |___
            |       |_  |
            |  :-)  |_| |
            |       |___|
            |_______|
    === CAFE {name} Runner ===""".format(
        path=brewing_from, name=name)

    print(border)
    print(mug)
    print(border)


def print_exception(file_=None, method=None, value=None, exception=None):
    """
        Prints exceptions in a standard format to stderr.
    """
    print("{0}".format("=" * 70), file=sys.stderr)
    if file_:
        print("{0}:".format(file_), file=sys.stderr, end=" ")
    if method:
        print("{0}:".format(method), file=sys.stderr, end=" ")
    if value:
        print("{0}:".format(value), file=sys.stderr, end=" ")
    if exception:
        print("{0}:".format(exception), file=sys.stderr, end=" ")
    print("\n{0}".format("-" * 70), file=sys.stderr)
    if exception is not None:
        print_exc(file=sys.stderr)
    print(file=sys.stderr)


def get_error(exception=None):
    """Gets errno from exception or returns one"""
    return getattr(exception, "errno", 1)
