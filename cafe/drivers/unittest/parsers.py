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


class SummarizeResults(object):

    def __init__(self, result_dict, master_testsuite,
                 execution_time):
        for keys, values in result_dict.items():
            setattr(self, keys, values)
        self.master_testsuite = master_testsuite
        self.execution_time = execution_time

    def get_passed_tests(self):
        all_tests = []
        actual_number_of_tests_run = []
        failed_tests = []
        skipped_tests = []
        errored_tests = []
        setup_errored_classes = []
        setup_errored_tests = []
        passed_obj_list = []
        for test in vars(self.master_testsuite).get('_tests'):
            all_tests.append(test)
        for failed_test in self.failures:
            failed_tests.append(failed_test[0])
        for skipped_test in self.skipped:
            skipped_tests.append(skipped_test[0])
        for errored_test in self.errors:
            if errored_test[0].__class__.__name__ != '_ErrorHolder':
                errored_tests.append(errored_test[0])
            else:
                setup_errored_classes.append(
                    str(errored_test[0]).split(".")[-1].rstrip(')'))
        if len(setup_errored_classes) != 0:
            for item_1 in all_tests:
                for item_2 in setup_errored_classes:
                    if item_2 == item_1.__class__.__name__:
                        setup_errored_tests.append(item_1)
        else:
            actual_number_of_tests_run = all_tests

        passed_tests = list(set(all_tests) - set(failed_tests) -
                            set(skipped_tests) - set(errored_tests) -
                            set(setup_errored_tests))

        for passed_test in passed_tests:
            passed_obj = Result(passed_test.__class__.__name__,
                                vars(passed_test).get('_testMethodName'))
            passed_obj_list.append(passed_obj)

        return passed_obj_list

    def get_skipped_tests(self):
        skipped_obj_list = []
        for item in self.skipped:
            skipped_obj = Result(item[0].__class__.__name__,
                                 vars(item[0]).get('_testMethodName'),
                                 skipped_msg=item[1])
            skipped_obj_list.append(skipped_obj)
        return skipped_obj_list

    def get_errored_tests(self):
        errored_obj_list = []
        for item in self.errors:
            if item[0].__class__.__name__ is not '_ErrorHolder':
                errored_obj = Result(item[0].__class__.__name__,
                                     vars(item[0]).get('_testMethodName'),
                                     error_trace=item[1])
            else:
                errored_obj = Result(str(item[0]).split(" ")[0],
                                     str(item[0]).split(".")[-1].rstrip(')'),
                                     error_trace=item[1])
            errored_obj_list.append(errored_obj)
        return errored_obj_list

    def parse_failures(self):
        failure_obj_list = []
        for failure in self.failures:
            failure_obj = Result(failure[0].__class__.__name__,
                                 vars(failure[0]).get('_testMethodName'),
                                 failure[1])
            failure_obj_list.append(failure_obj)

        return failure_obj_list

    def summary_result(self):
        summary_res = {'tests': str(self.testsRun),
                       'errors': str(len(self.errors)),
                       'failures': str(len(self.failures)),
                       'skipped': str(len(self.skipped))}
        return summary_res

    def gather_results(self):
        executed_tests = (self.get_passed_tests() + self.parse_failures() +
                          self.get_errored_tests() + self.get_skipped_tests())
        return executed_tests


class Result(object):
    def __init__(self, test_class_name, test_method_name, failure_trace=None,
                 skipped_msg=None, error_trace=None):
        self.test_class_name = test_class_name
        self.test_method_name = test_method_name
        self.failure_trace = failure_trace
        self.skipped_msg = skipped_msg
        self.error_trace = error_trace

    def __repr__(self):
        values = []
        for prop in self.__dict__:
            values.append("%s: %s" % (prop, self.__dict__[prop]))
        return dict('{' + ', '.join(values) + '}')
