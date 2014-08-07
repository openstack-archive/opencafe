"""
Copyright 2014 Rackspace

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
import logging

from cafe.engine.models.data_interfaces import ConfigSectionInterface


class JiraTrackerConfig(ConfigSectionInterface):

    SECTION_NAME = 'JIRA'

    def _get_json(self, key):
        log = logging.getLogger('RunnerLog')

        statuses = self.get(key)
        if not statuses:
            return None

        try:
            return json.loads(statuses)
        except ValueError as error:
            log.info('Invalid JSON for {0}. ValueError {1}'.format(key, error))
            return None

    @property
    def server(self):
        """The location of your JIRA server."""
        return self.get('server')

    @property
    def closed_statuses(self):
        """These statuses define a closed issue."""
        return self._get_json('closed_statuses')

    @property
    def closed_labels(self):
        """These labels define a closed issue."""
        return self._get_json('closed_labels')
