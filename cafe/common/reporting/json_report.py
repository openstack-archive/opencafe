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
import json

from cafe.common.reporting.base_report import BaseReport


class JSONReport(BaseReport):

    def generate_report(self, result_parser, all_results=None, path=None):
        """ Generates a JSON report in the specified directory. """

        num_tests = len(vars(
            result_parser.master_testsuite).get('_tests', []))
        errors = 0
        failures = 0
        skips = 0
        time = str(result_parser.execution_time)

        # Convert Result objects to dicts for processing
        individual_results = []
        for result in all_results:
            test_result = result.__dict__
            if test_result.get('failure_trace') is not None:
                test_result['result'] = "FAILED"
                failures += 1
            elif test_result.get('skipped_msg') is not None:
                test_result['result'] = "SKIPPED"
                skips += 1
            elif test_result.get('error_trace') is not None:
                test_result['result'] = "ERROR"
                errors += 1
            else:
                test_result['result'] = "PASSED"
            individual_results.append(test_result)

        # Build the result summary
        test_results = {
            'tests': num_tests,
            'failures': failures,
            'errors': errors,
            'skips': skips,
            'time': time,
            'results': individual_results
        }

        result_path = path or os.getcwd()
        if os.path.isdir(result_path):
            result_path += "/results.json"

        with open(result_path, 'wb') as result_file:
            json.dump(test_results, result_file)
