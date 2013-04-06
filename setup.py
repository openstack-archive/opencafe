"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import os
import sys
import cafe
import platform

# These imports are only possible on Linux/OSX
if platform.system().lower() != 'windows':
    import pwd
    import grp

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requires = open('pip-requires').readlines()

''' @todo: entry point should be read from a configuration and not hard coded 
           to the unittest driver's runner '''
setup(
    name='cafe',
    version=cafe.__version__,
    description='The Common Automation Framework Engine',
    long_description='{0}\n\n{1}'.format(
        open('README.md').read(),
        open('HISTORY.md').read()),
    author='Rackspace Cloud QE',
    author_email='cloud-cafe@lists.rackspace.com',
    url='http://rackspace.com',
    packages=find_packages(exclude=[]),
    package_data={'': ['LICENSE', 'NOTICE']},
    package_dir={'cafe': 'cafe'},
    include_package_data=True,
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    #https://the-hitchhikers-guide-to-packaging.readthedocs.org/en/latest/specification.html
    classifiers=(
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points = {
        'console_scripts':
        ['cafe-runner = cafe.drivers.unittest.runner:'
         'entry_point']}
)

''' @todo: need to clean this up or do it with puppet/chef '''
# Default Config Options
root_dir = "{0}/.cloudcafe".format(os.path.expanduser("~"))
log_dir = "{0}/logs".format(root_dir)
data_dir = "{0}/data".format(root_dir)
temp_dir = "{0}/temp".format(root_dir)
config_dir = "{0}/configs".format(root_dir)
use_verbose_logging = "False"

# Copy over the default configurations
if(os.path.exists("~install")):
    os.remove("~install")
    # Report
    print('\n'.join(["\t\t     ( (",
                     "\t\t        ) )",
                     "\t\t     .........    ",
                     "\t\t     |       |___ ",
                     "\t\t     |       |_  |",
                     "\t\t     |  :-)  |_| |",
                     "\t\t     |       |___|",
                     "\t\t     |_______|",
                     "\t\t === CAFE Core ==="]))
    print("========================================================")
    print("CAFE Core installed with the options:")
    print("Config File: {0}/engine.config".format(config_dir))
    print("log_directory={0}".format(log_dir))
    print("data_directory={0}".format(data_dir))
    print("temp_directory={0}".format(temp_dir))
    print("use_verbose_logging={0}".format(use_verbose_logging))
    print("========================================================")
else:
    # State file
    temp = open("~install", "w")
    temp.close()

    # Build Default directories
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    # Get uid and gid of the current user to set permissions (Linux/OSX only)
    if platform.system().lower() != 'windows':
        sudo_user = os.getenv("SUDO_USER")
        uid = pwd.getpwnam(sudo_user).pw_uid
        gid = pwd.getpwnam(sudo_user).pw_gid

        os.chown(root_dir, uid, gid)
        os.chown(log_dir, uid, gid)
        os.chown(data_dir, uid, gid)
        os.chown(temp_dir, uid, gid)
        os.chown(config_dir, uid, gid)
    
    # Build the default configuration file
    if(os.path.exists("{0}/engine.config".format(config_dir)) == False):
        config = open("{0}/engine.config".format(config_dir), "w")
        config.write("[CCTNG_ENGINE]\n")
        config.write("log_directory={0}\n".format(log_dir))
        config.write("data_directory={0}\n".format(data_dir))
        config.write("temp_directory={0}\n".format(temp_dir))
        config.write("use_verbose_logging={0}\n".format(use_verbose_logging))
        config.close()

        if platform.system().lower() != 'windows':
            os.chown("{0}/engine.config".format(config_dir), uid, gid)

