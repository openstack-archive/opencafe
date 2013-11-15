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

from cafe.engine.clients.base import BaseClient
from cafe.common.reporting import cclogging


class BaseSQLClient(BaseClient):

    _log = cclogging.getLogger(__name__)
    _driver = None
    _connection = None

    def connect(self, data_source_name=None, user=None, password=None,
                host=None, database=None):
        """
        Connects to self._driver with passed parameters

        @param data_source_name: The data source name
        @type data_source_name: String
        @param user: Username
        @type user: String
        @param password: Password
        @type password: String
        @param host: Hostname
        @type host: String
        @param database: Database Name
        @type database: String
        """
        if self._driver is None:
            message = 'Driver not set.'
            self._log.error(message)
            raise Exception(message)

        try:
            self._connection = self._driver.connect(
                data_source_name=data_source_name, user=user, password=password, host=host,
                database=database)
        except AttributeError:
            message = "No connect method found in self._driver module"
            self._log.error(message)
            raise Exception(message)

    def execute(self, operation, parameters=None, cursor=None):
        """
        Calls execute with operation & parameters sent in on either the passed
        cursor or a new cursor

        For more information on the execute command see:
        http://www.python.org/dev/peps/pep-0249/#id15

        @param operation: The operation being executed
        @type operation: String
        @param parameters: Sequence or map that wil be bound to variables in
                           the operation
        @type parameters: String or dictionary
        @param cursor: A pre-existing cursor
        @type cursor: object
        """
        if cursor is None:
            cursor = self._connection.cursor()
        return cursor.execute(operation, parameters)

    def execute_many(self, operation, seq_of_parameters=None, cursor=None):
        """
        Calls executemany with operation & parameters sent in on either the
        passed cursor or a new cursor

        For more information on the execute command see:
        http://www.python.org/dev/peps/pep-0249/#executemany

        @param operation: The operation being executed
        @type operation: String
        @param seq_of_parameters: The sequence or mappings that will be run
                                  against the operation
        @type seq_of_parameters: String or object
        @param cursor: A pre-existing cursor
        @type cursor: object
        """
        if cursor is None:
            cursor = self._connection.cursor()
        return cursor.executemany(operation, seq_of_parameters)

    def close(self):
        """
        Closes the connection
        """
        if self._connection is not None:
            self._connection.close()
            self._connection = None
