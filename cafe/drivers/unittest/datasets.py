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

from itertools import product
from string import ascii_letters, digits
import json

ALLOWED_FIRST_CHAR = "_{0}".format(ascii_letters)
ALLOWED_OTHER_CHARS = "{0}{1}".format(ALLOWED_FIRST_CHAR, digits)


class _Dataset(object):
    """Defines a set of data to be used as input for a data driven test.
    data_dict should be a dictionary with keys matching the keyword
    arguments defined in test method that consumes the dataset.
    name should be a string describing the dataset.
    This class should not be accessed directly. Use or extend DatasetList.
    """
    def __init__(self, name, data_dict, tags=None):
        self.name = name
        self.data = data_dict
        self.metadata = {'tags': tags or []}

    def apply_test_tags(self, tags):
        self.metadata['tags'] = list(
            set(self.metadata.get('tags')).union(set(tags)))

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

    def append_new_dataset(self, name, data_dict, tags=None):
        """Creates and appends a new Dataset"""
        self.append(_Dataset(name, data_dict, tags))

    def extend(self, dataset_list):
        if not isinstance(dataset_list, DatasetList):
            raise TypeError(
                "extend() argument must be type DatasetList, not {0}".format(
                    type(dataset_list)))
        super(DatasetList, self).extend(dataset_list)

    def extend_new_datasets(self, dataset_list):
        """Creates and extends a new DatasetList"""
        self.extend(dataset_list)

    def apply_test_tags(self, *tags):
        """Applys tags to all tests in dataset list"""
        for dataset in self:
            dataset.apply_test_tags(tags)

    def dataset_names(self):
        """Gets a list of dataset names from dataset list"""
        return [ds.name for ds in self]

    def dataset_name_map(self):
        """Creates a dictionary with key=count and value=dataset name"""
        return {count: ds.name for count, ds in enumerate(self)}

    def merge_dataset_tags(self, *dataset_lists):
        local_name_map = self.dataset_name_map()
        for dsl in dataset_lists:
            for foreign_ds in dsl:
                for location, name in local_name_map.items():
                    if name == foreign_ds.name:
                        self[location].metadata['tags'] = list(
                            set(self[location].metadata.get('tags')).union(
                                foreign_ds.metadata.get('tags')))

    @staticmethod
    def replace_invalid_characters(string, new_char="_"):
        """This functions corrects string so the following is true
        Identifiers (also referred to as names) are described by the
        following lexical definitions:
        identifier ::=  (letter|"_") (letter | digit | "_")*
        letter     ::=  lowercase | uppercase
        lowercase  ::=  "a"..."z"
        uppercase  ::=  "A"..."Z"
        digit      ::=  "0"..."9"
        """
        if not string:
            return string
        for char in set(string) - set(ALLOWED_OTHER_CHARS):
            string = string.replace(char, new_char)
        if string[0] in digits:
            string = "{0}{1}".format(new_char, string[1:])
        return string


class DatasetListCombiner(DatasetList):
    """Class that can be used to combine multiple DatasetList objects together.
    Produces the product of combining every dataset from each list together
    with the names merged together. The data is overridden in a cascading
    fashion, similar to CSS, where the last dataset takes priority.
    """

    def __init__(self, *datasets):
        super(DatasetListCombiner, self).__init__()
        for dataset_list in product(*datasets):
            tmp_dic = {}
            names = []
            for dataset in dataset_list:
                tmp_dic.update(dataset.data)
                names.append(dataset.name)
            self.append_new_dataset("_".join(names), tmp_dic)


class DatasetGenerator(DatasetList):
    """Generates Datasets from a list of dictionaries, which are named
    numericaly according to the source dictionary's order in the source list.
    If a base_dataset_name is provided, that is used as the base name postfix
    for all tests before they are numbered.
    """

    def __init__(self, list_of_dicts, base_dataset_name=None):
        super(DatasetGenerator, self).__init__()
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
        super(TestMultiplier, self).__init__()
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
        super(DatasetFileLoader, self).__init__()
        content = json.loads(str(file_object.read()))
        count = 0
        for dataset in content:
            name = dataset.get('name', str(count))
            data = dataset.get('data', dict())
            self.append_new_dataset(name, data)
            count += 1
