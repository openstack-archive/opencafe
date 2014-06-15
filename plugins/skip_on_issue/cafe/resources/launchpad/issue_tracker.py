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
import logging

from cafe.resources.launchpad.config import LaunchpadTrackerConfig
from lplight.client import LaunchpadClient


class LaunchpadTracker(object):

    @classmethod
    def is_bug_open(cls, bug_id):
        """Checks whether the Launchpad bug for the given bug id is open.
        An issue is considered open if its status is either "Fix Committed"
        or "Fix Released."
        """
        config = LaunchpadTrackerConfig()
        log = logging.getLogger('RunnerLog')
        launchpad = LaunchpadClient()

        resp = launchpad.get_bug_tasks(bug_id)
        if resp.status_code == 404:
            log.info('Couldn\'t find bug with ID {0}'.format(bug_id))

        tasks = resp.model or []
        for bug_task in tasks:
            if bug_task.bug_target_name == config.project:
                return bug_task.status not in ('Fix Committed', 'Fix Released')

        log.info('Bug does not affect project {0} '
                 'or project name is not correct.'.format(config.project))
        return False
