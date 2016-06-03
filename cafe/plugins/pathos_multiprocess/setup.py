# Copyright 2015 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""
This plugin installs the pathos multiprocess package.
Since pathos multiprocess is still in Beta, this plugin is considered
experimental.

If installed, the cafe unittest runners will use multiprocess instead of
python's default multiprocessing library.
"""
from setuptools import setup

setup(
    name='cafe_pathos_multiprocess_plugin',
    version='0.0.1',
    description='The Common Automation Framework Engine',
    author='Rackspace Cloud QE',
    author_email='cloud-cafe@lists.rackspace.com',
    url='http://rackspace.com',
    install_requires=['multiprocess'])
