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

from sys import stderr
from traceback import print_exc
import argparse
import importlib
import os

from cafe.configurator.managers import EngineConfigManager
from cafe.engine.config import EngineConfig

ENGINE_CONFIG = EngineConfig(
    os.environ.get("CAFE_ENGINE_CONFIG_FILE_PATH") or
    EngineConfigManager.ENGINE_CONFIG_PATH)


def print_exception(file_, method, value, e=""):
    print("{0}".format("=" * 70), file=stderr)
    print("{0}: {1}: {2}: {3}".format(
        file_, method, value, e), file=stderr)
    print("{0}".format("-" * 70), file=stderr)
    print_exc(file=stderr)
    print()


def import_repos(repo_list):
    repos = []
    for repo_name in repo_list:
        try:
            repos.append(importlib.import_module(repo_name))
        except Exception as e:
            print_exception("ArgumentParser", "import_repos", repo_name, e)
    if len(repo_list) != len(repos):
        exit(1)
    return repos


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
            print(
                "tree: {0} Does Not Exist".format(directory), file=stderr)
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


class ConfigAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        value = value if value.endswith('.config') else "{0}.config".format(
            value)
        path = "{0}/{1}".format(ENGINE_CONFIG.config_directory, value)
        if not os.path.exists(path):
            print("Argument Parser: Config does not exist: {0}".format(path),
                  file=stderr)
            exit(1)
        setattr(namespace, self.dest, value)


class RepoAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, import_repos(values))


class DataDirectoryAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        if not os.path.exists(value):
            print ("Argument Parser: DataDirectory does not exist: {0}".format(
                value))
            exit(1)
        setattr(namespace, self.dest, value)


class InputFileAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        if not os.path.exists(value):
            print("Argument Parser: Input File does not exist: {0}".format(
                value), file=stderr)
            exit(1)
        dic = {}
        count = 0
        lines = open(value).readlines()
        try:
            for line in lines:
                temp = line.replace("(", "").rstrip(")\n").split()
                test_list = dic.get(temp[1], [])
                test_list.append(temp[0])
                dic[temp[1]] = test_list
                count += 1
        except:
            print("Argument Parser: Line in incorrect format: {0}".format(
                line), file=stderr)
        if len(lines) != count:
            exit(1)
        setattr(namespace, self.dest, dic)


class ListAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if namespace.testrepos:
            print("\n<[TEST REPO]>\n")
            for repo in namespace.testrepos:
                tree(repo.__path__[0], " ", print_files=True)
                print()
        else:
            print("\n<[CONFIGS]>\n")
            tree(ENGINE_CONFIG.config_directory, " ", print_files=True)
        exit(0)


class TagAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values[0] == "+":
            values = values[1:]
            setattr(namespace, "all_tags", True)
        else:
            setattr(namespace, "all_tags", False)
        if len(values) < 1:
            print("Argument Parser: No tags specified: []", file=stderr)
            exit(1)
        setattr(namespace, self.dest, values)


class VerboseAction(argparse.Action):
    def __call__(self, parser, namespace, value, option_string=None):
        nums = (1, 2, 3)
        if value not in nums:
            print("Argument Parser: Verbose value not in {0}: {1}".format(
                nums, value), file=stderr)
        os.environ["VERBOSE"] = "true" if value == 3 else "false"
        setattr(namespace, self.dest, value)


class ArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        desc = "Open Common Automation Framework Engine"
        usage_string = """
            cafe-runner <config> <testrepos>... [--fail-fast]
                [--supress-load-tests] [--dry-run]
                [--data-directory=DATA_DIRECTORY] [--dotpath-regex=REGEX...]
                [--file] [--parallel=(class|test)] [--result=(json|xml)]
                [--result-directory=RESULT_DIRECTORY] [--tags=TAG...]
                [--verbose=VERBOSE]
            cafe-runner <config> <testrepo>... --list
            cafe-runner --list
            cafe-runner --help
            """
        super(ArgumentParser, self).__init__(
            usage=usage_string, description=desc)

        self.add_argument(
            "config",
            action=ConfigAction,
            metavar="<config>",
            help="test config.  Looks in the .opencafe/configs directory."
                 "Example: bsl/uk.json")

        self.add_argument(
            "testrepos",
            nargs="*",
            action=RepoAction,
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
            "--supress-load-tests", "-s",
            action="store_true",
            help="supress load tests method")

        self.add_argument(
            "--data-directory", "-D",
            action=DataDirectoryAction,
            help="Data directory override")

        self.add_argument(
            "--dotpath-regex", "-d",
            nargs="+",
            default=[],
            metavar="REGEX",
            help="Package Filter")

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
            choices=["json", "xml"],
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
            nargs="?",
            default=2,
            type=int,
            help="Set unittest output verbosity")

        self.add_argument(
            "--workers", "-w",
            nargs="?",
            default=10,
            type=int,
            help="Set number of workers for --parallel option")

    def parse_args(self, *args, **kwargs):
        args = super(ArgumentParser, self).parse_args(*args, **kwargs)
        if getattr(args, "all_tags", None) is None:
            args.all_tags = False
        return args

if __name__ == "__main__":
    args = ArgumentParser().parse_args()
    for key, value in sorted(args.__dict__.items()):
        print(key, value)
