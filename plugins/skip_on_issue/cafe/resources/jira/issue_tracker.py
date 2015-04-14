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

from cafe.resources.jira.config import JiraTrackerConfig
from jira.client import JIRA
from jira.exceptions import JIRAError
from requests.exceptions import RequestException


class JiraTracker(object):

    @classmethod
    def is_bug_open(cls, issue_id):
        """Checks if the JIRA issue is open. An issue is open if its status is
        not in the closed_statuses list, or if none of its labels are in the
        closed_labels list.
        """

        log = logging.getLogger('RunnerLog')

        config = JiraTrackerConfig()

        issue = None
        try:
            # exceptions from requests can bubble up here
            jira = JIRA(options={'server': config.server})

            # returns an Issue object; JIRAError on invalid id
            issue = jira.issue(issue_id)
        except JIRAError as error:
            log.info('Error getting issue from JIRA. '
                     'JIRAError: {0}'.format(error))
        except RequestException as error:
            log.info('Unable to connect to JIRA server {0}. '
                     'RequestException: {1}'.format(config.server, error))

        if cls._status_is_open(issue, config):
            return True
        elif cls._labels_are_open(issue, config):
            return True
        return False

    @classmethod
    def _status_is_open(cls, issue, config):
        # allow the issue's status to be ignored
        if config.closed_statuses is None:
            return False

        status = issue.fields.status
        if status is None:
            return True

        closed_statuses = [x.lower() for x in config.closed_statuses]
        return str(status).lower() not in closed_statuses

    @classmethod
    def _labels_are_open(cls, issue, config):
        # allow the issue's labels to be ignored
        if config.closed_labels is None:
            return False

        # Determine if the issue has any of its labels in closed_labels
        labels = set(str(x).lower() for x in issue.fields.labels)
        closed_labels = set(x.lower() for x in config.closed_labels)
        matches = labels.intersection(closed_labels)

        # the issue is open only if no labels are closed
        return not bool(matches)
