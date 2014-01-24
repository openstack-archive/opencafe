=====================================
Setting up a Development Environment
=====================================

OpenCAFE strongly recommends the use of Python virtual environments for development. As a way to manage your Python versions
and virtual environments, we suggest the use of pyenv its virtualenvwrapper plugin.


Installing pyenv
=================

The official installation guide is available here `pyenv on github <https://github.com/yyuu/pyenv#installation>`_. The official guide
includes instructions for Mac OS X as well.

Installing pyenv on Ubuntu:

.. code-block:: bash

    sudo apt-get install git python-pip make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev
    sudo pip install virtualenvwrapper

    git clone https://github.com/yyuu/pyenv.git ~/.pyenv
    git clone https://github.com/yyuu/pyenv-virtualenvwrapper.git ~/.pyenv/plugins/pyenv-virtualenvwrapper

    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init -)"' >> ~/.bashrc
    echo 'pyenv virtualenvwrapper' >> ~/.bashrc

    exec $SHELL

Installing a fresh version of Python
=====================================

Now that pyenv and the virtualenvwrapper plugin is installed. We need to download and install a version of python. In this case, we're going to install Python 2.7.6.

.. code-block:: bash

    # Install
    pyenv install 2.7.6

    # Set 2.7.6 as your shell default
    pyenv global 2.7.6

Working with virtual environments
===============================================
There are four primary commands that are used to manage your virtual environments.

Create
-------
.. code-block:: bash

    # Allows for you to new create a virtual environment based
    # on your current python(s) versions set my pyenv.
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

