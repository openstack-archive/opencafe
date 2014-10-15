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

import collections
import inspect
import six
from six.moves import zip_longest
from importlib import import_module

from types import FunctionType
from unittest import TestCase
from warnings import warn, simplefilter

from cafe.common.reporting import cclogging

TAGS_DECORATOR_TAG_LIST_NAME = "__test_tags__"
TAGS_DECORATOR_ATTR_DICT_NAME = "__test_attrs__"
DATA_DRIVEN_TEST_ATTR = "__data_driven_test_data__"
DATA_DRIVEN_TEST_PREFIX = "ddtest_"


class DataDrivenFixtureError(Exception):
    pass


def _add_tags(func, tags):
    if not getattr(func, TAGS_DECORATOR_TAG_LIST_NAME, None):
        setattr(func, TAGS_DECORATOR_TAG_LIST_NAME, [])
    func.__test_tags__ = list(set(func.__test_tags__).union(set(tags)))
    return func


def _add_attrs(func, attrs):
    if not getattr(func, TAGS_DECORATOR_ATTR_DICT_NAME, None):
        setattr(func, TAGS_DECORATOR_ATTR_DICT_NAME, {})
    func.__test_attrs__.update(attrs)
    return func


def tags(*tags, **attrs):
    """Adds tags and attributes to tests, which are interpreted by the
    cafe-runner at run time
    """
    def decorator(func):
        func = _add_tags(func, tags)
        func = _add_attrs(func, attrs)
        return func
    return decorator


def data_driven_test(*dataset_sources, **kwargs):
    """Used to define the data source for a data driven test in a
    DataDrivenFixture decorated Unittest TestCase class"""

    def decorator(func):
        # dataset_source checked for backward compatibility
        combined_lists = kwargs.get("dataset_source") or []
        for dataset_list in dataset_sources:
            combined_lists += dataset_list
        setattr(func, DATA_DRIVEN_TEST_ATTR, combined_lists)
        return func
    return decorator


class DummyDataDrivenClass(object):
    pass


def DataDrivenClass(*dataset_lists):
    def decorator(cls):
        # This case works but you are Decorating the class twice with the
        # DataDrivenFixture
        if getattr(cls, "__DATA_DRIVEN_FIXTURE__", False):
            warn("DataDrivenFixture decorator is not needed with "
                 "DataDrivenClass")
        module = import_module(cls.__module__)
        for dataset_list in dataset_lists:
            for dataset in dataset_list:
                class_name = "{0}_{1}".format(cls.__name__, dataset.name)
                new_class = DataDrivenFixture(
                    type(class_name, (cls,), dataset.data))
                new_class.__module__ = cls.__module__
                setattr(module, dataset.name, new_class)
        return DummyDataDrivenClass
    return decorator


def DataDrivenFixture(cls):
    """Generates new unittest test methods from methods defined in the
    decorated class"""
    # This case does not work because the DataDrivenClass doesn't return the
    # class
    if issubclass(cls, DummyDataDrivenClass):
        raise DataDrivenFixtureError(
            "DataDrivenFixture is not needed when using DataDrivenClass")

    if not issubclass(cls, TestCase):
        raise DataDrivenFixtureError

    # adds a variable to tell if the DataDrivenFixture decorator is used
    cls.__DATA_DRIVEN_FIXTURE__ = True

    test_case_attrs = dir(cls)
    for attr_name in test_case_attrs:
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
            new_test_name = "test_{0}_{1}".format(
                base_test_name, dataset.name)

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


def skip_open_issue(type, bug_id):
    simplefilter('default', DeprecationWarning)
    warn('cafe.drivers.unittest.decorators.skip_open_issue() has been moved '
         'to cafe.drivers.unittest.issue.skip_open_issue()',
         DeprecationWarning)

    try:
        from cafe.drivers.unittest.issue import skip_open_issue as skip_issue
        return skip_issue(type, bug_id)
    except ImportError:
        print ('* Skip on issue plugin is not installed. Please install '
               'the plugin to use this functionality')
    return lambda obj: obj


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
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            value = self.func(*args)
            self.func._log.debug("Uncacheable.  Data returned")
            self._stop_logging()
            return value

        if args in self.cache:
            self.func._log.debug("Cached data returned.")
            self._stop_logging()
            return self.cache[args]

        else:
            value = self.func(*args)
            self.cache[args] = value
            self.func._log.debug("Data cached for future calls")
            self._stop_logging()
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    def _start_logging(self, log_file_name):
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
            self.func._log.removeHandler(self.func._log_handler)
