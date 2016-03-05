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
from importlib import import_module
from inspect import isclass
from requests.packages import urllib3
from time import time
import pkgutil
import re
import requests
import six

from cafe.common.reporting import cclogging
from cafe.engine.models.base import AutoMarshallingModel

urllib3.disable_warnings()


class ClassPropertyDescriptor(object):

    def __init__(self, fget, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj, klass=None):
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()


def classproperty(func):
    if not isinstance(func, (classmethod, staticmethod)):
        func = classmethod(func)
    return ClassPropertyDescriptor(func)


class BaseClass(object):
    @classproperty
    def _log(cls):
        return cclogging.getLogger(cclogging.get_object_namespace(cls))


def _log_transaction(func):
    def _safe_decode(text, incoming="utf-8", errors="replace"):
        """Decodes incoming text/bytes string using `incoming`
           if they"re not already unicode.

        :param incoming: Text"s current encoding
        :param errors: Errors handling policy. See here for valid
            values http://docs.python.org/2/library/codecs.html
        :returns: text or a unicode `incoming` encoded
                    representation of it.
        """
        if isinstance(text, six.text_type):
            return text

        return text.decode(incoming, errors)

    def request(cls, method, url, **kwargs):
        """Logging wrapper for any method that returns a requests response.
        Logs requestslib response objects, and the args and kwargs
        sent to the request() method, to the provided log at the provided
        log level.
        """
        log = cls._log
        logline = "".join([
            "\n{0}\nREQUEST ARGS/KWARGS\n{0}\n".format("-" * 19),
            "method..: {0}\n".format(method),
            "url.....: {0}\n".format(url),
            "kwargs..: {0}\n".format(kwargs),
            "-" * 79])
        try:
            log.debug(_safe_decode(logline))
        except Exception as exception:
            # Ignore all exceptions that happen in logging, then log them
            log.info(
                "Exception occured while logging signature of calling"
                "method in http client")
            log.exception(exception)

        # Make the request and time it"s execution
        try:
            start = time()
            response = func(cls, method, url, **kwargs)
            elapsed = time() - start
        except Exception as exception:
            logline = "".join([
                "\n{0}\nREQUEST EXCEPTION\n{0}\n".format("-" * 17),
                "Method.....: {0}\n".format(method),
                "URL........: {0}\n".format(url),
                "Exception..: {0}\n".format(exception),
                "-" * 79])
            log.exception(logline)
            raise exception

        # requests lib 1.0.0 renamed body to data in the request object
        if hasattr(response.request, "body"):
            request_body = response.request.body
        elif hasattr(response.request, "data"):
            request_body = response.request.data
        else:
            log.info(
                "Unable to log request body, neither a 'data' nor a "
                "'body' object could be found")

        # requests lib 1.0.4 removed params from response.request
        request_url = response.request.url
        request_params = ""
        if hasattr(response.request, "params"):
            request_params = response.request.params
        elif "?" in request_url:
            request_url, request_params = request_url.split("?")

        logline = "".join([
            "\n{0}\nREQUEST SENT\n{0}\n".format("-" * 12),
            "request method..: {0}\n".format(response.request.method),
            "request url.....: {0}\n".format(request_url),
            "request params..: {0}\n".format(request_params),
            "request headers.: {0}\n".format(response.request.headers),
            "request body....: {0}\n".format(request_body),
            "-" * 79])
        try:
            log.debug(_safe_decode(logline))
        except Exception as exception:
            # Ignore all exceptions that happen in logging, then log them
            log.exception("\n{0}\nREQUEST INFO\n{0}\n".format("-" * 12))
            log.exception(exception)

        logline = "".join([
            "\n{0}\nRESPONSE RECEIVED\n{0}\n".format("-" * 17),
            "response status..: {0}\n".format(response),
            "response time....: {0}\n".format(elapsed),
            "response headers.: {0}\n".format(response.headers),
            "response body....: {0}\n".format(response.content),
            "-" * 79])
        try:
            log.debug(_safe_decode(logline))
        except Exception as exception:
            # Ignore all exceptions that happen in logging, then log them
            log.exception("\n{0}\nRESPONSE INFO\n{0}\n".format("-" * 13))
            log.exception(exception)
        return response
    return request


class BaseHTTPClient(BaseClass):
    """Re-implementation of Requests" api.py that removes many assumptions.
    Adds verbose logging.
    Adds support for response-code based exception injection.
    (Raising exceptions based on response code)

    @see: http://docs.python-requests.org/en/latest/api/#configurations
    """
    def __init__(self):
        super(BaseHTTPClient, self).__init__()

    @classmethod
    @_log_transaction
    def request(cls, method, url, **kwargs):
        headers = {
            "Connection": None, "Accept-Encoding": None,
            "Accept": None, "User-Agent": None}
        verify = kwargs.pop("verify", False)
        headers.update(kwargs.pop("headers", {}))
        return requests.request(
            method, url, verify=verify, headers=headers, **kwargs)

    def put(self, url, **kwargs):
        """ HTTP PUT request """
        return self.request("PUT", url, **kwargs)

    def copy(self, url, **kwargs):
        """ HTTP COPY request """
        return self.request("COPY", url, **kwargs)

    def post(self, url, **kwargs):
        """ HTTP POST request """
        return self.request("POST", url, **kwargs)

    def get(self, url, **kwargs):
        """ HTTP GET request """
        return self.request("GET", url, **kwargs)

    def head(self, url, **kwargs):
        """ HTTP HEAD request """
        return self.request("HEAD", url, **kwargs)

    def delete(self, url, **kwargs):
        """ HTTP DELETE request """
        return self.request("DELETE", url, **kwargs)

    def options(self, url, **kwargs):
        """ HTTP OPTIONS request """
        return self.request("OPTIONS", url, **kwargs)

    def patch(self, url, **kwargs):
        """ HTTP PATCH request """
        return self.request("PATCH", url, **kwargs)


class AutoMarshallingHTTPClient(BaseHTTPClient):
    def __init__(self, serialize_format=None):
        super(AutoMarshallingHTTPClient, self).__init__()
        self.serialize_format = serialize_format
        self.default_headers = {}
        self._response_models = {}

    def request(
        self, method, url, headers=None, params=None, data=None,
            request_entity=None, requestslib_kwargs=None):
        requestslib_kwargs = requestslib_kwargs or {}

        method = requestslib_kwargs.pop("method", method)
        url = requestslib_kwargs.pop("url", url)
        headers = dict(self.default_headers, **(headers or {}))
        data = requestslib_kwargs.pop("data", self._serialize(request_entity))
        kwargs = dict(headers=headers, params=params, data=data)
        kwargs.update(requestslib_kwargs)

        response = super(AutoMarshallingHTTPClient, self).request(
            method, url, **kwargs)

        response.request.entity = request_entity
        response.entity = self._get_response_entity(response)

        return response

    def populate_response_models(self, dot_path):
        try:
            if isinstance(dot_path, list):
                for path in dot_path:
                    self.populate_response_models(path)
                return
            else:
                package = import_module(dot_path)
        except Exception as e:
            self._log.exception(e)
            raise e
        for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__,
            prefix="{0}.".format(package.__name__),
                onerror=lambda x: None):
            try:
                module = import_module(modname)
            except Exception as e:
                self._log.exception(e)
                raise e
            for k, obj in vars(module).items():
                if isclass(obj) and issubclass(obj, AutoMarshallingModel):
                    key = self._get_key(obj)
                    if key is not None:
                        self._response_models[key] = obj

    @classmethod
    def _get_key(cls, obj):
        """ override this to change key to look at other things like the url"""
        codes = cls._to_list_of_str(getattr(obj, "STATUS_CODE", None))
        urls = cls._to_list_of_str(getattr(obj, "PATH_URL", None))
        methods = cls._to_list_of_str(getattr(obj, "METHOD", "GET"))
        try:
            if codes is not None and urls is not None:
                for index, url in enumerate(urls):
                    if not url.endswith("$"):
                        urls[index] += "$"
                ret_val = (tuple(codes), tuple(urls), tuple(methods))
                hash(ret_val)
                return ret_val
        except Exception as e:
            cls._log.exception(e)
        return None

    @staticmethod
    def _to_list_of_str(var):
        if var is None:
            return None
        if isinstance(var, list) or isinstance(var, tuple):
            return [str(x) for x in set(var)]
        else:
            return [str(var)]

    def _get_response_entity(self, response):
        for key, model in self._response_models.items():
            status_codes, urls, methods = key
            if str(response.status_code) not in status_codes:
                continue
            if response.request.method not in methods:
                continue
            for url in urls:
                request_path = response.request.path_url.split("?", 1)[0]
                match = re.search(url, request_path)
                if not match:
                    continue
                ct = response.headers.get("content-type", "")
                for type_ in ["xml", "json", "pdf", "text"]:
                    if type_ in ct:
                        return model.deserialize(response.content, type_)
        return None

    def _serialize(self, request_entity):
        if request_entity is not None:
            func_name = "_obj_to_{0}".format(self.serialize_format)
            func = getattr(request_entity, func_name)
            return func()
