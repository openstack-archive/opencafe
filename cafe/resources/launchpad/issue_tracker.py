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
from launchpadlib.launchpad import Launchpad


class LaunchpadTracker(object):

    @classmethod
    def is_bug_open(cls, bug_id):
        """Checks whether the Launchpad bug for the given bug id is open.
        An issue is considered open if its status is either "Fix Committed"
        or "Fix Released."
        """
        config = LaunchpadTrackerConfig()
        log = logging.getLogger('RunnerLog')
        launchpad = Launchpad.login_anonymously(consumer_name='test',
                                                service_root='production')
        try:
            bug = launchpad.bugs[bug_id]
        except KeyError as error:
            # Invalid bug ID
            log.info('Invalid bug ID. Key Error: {0}'.format(error))
            return False

        tasks = bug.bug_tasks
        entries = tasks.entries
        for bug_entry in entries:
            if bug_entry['bug_target_name'] == config.project:
                return bug_entry['status'] not in ('Fix Committed',
                                                   'Fix Released')

        log.info('Bug does not affect project {0} '
                 'or project name is not correct.'.format(config.project))
        return False
