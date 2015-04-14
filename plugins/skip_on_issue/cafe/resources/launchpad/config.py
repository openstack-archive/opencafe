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

from cafe.engine.models.data_interfaces import ConfigSectionInterface


class LaunchpadTrackerConfig(ConfigSectionInterface):

    SECTION_NAME = 'LAUNCHPAD'

    # Project name in Launchpad (name in URL of project, not display name)
    @property
    def project(self):
        return self.get('project')

    @property
    def use_status(self):
        """Specifies whether to check the status of the bug."""
        return self.get_boolean('use_status', default=True)

    @property
    def closed_tags(self):
        """These tags define a closed launchpad bug."""
        return self.get_json('closed_tags')
