"""
Copyright 2013-2014 Rackspace

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

import sys
from subprocess import call
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.test import test as TestCommand


# Post-install engine configuration
def _post_install(dir):
    call(['cafe-config', 'engine', '--init-install'])
    call(['cafe-config', 'plugins', 'add', 'plugins'])
    call(['cafe-config', 'plugins', 'install', 'http'])
    print(
        """
         ( (
            ) )
        ........
        |      |___
        |      |_  |
        |  :-) |_| |
        |      |___|
        |______|
    === OpenCAFE ===

    -----------------------------------------------------------------
    If you wish to install additional plugins, you can do so through
    the cafe-config tool.

    Example:
    $ cafe-config plugins install mongo
    -----------------------------------------------------------------
    """)

# Reading Requires
requires = open('pip-requires').readlines()

# Add additional requires for Python 2.6 support
if sys.version_info < (2, 7):
    oldpy_requires = ['argparse>=1.2.1', 'unittest2>=0.5.1']
    requires.extend(oldpy_requires)


# cmdclass hook allows setup to make post install call
class install(_install):
    def run(self):
        _install.run(self)
        self.execute(
            _post_install, (self.install_lib,),
            msg="\nRunning post install tasks...")


# tox integration
class Tox(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

# Normal setup stuff
setup(
    name='opencafe',
    version='0.2.0',
    description='The Common Automation Framework Engine',
    long_description='{0}'.format(open('README.rst').read()),
    author='CafeHub',
    author_email='cloud-cafe@lists.rackspace.com',
    url='http://opencafe.readthedocs.org',
    packages=find_packages(),
    namespace_packages=['cafe'],
    install_requires=requires,
    license=open('LICENSE').read(),
    zip_safe=False,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points = {
        'console_scripts':
        ['cafe-runner = cafe.drivers.unittest.runner:entry_point',
         'behave-runner = cafe.drivers.behave.runner:entry_point',
         'vows-runner = cafe.drivers.pyvows.runner:entry_point',
         'specter-runner = cafe.drivers.specter.runner:entry_point',
         'cafe-config = cafe.configurator.cli:entry_point']},
    tests_require=['tox'],
    cmdclass={
        'install': install,
        'test': Tox})
