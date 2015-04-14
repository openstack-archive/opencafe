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

from cafe.common.reporting import cclogging


class RequiredClientNotDefinedError(Exception):
    """Raised when a behavior method call can't find a required client """
    pass


def behavior(*required_clients):
    """Decorator that tags method as a behavior, and optionally adds
    required client objects to an internal attribute.  Causes calls to this
    method to throw RequiredClientNotDefinedError exception if the containing
    class does not have the proper client instances defined.
    """

    def _decorator(func):
        # Unused for now
        setattr(func, '__is_behavior__', True)
        setattr(func, '__required_clients__', [])
        for client in required_clients:
            func.__required_clients__.append(client)

        def _wrap(self, *args, **kwargs):
            available_attributes = vars(self)
            missing_clients = []
            all_requirements_satisfied = True

            if required_clients:
                for required_client in required_clients:
                    required_client_found = False
                    for attr in available_attributes:
                        attribute = getattr(self, attr, None)
                        if isinstance(attribute, required_client):
                            required_client_found = True
                            break

                    all_requirements_satisfied = (
                        all_requirements_satisfied and
                        required_client_found)

                    missing_clients.append(required_client)

                if not all_requirements_satisfied:
                    msg_plurality = ("an instance" if len(missing_clients) <= 1
                                     else "instances")
                    msg = ("Behavior {0} expected {1} of {2} but couldn't"
                           " find one".format(
                               func, msg_plurality, missing_clients))
                    raise RequiredClientNotDefinedError(msg)
            return func(self, *args, **kwargs)
        return _wrap
    return _decorator


class BaseBehavior(object):
    def __init__(self):
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))
