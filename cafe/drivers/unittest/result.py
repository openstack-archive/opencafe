"""
Copyright 2014 Rackspace

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

from cafe.drivers.unittest.decorators import TAGS_DECORATOR_ATTR_DICT_NAME


class TaggedTextTestResult(TextTestResult):

    """ Extended TextTestResult object to include support for tagged methods"""

    def __init__(self, stream, descriptions, verbosity):
        super(TaggedTextTestResult, self).__init__(
            stream, descriptions, verbosity)
        self.mapping = TestCaseTagMapping(self)

    def stopTest(self, test):
        """ Override stopTest method to capture test object and extract tags"""
        super(TaggedTextTestResult, self).stopTest(test)
        test_method = getattr(test, test._testMethodName)
        if hasattr(test_method, TAGS_DECORATOR_TAG_LIST_NAME):
            self.mapping.update_mapping(test._testMethodName, getattr(
                test_method, TAGS_DECORATOR_TAG_LIST_NAME))
        if hasattr(test_method, TAGS_DECORATOR_ATTR_DICT_NAME):
            self.mapping.update_attribute_mapping(
                test._testMethodName, getattr(test_method,
                                              TAGS_DECORATOR_ATTR_DICT_NAME))


class TestCaseTagMapping(object):

    """ Test case mapping class which keeps track of test-to-tag and
        tag-to-test mapping
    """

    def __init__(self, test_result):
        self.test_ref = test_result
        self.test_to_tag_mapping = dict()
        self.tag_to_test_mapping = dict()
        self.test_to_attribute_mapping = dict()
        self.attribute_to_test_mapping = dict()

    def update_mapping(self, test_name, tag_list):
        """ Takes the test name and the list of associated tags and updates
            the mapping
        """
        if not self.test_to_tag_mapping.__contains__(test_name):
            self.test_to_tag_mapping[test_name] = tag_list
        for tag in tag_list:
            if self.tag_to_test_mapping.__contains__(
                    tag) and not self.tag_to_test_mapping.get(
                    tag).__contains__(test_name):
                self.tag_to_test_mapping[tag].append(test_name)
            else:
                self.tag_to_test_mapping[tag] = [test_name]

    def update_attribute_mapping(self, test_name, attribute_list):
        if not self.test_to_attribute_mapping.__contains__(test_name):
            self.test_to_attribute_mapping[test_name] = attribute_list
        for attribute, entries in attribute_list.items():
            for entry in entries.split(","):
                entry = entry.lstrip().rstrip()
                attribute_tuple = (attribute, entry)
                if self.attribute_to_test_mapping.__contains__(
                        attribute_tuple) and not \
                    self.attribute_to_test_mapping.get(
                        attribute_tuple).__contains__(test_name):
                    self.attribute_to_test_mapping[attribute_tuple].append(
                        test_name)
                else:
                    self.attribute_to_test_mapping[
                        attribute_tuple] = [test_name]

    def print_test_to_tag_mapping(self):
        """ Prints the test-to-tag dict mapping to result stream """
        max_len = 0
        self.test_ref.stream.writeln()
        self.test_ref.stream.writeln("Tags and attributes associated to tests")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        max_len = self.__get_max_entry_length(self.test_to_tag_mapping.keys())

        for entry in self.test_to_tag_mapping.keys():
            self.test_ref.stream.write("{entry}{spacer}: ".format(
                entry=entry, spacer=(" " * (max_len - len(entry)))))
            self.test_ref.stream.write(
                str(self.test_to_tag_mapping.get(entry)))
            if entry in self.test_to_attribute_mapping:
                self.test_ref.stream.write(" Attributes: {attributes}".format(
                    attributes=str(self.test_to_attribute_mapping.get(entry))))
            self.test_ref.stream.write("\n")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        self.test_ref.stream.flush()

    def print_tag_to_test_mapping(self):
        """ Prints the tag-to-test dict mapping to result stream """
        max_len = 0
        self.test_ref.stream.writeln("Tests associated to tags")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        max_len = self.__get_max_entry_length(self.tag_to_test_mapping.keys())

        for entry in self.tag_to_test_mapping.keys():
            self.test_ref.stream.write("{entry}{spacer} : ".format(
                entry=entry, spacer=(" " * (max_len - len(entry)))))
            self.test_ref.stream.writeln(self.__generate_summary(
                entry, self.tag_to_test_mapping))
            self.test_ref.stream.writeln(
                str(self.tag_to_test_mapping.get(entry)))
            self.test_ref.stream.writeln("\n")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        self.test_ref.stream.flush()

    def print_attribute_to_test_mapping(self):
        """ Prints the attribute-to-test dict mapping to result stream """
        max_len = 0
        self.test_ref.stream.writeln("Tests associated to attributes")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        max_len = self.__get_max_entry_length(
            self.attribute_to_test_mapping.keys())

        for entry in self.attribute_to_test_mapping.keys():
            self.test_ref.stream.write("{entry}{spacer} : ".format(
                entry=entry, spacer=(" " * (max_len - len(str(entry))))))
            self.test_ref.stream.writeln(self.__generate_summary(
                entry, self.attribute_to_test_mapping))
            self.test_ref.stream.writeln(
                str(self.attribute_to_test_mapping.get(entry)))
            self.test_ref.stream.writeln("\n")
        self.test_ref.stream.writeln(self.test_ref.separator1)
        self.test_ref.stream.flush()

    def write_to_stream(self, data):
        """ Writes to the stream object passed to the result object
        """
        self.test_ref.stream.write(data)
        self.test_ref.stream.flush()

    @staticmethod
    def __tuple_contains(test, test_ref_list):
        if test_ref_list is None or len(test_ref_list) == 0:
            return False
        else:
            for item in test_ref_list:
                if vars(item[0]).get('_testMethodName') == test:
                    return True
        return False

    @staticmethod
    def __get_max_entry_length(listing):
        max_len = 0
        for entry in listing:
            if type(entry) is not str:
                entry = str(entry)
            if len(entry) > max_len:
                max_len = len(entry)
        return max_len

    def __generate_summary(self, tag, listing):
        """ Generates a run summary for a given tag """
        pass_count = 0
        fail_count = 0
        skip_count = 0
        error_count = 0

        tests = listing.get(tag)
        for test in tests:
            if self.__tuple_contains(test, self.test_ref.failures):
                fail_count += 1
                continue
            elif self.__tuple_contains(test, self.test_ref.errors):
                error_count += 1
                continue
            elif self.__tuple_contains(test, self.test_ref.skipped):
                skip_count += 1
                continue
            else:
                pass_count += 1
        total_count = pass_count + fail_count + skip_count + error_count
        if pass_count == 0:
            pass_rate = float(0)
        else:
            pass_rate = 100 * float(pass_count) / float(total_count)
        return ("Pass: {0} Fail: {1} Error: {2} Skipped: {3} Total: {4} "
                "Pass Rate: {5}%").format(pass_count, fail_count, error_count,
                                          skip_count, total_count, pass_rate)
