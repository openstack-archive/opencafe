===========
Quickstart
===========

**The goals of this section of the guide are to provide a detailed explaination
of how to use some of the basic OpenCafe components, as well as to explain
what types of problems are solved by using OpenCafe. Further details on each
component can be found in the rest of the documentation.**

Installation
============

To get started, We should install and initialize OpenCafe. We can do this by
running the following commands:

.. code-block:: bash

    pip install opencafe
    cafe-config init

Making HTTP Requests
====================

As an example, we can write a few tests for the GitHub API. For the sake of
this example, we will assume that we don't have language bindings or SDKs for
our API which is common for APIs in development. We can create a simple client
using the BaseHTTPClient class provided by the OpenCafe HTTP plugin, which is
a lightweight wrapper for the ``requests`` package. First, we'll need to
install the HTTP plugin:

.. code-block:: bash

    cafe-config plugin install http

Now we can create a simple python script to request the details of a GitHub
issue:

.. code-block:: python
    
    import json
    import os

    from cafe.engine.http.client import BaseHTTPClient

    # Opencafe normally expects for a configuration data file to be set beforeit is
    # run. For these examples this isn't necessary, but the value still needs to be set.
    # This is behavior that we should fix, but hasn't been at the time this guide was written
    os.environ['CAFE_ENGINE_CONFIG_FILE_PATH']='.' 
    client = BaseHTTPClient()
    response = client.get('https://api.github.com/repos/cafehub/opencafe/issues/42')
    print json.dumps(response.json(), indent=2)

This will generate some warnings that we will address later, but the outcome
should be similar to the following:

.. code-block:: bash

    {
        "labels": [],
        "number": 42,
        "assignee": null,
        "repository_url": "https://api.github.com/repos/CafeHub/opencafe",
        "closed_at": "2017-02-28T16:32:28Z",
        "id": 210568122,
        "title": "Adds a Travis CI config to run tox",
        "pull_request": {
            "url": "https://api.github.com/repos/CafeHub/opencafe/pulls/42",
            "diff_url": "https://github.com/CafeHub/opencafe/pull/42.diff",
            "html_url": "https://github.com/CafeHub/opencafe/pull/42",
            "patch_url": "https://github.com/CafeHub/opencafe/pull/42.patch"
        },
        "comments": 0,
        "state": "closed",
        "body": "",
        "labels_url": "https://api.github.com/repos/CafeHub/opencafe/issues/42/labels{/name}",
        "events_url": "https://api.github.com/repos/CafeHub/opencafe/issues/42/events",
        "comments_url": "https://api.github.com/repos/CafeHub/opencafe/issues/42/comments",
        "html_url": "https://github.com/CafeHub/opencafe/pull/42",
        "updated_at": "2017-02-28T16:32:28Z",
        "user": {
            "following_url": "https://api.github.com/users/dwalleck/following{/other_user}",
            "events_url": "https://api.github.com/users/dwalleck/events{/privacy}",
            "organizations_url": "https://api.github.com/users/dwalleck/orgs",
            "url": "https://api.github.com/users/dwalleck",
            "gists_url": "https://api.github.com/users/dwalleck/gists{/gist_id}",
            "html_url": "https://github.com/dwalleck",
            "subscriptions_url": "https://api.github.com/users/dwalleck/subscriptions",
            "avatar_url": "https://avatars2.githubusercontent.com/u/843116?v=3",
            "repos_url": "https://api.github.com/users/dwalleck/repos",
            "received_events_url": "https://api.github.com/users/dwalleck/received_events",
            "gravatar_id": "",
            "starred_url": "https://api.github.com/users/dwalleck/starred{/owner}{/repo}",
            "site_admin": false,
            "login": "dwalleck",
            "type": "User",
            "id": 843116,
            "followers_url": "https://api.github.com/users/dwalleck/followers"
        },
        "milestone": null,
        "closed_by": {
            "following_url": "https://api.github.com/users/jidar/following{/other_user}",
            "events_url": "https://api.github.com/users/jidar/events{/privacy}",
            "organizations_url": "https://api.github.com/users/jidar/orgs",
            "url": "https://api.github.com/users/jidar",
            "gists_url": "https://api.github.com/users/jidar/gists{/gist_id}",
            "html_url": "https://github.com/jidar",
            "subscriptions_url": "https://api.github.com/users/jidar/subscriptions",
            "avatar_url": "https://avatars2.githubusercontent.com/u/1134139?v=3",
            "repos_url": "https://api.github.com/users/jidar/repos",
            "received_events_url": "https://api.github.com/users/jidar/received_events",
            "gravatar_id": "",
            "starred_url": "https://api.github.com/users/jidar/starred{/owner}{/repo}",
            "site_admin": false,
            "login": "jidar",
            "type": "User",
            "id": 1134139,
            "followers_url": "https://api.github.com/users/jidar/followers"
        },
        "locked": false,
        "url": "https://api.github.com/repos/CafeHub/opencafe/issues/42",
        "created_at": "2017-02-27T18:34:21Z",
        "assignees": []
    }

The BaseHTTPClient returns the same response that ``requests`` would, so we
can treat the response similarly to view its content. At this point, it
doesn't look like the OpenCafe HTTP plugin is adding any more value than
``requests`` would. Let's see what we can do about that. First, let's setup
logging and see what happens.

.. code-block:: python

    import json
    import logging
    import os
    import sys

    from cafe.engine.http.client import BaseHTTPClient
    from cafe.common.reporting import cclogging


    os.environ['CAFE_ENGINE_CONFIG_FILE_PATH']='.'
    cclogging.init_root_log_handler()
    root_log = logging.getLogger()
    root_log.addHandler(logging.StreamHandler(stream=sys.stderr))
    root_log.setLevel(logging.DEBUG)

    client = BaseHTTPClient()
    response = client.get('https://api.github.com/repos/cafehub/opencafe/issues/42')

The ``cclogging`` package simplifies parts of working with the standard Python
logger, such as creating and initializing a logger. With logging enabled,
let's execute our script again to see the difference.

.. code-block:: bash

    (cafe-demo) dwalleck@MINERVA:~$ python demo.py
    Environment variable 'CAFE_MASTER_LOG_FILE_NAME' is not set. A null root log handler will be used, no logs will be written.(<cafe.engine.http.client.BaseHTTPClient object at 0x7fd2a58cf550>, 'GET', 'https://api.github.com/repos/cafehub/opencafe/issues/42') {}
    No section: 'PLUGIN.HTTP'.  Using default value '0' instead
    Starting new HTTPS connection (1): api.github.com
    https://api.github.com:443 "GET /repos/cafehub/opencafe/issues/42 HTTP/1.1" 200 None

    ------------
    REQUEST SENT
    ------------
    request method..: GET
    request url.....: https://api.github.com/repos/cafehub/opencafe/issues/42
    request params..:
    request headers.: {'Connection': 'keep-alive', 'Accept-Encoding': 'gzip, deflate', 'Accept': '*/*', 'User-Agent': 'python-requests/2.13.0'}
    request body....: None


    -----------------
    RESPONSE RECEIVED
    -----------------
    response status..: <Response [200]>
    response time....: 0.35421204567
    response headers.: {'X-XSS-Protection': '1; mode=block', 'Content-Security-Policy': "default-src 'none'", 'Access-Control-Expose-Headers': 'ETag, Link, X-GitHub-OTP, X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset, X-OAuth-Scopes, X-Accepted-OAuth-Scopes, X-Poll-Interval', 'Transfer-Encoding': 'chunked', 'Last-Modified': 'Thu, 13 Apr 2017 19:13:26 GMT', 'Access-Control-Allow-Origin': '*', 'X-Frame-Options': 'deny', 'Status': '200 OK', 'X-Served-By': 'eef8b8685a106934dcbb4b7c59fba0bf', 'X-GitHub-Request-Id': 'FA86:30F6:B12CE5:ED8475:58F8F029', 'ETag': 'W/"2fbeb849316f7b18e9138ea40d150441"', 'Date': 'Thu, 20 Apr 2017 17:30:17 GMT', 'X-RateLimit-Remaining': '59', 'Strict-Transport-Security': 'max-age=31536000; includeSubdomains; preload', 'Server': 'GitHub.com', 'X-GitHub-Media-Type': 'github.v3; format=json', 'X-Content-Type-Options': 'nosniff', 'Content-Encoding': 'gzip', 'Vary': 'Accept, Accept-Encoding', 'X-RateLimit-Limit': '60', 'Cache-Control': 'public, max-age=60, s-maxage=60', 'Content-Type': 'application/json; charset=utf-8', 'X-RateLimit-Reset': '1492713017'}
    response body....: {"url":"https://api.github.com/repos/CafeHub/opencafe/issues/42","repository_url":"https://api.github.com/repos/CafeHub/opencafe","labels_url":"https://api.github.com/repos/CafeHub/opencafe/issues/42/labels{/name}","comments_url":"https://api.github.com/repos/CafeHub/opencafe/issues/42/comments","events_url":"https://api.github.com/repos/CafeHub/opencafe/issues/42/events","html_url":"https://github.com/CafeHub/opencafe/pull/42","id":210568122,"number":42,"title":"Adds a Travis CI config to run tox","user":{"login":"dwalleck","id":843116,"avatar_url":"https://avatars2.githubusercontent.com/u/843116?v=3","gravatar_id":"","url":"https://api.github.com/users/dwalleck","html_url":"https://github.com/dwalleck","followers_url":"https://api.github.com/users/dwalleck/followers","following_url":"https://api.github.com/users/dwalleck/following{/other_user}","gists_url":"https://api.github.com/users/dwalleck/gists{/gist_id}","starred_url":"https://api.github.com/users/dwalleck/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/dwalleck/subscriptions","organizations_url":"https://api.github.com/users/dwalleck/orgs","repos_url":"https://api.github.com/users/dwalleck/repos","events_url":"https://api.github.com/users/dwalleck/events{/privacy}","received_events_url":"https://api.github.com/users/dwalleck/received_events","type":"User","site_admin":false},"labels":[],"state":"closed","locked":false,"assignee":null,"assignees":[],"milestone":null,"comments":0,"created_at":"2017-02-27T18:34:21Z","updated_at":"2017-02-28T16:32:28Z","closed_at":"2017-02-28T16:32:28Z","pull_request":{"url":"https://api.github.com/repos/CafeHub/opencafe/pulls/42","html_url":"https://github.com/CafeHub/opencafe/pull/42","diff_url":"https://github.com/CafeHub/opencafe/pull/42.diff","patch_url":"https://github.com/CafeHub/opencafe/pull/42.patch"},"body":"","closed_by":{"login":"jidar","id":1134139,"avatar_url":"https://avatars2.githubusercontent.com/u/1134139?v=3","gravatar_id":"","url":"https://api.github.com/users/jidar","html_url":"https://github.com/jidar","followers_url":"https://api.github.com/users/jidar/followers","following_url":"https://api.github.com/users/jidar/following{/other_user}","gists_url":"https://api.github.com/users/jidar/gists{/gist_id}","starred_url":"https://api.github.com/users/jidar/starred{/owner}{/repo}","subscriptions_url":"https://api.github.com/users/jidar/subscriptions","organizations_url":"https://api.github.com/users/jidar/orgs","repos_url":"https://api.github.com/users/jidar/repos","events_url":"https://api.github.com/users/jidar/events{/privacy}","received_events_url":"https://api.github.com/users/jidar/received_events","type":"User","site_admin":false}}
    -------------------------------------------------------------------------------

That's a little better. We get a verbose log entry for the details of request
made and the response we received.  The output from the HTTP client is meant
to be human readable and to create an audit trail of what occurred while a
test or script was executed.

Creating a Basic Application Client
===================================

Now let's add a few more requests to our script:

.. code-block:: python

    import json
    import logging
    import os
    import sys

    from cafe.engine.http.client import BaseHTTPClient
    from cafe.common.reporting import cclogging


    os.environ['CAFE_ENGINE_CONFIG_FILE_PATH']='.'
    cclogging.init_root_log_handler()
    root_log = logging.getLogger()
    root_log.addHandler(logging.StreamHandler(stream=sys.stderr))
    root_log.setLevel(logging.DEBUG)


    client = BaseHTTPClient()
    response = client.get('https://api.github.com/repos/cafehub/opencafe/issues/42')
    response = client.get('https://api.github.com/repos/cafehub/opencafe/commits')
    response = client.get('https://api.github.com/repos/cafehub/opencafe/forks')

As we make more requests, a few concerns come to mind. Right now we are
hard-coding the base url (https://api.github.com) in each request. The
organization and project names are both something that could change. At the very
least, we should factor out what is common between the requests or what is
likely to change as we grow this script:

.. code:: python

    import json
    import logging
    import os
    import sys

    from cafe.engine.http.client import BaseHTTPClient
    from cafe.common.reporting import cclogging


    os.environ['CAFE_ENGINE_CONFIG_FILE_PATH']='.'
    cclogging.init_root_log_handler()
    root_log = logging.getLogger()
    root_log.addHandler(logging.StreamHandler(stream=sys.stderr))
    root_log.setLevel(logging.DEBUG)

    client = BaseHTTPClient()
    base_url = 'https://api.github.com'
    organization = 'cafehub'
    project = 'opencafe'
    issue_id = 42

    response = client.get(
        '{base_url}/repos/{org}/{project}/commits'.format(
            base_url=base_url, org=organization, project=project))

    response = client.get(
        '{base_url}/repos/{org}/{project}/issues/{issue_id}'.format(
            base_url=base_url, org=organization, project=project,
            issue_id=issue_id))

    response = client.get(
        '{base_url}/repos/{org}/{project}/forks'.format(
            base_url=base_url, org=organization, project=project))

The GitHub API is expansive, so we could go on for some time defining more
requests. Rather than defining these in-line, defining these functions in a
common class would make more sense from an organization sense.

.. code:: python

    import json
    import logging
    import os
    import sys

    from cafe.engine.clients.base import BaseClient
    from cafe.engine.http.client import BaseHTTPClient
    from cafe.common.reporting import cclogging


    class GitHubClient(BaseHTTPClient):

        def __init__(self, base_url):
            super(GitHubClient, self).__init__()
            self.base_url = base_url
        
        def get_project_commits(self, org_name, project_name):
            return self.get(
                '{base_url}/repos/{org}/{project}/commits'.format(
                    base_url=base_url, org=org_name, project=project))
        
        def get_issue_by_id(self, org_name, project_name, issue_id):
            return self.get(
                '{base_url}/repos/{org}/{project}/issues/{issue_id}'.format(
                    base_url=base_url, org=org_name, project=project,
                    issue_id=issue_id))
        
        def get_project_forks(self, org_name, project_name):
            return self.get(
                '{base_url}/repos/{org}/{project}/forks'.format(
                    base_url=base_url, org=org_name, project=project))

    os.environ['CAFE_ENGINE_CONFIG_FILE_PATH']='.'
    cclogging.init_root_log_handler()
    root_log = logging.getLogger()
    root_log.addHandler(logging.StreamHandler(stream=sys.stderr))
    root_log.setLevel(logging.DEBUG)

    base_url = 'https://api.github.com'
    organization = 'cafehub'
    project = 'opencafe'
    issue_id = 42
    client = GitHubClient(base_url)

    resp1 = client.get_project_commits(org_name=organization, project_name=project)
    resp2 = client.get_issue_by_id(org_name=organization, project_name=project, issue_id=issue_id)
    resp3 = client.get_project_forks(org_name=organization, project_name=project) 

Our client subclasses the BaseHTTPClient, so there's no longer a need to
create an instance of the client. This creates the foundation for a simple
language binding for our API under test.

Now that our HTTP requests are in better shape, let's talk about dealing with
the responses. The ``requests`` response object has a ``json`` method that will
transform the body of the response into a Python dictionary. While treating the
response content as a dictionary is good enough for quick scripts and possibly
for working with very stable APIs, it has challenges that we should consider
before going further.

Accessing the response as a dictionary isn't too difficult when a response body
has one or two properties, but let's jump back to the first response output we
looked at. It has dozens of properties, including ones that are nested. Using
the response as-is requires memorizing the response structure or constantly
referencing API documentation as you code. If you make a mistake with the name
of a property, you may not find that out until you run the code. Also, when the
name of one of the properties or the structure of the API response changes,
this means tediously changing the property each place it is used or trying to
do a string replace across the project, which is an error-prone process.

Writing Request and Response Models
===================================

An alternate approach is to deserialize the JSON response to an object. This
is the approach that most SDKs and language bindings use. This
greatly simplifies refactoring of response properties and has the added bonus
of error detection by linters if you use an invalid property name. If you're
using a code editor which offers autocomplete functionality, you can also
use that when developing new tests, which removes most of the need to
reference API documentation after you've done the groundwork developing the
response models. Here's an example of what the response model for our first
request would look like:

.. code:: python

    class Issue(AutoMarshallingModel):

        def __init__(self, url, repository_url, labels_url, comments_url, events_url,
                    html_url, id, number, title, user, labels, state, locked,
                    assignee, assignees, milestone, comments, created_at,
                    updated_at, closed_at, body, closed_by):
            
            self.url = url
            self.repository_url = repository_url
            self.labels_url = labels_url
            self.comments_url = comments_url
            self.events_url = events_url
            self.html_url = html_url
            self.id = id
            self.number = number
            self.title = title
            self.user = user
            self.labels = labels
            self.state = state
            self.locked = locked
            self.assignee = assignee
            self.assignees = assignees
            self.milestone = milestone
            self.comments = comments
            self.created_at = created_at
            self.updated_at = updated_at
            self.closed_at = closed_at
            self.body = body
            self.closed_by = closed_by

        @classmethod
        def _json_to_obj(cls, serialized_str):
            resp_dict = json.loads(serialized_str)
            user = User(**resp_dict.get('user'))
            
            assignees = []
            for assignee in resp_dict.get('assignees'):
                assignees.append(User(**assignee))
            
            assignee = None
            if resp_dict.get('assignee'):
                assignee = User(**resp_dict.get('assignee'))

            labels = []
            for label in labels:
                labels.append(Label(**label))
            
            return Issue(
                url=resp_dict.get('url'),
                repository_url=resp_dict.get('repository_url'),
                labels_url=resp_dict.get('labels_url'),
                comments_url=resp_dict.get('comments_url'),
                events_url=resp_dict.get('events_url'),
                html_url=resp_dict.get('html_url'),
                id=resp_dict.get('id'),
                number=resp_dict.get('number'),
                title=resp_dict.get('title'),
                user=user,
                labels=labels,
                state=resp_dict.get('state'),
                locked=resp_dict.get('locked'),
                assignee=assignee,
                assignees=assignees,
                milestone=resp_dict.get('milestone'),
                comments=resp_dict.get('comments'),
                created_at=resp_dict.get('created_at'),
                updated_at=resp_dict.get('updated_at'),
                closed_at=resp_dict.get('closed_at'),
                body=resp_dict.get('body'),
                closed_by=resp_dict.get('closed_by'))


    class User(AutoMarshallingModel):

        def __init__(self, login, id, avatar_url, gravatar_id, url, html_url,
                    followers_url, following_url, gists_url, starred_url,
                    subscriptions_url, organizations_url, repos_url, events_url,
                    received_events_url, type, site_admin):
            
            self.login = login
            self.id = id
            self.avatar_url = avatar_url
            self.gravatar_id = gravatar_id
            self.url = url
            self.html_url = html_url
            self.followers_url = followers_url
            self.following_url = following_url
            self.gists_url = gists_url
            self.starred_url = starred_url
            self.subscriptions_url = subscriptions_url
            self.organizations_url = organizations_url
            self.repos_url = repos_url
            self.events_url = events_url
            self.received_events_url = received_events_url
            self.type = type
            self.site_admin = site_admin
        
        @classmethod
        def _json_to_obj(cls, serialized_str):
            resp_dict = json.loads(serialized_str)
            return User(**resp_dict)


    class Label(AutoMarshallingModel):

        def __init__(self, id, url, name, color, default):
            
            self.id = id
            self.url = url
            self.name = name
            self.color = color
            self.default = default
        
        @classmethod
        def _json_to_obj(cls, serialized_str):
            resp_dict = json.loads(serialized_str)
            return Label(**resp_dict)

Any class that inherits from the AutoMarshallingModel class is expected
to implement the _json_to_obj method, _obj_to_json method, or both. This
depends on whether the model is being used to handle requests, responses,
or both.

This example creates quite a bit of boilerplate code. We used an explicit
example so that it would be easy to understand what this code does. However,
because these objects are explicitly defined, static analysis tools will be
able to assist us going forward. It also allows code editors that support
Python autocompletion to work with our models. In more practical
implementations, you may want to take advantage of Python's dynamic
nature to simplify the setting of properties.

Writing an Auto-Serializing Client
==================================

Now that we have response models, we can refactor our client to use them.

.. code:: python

    from cafe.engine.http.client import AutoMarshallingHTTPClient


    class GitHubClient(AutoMarshallingHTTPClient):

        def __init__(self, base_url):
            super(GitHubClient, self).__init__(
                serialize_format='json', deserialize_format='json')
            self.base_url = base_url
            
        def get_issue_by_id(self, org_name, project_name, issue_id):
            url = '{base_url}/repos/{org}/{project}/issues/{issue_id}'.format(
                base_url=self.base_url, org=organization, project=project,
                issue_id=issue_id)
            return self.get(url, response_entity_type=Issue)

There's a few changes to note. The AutoMarshallingHTTPClient class replaces
BaseHTTPClient as the parent class because it is aware of request and response
content types. The response_entity_type parameter defines what type to expect
the response to be. This together with serialization formats set when the
client was instantiated determine which serialization methods are called on the
response contents. This can be used to create a single API client that can
handle both JSON and XML response types. This can be an extremely useful
capability to have when you want to write code a single that is able to test
both the JSON and XML capabilities of an API.

Managing Test Data
==================

Before we start writing our tests, let's step back and deal with one more
issue. In the original code, we had statically defined certain data
such as the GitHub URL, the organization name, and the project name. There
are many reasons why you should not hardcode these types of values in your
code. Of those, the most important to us is that we should not have to make
code changes whenever we want to use different test data. We should be able to
provide the test data at runtime, which allows our code to be more flexible and
portable. 

There are many sources we could use for our test data, but for this example we
will use a plain text file with headers that can be parsed by Python's
``SafeConfigParser``. For this to work, we will need to create a class that
represents the data that we want to store in the file.

.. code:: python

    from cafe.engine.models.data_interfaces import ConfigSectionInterface


    class GitHubConfig(ConfigSectionInterface):

        SECTION_NAME = 'GitHub'

        @property
        def base_url(self):
            return self.get('base_url')

        @property
        def organization(self):
            return self.get('organization')

        @property
        def project(self):
            return self.get('project')

        @property
        def issue_id(self):
            return self.get('issue_id')

Note that there is nothing in this class that explicitly states the
type of the data source. This is because the OpenCafe ``data_interfaces``
package provides a generic interface for data sources including environment
variables and JSON data. For the purpose of this guide, we will just use
plain text files.

Our class defines that there should have a section titled ``GitHub`` in our
configuration file with four properties. The actual configuration file would
look similar to the following example:

.. code:: python

    [GitHub]
    base_url = https://api.github.com
    organization = cafehub
    project = opencafe
    issue_id = 42

Writing and Running a Test
==========================

**From this point in the demo, you can use the** `opencafe-demo`_
**project to follow along with the guide if you want to execute the steps
yourself.**

.. _opencafe-demo: https://github.com/dwalleck/opencafe-demo

Now that we have our test infrastructure in order, we can write several tests
to see how OpenCafe operates.

.. code:: python

    from cafe.drivers.unittest.fixtures import BaseTestFixture

    from opencafe_demo.github.github_client import GitHubClient
    from opencafe_demo.github.github_config import GitHubConfig


    class BasicGitHubTest(BaseTestFixture):

        @classmethod
        def setUpClass(cls):
            super(BasicGitHubTest, cls).setUpClass()  # Sets up logging/reporting for the test
            cls.config_data = GitHubConfig()

            cls.organization = cls.config_data.organization
            cls.project = cls.config_data.project
            cls.issue_id = cls.config_data.issue_id
            cls.client = GitHubClient(cls.config_data.base_url)

        def test_get_issue_response_code_is_200(self):
            response = self.client.get_project_issue(
                self.organization, self.project, self.issue_id)
            self.assertEqual(response.status_code, 200)

        def test_id_is_not_null_for_get_issue_request(self):
            response = self.client.get_project_issue(
                self.organization, self.project, self.issue_id)
            # The response signature is the raw response from Requests except
            # for the `entity` property, which is the object that represents
            # the response content
            issue = response.entity
            self.assertIsNotNone(issue.id)

In this test class, we inherit from OpenCafe's ``BaseTestFixture`` class. This
base class automatically handles all of the logging setup that we were
previously doing by hand. The ``BaseTestFixture`` class inherits from Python's
``unittest.TestCase``, so for all intents and purposes it behaves the
same as any other unittest-based test.

Before we can run this test, we need to get our configuration data file in
place. When we executed the ``cafe-config init`` command at the start of the
guide, you may have noticed in the output that several directories were
created. You should now have a ``.opencafe`` directory, which is where all
configuration data and test logs will be stored by default (these paths can be
changed in the ``.opencafe/engine.config`` file. See the full documentation for
further details). We will need to create a directory named ``GitHub`` in which
we will put our configuration file which we will call ``prod.config``. The
names used are arbitrary, but they create a convention that will be used when
we begin running our tests.

OpenCafe uses a convention based on ``<product-name>`` and
``<config-file-name>`` for finding configuration data and setting logging
locations. For configuration files, the ``<config-file-name>`` file will be
loaded from the ``.opencafe/configs/<product-name>`` directory. For logging,
logs for each test run will be saved in a unique directory named by the date
time stamp of when the tests were run in the ``.opencafe/logs/<product-name>/<config-file-name>``
directory.

For this guide, I'll be using OpenCafe's unittest-based runner to execute the
tests. All the tests in the ``github`` project can be run by executing
``cafe-runner github prod.config``.

.. code:: bash

    (cafe-demo) dwalleck@minerva:~$ cafe-runner github prod.config
    
        ( (
        ) )
    .........
    |       |___
    |       |_  |
    |  :-)  |_| |
    |       |___|
    |_______|
    === CAFE Runner ===
    ======================================================================================================================================================
    Percolated Configuration
    ------------------------------------------------------------------------------------------------------------------------------------------------------
    BREWING FROM: ....: /home/dwalleck/cafe-demo/local/lib/python2.7/site-packages/opencafe_demo
    ENGINE CONFIG FILE: /home/dwalleck/cafe-demo/.opencafe/engine.config
    TEST CONFIG FILE..: /home/dwalleck/cafe-demo/.opencafe/configs/github/prod.config
    DATA DIRECTORY....: /home/dwalleck/cafe-demo/.opencafe/data
    LOG PATH..........: /home/dwalleck/cafe-demo/.opencafe/logs/github/prod.config/2017-04-19_11_26_38.698599
    ======================================================================================================================================================
    test_get_issue_response_code_is_200 (opencafe_demo.github.test_issues_api.BasicGitHubTest) ... ok
    test_id_is_not_null_for_get_issue_request (opencafe_demo.github.test_issues_api.BasicGitHubTest) ... ok

    ----------------------------------------------------------------------
    Ran 2 tests in 0.543s

    OK
    ======================================================================================================================================================
    Detailed logs: /home/dwalleck/cafe-demo/.opencafe/logs/github/prod.config/2017-04-19_11_26_38.698599
    ------------------------------------------------------------------------------------------------------------------------------------------------------

The preamble output from the test runner pretty prints the location of all
configuration files used for the test run, as well as the the location of the
logs generated during the test run. Here's what the contents of the log
directory look like:

.. code:: bash

    (cafe-demo) dwalleck@minerva:~$ cd /home/dwalleck/cafe-demo/.opencafe/logs/github/prod.config/2017-04-19_11_26_38.698599
    (cafe-demo) dwalleck@minerva:~/cafe-demo/.opencafe/logs/github/prod.config/2017-04-19_11_26_38.698599$ ls -la
    total 36
    drwxrwxrwx 0 dwalleck dwalleck   512 Apr 19 11:26 .
    drwxrwxrwx 0 dwalleck dwalleck   512 Apr 19 11:26 ..
    -rw-rw-rw- 1 dwalleck dwalleck 15613 Apr 19 11:26 cafe.master.log
    -rw-rw-rw- 1 dwalleck dwalleck 15353 Apr 19 11:26 opencafe_demo.github.test_issues_api.BasicGitHubTest.log

Two log files were generated by this test run. The second log file is named by
the full package name of the test class that was run. If there had been
multiple test classes loaded for execution, there would be one file per class
run. The benefit of this is to be able to jump directly to the log file that
you are interested in inspecting. The contents of the logs contain the HTTP
requests made during test execution, but they also contain headers to mark
what point the in the lifecycle of the test is being executed:

.. code:: bash

    2017-04-19 11:26:38,838: INFO: root: ========================================================
    2017-04-19 11:26:38,840: INFO: root: Fixture......: opencafe_demo.github.test_issues_api.BasicGitHubTest
    2017-04-19 11:26:38,840: INFO: root: Created At...: 2017-04-19 11:26:38.838285
    2017-04-19 11:26:38,840: INFO: root: ========================================================
    2017-04-19 11:26:38,842: INFO: root: ========66================================================
    2017-04-19 11:26:38,842: INFO: root: Test Case....: test_get_issue_response_code_is_200
    2017-04-19 11:26:38,843: INFO: root: Created At...: 2017-04-19 11:26:38.838285
    2017-04-19 11:26:38,843: INFO: root: No Test description.
    2017-04-19 11:26:38,843: INFO: root: ========================================================

The other file, ``cafe.master.log`` is a summation of the other log files in
the order the tests were executed. This allows the user to consume the logs
however they find easiest.
