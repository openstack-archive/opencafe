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
import xml.etree.ElementTree as ET

from cafe.common.reporting.base_report import BaseReport


class XMLReport(BaseReport):

    def generate_report(self, result_parser, all_results=None, directory=None):
        """ Generates an XML report in the specified directory. """
        executed_tests = result_parser.gather_results()
        summary_result = result_parser.summary_result()
        num_tests = len(vars(result_parser.master_testsuite).get('_tests'))
        root = ET.Element("testsuite")
        root.attrib['name'] = ''
        root.attrib['tests'] = str(num_tests)
        root.attrib['errors'] = summary_result['errors']
        root.attrib['failures'] = summary_result['failures']
        root.attrib['skips'] = summary_result['skipped']
        root.attrib['time'] = str(result_parser.execution_time)

        for testcase in executed_tests:
            testcase_tag = ET.SubElement(root, 'testcase')
            testcase_tag.attrib['classname'] = testcase.test_class_name
            testcase_tag.attrib['name'] = testcase.test_method_name
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

        result_dir = directory or os.getcwd()
        file = open(result_dir + "/results.xml", 'wb')
        ET.ElementTree(root).write(file)
        file.close()
