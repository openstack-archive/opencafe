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

from datetime import datetime
import os
import sys
import uuid

import pytz
import subunit

from cafe.common.reporting.base_report import BaseReport


class SubunitReport(BaseReport):
    def generate_report(self, result_parser, all_results=None, path=None):
        """ Generates a Subunit report in the specified directory. """

        result_path = path or os.getcwd()
        if os.path.isdir(result_path):
            result_path += "/subunit_results"

        with open(result_path, 'wb') as result_file:
            output = subunit.v2.StreamResultToBytes(result_file)
            output.startTestRun()

            # Convert Result objects to dicts for processing
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
                if test_result['test_method_name'] == "setUpClass":
                    # This case is to match the tempest format
                    test_id = "{0} ({1})".format(
                        test_result['test_method_name'],
                        test_result['test_class_name'])
                else:
                    test_id = "{0}.{1}".format(
                        test_result['test_class_name'],
                        test_result['test_method_name'])
                kwargs = {
                    "timestamp": datetime.now(pytz.UTC),
                    "test_id": unicode(test_id)}
                output.status(**kwargs)
                kwargs["test_status"] = test_result['result']
                kwargs["file_bytes"] = bytes(test_result.get(
                    'failure_trace') or test_result.get('error_trace') or "0")
                kwargs["file_name"] = "stdout"
                kwargs["mime_type"] = unicode("text/plain;charset=utf8")
                output.status(**kwargs)

            output.stopTestRun()
