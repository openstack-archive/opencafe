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

import os
import unittest

from cafe.configurator.managers import EngineConfigManager
from cafe.drivers.unittest.arguments import ArgumentParser
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.decorators import (
    data_driven_test, DataDrivenFixture)
from cafe.engine.config import EngineConfig


ENGINE_CONFIG = EngineConfig(
    os.environ.get("CAFE_ENGINE_CONFIG_FILE_PATH") or
    EngineConfigManager.ENGINE_CONFIG_PATH)

CONFIG_NAME = "test.config"
TEST_CONFIG = "{0}{1}{2}".format(
    ENGINE_CONFIG.config_directory, os.sep, CONFIG_NAME)


class PositiveDataGenerator(DatasetList):
    """Generates positive tests for ArgumentParser"""
    def __init__(self):
        super(PositiveDataGenerator, self).__init__()
        self.append_new_dataset("Base", {"arg_update": [], "update": {}})
        self.append_new_dataset("tag_no_plus", {
            "arg_update": ["-t", "one", "two", "three"],
            "update": {"tags": ["one", "two", "three"]}})

        self.append_new_dataset("tag_plus", {
            "arg_update": ["-t", "+", "two", "three"],
            "update": {"tags": ["two", "three"], "all_tags": True}})

        self.append_new_dataset("data_directory", {
            "arg_update": ["-D", "/"],
            "update": {"data_directory": "/"}})

        self.append_new_dataset("result_directory", {
            "arg_update": ["--result-directory", "/"],
            "update": {"result_directory": "/"}})

        self.append_new_dataset("dotpath_regex", {
            "arg_update": ["-d", ".*", "..."],
            "update": {"dotpath_regex": [".*", "..."]}})

        self.append_new_dataset("dry_run", {
            "arg_update": ["--dry-run"],
            "update": {"dry_run": True}})

        self.append_new_dataset("exit_on_error", {
            "arg_update": ["--exit-on-error"],
            "update": {"exit_on_error": True}})

        self.append_new_dataset("failfast", {
            "arg_update": ["--failfast"],
            "update": {"failfast": True}})

        self.append_new_dataset("supress_load_tests", {
            "arg_update": ["--supress-load-tests"],
            "update": {"supress_load_tests": True}})

        self.append_new_dataset("parallel_class", {
            "arg_update": ["--parallel", "class"],
            "update": {"parallel": "class"}})

        self.append_new_dataset("parallel_test", {
            "arg_update": ["--parallel", "test"],
            "update": {"parallel": "test"}})

        self.append_new_dataset("result_json", {
            "arg_update": ["--result", "json"],
            "update": {"result": "json"}})

        self.append_new_dataset("result_xml", {
            "arg_update": ["--result", "xml"],
            "update": {"result": "xml"}})

        for i in range(1, 4):
            i = str(i)
            self.append_new_dataset("verbose_" + i, {
                "arg_update": ["--verbose", i],
                "update": {"verbose": int(i)}})

        for i in range(1, 4):
            i = str(i)
            self.append_new_dataset("workers_" + i, {
                "arg_update": ["--workers", i],
                "update": {"workers": int(i)}})

        self.append_new_dataset("file", {
            "arg_update": ["--file", TEST_CONFIG],
            "update": {"file": {"tests.repo.cafe_tests.NoDataGenerator": [
                "test_fail", "test_pass"]}}})

        self.append_new_dataset("list", {"arg_update": ["-l"]})


@DataDrivenFixture
class ArgumentsTests(unittest.TestCase):
    """ArgumentParser Tests"""
    good_package = "tests.repo"
    bad_package = "tests.fakerepo"
    good_module = "tests.repo.test_module"
    bad_module = "tests.repo.blah"
    bad_path = "tests."
    good_config = CONFIG_NAME
    base_arguments = [good_config, good_package]
    config = TEST_CONFIG
    expected_base = {
        "config": good_config,
        "testrepos": [good_package],
        "tags": [],
        "all_tags": False,
        "data_directory": None,
        "dotpath_regex": [],
        "dry_run": False,
        "exit_on_error": False,
        "failfast": False,
        "supress_load_tests": False,
        "parallel": None,
        "result": None,
        "result_directory": "./",
        "verbose": 2,
        "workers": 10,
        "file": {},
        "list": None}

    @classmethod
    def setUpClass(cls):
        super(ArgumentsTests, cls).setUpClass()
        file_ = open(cls.config, "w")
        file_.write("test_fail (tests.repo.test_module.NoDataGenerator)\n")
        file_.write("test_pass (tests.repo.test_module.NoDataGenerator)\n")
        file_.close()

    def get_updated_expected(self, **kwargs):
        """Creates an updated base argument dictionary for compare"""
        dic = {}
        dic.update(self.expected_base)
        dic.update(kwargs)
        return dic

    @data_driven_test(PositiveDataGenerator())
    def ddtest_arguments_positive(self, arg_update=None, update=None):
        """Test different argument configurations"""
        arg_list = self.base_arguments + (arg_update or [])
        expected = self.get_updated_expected(**(update or {}))
        try:
            args = ArgumentParser().parse_args(arg_list)
            for key, value in expected.items():
                self.assertEqual(value, getattr(args, key, "NoValueFound"))
        except SystemExit as exception:
            if exception.code != 0:
                self.assertEqual(exception, None)
