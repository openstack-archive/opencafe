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
