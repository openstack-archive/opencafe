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

from cafe.common.reporting.json_report import JSONReport
from cafe.common.reporting.xml_report import XMLReport
from cafe.common.reporting.subunit_report import SubunitReport


class Reporter:

    def __init__(self, result_parser, all_results):
        self.result_parser = result_parser
        self.all_results = all_results

    def generate_report(self, result_type, path=None):
        """ Creates a report object based on what type is given and generates
        the report in the specified directory.
        """
        if result_type == 'json':
            report = JSONReport()
        elif result_type == 'xml':
            report = XMLReport()
        elif result_type == 'subunit':
            report = SubunitReport()

        report.generate_report(
            result_parser=self.result_parser, all_results=self.all_results,
            path=path)
