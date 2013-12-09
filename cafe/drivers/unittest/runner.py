#!/usr/bin/env python
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
import imp
import os
import sys
import time
from fnmatch import fnmatch
from inspect import getmembers, isclass
from multiprocessing import Process, Manager
from re import search
from traceback import extract_tb
import unittest2 as unittest
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cafe.common.reporting.cclogging import log_results
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.decorators import (
    TAGS_DECORATOR_TAG_LIST_NAME, TAGS_DECORATOR_ATTR_DICT_NAME)
from cafe.common.reporting.reporter import Reporter
from cafe.configurator.managers import TestEnvManager


def tree(directory, padding, print_files=False):
    """
    creates an ascii tree for listing files or configs
    """
    files = []
    dir_token = "{0}+-".format(padding[:-1])
    dir_path = os.path.basename(os.path.abspath(directory))

    print "{0}{1}/".format(dir_token, dir_path)

    padding = "{0}{1}".format(padding, " ")

    if print_files:
        try:
            files = os.listdir(directory)
        except OSError:
            print "Directory: {0} Does Not Exist".format(directory)
    else:
        files = [name for name in os.listdir(directory) if
                 os.path.isdir(os.path.join(directory, name))]
    count = 0
    for file_name in files:
        count += 1
        path = os.path.join(directory, file_name)
        if os.path.isdir(path):
            if count == len(files):
                tree(path, "".join([padding, " "]), print_files)
            else:
                tree(path, "".join([padding, "|"]), print_files)
        else:
            if (not file_name.endswith(".pyc") and file_name != "__init__.py"):
                print "{0}{1}".format(padding, file_name)


def error_msg(e_type, e_msg):
    """
    creates an error message
    """
    err_msg = "<[WARNING {0} ERROR {1}]>".format(str(e_type), str(e_msg))

    return err_msg


def print_traceback():
    """
    formats and prints out a minimal stack trace
    """
    info = sys.exc_info()
    excp_type, excp_value = info[:2]
    err_msg = error_msg(excp_type.__name__,
                        excp_value)
    print err_msg
    for file_name, lineno, function, text in extract_tb(info[2]):
        print ">>>", file_name
        print "  > line", lineno, "in", function, repr(text)
    print "-" * 100


class _WritelnDecorator(object):
    """Used to decorate file-like objects with a handy "writeln" method"""

    def __init__(self, stream):
        self.stream = stream

    def __setstate__(self, data):
        self.__dict__.update(data)

    def __getattr__(self, attr):
        return getattr(self.stream, attr)

    def writeln(self, arg=None):
        if arg:
            self.write(arg)
        self.write("\n")


class OpenCafeParallelTextTestRunner(unittest.TextTestRunner):
    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1):
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions
        self.verbosity = verbosity

    def run(self, test):
        """Run the given test case or test suite."""
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        run = result.testsRun
        return result


class LoadedTestClass(object):
    def __init__(self, loaded_module):
        self.module = loaded_module
        self.module_path = self._get_module_path(loaded_module)
        self.module_name = self._get_module_name(loaded_module)

    def _get_class_names(self, loaded_module):
        """
        gets all the class names in an imported module
        """

        for _, obj in getmembers(loaded_module, isclass):
            temp_obj = obj
            try:
                while temp_obj.__base__ != object:
                    if (temp_obj.__base__ == unittest.TestCase
                            or temp_obj.__base__ == BaseTestFixture
                            and temp_obj != obj.__base__):
                                if not search("fixture", obj.__name__.lower()):
                                    yield obj.__name__
                                break
                    else:
                        temp_obj = temp_obj.__base__
            except AttributeError:
                continue

    def _get_class(self, loaded_module, test_class_name):
        class_ = None
        try:
            class_ = getattr(loaded_module, test_class_name)
        except AttributeError, e:
            print e
            return None

        return class_

    def get_instances(self):
        loaded = []
        for class_name in self._get_class_names(self.module):
            if class_name not in loaded:
                loaded.append(class_name)
                yield self._get_class(self.module, class_name)

    def _get_module_path(self, loaded_module):
        return os.path.dirname(loaded_module.__file__)

    def _get_module_name(self, loaded_module):
        return loaded_module.__name__.split(".")[1]


class SuiteBuilder(object):
    def __init__(self, module_regex, method_regex, cl_tags, supress_flag):
        self.module_regex = module_regex
        self.method_regex = method_regex
        self.tags = cl_tags
        self.supress = supress_flag

    def get_dotted_path(self, path, split_token):
        """
        creates a dotted path for use by unittest"s loader
        """
        try:
            position = len(path.split(split_token)) - 1
            temp_path = "{0}{1}".format(
                split_token, path.split(split_token)[position])
            split_path = os.path.split(temp_path)
            dotted_path = ".".join(split_path)
        except AttributeError:
            return None
        except Exception:
            return None

        return dotted_path

    def find_root(self, path, target):
        """
        walks the path searching for the target root folder.
        """
        for root, _, _ in os.walk(path):
            if target in os.path.basename(root):
                return root

    def find_file(self, path, target):
        """
        walks the path searching for the target file. the full to the target
        file is returned
        """
        for root, _, files in os.walk(path):
            for file_name in files:
                if (target in file_name and not file_name.endswith(".pyc")):
                    return os.path.join(root, file_name)

    def find_subdir(self, path, target):
        """
        Walks the path searching for the target subdirectory.
        The full path to the target subdirectory is returned
        """
        for root, dirs, _ in os.walk(path):
            for dir_name in dirs:
                if target in dir_name:
                    return os.path.join(root, dir_name)

    def drill_path(self, path, target):
        """
        walks the path searching for the last instance of the target path.
        """
        return_path = {}
        for root, _, _ in os.walk(path):
            if target in os.path.basename(root):
                return_path[target] = root

        return return_path

    def load_module(self, module_path):
        """
        uses imp to load a module
        """
        loaded_module = None

        module_name = os.path.basename(module_path)
        package_path = os.path.dirname(module_path)

        pkg_name = os.path.basename(package_path)
        root_path = os.path.dirname(package_path)

        module_name = module_name.split('.')[0]

        f, p_path, description = imp.find_module(pkg_name, [root_path])

        loaded_pkg = imp.load_module(pkg_name, f, p_path, description)

        f, m_path, description = imp.find_module(
            module_name, loaded_pkg.__path__)
        try:
            mod = "{0}.{1}".format(loaded_pkg.__name__, module_name)
            loaded_module = imp.load_module(mod, f, m_path, description)
        except ImportError:
            raise

        return loaded_module

    def get_modules(self, rootdir):
        """
        generator yields modules matching the module_regex
        """
        for root, _, files in os.walk(rootdir):
            for name in files:
                if (fnmatch(name, self.module_regex)
                        and name != "__init__.py"
                        and not name.endswith(".pyc")):
                    file_name = name.split(".")[0]
                    full_path = "{0}/{1}".format(root, file_name)
                    yield full_path

    def _parse_tags(self, tags):
        """
        tags sent in from the command line are sent in as a string.
        returns a list of tags and a "+" token if it is present.
        """
        token = None
        tag_list = []
        attrs = {}

        if tags[0] == "+":
            token = tags[0]
            tags = tags[1:]

        for tag in tags:
            tokens = tag.split("=")
            if len(tokens) > 1:
                attrs[tokens[0]] = tokens[1]
            else:
                tag_list[len(tag_list):] = [tag]

        return tag_list, attrs, token

    def _check_attrs(self, method, attrs, token=None):
        """
        checks to see if the method passed in has matching key=value
        attributes. if a "+" token is passed only method that contain
        foo and bar will be match
        """
        truth_values = []
        method_attrs = {}

        attr_keys = attrs.keys()
        method_attrs = method.__dict__[TAGS_DECORATOR_ATTR_DICT_NAME]
        method_attrs_keys = method_attrs.keys()

        for attr_key in attr_keys:
            if attr_key in method_attrs_keys:
                method_val = method_attrs[attr_key]
                attr_val = attrs[attr_key]
                truth_values[len(truth_values):] = [method_val == attr_val]
            else:
                truth_values[len(truth_values):] = [False]

        return (
            False not in truth_values if token == "+"
            else True in truth_values)

    def _check_tags(self, method, tags, token):
        """
        checks to see if the method passed in has matching tags.
        if the tags are (foo, bar) this method will match foo or
        bar. if a "+" token is passed only method that contain
        foo and bar will be match
        """
        method_tags = method.__dict__.get(TAGS_DECORATOR_TAG_LIST_NAME)
        match = set(tags).intersection(method_tags)
        return match == set(tags) if token == "+" else bool(match)

    def _check_method(self, class_, method_name, tags, attrs, token):
        load_test_flag = False
        attr_flag = False
        tag_flag = False

        method = getattr(class_, method_name)

        if (dict(method.__dict__)
                and TAGS_DECORATOR_TAG_LIST_NAME in method.__dict__):
            if tags and not attrs:
                tag_flag = self._check_tags(method, tags, token)
                load_test_flag = tag_flag

            elif not tags and attrs:
                attr_flag = self._check_attrs(method, attrs, token)
                load_test_flag = attr_flag

            elif tags and attrs:
                tag_flag = self._check_tags(method, tags, token)
                attr_flag = self._check_attrs(method, attrs, token)
                load_test_flag = attr_flag and tag_flag

        return load_test_flag

    def build_suite(self, loaded_module):
        """
        loads the found tests and builds the test suite
        """
        tag_list = []
        attrs = {}
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        loaded = LoadedTestClass(loaded_module)

        if self.tags:
            tag_list, attrs, token = self._parse_tags(self.tags)

        if (hasattr(loaded_module, "load_tests")
                and not self.supress
                and self.method_regex == "test_*"
                and self.tags is None):
            load_tests = getattr(loaded_module, "load_tests")
            suite.addTests(load_tests(loader, None, None))
            return suite

        for class_ in loaded.get_instances():
            for method_name in dir(class_):
                load_test_flag = False

                if fnmatch(method_name, self.method_regex):
                    if not self.tags:
                        load_test_flag = True
                    else:
                        load_test_flag = self._check_method(
                            class_, method_name, tag_list, attrs, token)
                    if load_test_flag:
                        suite.addTest(class_(method_name))
        return suite

    def get_tests(self, module_path):
        suite = unittest.TestSuite()

        try:
            loaded_module = self.load_module(module_path)
        except ImportError:
            print_traceback()
            return None

        try:
            suite = self.build_suite(loaded_module)
        except Exception:
            print_traceback()
            return None

        return suite

    def generate_suite(self, path, suite=None):
        master_suite = suite or unittest.TestSuite()
        for module_path in self.get_modules(path):
            st = self.get_tests(module_path)
            if st:
                master_suite.addTests(st)
        return master_suite

    def generate_suite_list(self, path, suite_list=None):
        master_suite_list = suite_list or []
        for module_path in self.get_modules(path):
            st = self.get_tests(module_path)
            if st:
                master_suite_list.append(st)
        return master_suite_list


class _UnittestRunnerCLI(object):

    class ListAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            product = namespace.product or ""
            test_env_mgr = TestEnvManager(product, None)
            test_dir = os.path.expanduser(
                os.path.join(test_env_mgr.test_repo_path, product))
            product_config_dir = os.path.expanduser(os.path.join(
                test_env_mgr.engine_config_interface.config_directory,
                product))

            def _print_test_tree():
                print "\n<[TEST REPO]>\n"
                tree(test_dir, " ", print_files=True)

            def _print_config_tree():
                print "\n<[CONFIGS]>\n"
                tree(product_config_dir, " ", print_files=True)

            def _print_product_tree():
                print "\n<[PRODUCTS]>\n"
                tree(test_env_mgr.test_repo_path, " ", print_files=False)

            def _print_product_list():
                print "\n<[PRODUCTS]>\n"
                print "+-{0}".format(product_config_dir)
                print "\n".join(
                    ["  +-{0}/".format(dirname) for dirname in os.listdir(
                        product_config_dir)])

            #If no values passed, print a default
            if not values:
                if namespace.product and namespace.config:
                    _print_test_tree()
                elif namespace.product and not namespace.config:
                    _print_config_tree()
                    _print_test_tree()
                elif not namespace.product and not namespace.config:
                    _print_product_list()

            # Loop through values so that the trees get printed in the order
            # the values where passed on the command line
            for arg in values:
                if arg == 'products':
                    _print_product_tree()

                if arg == 'configs':
                    _print_config_tree()

                if arg == 'tests':
                    _print_test_tree()

            exit(0)

    class ProductAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # Add the product to the namespace
            setattr(namespace, self.dest, values)

    class ConfigAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # Make sure user provided config name ends with '.config'
            if values is not None:
                if not str(values).endswith('.config'):
                    values = "{0}{1}".format(values, ".config")

                test_env = TestEnvManager(namespace.product or "", values)
                if not os.path.exists(test_env.test_config_file_path):
                    print (
                        "cafe-runner: error: config file at {0} does not "
                        "exist".format(test_env.test_config_file_path))
                    exit(1)

            setattr(namespace, self.dest, values)

    class ModuleRegexAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # Make sure user-specified module name has a .py at the end of it
            if ".py" not in str(values):
                values = "{0}{1}".format(values, ".py")

            setattr(namespace, self.dest, values)

    class MethodRegexAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            # Make sure user-specified method name has test_ at the start of it

            if 'test_' not in str(values):
                values = "{0}{1}".format("test_", values)

            setattr(namespace, self.dest, values)

    class DataAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            dict_string = ""
            data_range = len(values)

            for i in range(data_range):
                values[i] = values[i].replace("=", "': '")
                values[i] = "'{0}'".format(values[i])

            dict_string = ", ".join(values)
            dict_string = "{0}{1}{2}".format("{", dict_string, "}")
            os.environ["DICT_STRING"] = dict_string
            setattr(namespace, self.dest, values)

    class DataDirectoryAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            if not os.path.exists(values):
                print (
                    "cafe-runner: error: data-directory '{0}' does not "
                    "exist".format(values))
                exit(1)
            setattr(namespace, self.dest, values)

    class VerboseAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):

            msg = None
            if values is None:
                msg = "-v/--verbose requires an integer value of 1, 2 or 3"

            elif values not in (1, 2, 3):
                msg = (
                    "cafe-runner: error: {0} is not a valid argument for "
                    "-v/--verbose".format(values))
            if msg:
                print parser.usage
                print msg
                exit(1)

            os.environ["VERBOSE"] = "true" if values == 3 else "false"
            setattr(namespace, self.dest, values)

    def get_cl_args(self):
        """
        collects and parses the command line args
        creates the runner"s help msg
        """
        base = "{0} {1} {2}".format("cafe-runner", "<product>", "<config>")
        mod = "{0} {1}".format("-m", "<module pattern>")
        mthd = "{0} {1}".format("-M", "<test method>")
        testtag = "{0} {1}".format("-t", "[tag tag...]")
        pkg = "{0} {1}".format("-p", "[package package...]")

        usage_string = """
        *run all the tests for a product
        {baseargs}

        *run all the tests for a product with matching module name pattern
        {baseargs} {module}

        *run all the tests for a product with matching the method name pattern
        {baseargs} {method}

        *run all the tests for a product with matching tag(s)
        {baseargs} {tags}

        *run all the tests for a product with matching the method name pattern
        and matching tag(s)
        {baseargs} {method} {tags}

        *run all the tests for a product with matching module name pattern,
        method name pattern and matching tag(s)
        {baseargs} {module} {method} {tags}

        **run all modules in a package(s) for a product
        {baseargs} {package}

        **run all modules in a package(s) for a product matching a name pattern
        {baseargs} {package} {module}

        **run all modules in a package(s) for a product with matching method
        name pattern
        {baseargs} {package} {module} {method}

        **run all modules in a package(s) for a product with matching tag(s)
        {baseargs} {package} {tags}

        **run all modules in a package(s) for a product with matching method
        name pattern and matching tag(s)
        {baseargs} {package} {method} {tags}

        **run all modules in a package(s) for a product with matching module
        name pattern, method name pattern and matching tag(s)
        {baseargs} {package} {module} {method} {tags}

        LIST:
        format: -l/--list [products, configs, tests]
        Can be used to list products, configs and tests if used as a flag or
        as a replacement for any required argument.

        As an optional flag:
        -l/--list 'products', 'configs' or 'tests' can be used anywhere as an
        optional flag to print the respective list.  The runner will exit
        after the list is printed.

        As a replacement for any positional flag:
        *list all products
            cafe-runner -l/--list

        *list configs and tests for a product
            cafe-runner <product> -l/--list

        *list tests for a product
            cafe-runner <product> <config> -l/--list

        TAGS:
        format: -t [+] tag1 tag2 tag3 key1=value key2=value
        By default tests with that match any of the tags will be returned.
        Sending a "+" as the first character in the tag list will only
        returned all the tests that match all the tags.

        config file and optional module name given on the command line
        do not have .config and .py extensions respectively.

        by default if no packages are specified, all tests under the
        product"s test repo folder will be run.

        runner will search under the products testrepo folder for the
        package so full dotted package paths are not necessary on the
        command line.

        if a module is specified, all modules matching the name pattern
        will be run under the products test repo folder or packages (if
        specified).
        """.format(
            baseargs=base, package=pkg, module=mod, method=mthd, tags=testtag)

        desc = "Cloud Common Automated Engine Framework"

        argparser = argparse.ArgumentParser(
            usage=usage_string, description=desc)

        argparser.add_argument(
            "product",
            action=self.ProductAction,
            nargs='?',
            default=None,
            metavar="<product>",
            help="product name")

        argparser.add_argument(
            "config",
            action=self.ConfigAction,
            nargs='?',
            default=None,
            metavar="<config_file>",
            help="product test config")

        argparser.add_argument(
            "-v", "--verbose",
            action=self.VerboseAction,
            nargs="?",
            default=2,
            type=int,
            help="set unittest output verbosity")

        argparser.add_argument(
            "-l", "--list",
            action=self.ListAction,
            nargs="*",
            choices=["products", "configs", "tests"],
            help="list tests and or configs")

        argparser.add_argument(
            "-f", "--fail-fast",
            default=False,
            action="store_true",
            help="fail fast")

        argparser.add_argument(
            "-s", "--supress-load-tests",
            default=False,
            action="store_true",
            dest="supress_flag",
            help="supress load tests method")

        argparser.add_argument(
            "-p", "--packages",
            nargs="*",
            default=None,
            metavar="[package(s)]",
            help="test package(s) in the product's "
                 "test repo")

        argparser.add_argument(
            "-m", "--module-regex", "--module",
            action=self.ModuleRegexAction,
            default="*.py",
            metavar="<module>",
            help="test module regex - defaults to '*.py'")

        argparser.add_argument(
            "-M", "--method-regex",
            action=self.MethodRegexAction,
            default="test_*",
            metavar="<method>",
            help="test method regex defaults to 'test_'")

        argparser.add_argument(
            "-t", "--tags",
            nargs="*",
            default=None,
            metavar="tags",
            help="tags")

        argparser.add_argument(
            "--result",
            choices=["json", "xml"],
            help="generates a specified formatted result file")

        argparser.add_argument(
            "--result-directory",
            help="directory for result file to be stored")

        argparser.add_argument(
            "--parallel",
            action="store_true",
            default=False)

        argparser.add_argument(
            "--data-directory",
            action=self.DataDirectoryAction,
            help="directory for tests to get data from")

        argparser.add_argument(
            "-d", "--data",
            action=self.DataAction,
            nargs="*",
            default=None,
            metavar="data",
            help="arbitrary test data")

        args = argparser.parse_args()

        # Special case for when product or config is missing and --list
        # wasn't called
        if args.product is None or args.config is None:
            print argparser.usage
            print (
                "cafe-runner: error: You must supply both a product and a "
                "config to run tests")
            exit(1)

        if (args.result or args.result_directory) and (
                args.result is None or args.result_directory is None):
            print argparser.usage
            print (
                "cafe-runner: error: You must supply both a --result and a "
                "--result-directory to print out json or xml formatted "
                "results.")
            exit(1)

        return args


class UnittestRunner(object):
    def __init__(self):
        self.cl_args = _UnittestRunnerCLI().get_cl_args()
        self.test_env = TestEnvManager(
            self.cl_args.product, self.cl_args.config)

        # If something in the cl_args is supposed to override a default, like
        # say that data directory or something, it needs to happen before
        # finalize() is called
        self.test_env.test_data_directory = (
            self.test_env.test_data_directory or self.cl_args.data_directory)
        self.product_repo_path = os.path.join(
            self.test_env.test_repo_path, self.cl_args.product)
        self.test_env.finalize()
        self.print_mug_and_paths(self.test_env)

    @staticmethod
    def print_mug_and_paths(test_env):
        print """
    ( (
     ) )
  .........
  |       |___
  |       |_  |
  |  :-)  |_| |
  |       |___|
  |_______|
=== CAFE Runner ==="""
        print "=" * 150
        print "Percolated Configuration"
        print "-" * 150
        print "BREWING FROM: ....: {0}".format(test_env.test_repo_path)
        print "ENGINE CONFIG FILE: {0}".format(test_env.engine_config_path)
        print "TEST CONFIG FILE..: {0}".format(test_env.test_config_file_path)
        print "DATA DIRECTORY....: {0}".format(test_env.test_data_directory)
        print "LOG PATH..........: {0}".format(test_env.test_log_dir)
        print "=" * 150

    @staticmethod
    def execute_test(runner, test, results):
        result = runner.run(test)
        results.append(result)

    @staticmethod
    def get_runner(parallel, fail_fast, verbosity):
        test_runner = None

        # Use the parallel text runner so the console logs look correct
        if parallel:
            test_runner = OpenCafeParallelTextTestRunner(
                verbosity=int(verbosity))
        else:
            test_runner = unittest.TextTestRunner(verbosity=int(verbosity))

        test_runner.failfast = fail_fast
        return test_runner

    @staticmethod
    def dump_results(start, finish, results):
        print "-" * 71

        tests_run = 0
        errors = 0
        failures = 0
        for result in results:
            tests_run += result.testsRun
            errors += len(result.errors)
            failures += len(result.failures)

        print "Ran {0} test{1} in {2:.3f}s".format(
            tests_run, "s" if tests_run != 1 else "", finish - start)

        if failures or errors:
            print "\nFAILED ({0}{1}{2})".format(
                "Failures={0}".format(failures) if failures else "",
                " " if failures and errors else "",
                "Errors={0}".format(errors) if errors else "")

        return errors, failures, tests_run

    def run(self):
        """
        loops through all the packages, modules, and methods sent in from
        the command line and runs them
        """
        master_suite = unittest.TestSuite()
        parallel_test_list = []

        builder = SuiteBuilder(
            self.cl_args.module_regex,
            self.cl_args.method_regex,
            self.cl_args.tags,
            self.cl_args.supress_flag)

        test_runner = self.get_runner(
            self.cl_args.parallel,
            self.cl_args.fail_fast,
            self.cl_args.verbose)

        #Build master test suite
        if self.cl_args.packages:
            for package_name in self.cl_args.packages:
                path = builder.find_subdir(
                    self.product_repo_path, package_name)
                if path is None:
                    print error_msg("PACKAGE", package_name)
                    continue
                master_suite = builder.generate_suite(path, master_suite)
                if self.cl_args.parallel:
                    parallel_test_list = builder.generate_suite_list(
                        path, parallel_test_list)
        else:
            master_suite = builder.generate_suite(
                self.product_repo_path)
            if self.cl_args.parallel:
                parallel_test_list = builder.generate_suite_list(
                    self.product_repo_path)

        if self.cl_args.parallel:
            exit_code = self.run_parallel(
                parallel_test_list,
                test_runner,
                result_type=self.cl_args.result,
                results_path=self.cl_args.result_directory)
            exit(exit_code)
        else:
            exit_code = self.run_serialized(
                master_suite,
                test_runner,
                result_type=self.cl_args.result,
                results_path=self.cl_args.result_directory)
            exit(exit_code)

    def run_parallel(
            self, test_suites, test_runner, result_type=None,
            results_path=None):

        exit_code = 0
        proc = None
        unittest.installHandler()
        processes = []
        manager = Manager()
        results = manager.list()
        start = time.time()

        for test_suite in test_suites:
            proc = Process(
                target=self.execute_test,
                args=(test_runner, test_suite, results))
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        finish = time.time()

        errors, failures, _ = self.dump_results(start, finish, results)

        if result_type is not None:
            all_results = []
            for tests, result in zip(test_suites, results):
                result_parser = SummarizeResults(
                    vars(result), tests, (finish - start))
                all_results += result_parser.gather_results()

            reporter = Reporter(
                result_parser=result_parser, all_results=all_results)
            reporter.generate_report(
                result_type=result_type, path=results_path)

        if failures or errors:
            exit_code = 1

        return exit_code

    def run_serialized(
            self, master_suite, test_runner, result_type=None,
            results_path=None):

        exit_code = 0
        unittest.installHandler()
        start_time = time.time()
        result = test_runner.run(master_suite)
        total_execution_time = time.time() - start_time

        if result_type is not None:
            result_parser = SummarizeResults(vars(result), master_suite,
                                             total_execution_time)
            all_results = result_parser.gather_results()
            reporter = Reporter(result_parser=result_parser,
                                all_results=all_results)
            reporter.generate_report(result_type=result_type,
                                     path=results_path)

        log_results(result)
        if not result.wasSuccessful():
            exit_code = 1

        return exit_code


def entry_point():
    runner = UnittestRunner()
    runner.run()
    exit(0)
