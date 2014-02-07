.. _repository: https://github.com/CafeHub/opencafe

====================================
Welcome to OpenCAFE's documentation!
====================================

What is OpenCAFE
==================

The Common Automation Framework Engine (CAFE) is the core engine/driver used to build an automated testing framework. It is designed to be used as the base engine for building an automated framework for API and non-UI resource testing. It is designed to support functional, integration and reliability testing. The engine is NOT designed to support performance or load testing.

CAFE core provides models, patterns, and assorted common tools for building automated tests. It provides its own light weight unittest based runner, however, it is designed to be modular. It can be extended to support most test case front ends/runners (nose, pytest, lettuce, testr, etc...) through driver plug-ins.


Relevant Links
================
* GitHub: `Repository`_
* CI: *Coming soon*
* Coverage: *Coming soon*


Contents
============
.. toctree::
   :maxdepth: 2

   getting_started/index
   contributing/index
   architecture/index
   plugin_dev/index
   faq/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`