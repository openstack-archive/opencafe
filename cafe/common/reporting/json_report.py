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

import os
import json

from cafe.common.reporting.base_report import BaseReport


class JSONReport(BaseReport):

    def generate_report(self, result_parser, all_results=None, path=None):
        """ Generates a JSON report in the specified directory. """

        num_tests = len(all_results)
        errors = len([result.error_trace for result in all_results
                      if result.error_trace])
        failures = len([result.failure_trace for result in all_results
                        if result.failure_trace])
        skips = len([result.skipped_msg for result in all_results
                     if result.skipped_msg])
        time = str(result_parser.execution_time)
        if result_parser.datagen_time is not None:
            datagen_time = str(result_parser.datagen_time)

        # Convert Result objects to dicts for processing
        individual_results = []
        for result in all_results:
            test_result = result.__dict__
            if test_result.get('failure_trace') is not None:
                test_result['result'] = "FAILED"
            elif test_result.get('skipped_msg') is not None:
                test_result['result'] = "SKIPPED"
            elif test_result.get('error_trace') is not None:
                test_result['result'] = "ERROR"
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
        # Add new metrics to result summary if available
        if datagen_time is not None:
            test_results['datagen_time'] = datagen_time
            test_results['total_time'] = str(float(time) + float(datagen_time))

        result_path = path or os.getcwd()
        if os.path.isdir(result_path):
            result_path += "/results.json"

        with open(result_path, 'w') as result_file:
            json.dump(test_results, result_file)
