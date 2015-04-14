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

from mock import MagicMock
import unittest

from cafe.engine.soap.client import BaseSoapClient


class SoapClientTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        super(SoapClientTests, cls).setUpClass()

        cls.wsdl = "http://fake.wsdl"
        cls.endpoint = "http://fake.url.endpoint"
        cls.username = "fake_username"
        cls.password = "fakepassword12345"
        cls.plugins = None

    def test_create_soap_client_object(self):
        soap_client_object = BaseSoapClient
        soap_client_object.__init__ = MagicMock()
        soap_client_object.__init__(
            wsdl=self.wsdl,
            endpoint=self.endpoint,
            username=self.username,
            password=self.password,
            plugins=self.plugins)
        soap_client_object.__init__.assert_called_once_with(
            wsdl=self.wsdl,
            endpoint=self.endpoint,
            username=self.username,
            password=self.password,
            plugins=self.plugins)
