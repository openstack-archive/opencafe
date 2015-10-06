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

import logging

from cafe.resources.launchpad.config import LaunchpadTrackerConfig
from lplight.client import LaunchpadClient


class LaunchpadTracker(object):

    @classmethod
    def is_bug_open(cls, bug_id):
        """Checks whether the Launchpad bug for the given bug id is open.
        An issue is considered open if its status is either "Fix Committed"
        or "Fix Released". An issue is also open if none of its tags are in
        the closed_tags list in the config file.
        """
        config = LaunchpadTrackerConfig()
        log = logging.getLogger('RunnerLog')
        launchpad = LaunchpadClient()

        # check the bug's tags
        if config.closed_tags is not None:
            bug_resp = launchpad.get_bug_by_id(bug_id)
            cls._log_if_not_found(log, bug_resp, bug_id)

            tags = bug_resp.model.tags if bug_resp.model else None
            if cls._bug_tags_are_open(tags, config):
                return True

        # check the bug's status
        if config.use_status:
            tasks_resp = launchpad.get_bug_tasks(bug_id)
            cls._log_if_not_found(log, tasks_resp, bug_id)

            tasks = tasks_resp.model or []
            if cls._bug_status_is_open(tasks, config):
                return True

        log.info('Bug does not affect project {0} '
                 'or project name is not correct.'.format(config.project))
        return False

    @classmethod
    def _log_if_not_found(cls, log, resp, bug_id):
        if resp.status_code == 404:
            log.info('Couldn\'t find bug with ID {0}'.format(bug_id))

    @classmethod
    def _bug_status_is_open(cls, tasks, config):
        for bug_task in tasks:
            if bug_task.bug_target_name == config.project:
                return bug_task.status not in ('Fix Committed', 'Fix Released')
        return False

    @classmethod
    def _bug_tags_are_open(cls, tags, config):
        if tags is None:
            return False
        tag_set = set(x.lower() for x in tags)
        closed_tags = set(x.lower() for x in config.closed_tags)
        matches = tag_set.intersection(closed_tags)
        return not bool(matches)
