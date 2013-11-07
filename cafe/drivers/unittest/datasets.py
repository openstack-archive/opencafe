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

import json
import collections
import inspect
from cafe.common.reporting import cclogging


class _Dataset(object):
    def __init__(self, name, data_dict):
        """Defines a set of data to be used as input for a data driven test.
        data_dict should be a dictionary with keys matching the keyword
        arguments defined in test method that consumes the dataset.
        name should be a string describing the dataset.
        """

        self.name = name
        self.data = data_dict

    def __repr__(self):
        return "<name:{0}, data:{1}>".format(self.name, self.data)


class DatasetList(list):
    """Specialized list-like object that holds Dataset objects"""

    def append(self, dataset):
        if not isinstance(dataset, _Dataset):
            raise TypeError(
                "append() argument must be type Dataset, not {0}".format(
                    type(dataset)))

        super(DatasetList, self).append(dataset)

    def append_new_dataset(self, name,  data_dict):
        """Creates and appends a new Dataset"""
        self.append(_Dataset(name, data_dict))


class DatasetGenerator(DatasetList):
    """Generates Datasets from a list of dictionaries, which are named
    numericaly according to the source dictionary's order in the source list.
    If a base_dataset_name is provided, that is used as the base name postfix
    for all tests before they are numbered.
    """

    def __init__(self, list_of_dicts, base_dataset_name=None):
        count = 0
        for kwdict in list_of_dicts:
            test_name = "{0}_{1}".format(base_dataset_name or "dataset", count)
            self.append_new_dataset(test_name, kwdict)
            count += 1


class TestMultiplier(DatasetList):
    """Creates num_range number of copies of the source test,
    and names the new tests numerically.  Does not generate Datasets.
    """

    def __init__(self, num_range):
        for num in range(num_range):
            name = "{0}".format(num)
            self.append_new_dataset(name, dict())


class DatasetFileLoader(DatasetList):
    """Reads a file object's contents in as json and converts them to
    lists of Dataset objects.
    Files should be opened in 'rb' (read binady) mode.
    File should be a list of dictionaries following this format:
    [{'name':"dataset_name", 'data':{key:value, key:value, ...}},]
    if name is ommited, it is replaced with that dataset's location in the
    load order, so that not all datasets need to be named.
    """
    def __init__(self, file_object):
        content = json.loads(str(file_object.read()))
        count = 0
        for dataset in content:
            name = dataset.get('name', str(count))
            data = dataset.get('data', dict())
            self.append_new_dataset(name, data)
            count += 1


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
        self.__name__ = func.func_name

    def __call__(self, *args):
        self._start_logging(cclogging.get_object_namespace(args[0]))
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
            self.func._log.debug(
                "Data cached for future calls: {0}".format(value))
            self._stop_logging()
            return value

    def __repr__(self):
        """Return the function's docstring."""
        return self.func.__doc__

    # Because the root log is initialized in the base test fixture, and because
    # datalist generators are run before that test fixture is initialized,
    # it is neccessary to add a log handler to the root logger so that logs
    # get logged.  Once the root log handler initialization is moved
    # upstream of the base test fixture initialization, this code can be
    # removed.
    def _start_logging(self, log_file_name):
        setattr(self.func, '_log_handler', cclogging.setup_new_cchandler(
            log_file_name))
        setattr(self.func, '_log', cclogging.getLogger(''))
        self.func._log.addHandler(self.func._log_handler)
        curframe = inspect.currentframe()
        self.func._log.debug("{0} called from {1}".format(
            self.__name__, inspect.getouterframes(curframe, 2)[2][3]))

    def _stop_logging(self):
        self.func._log.removeHandler(self.func._log_handler)
