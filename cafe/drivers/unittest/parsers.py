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

from unittest.suite import _ErrorHolder
import json


class SummarizeResults(object):
    """Reads in vars dict from suite and builds a Summarized results obj"""
    def __init__(self, result_dict, tests, execution_time, datagen_time=None):
        self.datagen_time = datagen_time
        self.execution_time = execution_time
        self.all_tests = tests
        self.failures = result_dict.get("failures", [])
        self.skipped = result_dict.get("skipped", [])
        self.errors = result_dict.get("errors", [])
        self.tests_run = result_dict.get("testsRun", 0)

    def get_passed_tests(self):
        """Gets a list of results objects for passed tests"""
        errored_tests = [
            t[0] for t in self.errors if not isinstance(t[0], _ErrorHolder)]
        setup_errored_classes = [
            str(t[0]).split(".")[-1].rstrip(')')
            for t in self.errors if isinstance(t[0], _ErrorHolder)]
        setup_errored_tests = [
            t for t in self.all_tests
            if t.__class__.__name__ in setup_errored_classes]

        passed_tests = list(
            set(self.all_tests) -
            set([test[0] for test in self.failures]) -
            set([test[0] for test in self.skipped]) -
            set(errored_tests) - set(setup_errored_tests))

        return [self._create_result(t) for t in passed_tests]

    def summary_result(self):
        """Returns a dictionary containing counts of tests and statuses"""
        return {
            'tests': self.tests_run,
            'errors': len(self.errors),
            'failures': len(self.failures),
            'skipped': len(self.skipped)}

    def gather_results(self):
        """Gets a result obj for all tests ran and failed setup classes"""
        return (
            self.get_passed_tests() +
            [self._create_result(t, "failures") for t in self.failures] +
            [self._create_result(t, "errored") for t in self.errors] +
            [self._create_result(t, "skipped") for t in self.skipped])

    @staticmethod
    def _create_result(test, type_="passed"):
        """Creates a Result object from a test and type of test"""

        test_time = 0
        msg_type = {"failures": "failure_trace", "skipped": "skipped_msg",
                    "errored": "error_trace"}
        if type_ == "passed":
            test_method_name = getattr(test, '_testMethodName', "")
            test_time = getattr(test, "_duration", 0)
            if test_time:
                test_time = test_time.total_seconds()
            dic = {"test_method_name": getattr(test, '_testMethodName', ""),
                   "test_class_name": "{0}.{1}".format(
                       str(test.__class__.__module__),
                       str(test.__class__.__name__)),
                   "test_time": test_time}

        elif (type_ in ["failures", "skipped", "errored"] and
              not isinstance(test[0], _ErrorHolder)):
            test_method_name = getattr(test[0], '_testMethodName', "")
            test_time = getattr(test[0], "_duration", 0)
            if test_time:
                test_time = test_time.total_seconds()
            dic = {"test_method_name": test_method_name,
                   "test_class_name": "{0}.{1}".format(
                       str(test[0].__class__.__module__),
                       str(test[0].__class__.__name__)),
                   msg_type.get(type_, "error_trace"): test[1],
                   "test_time": test_time}
        else:
            dic = {"test_method_name": str(test[0]).split(" ")[0],
                   "test_class_name": str(test[0]).split("(")[1].rstrip(")"),
                   msg_type.get(type_, "error_trace"): test[1]}
        return Result(**dic)


class Result(object):
    """Result object used to create the json and xml results"""
    def __init__(
            self, test_class_name, test_method_name, failure_trace=None,
            skipped_msg=None, error_trace=None, test_time=0):

        self.test_class_name = test_class_name
        self.test_method_name = test_method_name
        self.failure_trace = failure_trace
        self.skipped_msg = skipped_msg
        self.error_trace = error_trace
        self.test_time = test_time

    def __repr__(self):
        return json.dumps(self.__dict__)
