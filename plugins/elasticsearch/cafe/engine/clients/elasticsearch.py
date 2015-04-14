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

from time import sleep

from pyes import ES
from pyes import TermQuery, BoolQuery, Search
from pyes.connection import NoServerAvailable
from pyes.connection_http import update_connection_pool
from pyes.exceptions import IndexMissingException

from cafe.engine.clients.base import BaseClient


class BaseElasticSearchClient(BaseClient):

    def __init__(self, servers, index=None):
        """
        @param servers: Make sure to include the port with the server address
        @param index: Document index
        @return:
        """
        super(BaseElasticSearchClient, self).__init__()
        self.connection = None
        self.servers = servers

        if index is not None:
            self.index = index if type(index) is list else [index]

    def connect(self, connection_pool=1, bulk_size=10):
        update_connection_pool(connection_pool)

        try:
            self.connection = ES(self.servers, bulk_size=bulk_size)
        except NoServerAvailable:
            self._log.error('Failed to connect to elastic search server')
            return False
        return True

    def close(self):
        self.connection = None

    def _create_term_query(self, must_list):
        # TODO: add remaining conditional list functionality.
        query = BoolQuery()
        for term in must_list:
            query.add_must(term)

    def refresh_index(self, index_name, wait=1):
        self._log.info('ES: Refreshing index {0}'.format(index_name))
        self.connection.indices.refresh(index_name, timesleep=wait)

    def has_index(self, index_name):
        self._log.info('ES: Checking for index {0}'.format(index_name))
        try:
            self.connection.status(index_name)
        except IndexMissingException:
            return False
        return True

    def wait_for_index(self, index_name, wait=30):
        """ Checks to see if an index exists.
        Checks every second for int(X) seconds and returns True if successful
        """
        for i in range(0, int(wait)):
            if self.has_index(index_name):
                return True

            sleep(1)
        return False

    def wait_for_messages(self, name, value, num=1, index=None, max_wait=30):
        """ Wait for a specific number of messages to be returned within a
        specified amount of time.
        Checks every second for {max_wait} seconds and returns a list of msgs
        """
        for i in range(0, int(max_wait)):
            msgs = self.find_term(name=name, value=value, size=1, index=index)
            if len(msgs) == num:
                return msgs
            sleep(1)
        return []

    def delete_index(self, index_name):
        self._log.info('ES: Deleting index {0}'.format(index_name))
        self.connection.delete_index(index_name)

    def find_term(self, name, value, size=10, index=None):
        if not self.connection:
            return

        query = TermQuery(name, value)
        return self.connection.search(query=Search(query, size=size),
                                      indices=index or self.index)

    def find(self, filter_terms, size=10, doc_types=None, index=None):
        if not self.connection:
            return

        query = self._create_term_query(must_list=filter_terms)
        return self.connection.search(query=Search(query, size=size),
                                      indices=index or self.index,
                                      doc_types=doc_types)

    def find_one(self, filter_terms, doc_types=None, index=None):
        if not self.connection:
            return

        results = self.find(filter_terms=filter_terms, size=1,
                            doc_types=doc_types, index=index)
        return results[0] if len(results) > 0 else None
