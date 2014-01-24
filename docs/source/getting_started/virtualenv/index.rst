.. _working_with_virtualenv:

===================================
Working with virtual environments
===================================
For a complete guide on using virtualenv, please refer to the `virtualenv <http://www.virtualenv.org/>`_ and `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org>`_ documentation


Using virtualenvwrapper
=========================
There are four primary commands that are used to manage your virtual environments with virtualenvwrapper.

Create
-------
When you create a virtualenv with virtualenvwrapper it creates a virtual environment within the $HOME/.virtualenvs folder.

.. code-block:: bash

    # Allows for you to new create a virtual environment based
    # on your current python version(s)
    mkvirtualenv CloudCAFE


Activate Environment
----------------------
.. code-block:: bash

    # Activates a virtual environment within your current shell.
    workon CloudCAFE


Deactivate Environment
----------------------
.. code-block:: bash

    # Deactivates a virtual environment within your current shell.
    deactivate


Remove Environment
----------------------
.. code-block:: bash

    # Deletes a virtual environment from your system.
    rmvirtualenv CloudCAFE
    