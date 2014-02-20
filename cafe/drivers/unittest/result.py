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

from unittest import TextTestResult
from cafe.drivers.unittest.decorators import TAGS_DECORATOR_TAG_LIST_NAME


class TaggedTextTestResult(TextTestResult):

    """ Extended TextTestResult object to include support for tagged methods"""

    def __init__(self, stream, descriptions, verbosity):
        super(TaggedTextTestResult, self).__init__(
            stream, descriptions, verbosity)
        self.mapping = TestCaseTagMapping(self)

    def stopTest(self, test):
        """ Override stopTest method to capture test object and extract tags"""
        super(TaggedTextTestResult, self)
        testMethod = getattr(test, test._testMethodName)
        if hasattr(testMethod, TAGS_DECORATOR_TAG_LIST_NAME):
            self.mapping.update_mapping(test._testMethodName, getattr(
                testMethod, TAGS_DECORATOR_TAG_LIST_NAME))

    def get_tag_mapping(self):
        """ Return reference to the TestCaseTagMapping object """
        return self.mapping


class TestCaseTagMapping(object):

    """ Test case mapping class which keeps track of test-to-tag and
        tag-to-test mapping
    """

    def __init__(self, test_result):
        self.test_ref = test_result
        self.test_to_tag_mapping = dict()
        self.tag_to_test_mapping = dict()

    def update_mapping(self, test_name, tag_list):
        """ Takes the test name and the list of associated tags and updates
            the mapping
        """
        if not self.test_to_tag_mapping.__contains__(test_name):
            self.test_to_tag_mapping[test_name] = tag_list
        for tag in tag_list:
            if self.tag_to_test_mapping.__contains__(tag) and not \
                    self.tag_to_test_mapping.get(tag).__contains__(test_name):
                self.tag_to_test_mapping[tag].append(test_name)
            else:
                self.tag_to_test_mapping[tag] = [test_name]

    def get_test_to_tag_mapping(self):
        """ Returns the test-to-tag dict mapping object """
        if len(self.test_to_tag_mapping) > 0:
            return self.test_to_tag_mapping
        else:
            self.test_ref.stream.write("Test to Tag mapping is empty")
            self.test_ref.stream.write("\n")
            return None

    def get_tag_to_test_mapping(self):
        """ Returns the tag-to-test dict mapping object """
        if len(self.tag_to_test_mapping) > 0:
            return self.tag_to_test_mapping
        else:
            self.test_ref.stream.write("Tag to Test mapping is empty")
            self.test_ref.stream.write("\n")
            return None

    def print_test_to_tag_mapping(self):
        """ Prints the test-to-tag dict mapping to result stream """
        max_len = 0
        self.test_ref.stream.writeln()
        self.test_ref.stream.writeln("Tags associated to tests")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        for entry in self.test_to_tag_mapping.keys():
            if len(entry) > max_len:
                max_len = len(entry)
        for entry in self.test_to_tag_mapping.keys():
            self.test_ref.stream.write(
                entry + " " * (max_len - len(entry)) + " : ")
            self.test_ref.stream.write(
                str(self.test_to_tag_mapping.get(entry)))
            self.test_ref.stream.write("\n")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        self.test_ref.stream.flush()

    def print_tag_to_test_mapping(self):
        """ Prints the tag-to-test dict mapping to result stream """
        max_len = 0
        self.test_ref.stream.writeln("Tests associated to tags")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        for entry in self.tag_to_test_mapping.keys():
            if len(entry) > max_len:
                max_len = len(entry)
        for entry in self.tag_to_test_mapping.keys():
            self.test_ref.stream.write(
                entry + " " * (max_len - len(entry)) + " : ")
            self.test_ref.stream.writeln(self.__generate_summary(entry))
            self.test_ref.stream.writeln(
                str(self.tag_to_test_mapping.get(entry)))
            self.test_ref.stream.writeln("\n")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        self.test_ref.stream.flush()

    def write_to_stream(self, data):
        """ Writes to the stream object passed to the result object
        """
        self.test_ref.stream.write(data)
        self.test_ref.stream.flush()

    def __tuple_contains(self, test, test_ref_list):
        if test_ref_list is None or len(test_ref_list) == 0:
            return False
        else:
            for item in test_ref_list:
                if vars(item[0]).get('_testMethodName') == test:
                    return True
                else:
                    return False

    def __generate_summary(self, tag):
        """ Generates a run summary for a given tag """
        pass_count = 0
        fail_count = 0
        skip_count = 0
        error_count = 0

        tests = self.tag_to_test_mapping.get(tag)
        for test in tests:
            if self.__tuple_contains(test, self.test_ref.failures):
                fail_count += 1
                continue
            elif self.__tuple_contains(test, self.test_ref.errors):
                error_count + 1
                continue
            elif self.__tuple_contains(test, self.test_ref.skipped):
                skip_count += 1
                continue
            else:
                pass_count += 1
        total_count = pass_count + fail_count + skip_count + error_count
        pass_rate = 100 * float(pass_count) / float(total_count)
        return "Pass: {0} Fail: {1} Error: {2} Skipped: {3} Total: {4} " \
               "Pass Rate: {5}%".format(str(pass_count),
                                        str(fail_count),
                                        str(error_count),
                                        str(skip_count),
                                        str(total_count),
                                        str(pass_rate))
