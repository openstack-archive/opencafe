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

import os
import sys
import time
import argparse
import unittest2 as unittest
import json
from re import search
from multiprocessing import Process, Manager
from datetime import datetime
from imp import find_module, load_module
from inspect import getmembers, isclass
from fnmatch import fnmatch
from traceback import extract_tb
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cafe.common.reporting.cclogging import log_results
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.decorators import (
    TAGS_DECORATOR_TAG_LIST_NAME, TAGS_DECORATOR_ATTR_DICT_NAME)
from cafe.configurator.managers import (
    UnittestRunnerTestEnvManager, EngineDirectoryManager, EngineConfigManager)

UnittestRunnerTestEnvManager.set_engine_config_path()
engine_config = UnittestRunnerTestEnvManager.get_engine_config_interface()
test_repo_path = UnittestRunnerTestEnvManager.set_test_repo_package_path()
BASE_DIR = EngineDirectoryManager.OPENCAFE_ROOT_DIR


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
        for class_name in self._get_class_names(self.module):
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
                split_token,
                path.split(split_token)[position])
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
        root_path = None

        for root, _, _ in os.walk(path):
            if os.path.basename(root).find(target) != -1:
                root_path = root
                break
            else:
                continue

        return root_path

    def find_file(self, path, target):
        """
        walks the path searching for the target file. the full to the target
        file is returned
        """
        file_path = None

        for root, _, files in os.walk(path):
            for file_name in files:
                if (file_name.find(target) != -1
                        and file_name.find(".pyc") == -1):
                    file_path = os.path.join(root, file_name)
                    break
                else:
                    continue

        return file_path

    def find_subdir(self, path, target):
        """
        walks the path searching for the target subdirectory.
        the full to the target subdirectory is returned
        """
        subdir_path = None

        for root, dirs, _ in os.walk(path):
            for dir_name in dirs:
                if dir_name.find(target) != -1:
                    subdir_path = os.path.join(root, dir_name)
                    break
                else:
                    continue

        return subdir_path

    def drill_path(self, path, target):
        """
        walks the path searching for the last instance of the target path.
        """
        return_path = {}
        for root, _, _ in os.walk(path):
            if os.path.basename(root).find(target) != -1:
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

        if module_name.find(".py") != -1:
            module_name = module_name.split(".")[0]

        f, p_path, description = find_module(pkg_name, [root_path])
        loaded_pkg = load_module(pkg_name, f, p_path, description)

        f, m_path, description = find_module(
            module_name,
            loaded_pkg.__path__)
        try:
            mod = "{0}.{1}".format(loaded_pkg.__name__, module_name)
            loaded_module = load_module(mod, f, m_path, description)
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
                        and name.find("init") == -1
                        and name.find(".pyc") == -1):
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

    def check_attrs(self, method, attrs, token=None):
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
        temp = ""
        if token == "+":
            temp = "False not in"
        else:
            temp = "True in"
        eval_string = "{0} {1}".format(temp, "truth_values")

        return eval(eval_string)

    def check_tags(self, method, tags, token):
        """
        checks to see if the method passed in has matching tags.
        if the tags are (foo, bar) this method will match foo or
        bar. if a "+" token is passed only method that contain
        foo and bar will be match
        """
        truth_values = []
        method_tags = []

        method_tags = method.__dict__[TAGS_DECORATOR_TAG_LIST_NAME]

        for tag in tags:
            if tag in method_tags:
                truth_values[len(truth_values):] = [True]
            else:
                truth_values[len(truth_values):] = [False]

        temp = ""
        if token == "+":
            temp = "False not in"
        else:
            temp = "True in"
        eval_string = "{0} {1}".format(temp, "truth_values")

        return eval(eval_string)

    def check_method(self, class_, method_name, tags, attrs, token):
        load_test_flag = False
        attr_flag = False
        tag_flag = False

        method = getattr(class_, method_name)

        if dict(method.__dict__) \
                and TAGS_DECORATOR_TAG_LIST_NAME in method.__dict__:
            if tags and not attrs:
                tag_flag = self.check_tags(
                    method,
                    tags,
                    token)
                load_test_flag = tag_flag
            elif not tags and attrs:
                attr_flag = self.check_attrs(
                    method,
                    attrs,
                    token)
                load_test_flag = attr_flag
            elif tags and attrs:
                tag_flag = self.check_tags(
                    method,
                    tags,
                    token)
                attr_flag = self.check_attrs(
                    method,
                    attrs,
                    token)
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
                        load_test_flag = self.check_method(
                            class_,
                            method_name,
                            tag_list,
                            attrs,
                            token)

                    if load_test_flag:
                        try:
                            suite.addTest(class_(method_name))
                        except ImportError:
                            raise
                        except AttributeError:
                            raise
                        except Exception:
                            raise
        return suite

    def get_tests(self, module_path):
        suite = unittest.TestSuite()

        try:
            loaded_module = self.load_module(module_path)
        except ImportError:
            print_traceback()
            return None

        try:
            suite = self.build_suite(
                loaded_module)
        except ImportError:
            print_traceback()
            return None
        except AttributeError:
            print_traceback()
            return None
        except Exception:
            print_traceback()
            return None

        return suite


class EnvironmentSetup(object):
    def __init__(self):
        pass

    def get_cl_args(self):
        """
        collects and parses the command line args
        creates the runner"s help msg
        """
        base = "{0} {1} {2}".format(
            "cafe-runner",
            "<product>",
            "<config>")
        mod = "{0} {1}".format(
            "-m",
            "<module pattern>")
        mthd = "{0} {1}".format(
            "-M",
            "<test method>")
        testtag = "{0} {1}".format(
            "-t",
            "[tag tag...]")
        pkg = "{0} {1}".format(
            "-p",
            "[package package...]")

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

        *list tests for a product
        cafe-runner <product> -l "tests"

        *list configs for a product
        cafe-runner <product> -l "configs"

        *list tests and configs for a product
        cafe-runner <product> -l "tests" "configs"

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
            baseargs=base,
            package=pkg,
            module=mod,
            method=mthd,
            tags=testtag)

        desc = "Cloud Common Automated Engine Framework"

        argparser = argparse.ArgumentParser(
            usage=usage_string,
            description=desc)

        argparser.add_argument(
            "product",
            metavar="<product>",
            help="product name")

        argparser.add_argument(
            "config",
            nargs="?",
            default=None,
            metavar="<config_file>",
            help="product test config")

        argparser.add_argument(
            "-v", "--verbose",
            nargs="?",
            default=2,
            type=int,
            help="verbosity")

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
            "-m", "--module",
            default=None,
            metavar="<module>",
            help="test module regex - defaults to '*.py'")

        argparser.add_argument(
            "-M", "--method-regex",
            default=None,
            metavar="<method>",
            help="test method regex defaults to 'test_'")

        argparser.add_argument(
            "-t", "--tags",
            nargs="*",
            default=None,
            metavar="tags",
            help="tags")

        argparser.add_argument(
            "-l", "--list",
            nargs="*",
            choices=["tests", "configs"],
            metavar="'tests' 'configs'",
            help="list tests and or configs")

        argparser.add_argument(
            '--json-result',
            action="store_true",
            default=False,
            help="generates a json formatted result file")

        argparser.add_argument(
            "--parallel",
            action="store_true",
            default=False)

        argparser.add_argument(
            "--data-directory",
            help="directory for tests to get data from")

        argparser.add_argument(
            "-d", "--data",
            nargs="*",
            default=None,
            metavar="data",
            help="arbitrary test data")

        args = argparser.parse_args()

        if args.verbose < 0 or args.verbose > 3:
            print "cafe-runner: error: argument out of range: {0}".format(
                args.verbose)
            exit(1)

        return args

    def get_parent_path(self):
        if os.path.exists(BASE_DIR) is False:
            return None

        return BASE_DIR

    def get_repo_path(self, product):
        """
        returns the base string for the test repo directory
        """

        repo_path = None

        try:
            repo_path = os.path.join("{0}".format(
                test_repo_path),
                product)
        except AttributeError:
            pass

        try:
            if os.path.exists(repo_path) is False:
                return None
        except TypeError:
            return None

        return repo_path

    def get_config_file_name(self, cfg_file):
        cfg_file_name = None

        if cfg_file.find(".config") == -1:
            cfg_file_name = "{0}.{1}".format(cfg_file, "config")
        else:
            cfg_file_name = cfg_file

        return cfg_file_name

    def get_config_path(self, parent_path, product, cfg_file_name):
        """
        returns the base string for the config path
        """
        cfg_path = None

        try:
            cfg_path = os.path.join(
                parent_path,
                "configs",
                product,
                cfg_file_name)
        except AttributeError:
            pass

        try:
            if os.path.exists(cfg_path) is False:
                return None
        except TypeError:
            return None

        return cfg_path

    def get_module_regex(self, module):
        module_regex = module_regex = "*.py"

        if module:
            if module.find(".py") != -1:
                module_regex = module
            else:
                module_regex = "{0}.{1}".format(module, "py")

        return module_regex

    def get_method_regex(self, method):
        method_regex = "test_*"

        if method:
            if method.find("test_") != -1:
                method_regex = method
            else:
                method_regex = "{0}{1}".format("test_", method)

        return method_regex

    def parse_cl_data(self, data):
        dict_string = ""
        data_range = len(data)

        for i in range(data_range):
            data[i] = data[i].replace("=", "': '")
            data[i] = "'{0}'".format(data[i])

        dict_string = ", ".join(data)
        dict_string = "{0}{1}{2}".format("{", dict_string, "}")
        os.environ["DICT_STRING"] = dict_string

    def check_env_data(self, env_data, env_error):
        return check_data(env_data, env_error)


class RunnerSetup(object):
    def __init__(self):
        pass

    def get_runner(self, parallel, fail_fast, verbosity):
        test_runner = None

        # Use the parallel text runner so the console logs look correct
        if parallel:
            test_runner = OpenCafeParallelTextTestRunner(verbosity=int(verbosity))
        else:
            test_runner = unittest.TextTestRunner(verbosity=int(verbosity))

        test_runner.failfast = fail_fast

        return test_runner

    def get_safe_file_date(self):
        """
        @summary: Builds a date stamp that is safe for use in a file path/name
        @return: The safely formatted datetime string
        @rtype: C{str}
        """
        return str(datetime.now()).replace(" ", "_").replace(":", "_")

    def get_root_log_path(self, log_dir, product, config):
        root_log_path = None

        if not log_dir or not product or not config:
            return None
        else:
            root_log_path = os.path.join(log_dir, product, config)

        return root_log_path

    def get_stats_log_path(self, log_dir, product, config):
        stats_log_path = None

        if not log_dir or not product or not config:
            return None
        else:
            stats_log_path = os.path.join(
                log_dir, product, config, 'statistics')

        return stats_log_path

    def get_product_log_path(self, log_dir, product, config):
        product_log_path = None

        if not log_dir or not product or not config:
            return None
        else:
            product_log_path = os.path.join(
                log_dir, product, config, self.get_safe_file_date())
        return product_log_path

    def _set_default_data_dir(self):
        data_dir = os.path.expanduser(engine_config.data_directory)
        if not os.path.isdir(data_dir):
            os.makedirs(data_dir)

        return data_dir

    def _set_user_data_dir(self, dir_name):
        data_dir = None
        home = os.path.expanduser("~")

        if "home" not in os.path.expanduser(dir_name).split("/"):
            temp_dir = "{0}/{1}".format(home, dir_name)
        else:
            temp_dir = dir_name

        if os.path.isdir(temp_dir) is False:
            return None
        else:
            data_dir = temp_dir

        return data_dir

    def create_data_dir(self, user_data_dir):
        data_dir = None

        if user_data_dir is None:
            data_dir = self._set_default_data_dir()
        else:
            data_dir = self._set_user_data_dir(user_data_dir)

        return data_dir

    def create_stats_log_dir(self, stats_log_path):
        if os.path.isdir(stats_log_path) is not True:
            os.makedirs(stats_log_path)

    def create_product_log_dir(self, product_log_path):
        if os.path.isdir(product_log_path) is not True:
            os.makedirs(product_log_path)

    def set_env(self, key, value):
        """
        sets an environment var so the tests can find their respective
        product config path
        """
        os.environ[key] = value

    def check_runner_data(self, runner_data, runner_error):
        return check_data(runner_data, runner_error)


class OpenCafeRunner(object):
    """
    Open Cafe Runner
    """
    def __init__(self):
        pass

    def run_parallel(self, test_suites, test_runner, json_result=False):
        exit_code = 0
        proc = None
        unittest.installHandler()
        processes = []
        manager = Manager()
        results = manager.list()
        start = time.time()

        for test_suite in test_suites:
            proc = Process(target=execute_test, args=(
                test_runner,
                test_suite,
                results))
            processes.append(proc)
            proc.start()

        for proc in processes:
            proc.join()

        finish = time.time()

        errors, failures, _ = dump_results(start, finish, results)

        if json_result:
            all_results = []
            for tests, result in zip(test_suites, results):
                result_parser = SummarizeResults(
                    vars(result),
                    tests,
                    (finish - start))
                all_results += result_parser.gather_results()

            # Convert Result objects to dicts for serialization
            json_results = []
            for r in all_results:
                json_results.append(r.__dict__)
            with open(os.getcwd() + "/results.json", 'wb') as result_file:
                json.dump(json_results, result_file)

        if failures or errors:
            exit_code = 1

        return exit_code

    def run_serialized(self, master_suite, test_runner, json_result=False):
        exit_code = 0
        unittest.installHandler()
        start_time = time.time()
        result = test_runner.run(master_suite)
        total_execution_time = time.time() - start_time

        if json_result:
            result_parser = SummarizeResults(vars(result), master_suite,
                                             total_execution_time)
            all_results = result_parser.gather_results()

            # Convert Result objects to dicts for serialization
            json_results = []
            for r in all_results:
                json_results.append(r.__dict__)
            with open(os.getcwd() + "/results.json", 'wb') as result_file:
                json.dump(json_results, result_file)

        log_results(result)
        if not result.wasSuccessful():
            exit_code = 1

        return exit_code

    def run(self):
        """
        loops through all the packages, modules, and methods sent in from
        the command line and runs them
        """
        cl_args = None
        parent_path = None
        repo_path = None
        env_setup = None

        env_paths = {}
        env_setup = EnvironmentSetup()

        cl_args = env_setup.get_cl_args()
        cfg_file_name = env_setup.get_config_file_name(cl_args.config)

        parent_path = env_paths["parent_path"] = env_setup.get_parent_path()

        repo_path = env_paths["repo_path"] = env_setup.get_repo_path(
            cl_args.product)

        if cl_args.list is not None:
            print_tree(cl_args.product, cl_args.list, repo_path, parent_path)
            exit(0)
        else:
            method_regex = None
            module_regex = None
            config_path = None

            if cl_args.data:
                env_setup.parse_cl_data(cl_args.data)

            module_regex = env_setup.get_module_regex(cl_args.module)

            method_regex = env_setup.get_method_regex(cl_args.method_regex)

            cfg_file_name = env_setup.get_config_file_name(cl_args.config)

            config_path = env_paths["config_path"] = env_setup.get_config_path(
                parent_path,
                cl_args.product,
                cfg_file_name)

            env_error = \
                {"parent_path": ["DEFAULT DIR",
                                 "{0} does not exist".format(BASE_DIR)],
                 "config_path":
                    ["CONFIG",
                     "{0} config does not exist".format(cl_args.config)],
                 "repo_path":
                    ["REPO",
                     "{0} repo does not exist".format(cl_args.product)]}

            if env_setup.check_env_data(env_paths, env_error):
                print "Exiting"
                exit(1)

            test_suites = []
            builder = None
            stats_log_path = None
            product_log_path = None
            data_dir = None
            suite = unittest.TestSuite()
            master_suite = unittest.TestSuite()
            runner_setup = RunnerSetup()

            runner_paths = {}

            builder = SuiteBuilder(
                module_regex,
                method_regex,
                cl_args.tags,
                cl_args.supress_flag)

            test_runner = runner_setup.get_runner(
                cl_args.parallel,
                cl_args.fail_fast,
                cl_args.verbose)

            log_dir = os.path.expanduser(engine_config.log_directory)

            root_log_path = runner_paths["root_log_path"] = \
                runner_setup.get_root_log_path(
                    log_dir,
                    cl_args.product,
                    cfg_file_name)

            stats_log_path = runner_paths["stats_log_path"] = \
                runner_setup.get_stats_log_path(
                    log_dir,
                    cl_args.product,
                    cfg_file_name)

            product_log_path = runner_paths["product_log_path"] = \
                runner_setup.get_product_log_path(
                    log_dir,
                    cl_args.product,
                    cfg_file_name)

            data_dir = runner_paths["data_dir"] = \
                runner_setup.create_data_dir(cl_args.data_directory)

            master_log_file_name = engine_config.master_log_file_name

            runner_error = \
                {"stats_log_path":
                    ["CAFE_ROOT_LOG_PATH",
                     "{0} does not exist".format(stats_log_path)],
                 "product_log_path":
                    ["CAFE_TEST_LOG_PATH",
                     "{0} config does not exist".format(product_log_path)],
                 "data_dir":
                    ["CAFE_DATA_DIR_PATH", "{0} does not exist".format(data_dir)]}

            if runner_setup.check_runner_data(runner_paths, runner_error):
                print "Exiting"
                exit(1)

            runner_setup.create_stats_log_dir(stats_log_path)

            runner_setup.create_product_log_dir(product_log_path)

            verbose_flag = "false"
            if cl_args.verbose == 3:
                verbose_flag = "true"

            #TODO: change this so that it prints the key/value that errored
            try:
                runner_setup.set_env("CAFE_CONFIG_FILE_PATH", config_path)
                runner_setup.set_env("CAFE_ROOT_LOG_PATH", root_log_path)
                runner_setup.set_env("CAFE_TEST_LOG_PATH", product_log_path)
                runner_setup.set_env("CAFE_DATA_DIR_PATH", data_dir)
                runner_setup.set_env(
                    "CAFE_MASTER_LOG_FILE_NAME", master_log_file_name)
                runner_setup.set_env("VERBOSE", verbose_flag)
            except TypeError:
                print "Environment variable not set - Exiting"
                exit(1)

            print_paths(config_path, data_dir, product_log_path)

            if not cl_args.packages:
                for module_path in builder.get_modules(repo_path):
                    suite = builder.get_tests(module_path)
                    master_suite.addTests(suite)
                    test_suites.append(suite)
            else:
                for package_name in cl_args.packages:
                    test_path = builder.find_subdir(repo_path, package_name)

                    if test_path is None:
                        print error_msg("PACKAGE", package_name)
                        continue

                    for module_path in builder.get_modules(test_path):
                        suite = builder.get_tests(module_path)
                        master_suite.addTests(suite)
                        test_suites.append(suite)

            if cl_args.parallel:
                exit_code = self.run_parallel(
                    test_suites,
                    test_runner,
                    json_result=cl_args.json_result)
                exit(exit_code)
            else:
                exit_code = self.run_serialized(
                    master_suite,
                    test_runner,
                    json_result=cl_args.json_result)
                exit(exit_code)


def check_data(data, errors):
    error_flag = False
    for key in data:
        if not data[key]:
            err_msg = error_msg(
                errors[key][0],
                errors[key][1])
            error_flag = True
            print err_msg
    return error_flag


def execute_test(runner, test, results):
    result = runner.run(test)
    results.append(result)


def dump_results(start, finish, results):
    print "-" * 71

    run = 0
    errors = 0
    failures = 0
    for result in results:
        run += result.testsRun
        errors += len(result.errors)
        failures += len(result.failures)

    print ("Ran %d test%s in %.3fs" % (run,
                                       run != 1 and "s" or "",
                                       finish - start))

    fail = ""
    error = ""
    space = ""
    if failures:
        fail = "Failures=%d" % failures
    if errors:
        error = "Errors=%d" % errors
    if failures or errors:
        if failures and errors:
            space = " "
        print
        print "FAILED ({0}{1}{2})".format(fail, space, error)

    return errors, failures, run


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
            print "Config directory: {0} Does Not Exist".format(directory)
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
            if (file_name.find(".pyc") == -1 and
                    file_name != "__init__.py"):
                print "{0}{1}".format(padding, file_name)


def colorize(msg, color):
    """
    colorizes a string
    """
    end = "\033[1;m"
    colorized_msg = "".join([color, str(msg), end])

    return colorized_msg


def print_tree(product, list_args, repo_path, parent_path):
    arg_list = []
    if not list_args:
        arg_list = ["tests", "configs"]
    else:
        arg_list = list_args

    for arg in arg_list:
        if arg == "tests":
            banner = "\n<[TEST REPO]>\n"
            path = repo_path
        else:
            banner = "\n<[CONFIGS]>\n"
            path = os.path.join(
                parent_path,
                "configs",
                product)

        print banner
        tree(path, " ", print_files=True)


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


def print_paths(config_path, data_dir, log_path):
    print
    print "=" * 150
    print "Percolated Configuration"
    print "-" * 150
    print "ENGINE CONFIG FILE: {0}".format(
        EngineConfigManager.ENGINE_CONFIG_PATH)
    print "TEST CONFIG FILE..: {0}".format(config_path)
    print "DATA DIRECTORY....: {0}".format(data_dir)
    print "LOG PATH..........: {0}".format(log_path)
    print "=" * 150


def entry_point():
    brew = "Brewing from {0}".format(BASE_DIR)

    mug0 = "      ( ("
    mug1 = "       ) )"
    mug2 = "    ........."
    mug3 = "    |       |___"
    mug4 = "    |       |_  |"
    mug5 = "    |  :-)  |_| |"
    mug6 = "    |       |___|"
    mug7 = "    |_______|"
    mug8 = "=== CAFE Runner ==="

    print "\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}".format(
        mug0,
        mug1,
        mug2,
        mug3,
        mug4,
        mug5,
        mug6,
        mug7,
        mug8)

    print "-" * len(brew)
    print brew
    print "-" * len(brew)

    runner = OpenCafeRunner()
    runner.run()
    exit(0)
