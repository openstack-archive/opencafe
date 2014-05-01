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
import os
import shutil
import unittest
from uuid import uuid4

from cafe.common.reporting.reporter import Reporter
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.decorators import tags


def load_tests(*args, **kwargs):
    suite = unittest.suite.TestSuite()
    suite.addTest(ReportingTests('test_create_json_report'))
    suite.addTest(ReportingTests('test_create_xml_report'))
    suite.addTest(ReportingTests('test_create_json_report_w_file_name'))
    suite.addTest(ReportingTests('test_create_xml_report_w_file_name'))
    return suite


class FakeTests(unittest.TestCase):

    """ These tests are only used only to create a SummarizeResults object
    and will not actually run as a part of the suite.
    """

    def test_report_pass(self):
        pass

    def test_report_fail(self):
        pass

    def test_report_skip(self):
        pass

    def test_report_error(self):
        pass


class ReportingTests(unittest.TestCase):

    def setUp(self):
        """ Creates a SummarizeResults parser with fake tests and initializes
        the reporter. Also creates a directory for the created reports.
        """
        test_suite = unittest.suite.TestSuite()
        test_suite.addTest(FakeTests('test_report_pass'))
        test_suite.addTest(FakeTests('test_report_fail'))
        test_suite.addTest(FakeTests('test_report_skip'))
        test_suite.addTest(FakeTests('test_report_error'))

        self.failure_trace = 'Traceback: ' + str(uuid4())
        self.skip_msg = str(uuid4())
        self.error_trace = 'Traceback: ' + str(uuid4())
        result = {
            'testsRun': 4,
            'errors': [(FakeTests('test_report_error'), self.error_trace)],
            'skipped': [(FakeTests('test_report_skip'), self.skip_msg)],
            'failures': [(FakeTests('test_report_fail'), self.failure_trace)]}

        self.result_parser = SummarizeResults(
            master_testsuite=test_suite, result_dict=result,
            execution_time=1.23)
        self.all_results = self.result_parser.gather_results()
        self.reporter = Reporter(
            result_parser=self.result_parser, all_results=self.all_results,)

        self.results_dir = os.getcwd() + os.path.sep + 'test-reporting-results'
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)

    def _file_contains_test_info(self, file_path):
        """ Checks for generic test information (names and messages)
        in the specified report file.
        """
        return self._file_contains(
            file_path=file_path, target_strings=[
                'test_report_pass', 'test_report_fail', 'test_report_skip',
                'test_report_error', self.failure_trace, self.skip_msg,
                self.error_trace])

    def _file_contains(self, file_path, target_strings):
        """ Checks that the specified file contains all strings in the
        target_strings list.
        """
        for target_string in target_strings:
            if target_string in open(file_path).read():
                return True
        return False

    @tags('smoke', 'cli', execution='slow, fast', suite="test, integration")
    def test_create_json_report(self):
        """ Creates a json report and checks that the created report contains
        the proper test information.
        """
        self.reporter.generate_report(
            result_type='json', path=self.results_dir)
        results_file = self.results_dir + os.path.sep + 'results.json'
        self.assertTrue(os.path.exists(results_file))
        self.assertTrue(self._file_contains_test_info(file_path=results_file))

    @tags("cli", execution='slow')
    def test_create_xml_report(self):
        """ Creates an xml report and checks that the created report contains
        the proper test information.
        """
        self.reporter.generate_report(result_type='xml', path=self.results_dir)
        results_file = self.results_dir + os.path.sep + 'results.xml'
        self.assertTrue(os.path.exists(results_file))
        self.assertTrue(self._file_contains_test_info(file_path=results_file))

    @tags('smoke', 'cli', 'functional', execution='fast')
    def test_create_json_report_w_file_name(self):
        """ Creates a json report with a specified file name and checks that
        the created report contains the proper test information.
        """
        results_file = self.results_dir + os.path.sep + str(uuid4()) + '.json'
        self.reporter.generate_report(result_type='json', path=results_file)
        self.assertTrue(os.path.exists(results_file))
        self.assertTrue(self._file_contains_test_info(file_path=results_file))

    @tags('cli', 'functional')
    def test_create_xml_report_w_file_name(self):
        """ Creates an xml report with a specified file name and checks that
        the created report contains the proper test information.
        """
        results_file = self.results_dir + os.path.sep + str(uuid4()) + '.xml'
        self.reporter.generate_report(result_type='xml', path=results_file)
        self.assertTrue(os.path.exists(results_file))
        self.assertTrue(self._file_contains_test_info(file_path=results_file))

    def tearDown(self):
        """ Deletes created reports and directories. """
        if os.path.exists(self.results_dir):
            self.results_dir = shutil.rmtree(self.results_dir)
