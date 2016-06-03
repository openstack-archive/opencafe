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

import argparse
import os
import pkgutil
import sys
import time
import unittest
import uuid
from importlib import import_module
from inspect import isclass
from re import search
from traceback import print_exc
from cafe.common.reporting import cclogging
from cafe.common.reporting.reporter import Reporter
from cafe.configurator.managers import TestEnvManager
from cafe.drivers.unittest.decorators import (
    TAGS_DECORATOR_TAG_LIST_NAME, TAGS_DECORATOR_ATTR_DICT_NAME)
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.suite import OpenCafeUnittestTestSuite

# Support for the alternate dill-based multiprocessing library 'multiprocess'
# as an experimental workaround if you're having pickling errors.
try:
    from multiprocess import Process, Manager
    sys.stdout.write(
        "\n\nUtilizing the pathos multiprocess library. "
        "This feature is experimental\n\n")
except:
    from multiprocessing import Process, Manager


def tree(directory, padding, print_files=False):
    """
    creates an ascii tree for listing files or configs
    """
    files = []
    dir_token = "{0}+-".format(padding[:-1])
    dir_path = os.path.basename(os.path.abspath(directory))

    print("{0}{1}/".format(dir_token, dir_path))

    padding = "{0}{1}".format(padding, " ")

    if print_files:
        try:
            files = os.listdir(directory)
        except OSError:
            print("Directory: {0} Does Not Exist".format(directory))
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
                print("{0}{1}".format(padding, file_name))


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
        test(result)
        result.printErrors()
        return result


class SuiteBuilder(object):

    def __init__(self, cl_args, test_repo_name):
        self.packages = cl_args.packages or []
        self.module_regex = cl_args.module_regex
        self.method_regex = cl_args.method_regex
        self.tags = cl_args.tags
        self.supress = cl_args.supress_flag
        self.product = cl_args.product
        self.test_repo_name = test_repo_name

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

        attr_keys = list(attrs.keys())
        method_attrs = method.__dict__[TAGS_DECORATOR_ATTR_DICT_NAME]
        method_attrs_keys = list(method_attrs.keys())

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
        return match == set(method_tags) if token == "+" else bool(match)

    def _check_method(self, class_, method_name, tags, attrs, token):
        """
        checks tags on methods
        """
        load_test_flag = False
        attr_flag = False
        tag_flag = False

        method = getattr(class_, method_name)

        if (dict(method.__dict__) and
                TAGS_DECORATOR_TAG_LIST_NAME in method.__dict__):
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

    def get_classes(self, loaded_module):
        """
        finds all the classes in a loaded module calculates full path to class
        """
        classes = []
        for objname in dir(loaded_module):
            obj = getattr(loaded_module, objname, None)
            if (isclass(obj) and issubclass(obj, unittest.TestCase) and
                "fixture" not in obj.__name__.lower() and
                    getattr(obj, "__test__", True)):
                classes.append(obj)
        return classes

    def build_suite(self, module_path):
        """
        loads the found tests and builds the test suite
        """
        tag_list = []
        attrs = {}
        loader = unittest.TestLoader()
        suite = OpenCafeUnittestTestSuite()
        try:
            loaded_module = import_module(module_path)
        except Exception as e:
            sys.stderr.write("{0}\n".format("=" * 70))
            sys.stderr.write(
                "Failed to load module '{0}'\n".format(module_path, e))
            sys.stderr.write("{0}\n".format("-" * 70))
            print_exc(file=sys.stderr)
            sys.stderr.write("{0}\n".format("-" * 70))
            return

        if self.tags:
            tag_list, attrs, token = self._parse_tags(self.tags)

        if (hasattr(loaded_module, "load_tests") and
                not self.supress and
                not self.method_regex and
                self.tags is None):
            load_tests = getattr(loaded_module, "load_tests")
            suite.addTests(load_tests(loader, None, None))
            return suite

        for class_ in self.get_classes(loaded_module):
            for method_name in dir(class_):
                if (method_name.startswith("test_") and
                    search(self.method_regex, method_name) and
                    (not self.tags or self._check_method(
                        class_, method_name, tag_list, attrs, token))):
                    suite.addTest(class_(method_name))
        return suite

    def get_modules(self):
        """
        walks all modules in the test repo, filters by
        product and module filter. Filter passed in with -m
        returns a list of module dotpath strings
        """
        test_repo = import_module(self.test_repo_name)
        prefix = "{0}.".format(test_repo.__name__)
        product_path = "{0}{1}".format(prefix, self.product)
        modnames = []
        for importer, modname, is_pkg in pkgutil.walk_packages(
                path=test_repo.__path__, prefix=prefix,
                onerror=lambda x: None):
            if not is_pkg and modname.startswith(product_path):
                if (not self.module_regex or
                        self.module_regex in modname.rsplit(".", 1)[1]):
                    modnames.append(modname)

        filter_mods = []
        for modname in modnames:
            add_package = not bool(self.packages)
            for package in self.packages:
                if package in modname.rsplit(".", 1)[0]:
                    add_package = True
                    break
            if add_package:
                filter_mods.append(modname)
        filter_mods.sort()
        return filter_mods

    def generate_suite(self):
        """
        creates a single unittest test suite
        """
        master_suite = OpenCafeUnittestTestSuite()
        modules = self.get_modules()

        for modname in modules:
            suite = self.build_suite(modname)
            if suite:
                master_suite.addTests(suite)
        return master_suite

    def generate_suite_list(self):
        """
        creates a list containing unittest test suites
        """
        master_suite_list = []
        modules = self.get_modules()

        for modname in modules:
            suite = self.build_suite(modname)

            if suite and len(suite._tests):
                master_suite_list.append(suite)
        return master_suite_list


class _UnittestRunnerCLI(object):

    class ListAction(argparse.Action):

        def __call__(self, parser, namespace, values, option_string=None):

            product = namespace.product or ""
            test_env_mgr = TestEnvManager(
                product, None, test_repo_package_name=namespace.test_repo)
            test_dir = os.path.expanduser(
                os.path.join(test_env_mgr.test_repo_path, product))
            product_config_dir = os.path.expanduser(os.path.join(
                test_env_mgr.engine_config_interface.config_directory,
                product))

            def _print_test_tree():
                print("\n<[TEST REPO]>\n")
                tree(test_dir, " ", print_files=True)

            def _print_config_tree():
                print("\n<[CONFIGS]>\n")
                tree(product_config_dir, " ", print_files=True)

            def _print_product_tree():
                print("\n<[PRODUCTS]>\n")
                tree(test_env_mgr.test_repo_path, " ", print_files=False)

            def _print_product_list():
                print("\n<[PRODUCTS]>\n")
                print("+-{0}".format(product_config_dir))
                print("\n".join(
                    ["  +-{0}/".format(dirname) for dirname in os.listdir(
                        product_config_dir)]))

            # If no values passed, print a default
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
                    print(
                        "cafe-runner: error: config file at {0} does not "
                        "exist".format(test_env.test_config_file_path))
                    exit(1)

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
                print(
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
                print(parser.usage)
                print(msg)
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

        desc = "Open Common Automation Framework Engine"

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
            "--test-repo",
            default=None,
            metavar="<test-repo>",
            help="The name of the package containing the tests. "
                 "This overrides the value in the engine.config file, as well "
                 "as the CAFE_OPENCAFE_ENGINE_default_test_repo environment "
                 "variable.")

        argparser.add_argument(
            "-v", "--verbose",
            action=self.VerboseAction,
            nargs="?",
            default=2,
            type=int,
            help="set unittest output verbosity")

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
            nargs="+",
            default=None,
            metavar="<string filter>",
            help="Package Filter")

        argparser.add_argument(
            "-m", "--module-regex", "--module",
            default="",
            metavar="<string filter>",
            help="Test module filter")

        argparser.add_argument(
            "-M", "--method-regex",
            default="",
            metavar="<string filter>",
            help="Test method filter. defaults to 'test_'")

        argparser.add_argument(
            "-t", "--tags",
            nargs="*",
            default=None,
            metavar="tags",
            help="tags")

        argparser.add_argument(
            "--result",
            choices=["json", "xml", "subunit"],
            help="generates a specified formatted result file")

        argparser.add_argument(
            "--result-directory",
            help="directory for result file to be stored")

        argparser.add_argument(
            "--parallel",
            action="store_true",
            default=False)

        argparser.add_argument(
            "--dry-run",
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

        argparser.add_argument(
            "-l", "--list",
            action=self.ListAction,
            nargs="*",
            choices=["products", "configs", "tests"],
            help="list tests and or configs")

        args = argparser.parse_args()

        # Special case for when product or config is missing and --list
        # wasn't called
        if args.product is None or args.config is None:
            print(argparser.usage)
            print (
                "cafe-runner: error: You must supply both a product and a "
                "config to run tests")
            exit(1)

        if (args.result or args.result_directory) and (
                args.result is None or args.result_directory is None):
            print(argparser.usage)
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
            self.cl_args.product, self.cl_args.config,
            test_repo_package_name=self.cl_args.test_repo)

        # If something in the cl_args is supposed to override a default, like
        # say that data directory or something, it needs to happen before
        # finalize() is called
        self.test_env.test_data_directory = (
            self.test_env.test_data_directory or self.cl_args.data_directory)
        self.test_env.finalize()
        cclogging.init_root_log_handler()
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))
        self.product = self.cl_args.product
        self.print_mug_and_paths(self.test_env)

    @staticmethod
    def print_mug_and_paths(test_env):
        print("""
    ( (
     ) )
  .........
  |       |___
  |       |_  |
  |  :-)  |_| |
  |       |___|
  |_______|
=== CAFE Runner ===""")
        print("=" * 150)
        print("Percolated Configuration")
        print("-" * 150)
        print("BREWING FROM: ....: {0}".format(test_env.test_repo_path))
        print("ENGINE CONFIG FILE: {0}".format(test_env.engine_config_path))
        print("TEST CONFIG FILE..: {0}".format(test_env.test_config_file_path))
        print("DATA DIRECTORY....: {0}".format(test_env.test_data_directory))
        print("LOG PATH..........: {0}".format(test_env.test_log_dir))
        print("=" * 150)

    @staticmethod
    def execute_test(runner, test_id, test, results):
        result = runner.run(test)
        results.update({test_id: result})

    @staticmethod
    def get_runner(cl_args):
        test_runner = None

        # Use the parallel text runner so the console logs look correct
        if cl_args.parallel:
            test_runner = OpenCafeParallelTextTestRunner(
                verbosity=cl_args.verbose)
        else:
            test_runner = unittest.TextTestRunner(verbosity=cl_args.verbose)

        test_runner.failfast = cl_args.fail_fast
        return test_runner

    @staticmethod
    def dump_results(start, finish, results):
        print("-" * 71)

        tests_run = 0
        errors = 0
        failures = 0
        for key, result in list(results.items()):
            tests_run += result.testsRun
            errors += len(result.errors)
            failures += len(result.failures)

        print("Ran {0} test{1} in {2:.3f}s".format(
            tests_run, "s" if tests_run != 1 else "", finish - start))

        if failures or errors:
            print("\nFAILED ({0}{1}{2})".format(
                "Failures={0}".format(failures) if failures else "",
                " " if failures and errors else "",
                "Errors={0}".format(errors) if errors else ""))

        return errors, failures, tests_run

    def run(self):
        """
        loops through all the packages, modules, and methods sent in from
        the command line and runs them
        """
        master_suite = OpenCafeUnittestTestSuite()
        parallel_test_list = []
        test_count = 0

        builder = SuiteBuilder(self.cl_args, self.test_env.test_repo_package)
        test_runner = self.get_runner(self.cl_args)

        if self.cl_args.parallel:
            parallel_test_list = builder.generate_suite_list()
            test_count = len(parallel_test_list)
            if self.cl_args.dry_run:
                for suite in parallel_test_list:
                    for test in suite:
                        print(test)
                exit(0)
            exit_code = self.run_parallel(
                parallel_test_list, test_runner,
                result_type=self.cl_args.result,
                results_path=self.cl_args.result_directory)
        else:
            master_suite = builder.generate_suite()
            test_count = master_suite.countTestCases()
            if self.cl_args.dry_run:
                for test in master_suite:
                    print(test)
                exit(0)
            exit_code = self.run_serialized(
                master_suite, test_runner, result_type=self.cl_args.result,
                results_path=self.cl_args.result_directory)

        """
        Exit with a non-zero exit code if no tests where run, so that
        external monitoring programs (like Jenkins) can tell
        something is up
        """
        if test_count <= 0:
            exit_code = 1
        exit(exit_code)

    def run_parallel(
            self, test_suites, test_runner, result_type=None,
            results_path=None):

        exit_code = 0
        proc = None
        unittest.installHandler()
        processes = []
        manager = Manager()
        results = manager.dict()
        manager.dict()
        start = time.time()

        test_mapping = {}
        for test_suite in test_suites:
            # Give each test suite an uuid so it can be
            # matched to the correct test result
            test_id = str(uuid.uuid4())
            test_mapping[test_id] = test_suite

            proc = Process(
                target=self.execute_test,
                args=(test_runner, test_id, test_suite, results))
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        finish = time.time()

        errors, failures, _ = self.dump_results(start, finish, results)

        if result_type is not None:
            all_results = []
            for test_id, result in list(results.items()):
                tests = test_mapping[test_id]
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
            result_parser = SummarizeResults(
                vars(result), master_suite, total_execution_time)
            all_results = result_parser.gather_results()
            reporter = Reporter(
                result_parser=result_parser, all_results=all_results)
            reporter.generate_report(
                result_type=result_type, path=results_path)

        self._log_results(result)
        if not result.wasSuccessful():
            exit_code = 1

        return exit_code

    def _log_results(self, result):
        """Replicates the printing functionality of unittest's runner.run() but
        log's instead of prints
        """

        infos = []
        expected_fails = unexpected_successes = skipped = 0

        try:
            results = list(map(len, (
                result.expectedFailures, result.unexpectedSuccesses,
                result.skipped)))
            expected_fails, unexpected_successes, skipped = results
        except AttributeError:
            pass

        if not result.wasSuccessful():
            failed, errored = list(map(len, (result.failures, result.errors)))

            if failed:
                infos.append("failures={0}".format(failed))
            if errored:
                infos.append("errors={0}".format(errored))

            self.log_errors('ERROR', result, result.errors)
            self.log_errors('FAIL', result, result.failures)
            self._log.info("Ran {0} Tests".format(result.testsRun))
            self._log.info('FAILED ')
        else:
            self._log.info("Ran {0} Tests".format(result.testsRun))
            self._log.info("Passing all tests")

        if skipped:
            infos.append("skipped={0}".format(str(skipped)))
        if expected_fails:
            infos.append("expected failures={0}".format(expected_fails))
        if unexpected_successes:
            infos.append("unexpected successes={0}".format(
                str(unexpected_successes)))
        if infos:
            self._log.info(" ({0})\n".format((", ".join(infos),)))
        else:
            self._log.info("\n")

        print('=' * 150)
        print("Detailed logs: {0}".format(os.getenv("CAFE_TEST_LOG_PATH")))
        print('-' * 150)

    def log_errors(self, label, result, errors):
        border1 = '=' * 45
        border2 = '-' * 45

        for test, err in errors:
            msg = "{0}: {1}\n".format(label, result.getDescription(test))
            self._log.info(
                "{0}\n{1}\n{2}\n{3}".format(border1, msg, border2, err))


def entry_point():
    runner = UnittestRunner()
    runner.run()
    exit(0)
