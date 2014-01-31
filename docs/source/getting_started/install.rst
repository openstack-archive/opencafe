====================
Installing OpenCAFE
====================

Currently OpenCAFE is not available on PyPI *(coming soon)*. As a result, you will need to install via pip through either cloning the repository or using a release tarball.

Installing from the repository
===============================

The preferred method of installing OpenCAFE is using pip.

.. code-block:: bash

    # Clone Repository
    git clone git@github.com:CafeHub/opencafe.git

    # Change current directory
    cd opencafe

    # Install OpenCAFE
    pip install . --upgrade


Installing Plugins
====================

When you just install OpenCAFE, you only install the base framework. All other functionality is packaged into plugins.

Install
---------
To install a plugin use the following command

.. code-block:: bash
    
    # Installing the mongo plugin
    cafe-config plugins install mongo

List
---------
Retrieves a list of all plugins available to install

.. code-block:: bash
    
    cafe-config plugins list
