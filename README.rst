Open CAFE Core
==============

::

       ( (
          ) )
        .........
        |       |___
        |       |_  |
        |  :-)  |_| |
        |       |___|
        |_______|
    === CAFE Core ===

OpenCAFE, the Open Common Automation Framework Engine, is designed to be used
as the base for building an automated testing framework for API and other
(non-UI) testing.
It is designed to support all kinds of testing methodologies, such as unit,
functional and integration testing, using a model-based approach.
Although the engine is not designed with performance or load testing in mind,
as it prioritizes repeatability and (verbose) logging over performance, it can
be used to that end.


Installation
============
Source code is available at https://github.com/openstack/opencafe

Supported Operating Systems
---------------------------
Open CAFE Core has been developed primarily on and for Linux, but supports
installation and execution on BSD and other \*nix's, as well as OS X and
modern Windows.  It can be installed from pypi via pip or from source.

**It is recommended that you install OpenCAFE in a python virtualenv.**

From pypi via pip

::

    $ pip install opencafe

From source

::

    $ git clone https://github.com/openstack/opencafe.git
    $ cd opencafe
    $ python setup.py install

Post-install Configuration
==========================
Post-install, the ``cafe-config`` cli tool will become available.
It is used for installing
plugins and initializing the engine's default ``.opencafe`` directory.

Initialization
--------------
OpenCAFE uses a set of default locations for logging, storing
test configurations, test data, statistics, and the like; all of which are
set in, and read from, the ``engine.config`` file (in order to make it easy
for the end user to override the default behavior).  The ``engine.config``
file, and the directories it references, can be created on demand by running:

``cafe-config init``

This will create a directory named ``.opencafe`` in the user's home
directory, or in the case of a python virtualenv, in the virtualenv root
folder.

Installing Plugins
------------------
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

Package Structure Overview
==========================
``cafe.common.reporting``
-------------------------
Provides tools for logging and reporting.
This namespace should be used by plugins to add logging and reporting features.

``cafe.configurator``
---------------------
Used by the ``cafe-config`` cli tool for setting up new installations of opencafe.

``cafe.drivers``
----------------
Houses various test runner wrappers and supporting tools.
This namespace should be used by plugins to add new test runner support.

``cafe.engine``
---------------
Includes the base classes that OpenCAFE implementations will use to create behaviors, configs, clients and models.
This namespace should be used by plugins to add new clients.

``cafe.resources``
------------------
Deprecated.
Historically contained all modules that reference external resources to OpenCAFE. Currently acts only as a namespace for backward compatability with some plugins.

Terminology
-----------
Following are some notes on Open CAFE lingo and concepts.

* Implementation
    Although the engine can serve as a basic framework for testing, it's meant to be used as the base for the implementation of a product-specific testing framework.

* Product
    Anything that's being tested by an implementation of Open CAFE Core. If you would like to see a reference implementation, there is an `Open Source implementation <https://github.com/stackforge>`_ based on `OpenStack <http://www.openstack.org/>`_.

* Client / Client Method
    A **client** is an "at-least-one"-to-"at-most-one" mapping of a product's functionality to a collection of client methods.  Using a `REST API <https://en.wikipedia.org/wiki/Representational_state_transfer>`_ as an example, a client that represents that API in CAFE will contain at least one (but possibly more) method(s) for every function exposed by that API.  Should a call in the API prove to be too difficult or cumbersome to define via a single **client method**, then multiple client methods can be defined such that as a whole they represent the complete set of that API call's functionality. A **client method** should never be a superset of more than one call's functionality.

* Behavior
    A **behavior** is a many-to-many mapping of client methods to business logic, functioning as compound methods.  An example behavior might be to POST content, perform a GET to verify the POST, and then return the verified data

* Model
    A **model** can be many things, but generally is a class that describes a specific data object. An example may be a collection of logic for converting an XML or JSON response into a data object, so that a single consumer can be written to consume the model.

* Provider
    This is meant to be a convenience facade that performs configuration of clients and behaviors to provide configuration-based default combinations of different clients and behaviors.
