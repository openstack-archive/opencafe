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
from __future__ import print_function

from StringIO import StringIO
from unittest.runner import _WritelnDecorator
import importlib
import logging
import sys
import time
import unittest
import traceback

from multiprocessing import Process, Queue, active_children
from cafe.common.reporting.cclogging import init_root_log_handler
from cafe.common.reporting.reporter import Reporter
from cafe.configurator.managers import TestEnvManager
from cafe.drivers.unittest.arguments import ArgumentParser
from cafe.drivers.unittest.parsers import SummarizeResults
from cafe.drivers.unittest.suite_builder import SuiteBuilder, print_exception


def import_repos(repo_list):
    repos = []
    for repo_name in repo_list:
        try:
            repos.append(importlib.import_module(repo_name))
        except Exception as e:
            print_exception("Runner", "import_repos", repo_name, e)
    if len(repo_list) != len(repos):
        exit(1)
    return repos


def _make_result(verbose, failfast):
    stream = _WritelnDecorator(StringIO())
    result = unittest.TextTestResult(stream, True, verbose)
    result.buffer = False
    result.failfast = failfast
    return result


class UnittestRunner(object):
    def __init__(self):
        self.cl_args = ArgumentParser().parse_args()
        self.test_env = TestEnvManager(
            "", self.cl_args.config, test_repo_package_name="")
        self.test_env.test_data_directory = (
            self.cl_args.data_directory or self.test_env.test_data_directory)
        self.test_env.finalize()
        init_root_log_handler()
        self.print_mug()


        self.cl_args.testrepos = import_repos(self.cl_args.testrepos)
        self.print_configuration()
        self.suit_builder = SuiteBuilder(
            testrepos=self.cl_args.testrepos,
            tags=self.cl_args.tags,
            all_tags=self.cl_args.all_tags,
            dotpath_regex=self.cl_args.dotpath_regex,
            file_=self.cl_args.file,
            dry_run=self.cl_args.dry_run,
            exit_on_error=self.cl_args.exit_on_error)

    def process_result(self, dic):
        handlers = logging.getLogger().handlers
        for record in dic.get("logs"):
            for handler in handlers:
                handler.emit(record)
        sys.stderr.write("{0}\n".format(dic["result"].stream.buf.strip()))
        sys.stderr.flush()
        dic["result"].stream.seek(0)
        dic["result"].stream.truncate()
        dic["result"].printErrors()
        dic["result"].stream.seek(0)
        return dic

    def run(self):
        start = time.time()
        suites = self.suit_builder.get_suites()
        results = []
        to_worker = Queue()
        from_worker = Queue()
        verbose = self.cl_args.verbose
        failfast = self.cl_args.failfast
        workers = 1 * (not self.cl_args.parallel) or self.cl_args.workers

        for suite in suites:
            to_worker.put(suite)

        for _ in range(workers):
            to_worker.put(None)

        for _ in range(workers):
            Consumer(to_worker, from_worker, verbose, failfast).start()

        while active_children():
            if from_worker.qsize():
                results.append(self.process_result(from_worker.get()))
            time.sleep(.1)
        while not from_worker.empty():
            results.append(self.process_result(from_worker.get()))

        finish = time.time()
        self.dump_results(start, finish, results)

    def print_mug(self):
        print("\n    ( (        ")
        print("     ) )       ")
        print("  .........    ")
        print("  |       |___ ")
        print("  |       |_  |")
        print("  |  :-)  |_| |")
        print("  |       |___|")
        print("  |_______|    ")
        print("=== CAFE Runner ===")

    def print_configuration(self):
        print("=" * 150)
        print("Percolated Configuration")
        print("-" * 150)
        if self.cl_args.testrepos:
            print("BREWING FROM: ....: {0}".format(
                self.cl_args.testrepos[0].__name__))
            for repo in self.cl_args.testrepos[1:]:
                print("{0}{1}".format(" " * 20, repo.__name__))
        print("ENGINE CONFIG FILE: {0}".format(
            self.test_env.engine_config_path))
        print("TEST CONFIG FILE..: {0}".format(
            self.test_env.test_config_file_path))
        print("DATA DIRECTORY....: {0}".format(
            self.test_env.test_data_directory))
        print("LOG PATH..........: {0}".format(self.test_env.test_log_dir))
        print("=" * 150)

    def dump_results(self, start, finish, results):
        tests_run = errors = failures = 0
        all_results = []
        print("-" * 70)
        for i in results:
            result = i["result"]
            suite = i["suite"]
            tests_run += result.testsRun
            errors += len(result.errors)
            failures += len(result.failures)

            if result.stream.buf.strip():
                sys.stderr.write("{0}\n\n".format(
                    result.stream.buf.strip()))

            if self.cl_args.result is not None:
                result_parser = SummarizeResults(
                    vars(result), suite, (finish - start))
                all_results += result_parser.gather_results()

                reporter = Reporter(
                    result_parser=result_parser, all_results=all_results)
                reporter.generate_report(
                    result_type=self.cl_args.result,
                    path=self.cl_args.result_directory)

        print
        print("Ran {0} test{1} in {2:.3f}s".format(
            tests_run, "s" * bool(tests_run - 1), finish - start))

        if failures or errors:
            print("\nFAILED ({0}{1}{2})".format(
                "Failures={0}".format(failures) if failures else "",
                " " if failures and errors else "",
                "Errors={0}".format(errors) if errors else ""))
        if errors or failures:
            exit(1)
        return errors, failures, tests_run


class ParallelRecordHandler(logging.Handler):
    def __init__(self):
        super(ParallelRecordHandler, self).__init__()
        self._records = []

    def emit(self, record):
        self._records.append(record)


class Consumer(Process):
    def __init__(self, to_worker, from_worker, verbose, failfast):
        Process.__init__(self)
        self.to_worker = to_worker
        self.from_worker = from_worker
        self.verbose = verbose
        self.failfast = failfast

    def run(self):
        logger = logging.getLogger('')
        while True:
            result = _make_result(self.verbose, self.failfast)
            suite = self.to_worker.get()
            if suite is None:
                return
            handler = ParallelRecordHandler()
            logger.handlers = [handler]
            suite(result)
            result.stream.seek(0)
            for record in handler._records:
                if record.exc_info:
                    record.msg = "{0}\n{1}".format(
                        record.msg, traceback.format_exc(record.exc_info))
                record.exc_info = None
            dic = {"result": result, "logs": handler._records, "suite": suite}
            self.from_worker.put(dic)


def entry_point():
    runner = UnittestRunner()
    runner.run()
    exit(0)
