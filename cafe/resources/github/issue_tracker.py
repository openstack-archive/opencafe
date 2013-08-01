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

from cafe.resources.github.config import GitHubConfig
from github import Github
from github.GithubException import UnknownObjectException, \
    RateLimitExceededException


class GitHubTracker(object):

    @classmethod
    def is_bug_open(cls, issue_id):
        """Checks whether the GitHub issue for the given issue id is open.
        An issue is considered open if its state is open and it does not have
        a label that contains 'done' or 'complete.'
        """
        config = GitHubConfig()
        github = Github(login_or_token=config.token)
        log = logging.getLogger('RunnerLog')
        try:
            repo = github.get_repo(config.repo)
            issue = repo.get_issue(int(issue_id))
        except UnknownObjectException as error:
            log.info('Invalid issue number or GitHub repo. '
                     'UnknownObjectException: {0}'.format(error))
            return False
        except RateLimitExceededException as error:
            log.info('Rate limit for API calls exceeded.'
                     'GithubException: {0}'.format(error))
            return False

        if issue.state == 'closed':
            return False

        labels = issue.get_labels()
        for label in labels:
            label = label.name.lower()
            if 'done' in label or 'complete' in label:
                return False

        return True
