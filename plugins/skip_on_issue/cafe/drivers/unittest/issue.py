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

from unittest import skip

from cafe.resources.github.issue_tracker import GitHubTracker
from cafe.resources.launchpad.issue_tracker import LaunchpadTracker
from cafe.resources.jira.issue_tracker import JiraTracker


def skip_open_issue(type, bug_id):
    """ Skips the test if there is an open issue for that test.

    @param type: The issue tracker type (e.g., Launchpad, GitHub).
    @param bug_id: ID of the issue for the test.
    """
    if type.lower() == 'launchpad' and LaunchpadTracker.is_bug_open(
            bug_id=bug_id):
        return skip('Launchpad Bug #{0}'.format(bug_id))
    elif type.lower() == 'github' and GitHubTracker.is_bug_open(
            issue_id=bug_id):
        return skip('GitHub Issue #{0}'.format(bug_id))
    elif type.lower() == 'jira' and JiraTracker.is_bug_open(
            issue_id=bug_id):
        return skip('Jira Issue {0}'.format(bug_id))
    return lambda obj: obj
