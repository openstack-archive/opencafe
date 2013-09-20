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

    def generate_report(self, result_parser, all_results=None, directory=None):
        """ Generates a JSON report in the specified directory. """
        # Convert Result objects to dicts for serialization
        json_results = []
        for r in all_results:
            json_results.append(r.__dict__)

        result_dir = directory or os.getcwd()
        with open(result_dir + "/results.json", 'wb') as result_file:
            json.dump(json_results, result_file)
