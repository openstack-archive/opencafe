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

import unittest

from cafe.engine.http.behaviors import get_range_data


class TestHttpFunctions(unittest.TestCase):

    def test_get_range_data(self):
        data = '0123456789'
        data_subset = get_range_data(data, '0-4')
        self.assertEqual('01234', data_subset)

        data_subset = get_range_data(data, '5-9')
        self.assertEqual('56789', data_subset)

    def test_get_range_data_with_first_byte_pos(self):
        data = '0123456789'
        data_subset = get_range_data(data, '7-')
        self.assertEqual('789', data_subset)

    def test_get_range_data_with_last_byte_pos(self):
        data = '0123456789'
        data_subset = get_range_data(data, '-3')
        self.assertEqual('789', data_subset)


if __name__ == '__main__':
    unittest.main()
