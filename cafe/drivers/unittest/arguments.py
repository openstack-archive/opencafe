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

from __future__ import print_function

import argparse
import errno
import importlib
import os
import re
import sys

from cafe.configurator.managers import EngineConfigManager
from cafe.drivers.base import print_exception, get_error
from cafe.engine.config import EngineConfig


def get_engine_config():
    """
    Get the engine config.

    :return: Instantiated EngineConfig object
    :rtype: EngineConfig
    """
    return EngineConfig(
        os.environ.get("CAFE_ENGINE_CONFIG_FILE_PATH") or
        EngineConfigManager.ENGINE_CONFIG_PATH)


def tree(start):
    """
        Prints tree structure, files first then directories in alphabetical
        order.
    """
    start = os.path.abspath(os.path.expanduser(start))
    if not os.path.exists(start):
        print_exception(
            "Argument Parser", "tree", "{0} Does Not Exist".format(start))
        return
    elif os.path.isfile(start):
        print("+-{0}".format(os.path.basename(start)))
        return
    for path, dirs, files in os.walk(start):
        dirs.sort()
        files.sort()
        depth = path.replace(start, "").count(os.sep)
        print("{0}{1}+-{2}/".format(
            "  " * (depth > 0), "| " * (depth - 1), os.path.basename(path)))
        for file_ in files:
            if not file_.endswith(".pyc") and file_ != "__init__.py":
                print("  {0}{1}".format("| " * depth, file_))


class ConfigAction(argparse.Action):
    """
        Custom action that checks if config exists.
    """
    def __call__(self, parser, namespace, value, option_string=None):
        value = value if value.endswith('.config') else "{0}.config".format(
            value)
        path = "{0}/{1}".format(get_engine_config().config_directory, value)
        if not os.path.exists(path):
            parser.error(
                "ConfigAction: Config does not exist: {0}".format(path))
            exit(errno.ENOENT)
        setattr(namespace, self.dest, value)


class DataDirectoryAction(argparse.Action):
    """
        Custom action that checks if data-directory exists.
    """
    def __call__(self, parser, namespace, value, option_string=None):
        if not os.path.exists(value):
            parser.error(
                "DataDirectoryAction: Data directory does not exist: "
                "{0}".format(value))
            exit(errno.ENOENT)
        setattr(namespace, self.dest, value)


class InputFileAction(argparse.Action):
    """
        Custom action that reads in a file and uses the lines for a test order.
    """
    def __call__(self, parser, namespace, value, option_string=None):
        dic = {}
        try:
            lines = open(value).readlines()
            for count, line in enumerate(lines):
                temp = line.replace(")", "").strip().split(" (")
                dic[temp[1]] = dic.get(temp[1], []) + [temp[0]]
        except IndexError as exception:
            parser.error(
                "InputFileAction: Parsing of {0} failed: {1}".format(
                    line, exception))
        except IOError as exception:
            parser.error(
                "InputFileAction: File open failed: {0}".format(exception))
            exit(get_error(exception))
        setattr(namespace, self.dest, dic)


class ListAction(argparse.Action):
    """
        Custom action that lists either configs or tests.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.testrepos:
            print("\n<[TEST REPO]>\n")
            for repo in namespace.testrepos:
                path = importlib.import_module(repo.split(".")[0]).__path__[0]
                path = os.path.join(path, *repo.split(".")[1:])
                print(path)
                if os.path.exists("{0}.py".format(path)):
                    tree("{0}.py".format(path))
                else:
                    tree(path)
                print()
        else:
            print("\n<[CONFIGS]>\n")
            tree(get_engine_config().config_directory)
        exit(0)


class TagAction(argparse.Action):
    """
        Processes tag option.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        if values[0] == "+":
            values = values[1:]
            setattr(namespace, "all_tags", True)
        else:
            setattr(namespace, "all_tags", False)
        if len(values) < 1:
            parser.error("argument --tags/-t: expected at least one argument")
        setattr(namespace, self.dest, values)


class RegexAction(argparse.Action):
    """
        Processes regex option.
    """
    def __call__(self, parser, namespace, values, option_string=None):
        regex_list = []
        for regex in values:
            try:
                regex_list.append(re.compile(regex))
            except re.error as exception:
                parser.error(
                    "RegexAction: Invalid regex {0} reason: {1}".format(
                        regex, exception))
        setattr(namespace, self.dest, regex_list)


class VerboseAction(argparse.Action):
    """
        Custom action that sets VERBOSE environment variable.
    """
    def __call__(self, parser, namespace, value, option_string=None):
        os.environ["VERBOSE"] = "true" if value == 3 else "false"
        setattr(namespace, self.dest, value)


class ArgumentParser(argparse.ArgumentParser):
    """
        Parses all arguments.
    """
    def __init__(self):
        desc = "Open Common Automation Framework Engine"
        usage_string = """
            cafe-runner <config> <testrepos>... [--failfast]
                [--dry-run] [--data-directory=DATA_DIRECTORY]
                [--regex-list=REGEX...] [--file] [--parallel=(class|test)]
                [--result=(json|xml)] [--result-directory=RESULT_DIRECTORY]
                [--tags=TAG...] [--verbose=VERBOSE] [--exit-on-error]
                [--workers=NUM]
            cafe-runner <config> <testrepo>... --list
            cafe-runner --list
            cafe-runner --help
            """

        super(ArgumentParser, self).__init__(
            usage=usage_string, description=desc)

        self.prog = "Argument Parser"

        self.add_argument(
            "config",
            action=ConfigAction,
            metavar="<config>",
            help="test config.  Looks in the .opencafe/configs directory."
                 "Example: bsl/uk.json")

        self.add_argument(
            "testrepos",
            nargs="*",
            default=[],
            metavar="<testrepo>...",
            help="The name of the packages containing the tests. "
                 "This overrides the value in the engine.config file, as well "
                 "as the CAFE_OPENCAFE_ENGINE_default_test_repo environment "
                 "variable. Example: ubroast.bsl.v2 ubroast.bsl.v1")

        self.add_argument(
            "--dry-run",
            action="store_true",
            help="dry run.  Don't run tests just print them.  Will run data"
                 " generators.")

        self.add_argument(
            "--exit-on-error",
            action="store_true",
            help="Exit on module import error")

        self.add_argument(
            "--failfast", "-f",
            action="store_true",
            help="fail fast")

        self.add_argument(
            "--list", "-l",
            action=ListAction,
            nargs=0,
            help="Lists configs if no repo is specified otherwise lists tests"
                 " for all the specified repos.")

        self.add_argument(
            "--data-directory", "-D",
            action=DataDirectoryAction,
            help="Data directory override")

        self.add_argument(
            "--regex-list", "-d",
            action=RegexAction,
            nargs="+",
            default=[],
            metavar="REGEX",
            help="Filter by regex against dotpath down to test level"
                 "Example: tests.repo.cafe_tests.NoDataGenerator.test_fail"
                 "Example: 'NoDataGenerator\.*fail'"
                 "Takes in a list and matches on any")

        self.add_argument(
            "--file", "-F",
            metavar="INPUT_FILE",
            default={},
            action=InputFileAction,
            help="Runs only tests listed in file."
                 "  Can be created by copying --dry-run response")

        self.add_argument(
            "--parallel", "-P",
            choices=["class", "test"],
            help="Runs test in parallel by class grouping or test")

        self.add_argument(
            "--result", "-R",
            choices=["json", "xml", "subunit"],
            help="Generates a specified formatted result file")

        self.add_argument(
            "--result-directory",
            default="./",
            metavar="RESULT_DIRECTORY",
            help="Directory for result file to be stored")

        self.add_argument(
            "--tags", "-t",
            nargs="+",
            action=TagAction,
            default=[],
            metavar="TAG",
            help="""Run only tests that have tags set.
                By default tests that match any of the tags will be returned.
                Sending a "+" as the first tag in the tag list will only
                return the tests that match all the tags.""")

        self.add_argument(
            "--verbose", "-v",
            action=VerboseAction,
            choices=[1, 2, 3],
            default=2,
            type=int,
            help="Set unittest output verbosity")

        self.add_argument(
            "--workers", "-w",
            nargs="?",
            default=10,
            type=int,
            help="Set number of workers for --parallel option")

    def error(self, message):
        self.print_usage(sys.stderr)
        print_exception("Argument Parser", message)
        exit(get_error())

    def parse_args(self, *args, **kwargs):
        args = super(ArgumentParser, self).parse_args(*args, **kwargs)
        if getattr(args, "all_tags", None) is None:
            args.all_tags = False
        return args
