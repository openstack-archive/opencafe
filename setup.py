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

import os
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# Establish a consistent base directory relative to the setup.py file
os.chdir(os.path.abspath(os.path.dirname(__file__)))


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

# Package the plugin cache as package data
plugins = []
dir_path = os.path.join('cafe', 'plugins')
for dirpath, directories, filenames in os.walk(dir_path):
    dirpath = dirpath.lstrip('cafe{0}'.format(os.path.sep))
    for f in filenames:
        if f.endswith('.pyc'):
            continue
        target_file = os.path.join(dirpath, f)
        plugins.append(target_file)

setup(
    name='opencafe',
    version='0.2.6',
    description='The Common Automation Framework Engine',
    long_description='{0}'.format(open('README.rst').read()),
    author='CafeHub',
    author_email='cloud-cafe@lists.rackspace.com',
    url='http://opencafe.readthedocs.org',
    install_requires=['six'],
    packages=find_packages(exclude=('tests*', 'docs')),
    package_data={'cafe': plugins},
    license=open('LICENSE').read(),
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),
    entry_points={
        'console_scripts':
        ['cafe-runner = cafe.drivers.unittest.runner:entry_point',
         'cafe-parallel = cafe.drivers.unittest.runner_parallel:entry_point',
         'behave-runner = cafe.drivers.behave.runner:entry_point',
         'vows-runner = cafe.drivers.pyvows.runner:entry_point',
         'specter-runner = cafe.drivers.specter.runner:entry_point',
         'cafe-config = cafe.configurator.cli:entry_point']},
    tests_require=['tox'],
    cmdclass={'test': Tox})
