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

import json

from cafe.engine.models.base import AutoMarshallingModel


class MailgunEntity(AutoMarshallingModel):

    def __init__(self, message, id):
        """
        An object that represents a MailgunEntity.
        """
        super(MailgunEntity, self).__init__()
        self.message = message
        self.id = id

    def __repr__(self):
        values = []
        for prop in self.__dict__:
            values.append("{0}: {1}".format(prop, self.__dict__[prop]))
        return "[{represenation}]".format(represenation=', '.join(values))

    @classmethod
    def _json_to_obj(cls, serialized_str):
        """
        Returns an instance of a MailgunEntity based on the
        json serialized_str passed in.
        """
        response_dict = json.loads(serialized_str)
        response = MailgunEntity(**response_dict)
        return response
