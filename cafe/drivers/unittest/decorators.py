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
from importlib import import_module
from unittest import TestCase
from warnings import warn, simplefilter
import inspect
import re

from cafe.common.reporting import cclogging
from cafe.drivers.unittest.datasets import DatasetList
from cafe.drivers.unittest.fixtures import BaseTestFixture
from cafe.drivers.unittest.config import DriverConfig


DATA_DRIVEN_TEST_ATTR = "__data_driven_test_data__"
DATA_DRIVEN_TEST_PREFIX = "ddtest_"
TAGS_DECORATOR_ATTR_DICT_NAME = "__test_attrs__"
TAGS_DECORATOR_TAG_LIST_NAME = "__test_tags__"
PARALLEL_TAGS_LIST_ATTR = "__parallel_test_tags__"


class DataDrivenFixtureError(Exception):
    """Error if you apply DataDrivenClass to class that isn't a TestCase"""
    pass


def _add_tags(func, tags, attr):
    if not getattr(func, attr, None):
        setattr(func, attr, [])
    setattr(func, attr, list(set(getattr(func, attr)).union(set(tags))))
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
        """Calls _add_tags/_add_attrs to add tags to a func"""
        func = _add_tags(func, tags, TAGS_DECORATOR_TAG_LIST_NAME)
        func = _add_attrs(func, attrs)

        # add tags for parallel runner
        func = _add_tags(func, tags, PARALLEL_TAGS_LIST_ATTR)
        func = _add_tags(
            func, ["{0}={1}".format(k, v) for k, v in attrs.items()],
            PARALLEL_TAGS_LIST_ATTR)
        return func
    return decorator


def data_driven_test(*dataset_sources, **kwargs):
    """Used to define the data source for a data driven test in a
    DataDrivenFixture decorated Unittest TestCase class"""
    def decorator(func):
        """Combines and stores DatasetLists in __data_driven_test_data__"""
        dep_message = "DatasetList object required for data_generator"
        combined_lists = kwargs.get("dataset_source") or DatasetList()
        for key, value in kwargs.items():
            if key != "dataset_source" and isinstance(value, DatasetList):
                value.apply_test_tags(key)
            elif not isinstance(value, DatasetList):
                warn(dep_message, DeprecationWarning)
            combined_lists += value
        for dataset_list in dataset_sources:
            if not isinstance(dataset_list, DatasetList):
                warn(dep_message, DeprecationWarning)
            combined_lists += dataset_list
        setattr(func, DATA_DRIVEN_TEST_ATTR, combined_lists)
        return func
    return decorator


class EmptyDSLError(Exception):
    """Custom exception to allow errors in Datadriven classes with no data."""
    def __init__(self, dsl_namespace, original_test_list):
        general_message = (
            "The Dataset list used to generate this Data Driven Class was "
            "empty. No Fixtures or Tests were generated. Review the Dataset "
            "used to run this test.")
        DSL_information = "Dataset List location: {dsl_namespace}".format(
            dsl_namespace=dsl_namespace)
        pretty_test_list_header = (
            "The following {n} tests were not run".format(
                n=len(original_test_list)))
        pretty_test_list = "\t" + "\n\t".join(original_test_list)
        self.message = (
            "{general_message}\n{DSL_information}\n\n"
            "{pretty_test_list_header}\n{pretty_test_list}").format(
                general_message=general_message,
                DSL_information=DSL_information,
                pretty_test_list_header=pretty_test_list_header,
                pretty_test_list=pretty_test_list)
        super(EmptyDSLError, self).__init__(self.message)


class _FauxDSLFixture(BaseTestFixture):
    """Faux Test Fixture and Test class to inject into DDC that lack data."""

    dsl_namespace = None
    original_test_list = []

    # This is so we don't have to call super as there will never be anything
    # here.
    _class_cleanup_tasks = []

    @classmethod
    def setUpClass(cls):
        """setUpClass to force a fixture error for DDCs which lack data."""
        raise EmptyDSLError(
            dsl_namespace=cls.dsl_namespace,
            original_test_list=cls.original_test_list)

    # A test method is required in order to allow this to be injected without
    # making changes to Unittest itself.
    def test_data_failed_to_generate(self):
        """Faux test method to allow injection."""
        pass


def DataDrivenClass(*dataset_lists):
    """Use data driven class decorator. designed to be used on a fixture."""
    def decorator(cls):
        """Creates classes with variables named after datasets.
        Names of classes are equal to (class_name with out fixture) + ds_name
        """
        module = import_module(cls.__module__)
        cls = DataDrivenFixture(cls)
        class_name = re.sub("fixture", "", cls.__name__, flags=re.IGNORECASE)
        if not re.match(".*fixture", cls.__name__, flags=re.IGNORECASE):
            cls.__name__ = "{0}Fixture".format(cls.__name__)

        unittest_driver_config = DriverConfig()

        for i, dataset_list in enumerate(dataset_lists):
            if (not dataset_list and
               not unittest_driver_config.ignore_empty_datasets):
                # The DSL did not generate anything
                class_name_new = "{class_name}_{exception}_{index}".format(
                    class_name=class_name,
                    exception="DSL_EXCEPTION",
                    index=i)
                # We are creating a new, special class here that willd allow us
                # to force an error during test set up that contains
                # information useful for triaging the DSL failure.
                # Additionally this should surface any tests that did not run
                # due to the DSL issue.
                new_cls = DataDrivenFixture(_FauxDSLFixture)
                new_class = type(
                    class_name_new,
                    (new_cls,),
                    {})
                dsl_namespace = cclogging.get_object_namespace(
                    dataset_list.__class__)
                test_ls = [test for test in dir(cls) if test.startswith(
                    'test_') or test.startswith(DATA_DRIVEN_TEST_PREFIX)]
                new_class.dsl_namespace = dsl_namespace
                new_class.original_test_list = test_ls
                new_class.__module__ = cls.__module__
                setattr(module, class_name_new, new_class)
            for dataset in dataset_list:
                class_name_new = "{0}_{1}".format(class_name, dataset.name)
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
            new_test_name = "test_{0}_{1}".format(base_test_name, dataset.name)

            new_test = create_func(original_test, new_test_name, dataset.data)

            # Copy over any other attributes the original test had (mainly to
            # support test tag decorator)
            for key, value in vars(original_test).items():
                if key != DATA_DRIVEN_TEST_ATTR:
                    setattr(new_test, key, value)

            # Set dataset tags and attrs
            new_test = _add_tags(
                new_test, dataset.metadata.get('tags', []),
                TAGS_DECORATOR_TAG_LIST_NAME)
            new_test = _add_tags(
                new_test, dataset.metadata.get('tags', []),
                PARALLEL_TAGS_LIST_ATTR)

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
