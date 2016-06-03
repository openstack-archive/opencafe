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
import xml.etree.ElementTree as ET

from cafe.common.reporting.base_report import BaseReport


class XMLReport(BaseReport):

    def generate_report(self, result_parser, all_results=None, path=None):
        """Generates an XML report in the specified directory."""
        num_tests = len(all_results)
        root = ET.Element("testsuite")
        root.attrib['name'] = ''
        root.attrib['tests'] = str(num_tests)

        root.attrib['errors'] = str(len(
            [result.error_trace for result in all_results
             if result.error_trace]))
        root.attrib['failures'] = str(len(
            [result.failure_trace for result in all_results
             if result.failure_trace]))
        root.attrib['skips'] = str(len(
            [result.skipped_msg for result in all_results
             if result.skipped_msg]))
        root.attrib['time'] = str(result_parser.execution_time)
        if result_parser.datagen_time is not None:
            root.attrib['datagen_time'] = str(result_parser.datagen_time)
            root.attrib['total_time'] = str(
                float(root.attrib['time']) +
                float(root.attrib['datagen_time']))

        for testcase in all_results:
            testcase_tag = ET.SubElement(root, 'testcase')
            testcase_tag.attrib['classname'] = testcase.test_class_name
            testcase_tag.attrib['name'] = testcase.test_method_name
            testcase_tag.attrib['time'] = str(testcase.test_time)
            if testcase.failure_trace is not None:
                testcase_tag.attrib['result'] = "FAILED"
                failure_trace = testcase.failure_trace.split(":")
                error_tag = ET.SubElement(testcase_tag, 'failure')
                error_tag.attrib['type'] = failure_trace[1].split()[-1]
                error_tag.attrib['message'] = failure_trace[-1].strip()
                error_tag.text = testcase.failure_trace
            else:
                if testcase.skipped_msg is not None:
                    skipped_tag = ET.SubElement(testcase_tag, 'skipped')
                    skipped_tag_msg = testcase.skipped_msg.strip()
                    testcase_tag.attrib['result'] = "SKIPPED"
                    skipped_tag.attrib['message'] = skipped_tag_msg
                elif testcase.error_trace is not None:
                    testcase_tag.attrib['result'] = "ERROR"
                    error_trace = testcase.error_trace.split(":")
                    error_tag = ET.SubElement(testcase_tag, 'error')
                    error_tag.attrib['type'] = error_trace[1].split()[-1]
                    error_tag.attrib['message'] = error_trace[-1].strip()
                    error_tag.text = testcase.error_trace
                else:
                    testcase_tag.attrib['result'] = "PASSED"

        result_path = path or os.getcwd()
        if os.path.isdir(result_path):
            result_path += "/results.xml"

        file = open(result_path, 'wb')
        ET.ElementTree(root).write(file)
        file.close()
