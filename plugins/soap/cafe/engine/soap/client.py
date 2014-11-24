"""
Copyright 2014 Rackspace

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

import logging
import suds
import suds.xsd.doctor as suds_doctor
from suds.sax.element import Element

from cafe.engine.clients.base import BaseClient


class BaseSoapClient(BaseClient):
    """Base SOAP Client
    @summary: Provides a Basic SOAP client by re-implementing the
        lightweight suds client.
    @see: https://fedorahosted.org/suds/
    """
    def __init__(self, wsdl, endpoint=None, username=None, password=None,
                 plugins=None):
        super(BaseSoapClient, self).__init__()
        logging.getLogger('suds').setLevel(logging.CRITICAL)
        self.wsdl = wsdl
        self.endpoint = endpoint
        self.username = username
        self.password = password

        # Fix import for parsing most WSDLs
        ns_import = suds_doctor.Import(
            'http://schemas.xmlsoap.org/soap/encoding/')
        doctor = suds_doctor.ImportDoctor(ns_import)
        if plugins is None:
            plugins = [doctor]
        else:
            plugins.extend([doctor])
        self.client = suds.client.Client(wsdl,
                                         location=endpoint,
                                         username=username,
                                         password=password,
                                         faults=False,
                                         plugins=plugins,
                                         cache=None)

    def get_service(self):
        """ Get Service
        @summary: Gets the service methods from the instantiated client.
        @return: self.client.service
        @rtype: Tuple
        """
        return self.client.service

    def set_location(self, location):
        """ Set Location
        @summary: Sets location on the instantiated client.
        @return: None
        """
        self.client.set_options(location=location)

    def set_credentials(self, username, password):
        """ Set Credentials
        @summary: Sets credentials for the instantiated client.
        @return: None
        """
        self.client.set_options(username=username, password=password)

    def set_wsdl(self, wsdl):
        """ Set WSDL
        @summary: Sets WSDL on the instantiated client.
        @return: None
        """
        self.client.wsdl = wsdl

    def set_headers(self, header_list):
        """ Set Headers
        @summary: Sets Headers on the instantiated client.
        @return: None
        @note: Expecting a list of headers with each header being a dictionary
            consisting of:
                header['ns_prefix'] = prefix for the namespace
                header['ns_url'] = url of the namespace
                header['name'] = name of the header element (tag name)
                header['text'] = text of the header element
        """
        element_list = []
        for header in header_list:
            namespace = (header['ns_prefix'], header['ns_url'])
            element = Element(header['name'],
                              ns=namespace).setText(header['text'])
            element_list.append(element)
        self.client.set_options(soapheaders=element_list)
