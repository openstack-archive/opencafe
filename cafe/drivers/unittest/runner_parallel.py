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

from multiprocessing import Process, Queue
from StringIO import StringIO
from unittest.runner import _WritelnDecorator
import importlib
import logging
import os
import sys
import time
import traceback
import unittest

from cafe.common.reporting import cclogging
from cafe.common.reporting.reporter import Reporter
from cafe.configurator.managers import ENGINE_CONFIG_PATH
from cafe.drivers.base import print_exception, get_error
from cafe.drivers.unittest.arguments import ArgumentParser
from cafe.drivers.unittest.datasets import create_dd_class
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.suite import OpenCafeUnittestTestSuite
from cafe.drivers.unittest.suite_builder import SuiteBuilder
from cafe.engine.config import EngineConfig


def _make_result(verbose, failfast):
    """Creates a TextTestResult object that writes a stream to a StringIO"""
    stream = _WritelnDecorator(StringIO())
    result = unittest.TextTestResult(stream, True, verbose)
    result.buffer = False
    result.failfast = failfast
    return result


def import_repos(repo_list):
    """Imports the repos passed in on the command line"""
    repos = []
    for repo_name in repo_list:
        try:
            repos.append(importlib.import_module(repo_name))
        except Exception as exception:
            print_exception(
                "Runner", "import_repos", repo_name, exception)
    if len(repo_list) != len(repos):
        exit(get_error(exception))
    return repos


class UnittestRunner(object):
    """OpenCafe UnittestRunner"""
    def __init__(self):
        self.print_mug()
        self.cl_args = ArgumentParser().parse_args()
        self.config = EngineConfig()
        cclogging.init_root_log_handler()
        self.print_configuration(self.cl_args.testrepos)
        self.cl_args.testrepos = import_repos(self.cl_args.testrepos)

        self.suites = SuiteBuilder(
            testrepos=self.cl_args.testrepos,
            tags=self.cl_args.tags,
            all_tags=self.cl_args.all_tags,
            regex_list=self.cl_args.regex_list,
            file_=self.cl_args.file,
            exit_on_error=self.cl_args.exit_on_error).get_suites()
        if self.cl_args.dry_run:
            for tests, class_, dataset in self.suites:
                name = dataset.name if dataset is not None else class_.__name__
                for test in tests:
                    print("{0} ({1}.{2})".format(
                        test, class_.__module__, name))
            exit(0)

    def run(self):
        """Starts the run of the tests"""
        results = []
        worker_list = []
        to_worker = Queue()
        from_worker = Queue()
        verbose = self.cl_args.verbose
        failfast = self.cl_args.failfast
        workers = int(not self.cl_args.parallel) or self.cl_args.workers

        start = time.time()
        count = 0
        for tests, class_, dataset in self.suites:
            create_dd_class(class_, dataset)
            to_worker.put((tests, class_, dataset))
            count += 1

        for _ in range(workers):
            to_worker.put(None)

        # A second try catch is needed here because queues can cause locking
        # when they go out of scope, especially when termination signals used
        try:
            for _ in range(workers):
                proc = Consumer(to_worker, from_worker, verbose, failfast)
                worker_list.append(proc)
                proc.start()

            for _ in range(count):
                results.append(self.log_result(from_worker.get()))

            tests_run, errors, failures = self.compile_results(
                time.time() - start, results)
        except KeyboardInterrupt:
            print_exception("Runner", "run", "Keyboard Interrupt, exiting...")
            os.killpg(0, 9)
        return bool(sum([errors, failures, not tests_run]))

    @staticmethod
    def print_mug():
        """Prints the cafe mug"""
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

    def print_configuration(self, repos):
        """Prints the config/logs/repo/data_directory"""
        print("=" * 150)
        print("Percolated Configuration")
        print("-" * 150)
        if repos:
            print("BREWING FROM: ....: {0}".format(repos[0]))
            for repo in repos[1:]:
                print("{0}{1}".format(" " * 20, repo))
        print("ENGINE CONFIG FILE: {0}".format(ENGINE_CONFIG_PATH))
        print("TEST CONFIG FILE..: {0}".format(self.config.test_config))
        print("DATA DIRECTORY....: {0}".format(self.config.data_directory))
        print("LOG PATH..........: {0}".format(self.config.test_log_dir))
        print("=" * 150)

    @staticmethod
    def log_result(dic):
        """Gets logs and stream from Comsumer and outputs to logs and stdout.
           Then is clears the stream and prints the errors to stream for later
           output.
        """
        handlers = logging.getLogger().handlers
        # handlers can be added here to allow for extensible log storage
        for record in dic.get("logs"):
            for handler in handlers:
                handler.emit(record)

        # this line can be replace to add an extensible stdout/err location
        sys.stderr.write("{0}\n".format(dic["result"].stream.buf.strip()))
        sys.stderr.flush()
        dic["result"].stream.seek(0)
        dic["result"].stream.truncate()
        dic["result"].printErrors()
        dic["result"].stream.seek(0)
        return dic

    def compile_results(self, run_time, results):
        """Summarizes results and writes results to file if --result used"""
        all_results = []
        result_dict = {"tests": 0, "errors": 0, "failures": 0}
        for dic in results:
            result = dic["result"]
            all_results += dic.get("all_results")
            summary = dic.get("summary")
            for key in result_dict:
                result_dict[key] += summary[key]
            if result.stream.buf.strip():
                sys.stderr.write("{0}\n\n".format(
                    result.stream.buf.strip()))

        if self.cl_args.result is not None:
            reporter = Reporter(run_time, all_results)
            reporter.generate_report(
                self.cl_args.result, self.cl_args.result_directory)
        return self.print_results(run_time=run_time, **result_dict)

    def print_results(self, tests, errors, failures, run_time):
        """Prints results summerized in compile_results messages"""
        print("{0}".format("-" * 70))
        print("Ran {0} test{1} in {2:.3f}s".format(
            tests, "s" * bool(tests - 1), run_time))

        if failures or errors:
            print("\nFAILED ({0}{1}{2})".format(
                "failures={0}".format(failures) if failures else "",
                ", " if failures and errors else "",
                "errors={0}".format(errors) if errors else ""))
        print("{0}\nDetailed logs: {1}\n{2}".format(
            "=" * 150, self.config.test_log_dir, "-" * 150))
        return tests, errors, failures


class ParallelRecordHandler(logging.Handler):
    """Stores logs instead of logging them"""
    def __init__(self):
        super(ParallelRecordHandler, self).__init__()
        self._records = []

    def emit(self, record):
        """Standard logging method"""
        self._records.append(record)


class Consumer(Process):
    """This class runs as a process and does the test running"""
    def __init__(self, to_worker, from_worker, verbose, failfast):
        Process.__init__(self)
        self.to_worker = to_worker
        self.from_worker = from_worker
        self.verbose = verbose
        self.failfast = failfast

    def run(self):
        """Starts the worker listening"""
        logger = logging.getLogger('')
        while True:
            result = _make_result(self.verbose, self.failfast)
            suite = OpenCafeUnittestTestSuite()
            try:
                tests, class_, dataset = self.to_worker.get()
            except TypeError:
                return
            class_ = create_dd_class(class_, dataset)
            for test in tests:
                try:
                    test_obj = class_(test)
                    suite.addTest(test_obj)
                except ValueError as e:
                    print_exception("Runner_Worker", "run", test, e)

            handler = ParallelRecordHandler()
            logger.handlers = [handler]
            suite(result)
            result.stream.seek(0)
            for record in handler._records:
                if record.exc_info:
                    record.msg = "{0}\n{1}".format(
                        record.msg, traceback.format_exc(record.exc_info))
                record.exc_info = None
            result._previousTestClass = None
            result_parser = SummarizeResults(vars(result), suite)
            dic = {
                "all_results": result_parser.gather_results(),
                "summary": result_parser.summary_result(),
                "result": result,
                "logs": handler._records}
            self.from_worker.put(dic)


def entry_point():
    """Function setup.py links cafe-runner to"""
    try:
        runner = UnittestRunner()
        exit(runner.run())
    except KeyboardInterrupt:
        print_exception("Runner", "run", "Keyboard Interrupt, exiting...")
        os.killpg(0, 9)
