=====================================
Setting up a Development Environment
=====================================

OpenCAFE strongly recommends the use of Python virtual environments for development.

While not required, if you wish to manage your Python versions as well as virtual environments, we suggest the use of pyenv. Instructions on installing pyenv can be found here: :ref:`installing_pyenv`


Building your virtual environment
==================================
If you wish to run OpenCAFE in a virtual environment, then you will need to `install virtualenv <http://www.virtualenv.org/en/latest/virtualenv.html#installation>`_

For easier management of your virtual environments, it is recommended that you install virtualenvwrapper as well.

.. code-block:: bash

    sudo pip install virtualenvwrapper


Creating virtualenv and installing OpenCAFE
---------------------------------------------

.. code-block:: bash

    # Requires virtualenv and virtualenvwrapper to be installed
    mkvirtualenv OpenCAFE

    # Clone OpenCAFE Repo
    git clone git@github.com:stackforge/opencafe.git

    # Change directory into the newly cloned repository
    cd opencafe

    # Install OpenCAFE into your virtualenv
    pip install . --upgrade


Information regarding the operation of your virtual environment can be found here: :ref:`working_with_virtualenv`
