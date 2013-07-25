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

from types import FunctionType
from unittest2 import TestCase, skip

from cafe.resources.launchpad.issue_tracker import LaunchpadTracker

TAGS_DECORATOR_TAG_LIST_NAME = "__test_tags__"
TAGS_DECORATOR_ATTR_DICT_NAME = "__test_attrs__"
DATA_DRIVEN_TEST_ATTR = "__data_driven_test_data__"
DATA_DRIVEN_TEST_PREFIX = "ddtest_"


class DataDrivenFixtureError(Exception):
    pass


def tags(*tags, **attrs):
    """Adds tags and attributes to tests, which are interpreted by the
    cafe-runner at run time
    """

    def decorator(func):
        setattr(func, TAGS_DECORATOR_TAG_LIST_NAME, [])
        setattr(func, TAGS_DECORATOR_ATTR_DICT_NAME, {})
        func.__test_tags__.extend(tags)
        func.__test_attrs__.update(attrs)
        return func
    return decorator


def data_driven_test(dataset_source=None):
    """Used to define the data source for a data driven test in a
    DataDrivenFixture decorated Unittest TestCase class"""

    def decorator(func):
        setattr(func, DATA_DRIVEN_TEST_ATTR, dataset_source)
        return func
    return decorator


def DataDrivenFixture(cls):
    """Generates new unittest test methods from methods defined in the
    decorated class"""

    if not issubclass(cls, TestCase):
        raise DataDrivenFixtureError

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
                original_test.func_code, original_test.func_globals,
                name=new_test_name)

            # Copy over any other attributes the original test had (mainly to
            # support test tag decorator)
            for attr in list(set(dir(original_test)) - set(dir(new_test))):
                setattr(new_test, attr, getattr(original_test, attr))

            # Change the new test's default keyword values to the appropriate
            # new data as defined by the datasource decorator
            new_default_values = []
            for arg in list(original_test.func_code.co_varnames)[1:]:
                new_default_values.append(dataset.data[arg])
            setattr(new_test, "func_defaults", tuple(new_default_values))

            # Add the new test to the TestCase
            setattr(cls, new_test_name, new_test)
    return cls


def skip_open_issue(type, bug_id):
    """ Skips the test if there is an open issue for that test.

    @param type: The issue tracker type (e.g., Launchpad, GitHub).
    @param bug_id: ID of the issue for the test.
    """
    if type.lower() == 'launchpad' and LaunchpadTracker.is_bug_open(
            bug_id=bug_id):
        return skip('Launchpad Bug #{0}'.format(bug_id))
    return lambda obj: obj
