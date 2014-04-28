Open CAFE Core
----------------------------


.. code-block::

       ( (
          ) )
        .........
        |       |___
        |       |_  |
        |  :-)  |_| |
        |       |___|
        |_______|
    === CAFE Core ===


The Open Common Automation Framework Engine is the core engine/driver used to build an automated testing framework. It is designed to be used as the
base engine for building an automated framework for API and non-UI resource testing. It is designed to support functional, integration and
reliability testing. The engine is **NOT** designed to support performance or load testing.

CAFE core provides a model, a pattern and assorted common tools for building automated tests. It provides its own light weight unittest based
runner, however, it is designed to be modular. It can be extended to support most test case front ends/runners (nose, pytest, lettuce, testr, etc...)
through driver plug-ins.

Supported Operating Systems
---------------------------
Open CAFE Core has been developed primarily in Linux and MAC environments, however, it supports installation and
execution on Windows

Installation
------------
Open CAFE Core can be [installed with pip](https://pypi.python.org/pypi/pip) from the git repository after it is cloned to a local machine.

* Clone this repository to your local machine
* CD to the root directory in your cloned repository.
* Run "pip install . --upgrade" and pip will auto install all dependencies.

After the CAFE Core is installed you will have command line access to the default unittest runner, the cafe-runner. (See cafe-runner --help for more info)

Remember, open CAFE is just the core driver/engine. You have to build an implementation and test repository that use it!

Configuration
--------------
Open CAFE works out of the box with the cafe-runner (cafe.drivers.unittest). CAFE will auto-generate a base engine.config during installation. This
base configuration will be installed to: <USER_HOME>/.cloudcafe/configs/engine.config

If you wish to modify default installation values you can update the engine.config file after CAFE installation. Keep in mind that the Engine will
over-write this file on installation/upgrade.

Terminology
-----------
Following are some notes on Open CAFE lingo and concepts.

* Implementation
    Although the engine can serve as a basic framework for testing, it's meant to be used as the base for the implementation of a product-specific testing framework.

* Product
    Anything that's being tested by an implementation of Open CAFE Core. If you would like to see a refernce implementation, there is an [Open Source implementation](https://github.com/stackforge) based on [OpenStack](http://http://www.openstack.org/)


* Client / Client Method
    A **client** is an "at-least-one"-to-"at-most-one" mapping of a product's functionality to a collection of client methods.  Using a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer) as an example, a client that represents that API in CAFE will contain at least one (but possibly more) method(s) for every function exposed by that API.  Should a call in the API prove to be too difficult or cumbersome to define via a single **client method**, then multiple client methods can be defined such that as a whole they represent the complete set of that API call's functionality. A **client method** should never be a superset of more than one call's functionality.

* Behavior
    A **behavior** is a many-to-many mapping of client methods to business logic, functioning as compound methods.  An example behavior might be to POST content, perform a GET to verify the POST, and then return the verified data

* Model
    A **model** can be many things, but generally is a class that describes a specific data object. An example may be a collection of logic for converting an XML or JSON response into a data object, so that a single consumer can be written to consume the model.

* Provider
    This is meant to be a convenience facade that performs configuration of clients and behaviors to provide configuration-based default combinations of different clients and behaviors.

Basic CAFE Package Anatomy
--------------------------
Below is a short description of the top level CAFE Packages.

* cafe
    This is the root package. The wellspring from which the CAFE flows...

* common
    Contains modules common the entire engine. This is the primary namespace for tools, data generators, common reporting classes, etc...

* engine
    Contains all the base implementations of clients, behaviors, models to be used by a CAFE implementation. It also contains supported generic clients, behaviors and models. For instance, the engine.clients.remote_instance clients are meant to be used directly by an implementation.

* drivers
    The end result of CAFE is to build an implementation to talk to a particular product or products, and a repository of automated test cases. The drivers package is specifically for building CAFE support for various Python based test runners. There is a default unittest based driver implemented which heavily extends the basic unittest functionality. Driver plug-ins can easily be constructed to add CAFE support for most of the popular ones already available (nose, pytest, lettuce, testr, etc...) or even for 100% custom test case drivers if desired.

* resources
    Contains all modules that reference external resources to OpenCAFE. One example of an external resource is a Launchpad tracker.
