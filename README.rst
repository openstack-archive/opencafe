OpenCafe
========

.. image:: https://img.shields.io/pypi/v/opencafe.svg
    :target: https://pypi.python.org/pypi/opencafe

.. image:: https://travis-ci.org/CafeHub/opencafe.svg?branch=master
    :target: https://travis-ci.org/CafeHub/opencafe

When writing automated test sutes, there are some things that should
"just work". Problems like managing test data, logging, and results are
things that shouldn't have to be re-invented for every test project you work
on. OpenCafe aims to address that problem by providing solutions for the
commonly occuring challenges in the development and operation of functional
and end-to-end test suites.

Capabilities
------------

- Common sense conventions for test data and log management
- Per test run and per test logs and results
- Reference drivers for performing non-UI testing including HTTP, SSH,
  and WinRM
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

Post-install, the ``cafe-config`` cli tool will become available. It is used
for installing plugins and initializing OpenCafe's default directory
structure.

Initialization
^^^^^^^^^^^^^^
Running the ``cafe-config init`` command will create the default OpenCafe
directory structure in a directory named ``.opencafe``. This directory will
be located in either the current user's home directory or in the root of the
virtual environment you currently have active. This directory contains the
``/configs`` directory which stores configuration data, the ``/logs``
directory which holds the logging output from all tests executed, and the
``engine.config`` file, which sets the base test repository and allows the
user to override the default directories for logging and configuration.

Plugins
^^^^^^^

OpenCafe uses a plugin system to allow for core functionality to be extended
or for additional capabilities to be added. Plugins are essentially Python
packages, which may have their own Python dependencies. This design allows
implementors to only install dependencies for the functionality that they
intend to use, as the additional dependencies are installed at the same time
as the plugin.

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
