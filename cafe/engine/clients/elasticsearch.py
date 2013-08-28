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
from pyes import ES
from pyes import TermQuery, BoolQuery, Search
from pyes.connection import NoServerAvailable
from pyes.connection_http import update_connection_pool

from cafe.engine.clients.base import BaseClient


class BaseElasticSearchClient(BaseClient):

    def __init__(self, servers, index):
        """
        @param servers: Make sure to include the port with the server address
        @param index: Document index
        @return:
        """
        super(BaseElasticSearchClient, self).__init__()
        self.connection = None
        self.servers = servers
        self.index = index if type(index) is list else [index]

    def connect(self, connection_pool=1):
        update_connection_pool(connection_pool)

        try:
            self.connection = ES(self.servers)
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

    def find_term(self, name, value, size=10):
        if not self.connection:
            return

        query = TermQuery(name, value)
        return self.connection.search(query=Search(query, size=size),
                                      indices=self.index)

    def find(self, filter_terms, size=10, doc_types=None):
        if not self.connection:
            return

        query = self._create_term_query(must_list=filter_terms)
        return self.connection.search(query=Search(query, size=size),
                                      indices=self.index,
                                      doc_types=doc_types)

    def find_one(self, filter_terms, size=10, doc_types=None):
        if not self.connection:
            return

        results = self.find(filter_terms=filter_terms, size=size,
                            doc_types=doc_types)
        return results[0] if len(results) > 0 else None
