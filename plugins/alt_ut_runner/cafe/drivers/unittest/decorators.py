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

import inspect
import re
import six
from six.moves import zip_longest

from importlib import import_module
from types import FunctionType
from unittest import TestCase

from cafe.common.reporting import cclogging
from cafe.drivers.unittest.datasets import DatasetList

TAGS_DECORATOR_TAG_LIST_NAME = "__test_tags__"
DATA_DRIVEN_TEST_ATTR = "__data_driven_test_data__"
DATA_DRIVEN_TEST_PREFIX = "ddtest_"


class DataDrivenFixtureError(Exception):
    """Error if you apply DataDrivenClass to func that isn't a TestCase"""
    pass


def _add_tags(func, tag_list):
    """Adds tages to a function, stored in __test_tags__ variable"""
    func.__test_tags__ = list(set(
        getattr(func, TAGS_DECORATOR_TAG_LIST_NAME, []) + tag_list))
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

    if not issubclass(cls, TestCase):
        raise DataDrivenFixtureError

    for attr_name in dir(cls):
        if attr_name.startswith(DATA_DRIVEN_TEST_PREFIX) is False:
            # Not a data driven test, skip it
            continue

        original_test = getattr(cls, attr_name, None).__func__
        test_data = getattr(original_test, DATA_DRIVEN_TEST_ATTR, None)

        if test_data is None:
            # no data was provided to the datasource decorator or this is not a
            # data driven test, skip it.
            continue

        for dataset in test_data:
            # Name the new test based on original and dataset names
            base_test_name = str(original_test.__name__)[
                int(len(DATA_DRIVEN_TEST_PREFIX)):]
            new_test_name = DatasetList.replace_invalid_characters(
                "test_{0}_{1}".format(base_test_name, dataset.name))

            # Create a new test from the old test
            new_test = FunctionType(
                six.get_function_code(original_test),
                six.get_function_globals(original_test),
                name=new_test_name)

            # Copy over any other attributes the original test had (mainly to
            # support test tag decorator)
            for attr in list(set(dir(original_test)) - set(dir(new_test))):
                setattr(new_test, attr, getattr(original_test, attr))

            # Change the new test's default keyword values to the appropriate
            # new data as defined by the datasource decorator
            args, _, _, defaults = inspect.getargspec(original_test)

            # Self doesn't have a default, so we need to remove it
            args.remove('self')

            # Make sure we take into account required arguments
            kwargs = dict(
                zip_longest(
                    args[::-1], list(defaults or ())[::-1], fillvalue=None))

            kwargs.update(dataset.data)

            # Make sure the updated values are in the correct order
            new_default_values = [kwargs[arg] for arg in args]
            setattr(new_test, "func_defaults", tuple(new_default_values))

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
        """starts logging"""
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
        """stop logging"""
        self.func._log.removeHandler(self.func._log_handler)
