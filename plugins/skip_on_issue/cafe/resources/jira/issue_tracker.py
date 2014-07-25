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
import logging

from cafe.resources.jira.config import JiraTrackerConfig
from jira.client import JIRA
from jira.exceptions import JIRAError
from requests.exceptions import RequestException


class JiraTracker(object):

    @classmethod
    def is_bug_open(cls, issue_id):
        """Checks if the JIRA issue is open."""
        log = logging.getLogger('RunnerLog')

        config = JiraTrackerConfig()

        issue = None
        try:
            # exceptions from requests can bubble up here
            jira = JIRA(options={'server': config.server})

            # returns an Issue ojbect; JIRAError on invalid id
            issue = jira.issue(issue_id)
        except JIRAError as error:
            log.info('Error getting issue from JIRA. '
                     'JIRAError: {0}'.format(error))
        except RequestException as error:
            log.info('Unable to connect to JIRA server {0}. '
                     'RequestException: {1}'.format(config.server, error))

        status_name = None
        if issue:
            status_name = issue.fields.status.name

        closed_statuses = [x.lower() for x in config.closed_statuses]
        if status_name is None or status_name.lower() not in closed_statuses:
            return True
        return False
