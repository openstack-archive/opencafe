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

from ast import literal_eval

from cloudcafe.common.models.configuration import ConfigSectionInterface


class MailgunConfig(ConfigSectionInterface):

    SECTION_NAME = 'mailgun'

    @property
    def api_url(self):
        return self.get('api_url')

    @property
    def api_key(self):
        return self.get('api_key')

    @property
    def domain_name(self):
        return self.get('domain_name')

    @property
    def smtp_hostname(self):
        return self.get('smtp_hostname')

    @property
    def smtp_password(self):
        return self.get('smtp_password')

    @property
    def from_email(self):
        return self.get('from_email')

    @property
    def to_email(self):
        return literal_eval(self.get('to_email'))

    @property
    def attachments(self):
        return literal_eval(self.get('attachments'))
