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

from string import ascii_letters, digits
ALLOWED_FIRST_CHAR = "_{0}".format(ascii_letters)
ALLOWED_OTHER_CHARS = "{0}{1}".format(ALLOWED_FIRST_CHAR, digits)


class _Dataset(object):
    def __init__(self, name, data_dict, tags=None):
        """Defines a set of data to be used as input for a data driven test.
        data_dict should be a dictionary with keys matching the keyword
        arguments defined in test method that consumes the dataset.
        name should be a string describing the dataset.
        """

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
        for dataset in self:
            dataset.apply_test_tags(tags)

    def dataset_names(self):
        return [ds.name for ds in self]

    def dataset_name_map(self):
        name_map = {}
        count = 0
        for ds in self:
            name_map[count] = ds.name
            count += 1
        return name_map

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
