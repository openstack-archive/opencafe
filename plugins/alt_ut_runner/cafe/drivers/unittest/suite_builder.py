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
from __future__ import print_function

from inspect import isclass, ismethod
from sys import stderr
from traceback import print_exc
import importlib
import pkgutil
import re
import unittest

from cafe.drivers.unittest.decorators import TAGS_DECORATOR_TAG_LIST_NAME


def print_exception(file_, method, value, e=""):
    print("{0}".format("=" * 70), file=stderr)
    print("{0}: {1}: {2}: {3}".format(
        file_, method, value, e), file=stderr)
    print("{0}".format("-" * 70), file=stderr)
    print_exc(file=stderr)
    print()


class SuiteBuilder(object):
    def __init__(
        self, testrepos, tags=None, all_tags=False, dotpath_regex=None,
            file_=None, dry_run=False, exit_on_error=False):
        self.testrepos = testrepos
        self.tags = tags or []
        self.all_tags = all_tags
        self.regex_list = dotpath_regex or []
        self.exit_on_error = exit_on_error
        self.dry_run = dry_run
        # dict format {"ubroast.test.test1.TestClass": ["test_t1", "test_t2"]}
        self.file_ = file_ or {}

    def get_suites(self):
        test_suites = self._load_file()
        for class_ in self._get_classes(self._get_modules()):
            suite = unittest.suite.TestSuite()
            for test in self._get_tests(class_):
                suite.addTest(class_(test))
            if suite._tests:
                test_suites.append(suite)
        if self.dry_run:
            for suite in test_suites:
                for test in suite:
                    print(test)
            exit(0)
        return test_suites

    def _load_file(self):
        suites = []
        for key, value in self.file_.items():
            suite = unittest.suite.TestSuite()
            module, class_ = key.rsplit(".", 1)
            module = importlib.import_module(module)
            class_ = getattr(module, class_)
            for test in value:
                suite.addTest(class_(test))
            suites.append(suite)
        return suites

    def _get_modules(self):
        modules = []
        error = False
        for repo in self.testrepos:
            if not repo.__file__.endswith("__init__.pyc"):
                modules.append(repo)
                continue
            prefix = "{0}.".format(repo.__name__)
            for importer, modname, is_pkg in pkgutil.walk_packages(
                    path=repo.__path__, prefix=prefix, onerror=lambda x: None):
                if not is_pkg:
                    try:
                        modules.append(importlib.import_module(modname))
                    except Exception as e:
                        print_exception(
                            "Suite Builder", "import_module", modname, e)
                        error = True
        if self.exit_on_error and error:
            exit(1)
        return modules

    def _get_classes(self, modules):
        classes = []
        for loaded_module in modules:
            for objname in dir(loaded_module):
                obj = getattr(loaded_module, objname, None)
                if (isclass(obj) and issubclass(obj, unittest.TestCase) and
                        "fixture" not in obj.__name__.lower()):
                    if getattr(obj, "__test__", None) is not None:
                        print("Feature __test__ deprecated: Not skipping:"
                              "{0}".format(obj.__name__))
                        print("Use unittest.skip(reason)")
                    classes.append(obj)
        return classes

    def _get_tests(self, class_):
        tests = []
        for name in dir(class_):
            if name.startswith("test_") and self._check_test(class_, name):
                tests.append(name)
        return tests

    def _check_test(self, class_, test_name):
        test = getattr(class_, test_name)
        full_path = "{0}.{1}.{2}".format(
            class_.__module__, class_.__name__, test_name)
        ret_val = ismethod(test) and self._check_tags(test)
        regex_val = not self.regex_list
        for regex in self.regex_list:
            regex_val |= bool(re.search(regex, full_path))
        return ret_val & regex_val

    def _check_tags(self, test):
        """
        checks to see if the test passed in has matching tags.
        if the tags are (foo, bar) this function will match foo or
        bar. if a all_tags is true only tests that contain
        foo and bar will be matched including a test that contains
        (foo, bar, bazz)
        """
        test_tags = getattr(test, TAGS_DECORATOR_TAG_LIST_NAME, [])
        if self.all_tags:
            return all([tag in test_tags for tag in self.tags])
        else:
            return any([tag in test_tags for tag in self.tags] or [True])
