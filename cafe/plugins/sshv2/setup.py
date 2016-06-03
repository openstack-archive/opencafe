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
"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
"""
from setuptools import setup, find_packages

setup(
    name='cafe_sshv2_plugin',
    version='0.0.1',
    description='Paramiko based plugin for OpenCAFE',
    long_description='{0}'.format(open('README.rst').read()),
    author='Rackspace Cloud QE',
    author_email='cloud-cafe@lists.rackspace.com',
    url='http://rackspace.com',
    packages=find_packages(),
    namespace_packages=['cafe'],
    install_requires=['paramiko<2', 'pysocks'],
    zip_safe=False)
