OpenCafe
========

.. image:: https://img.shields.io/pypi/v/opencafe.svg
    :target: https://pypi.python.org/pypi/opencafe

.. image:: https://travis-ci.org/CafeHub/opencafe.svg?branch=master
    :target: https://travis-ci.org/CafeHub/opencafe



When writing automated suites, there are some things that should
"just work". Problems like managing test data, logging, and results
are something you shouldn't have to re-invent for every test project you
work on. OpenCafe aims to address that problem by providing solutions
for the commonly occurring challenges in the development and operation of
functional and end-to-end test suites.

Capabilities
------------

- Common sense conventions for test data and log management
- Per test run and per test logs and results
- Reference drivers for performing non-UI testing:
    - HTTP
    - SSH
    - WinRM
- Design patterns for building test clients for RESTful API applications
- Plugin system to allow for further customization

Installation
============

Core package
------------

From PyPI (recommended):

::

    $ pip install opencafe

From source:

::

    $ git clone https://github.com/CafeHub/opencafe.git
    $ cd opencafe
    $ pip install .

Post-install Configuration
--------------------------

Post-install, the ``cafe-config`` cli tool will become available.
It is used for installing
plugins and initializing the engine's default ``.opencafe`` directory.

Initialization
^^^^^^^^^^^^^^
OpenCAFE uses a set of default locations for logging, storing
test configurations, test data, statistics, and the like; all of which are
set in, and read from, the ``engine.config`` file (in order to make it easy
for the end user to override the default behavior).  The ``engine.config``
file, and the directories it references, can be created on demand by running:

``cafe-config init``

This will create a directory named ``.opencafe`` in the user's home
directory, or in the case of a python virtualenv, in the virtualenv root
folder.

Plugins
^^^^^^^

OpenCafe uses a plugin system to allow for core functionality to be
extended or for additional capabilities to be added. Plugins are
essentially Python packages, which may have their own Python dependencies.
This design allows implementors to only install dependencies for the
functionality that they intend to use, as the additional dependencies
are installed at the same time as the plugin.

The ``cafe-config plugins`` command is used to list and install plugins.

Example:

::

    $ cafe-config plugins list
    =================================
    * Available Plugins
      ... elasticsearch
      ... http
      ... mongo
      ... pathos_multiprocess
      ... rsyslog
      ... skip_on_issue
      ... soap
      ... ssh
      ... sshv2
      ... subunit
      ... winrm
    =================================

    $ cafe-config plugins install http
    =================================
    * Installing Plugins
      ... http
    =================================

Documentation
-------------

More in-depth documentation about the OpenCafe framework is located at
http://opencafe.readthedocs.org.

How to Contribute
-----------------

Contributions are always welcome. The CONTIBUTING.md file contains further
guidance on submitting changes to this project and the review process that
we follow.
