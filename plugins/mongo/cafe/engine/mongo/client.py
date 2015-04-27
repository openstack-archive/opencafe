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
import pymongo
from pymongo import MongoClient

from cafe.common.reporting import cclogging
from cafe.engine.clients.base import BaseClient


class BaseMongoClient(BaseClient):
    """
    @summary: Designed to be a simple interface to make calls to MongoDB
    """
    FAILED = 'failed'
    SUCCESS = 'success'
    _log = cclogging.getLogger(__name__)

    def __init__(self, hostname, db_name, username, password):
        super(BaseMongoClient, self).__init__()
        self.hostname = hostname
        self.db_name = db_name
        self.username = username
        self.password = password
        self.connection = None
        self.db = None

    @classmethod
    def from_connection_string(cls, uri):
        params = pymongo.uri_parser.parse_uri(uri)
        hosts = params.get('nodelist')

        if len(hosts) == 0:
            raise Exception("Invalid connection string: {uri}".format(
                uri=uri))
        host, port = hosts[0]
        return cls(hostname=host, db_name=params.get('database'),
                   username=params.get('username'),
                   password=params.get('password'))

    def is_connected(self):
        if self.connection:
            return self.connection.alive()
        return False

    def connect(self, hostname=None, db_name=None):
        """
        @summary: Connects to a server, but does not authenticate.
        @param hostname: if not specified it'll attempt to use init hostname
        @param db_name: if not specified it'll attempt to use init db_name
        @return:
        """
        if hostname is None:
            hostname = self.hostname
        if db_name is None:
            db_name = self.db_name

        self.connection = MongoClient(hostname)
        self.db = self.connection[db_name]

        result = 'Connected' if self.is_connected() else 'Failed to connect'
        self._log.debug('{0} to MongoDB: {1}'.format(result, hostname))

        return self.SUCCESS if self.is_connected() else self.FAILED

    def disconnect(self):
        self.connection.close()
        self._log.debug('Disconnected from MongoDB')

    def auth(self, username=None, password=None):
        """
        @summary: Attempts to auth with a connected db. Returns FAILED if
         there isn't an active connection.
        @param username: if not specified it'll attempt to use init username
        @param password: if not specified it'll attempt to use init password
        @return:
        """
        if not self.is_connected():
            return self.FAILED

        if username is None:
            username = self.username
        if password is None:
            password = self.password

        if username and password:
            self.db.authenticate(name=username, password=password)

        return self.SUCCESS

    def find_one(self, db_obj_name, filter=None):
        result_filter = filter or dict()
        if not self.is_connected():
            return self.FAILED

        db_obj = self.db[db_obj_name]
        return db_obj.find_one(result_filter)

    def delete(self, db_obj_name, filter=None, just_one=True):
        result_filter = filter or dict()
        if not self.is_connected():
            return self.FAILED

        db_obj = self.db[db_obj_name]
        return db_obj.remove(result_filter, just_one)
