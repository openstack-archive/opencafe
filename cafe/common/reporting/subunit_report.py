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

from cafe.common.reporting.base_report import BaseReport

import subunit


class SubunitReport(BaseReport):
    def generate_report(self, result_parser, all_results=None, path=None):
        """ Generates a Subunit report in the specified directory. """

        result_path = path or os.getcwd()
        if os.path.isdir(result_path):
            result_path += "/subunit_results"

        output = subunit.v2.StreamResultToBytes(open(result_path, 'w'))
        output.startTestRun()

        # Convert Result objects to dicts for processing
        individual_results = []
        for result in all_results:
            test_result = result.__dict__
            if test_result.get('failure_trace') is not None:
                test_result['result'] = "fail"
            elif test_result.get('skipped_msg') is not None:
                test_result['result'] = "skip"
            elif test_result.get('error_trace') is not None:
                test_result['result'] = "fail"
            else:
                test_result['result'] = "success"
            kwargs = {
                "timestamp": 0,
                "test_id": "{0}.{1}".format(
                    test_result['test_class_name'],
                    test_result['test_method_name'])}
            output.status.write_status(**kwargs)
            kwargs["test_status"] = test_result['result']
            output.status.write_status(**kwargs)

        output.stopTestRun()
