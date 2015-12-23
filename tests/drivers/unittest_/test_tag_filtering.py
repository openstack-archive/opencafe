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
import argparse
import os
import shutil
import unittest
from uuid import uuid4

from cafe.common.reporting.reporter import Reporter
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.decorators import tags
from cafe.drivers.unittest.runner import SuiteBuilder, _UnittestRunnerCLI


class FakeTests(unittest.TestCase):
    def test_fast(self):
        pass

    @tags(execution='slow')
    def test_slow(self):
        pass

    @tags('login')
    def test_login(self):
        pass

    @tags('logout')
    def test_logout(self):
        pass

    @tags('login', 'logout')
    def test_login_logout(self):
        pass

    def foo(self):
        self.fail()


class TagFilterTest(unittest.TestCase):

    def suite_builder(self):
        """
        Do the boilerplate to create a SuiteBuilder.
        """
        argparser = argparse.ArgumentParser()
        cl_args = argparser.parse_args()
        cl_args.packages = []
        cl_args.module_regex = ''
        cl_args.method_regex = ''
        cl_args.tags = []
        cl_args.supress_flag = None
        cl_args.product = None
        return SuiteBuilder(cl_args, '')

    def test_exclude_non_tests(self):
        """
        Method names that start with something other than test_ are not run as tests.
        """
        builder = self.suite_builder()
        self.assertFalse(builder.include_method('foo', FakeTests, '', [], {}, None))
        self.assertTrue(builder.include_method('test_fast', FakeTests, '', [], {}, None))
        self.assertTrue(builder.include_method('test_slow', FakeTests, '', [], {}, None))

    def test_only_tag_matching_tests(self):
        """
        When a compound tag like "execution=slow" is passed in, only run tests
        with that tag.
        """
        builder = self.suite_builder()
        self.assertFalse(builder.include_method('test_fast', FakeTests, '',
                                               [], {'execution': 'slow'}, None))
        self.assertTrue(builder.include_method('test_slow', FakeTests, '',
                                               [], {'execution': 'slow'}, None))

    def test_only_simple_tag_matching(self):
        """
        When a simple tag like "login" is passed in, only run tests with that tag.
        """
        builder = self.suite_builder()
        self.assertFalse(builder.include_method('test_fast', FakeTests, '',
                                               ['login'], {}, None))
        self.assertFalse(builder.include_method('test_slow', FakeTests, '',
                                               ['login'], {}, None))
        self.assertTrue(builder.include_method('test_login', FakeTests, '',
                                               ['login'], {}, None))

    def test_ored_tags(self):
        """
        Multiple tags are OR'ed together by default.
        eg: -t login logout
        """
        builder = self.suite_builder()
        self.assertFalse(builder.include_method('test_fast', FakeTests, '',
                                               ['login', 'logout'], {}, None))
        self.assertTrue(builder.include_method('test_login', FakeTests, '',
                                               ['login', 'logout'], {}, None))
        self.assertTrue(builder.include_method('test_logout', FakeTests, '',
                                               ['login', 'logout'], {}, None))
        self.assertTrue(builder.include_method('test_login_logout', FakeTests, '',
                                               ['login', 'logout'], {}, None))

    def test_anded_tags(self):
        """
        When a '+' character prefixes the list of tags, multiple tags are AND'ed
        together. eg: -t + login logout
        """
        builder = self.suite_builder()
        self.assertFalse(builder.include_method('test_fast', FakeTests, '',
                                               ['login', 'logout'], {}, '+'))
        self.assertFalse(builder.include_method('test_slow', FakeTests, '',
                                               ['login', 'logout'], {}, '+'))
        self.assertFalse(builder.include_method('test_login', FakeTests, '',
                                               ['login', 'logout'], {}, '+'))
        self.assertFalse(builder.include_method('test_logout', FakeTests, '',
                                               ['login', 'logout'], {}, '+'))
        self.assertTrue(builder.include_method('test_login_logout', FakeTests, '',
                                               ['login', 'logout'], {}, '+'))

    def test_negated_tag(self):
        """
        When a tag is prefixed with an underscore, include tests that *do not*
        have that tag.
        """
        builder = self.suite_builder()
        self.assertTrue(builder.include_method('test_fast', FakeTests, '',
                                               ['_login'], {}, None))
        self.assertTrue(builder.include_method('test_slow', FakeTests, '',
                                               ['_login'], {}, None))
        self.assertFalse(builder.include_method('test_login', FakeTests, '',
                                               ['_login'], {}, None))

    def test_negated_compound_tag(self):
        """
        When a compound tag is prefixed with an underscore, include tests that
        *do not* have that tag.
        """
        builder = self.suite_builder()
        self.assertTrue(builder.include_method('test_fast', FakeTests, '',
                                               ['_login'], {}, None))
        self.assertTrue(builder.include_method('test_slow', FakeTests, '',
                                               ['_login'], {}, None))
        self.assertFalse(builder.include_method('test_login', FakeTests, '',
                                               ['_login'], {}, None))

    def test_regex_filter(self):
        """
        When a regex filter is passed in, only tests with names matching
        the filter should be included.
        """
        builder = self.suite_builder()
        self.assertTrue(builder.include_method('test_fast', FakeTests, 'test_fa.*',
                                               [], {}, None))
        self.assertFalse(builder.include_method('test_slow', FakeTests, 'test_fa.*',
                                               [], {}, None))
        self.assertFalse(builder.include_method('test_login', FakeTests, 'test_fa.*',
                                               [], {}, None))
