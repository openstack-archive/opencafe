"""
@copyright: Copyright (c) 2014 Rackspace US, Inc.

Soap Client Tests
"""

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
