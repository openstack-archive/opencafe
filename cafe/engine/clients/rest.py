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
from warnings import warn, simplefilter
simplefilter("default", DeprecationWarning)
warn("cafe.engine.clients.rest has been moved to cafe.engine.http.client",
     DeprecationWarning)

from cafe.engine.http.client import (
    BaseClient, requests, time, _inject_exception, _log_transaction, cclogging)

from cafe.engine.http.client import BaseHTTPClient as BaseRestClient

from cafe.engine.http.client import \
    AutoMarshallingHTTPClient as AutoMarshallingRestClient

from cafe.engine.http.client import HTTPClient as RestClient
