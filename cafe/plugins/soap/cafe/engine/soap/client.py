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

import logging
import suds
import suds.xsd.doctor as suds_doctor

from cafe.engine.clients.base import BaseClient


class BaseSoapClient(BaseClient):
    """Base SOAP Client
    @summary: Provides a Basic SOAP client by wrapping the lightweight
        suds client.
    @see: https://fedorahosted.org/suds/
    """
    def __init__(self, wsdl, ns_import_location=None, location=None,
                 username=None, password=None, faults=False, plugins=None,
                 cache=None):
        super(BaseSoapClient, self).__init__()
        logging.getLogger('suds').setLevel(logging.CRITICAL)

        # Fix import for parsing most WSDLs
        if ns_import_location is None:
            ns_import_location = 'http://schemas.xmlsoap.org/soap/encoding/'
        ns_import = suds_doctor.Import(ns_import_location)
        doctor = suds_doctor.ImportDoctor(ns_import)

        if plugins is None:
            plugins = [doctor]
        else:
            plugins.extend([doctor])
        self.client = suds.client.Client(wsdl,
                                         location=location,
                                         username=username,
                                         password=password,
                                         faults=faults,
                                         plugins=plugins,
                                         cache=cache)

    def get_service(self):
        """ Get Service
        @summary: Gets the service methods from the instantiated client.
        @return: self.client.service
        @rtype: Tuple
        """
        return self.client.service
