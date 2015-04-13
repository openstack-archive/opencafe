"""
Copyright 2015 Rackspace

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

import inspect
import re

from importlib import import_module
from unittest import TestCase

from cafe.common.reporting import cclogging
from cafe.drivers.unittest.datasets import DatasetList

TAGS_LIST_ATTR = "__test_tags__"
DATA_DRIVEN_TEST_ATTR = "__data_driven_test_data__"
DATA_DRIVEN_TEST_PREFIX = "ddtest_"


class DataDrivenFixtureError(Exception):
    """Error if you apply DataDrivenClass to func that isn't a TestCase"""
    pass


def _add_tags(func, tag_list):
    """Adds tages to a function, stored in __test_tags__ variable"""
    func.__test_tags__ = list(set(
        getattr(func, TAGS_LIST_ATTR, []) + tag_list))
    return func


def tags(*tag_list, **attrs):
    """Adds tags and attributes to tests, which are interpreted by the
    cafe-runner at run time
    """
    def decorator(func):
        """Calls _add_tags to add tags to a function"""
        func = _add_tags(func, list(tag_list))
        func = _add_tags(func, [
            "{0}={1}".format(k, v) for k, v in attrs.items()])
        return func
    return decorator


def data_driven_test(*dataset_sources, **kwargs):
    """Used to define the data source for a data driven test in a
    DataDrivenFixture decorated Unittest TestCase class"""

    def decorator(func):
        """Combines and stores DatasetLists in __data_driven_test_data__"""
        combined_lists = DatasetList()
        for key, value in kwargs:
            if isinstance(value, DatasetList):
                value.apply_test_tags(key)
            else:
                print "DeprecationWarning Warning: non DataSetList passed to",
                print " data generator."
            combined_lists += value
        for dataset_list in dataset_sources:
            combined_lists += dataset_list
        setattr(func, DATA_DRIVEN_TEST_ATTR, combined_lists)
        return func
    return decorator


def DataDrivenClass(*dataset_lists):
    """Use data driven class decorator. designed to be used on a fixture"""
    def decorator(cls):
        """Creates classes with variables named after datasets.
        Names of classes are equal to (class_name with out fixture) + ds_name
        """
        module = import_module(cls.__module__)
        cls = DataDrivenFixture(cls)
        class_name = re.sub("fixture", "", cls.__name__, flags=re.IGNORECASE)
        if not re.match(".*fixture", cls.__name__, flags=re.IGNORECASE):
            cls.__name__ = "{0}Fixture".format(cls.__name__)
        for dataset_list in dataset_lists:
            for dataset in dataset_list:
                class_name_new = "{0}_{1}".format(class_name, dataset.name)
                class_name_new = DatasetList.replace_invalid_characters(
                    class_name_new)
                new_class = type(class_name_new, (cls,), dataset.data)
                new_class.__module__ = cls.__module__
                setattr(module, class_name_new, new_class)
        return cls
    return decorator


def DataDrivenFixture(cls):
    """Generates new unittest test methods from methods defined in the
    decorated class"""
    def create_func(original_test, new_name, kwargs):
        """Creates a function to add to class for ddtests"""
        def new_test(self):
            """Docstring gets replaced by test docstring"""
            func = getattr(self, original_test.__name__)
            func(**kwargs)
        new_test.__name__ = new_name
        new_test.__doc__ = original_test.__doc__
        return new_test

    if not issubclass(cls, TestCase):
        raise DataDrivenFixtureError

    for attr_name in dir(cls):
        if attr_name.startswith(DATA_DRIVEN_TEST_PREFIX) is False:
            # Not a data driven test, skip it
            continue
        original_test = getattr(cls, attr_name, None)
        if not callable(original_test):
            continue

        test_data = getattr(original_test, DATA_DRIVEN_TEST_ATTR, [])

        for dataset in test_data:
            # Name the new test based on original and dataset names
            base_test_name = attr_name[int(len(DATA_DRIVEN_TEST_PREFIX)):]
            new_test_name = DatasetList.replace_invalid_characters(
                "test_{0}_{1}".format(base_test_name, dataset.name))

            new_test = create_func(original_test, new_test_name, dataset.data)

            # Copy over any other attributes the original test had (mainly to
            # support test tag decorator)
            for key, value in vars(original_test).items():
                if key != DATA_DRIVEN_TEST_ATTR:
                    setattr(new_test, key, value)

            # Set dataset tags and attrs
            new_test = _add_tags(new_test, dataset.metadata.get('tags', []))

            # Add the new test to the decorated TestCase
            setattr(cls, new_test_name, new_test)
    return cls


class memoized(object):

    """
    Decorator.
    @see: https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
    Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).

    Adds and removes handlers to root log for the duration of the function
    call, or logs return of cached result.
    """

    def __init__(self, func):
        self.func = func
        self.cache = {}
        self.__name__ = func.__name__

    def __call__(self, *args):
        log_name = "{0}.{1}".format(
            cclogging.get_object_namespace(args[0]), self.__name__)
        self._start_logging(log_name)

        try:
            hash(args)
        except TypeError:  # unhashable arguments in args
            value = self.func(*args)
            debug = "Uncacheable.  Data returned"
        else:
            if args in self.cache:
                value = self.cache[args]
                debug = "Cached data returned."
            else:
                value = self.cache[args] = self.func(*args)
                debug = "Data cached for future calls"

        self.func._log.debug(debug)
        self._stop_logging()
        return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def _start_logging(self, log_file_name):
        """Starts logging"""
        setattr(self.func, '_log_handler', cclogging.setup_new_cchandler(
            log_file_name))
        setattr(self.func, '_log', cclogging.getLogger(''))
        self.func._log.addHandler(self.func._log_handler)
        try:
            curframe = inspect.currentframe()
            self.func._log.debug("{0} called from {1}".format(
                self.__name__, inspect.getouterframes(curframe, 2)[2][3]))
        except:
            self.func._log.debug(
                "Unable to log where {0} was called from".format(
                    self.__name__))

    def _stop_logging(self):
        """Stop logging"""
        self.func._log.removeHandler(self.func._log_handler)
