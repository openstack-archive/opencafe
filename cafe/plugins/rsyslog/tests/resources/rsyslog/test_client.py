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

from unittest import TestCase

from cafe.resources.rsyslog.client import RSyslogClient, MessageHandler


class TestSyslogClient(TestCase):
    DEFAULT_SD_DICT = {
        'test_project': {
            'token': 'test-token',
            'tenant': 'test-tenant'
        }
    }

    SAMPLE_SD_DICT = {
        'origin': {
            'software': 'opencafe-rsyslog'
        }
    }

    def setUp(self):
        self.client = RSyslogClient(default_sd=self.DEFAULT_SD_DICT)
        self.client.connect()

    def tearDown(self):
        self.client.close()

    def test_conversion_between_sd_dict_to_syslog_str(self):
        result = MessageHandler.sd_dict_to_syslog_str(self.SAMPLE_SD_DICT)
        self.assertEqual(result, '[origin software="opencafe-rsyslog"]')

    def test_send_basic_message(self):
        result = self.client.send(priority=1, msg='bam',
                                  sd=self.SAMPLE_SD_DICT)

        # A socket should return None if it was successful.
        self.assertIsNone(result)
