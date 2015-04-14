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

import argparse
import os
import subprocess
from cafe.configurator.managers import TestEnvManager


def entry_point():

    # Set up arguments
    argparser = argparse.ArgumentParser(prog='vows-runner')

    argparser.add_argument(
        "product",
        nargs=1,
        metavar="<product>",
        help="Product name")

    argparser.add_argument(
        "config",
        nargs=1,
        metavar="<config_file>",
        help="Product test config")

    argparser.add_argument(
        dest='vows_opts',
        nargs=argparse.REMAINDER,
        metavar="<vows_opts>",
        help="Options to pass to PyVows")

    args = argparser.parse_args()
    config = str(args.config[0])
    product = str(args.product[0])
    vows_opts = args.vows_opts

    test_env_manager = TestEnvManager(product, config)
    test_env_manager.finalize()

    product_root_test_path = os.path.join(
        test_env_manager.test_repo_path, product)

    # Attempts to use first positional argument after product config as a
    # sub-path to the test repo path. If not a sub-path, raise exception.
    if vows_opts and not vows_opts[0].startswith('-'):
        user_provided_path = vows_opts[0]
        attempted_sub_path = os.path.join(
            product_root_test_path,
            user_provided_path.lstrip(os.path.sep))

        if os.path.exists(attempted_sub_path):
            vows_opts[0] = attempted_sub_path
        else:
            raise Exception(
                "{directory} is not a sub-path in the {repo} repo.".format(
                    directory=vows_opts[0],
                    repo=test_env_manager.test_repo_package))
    else:
        vows_opts.insert(0, product_root_test_path)

    print_mug(vows_opts[0])
    vows_opts.insert(0, "pyvows")

    subprocess.call(vows_opts)

    exit(0)


def print_mug(base_dir):
    brew = "Brewing from {0}".format(base_dir)

    mug0 = "      ( ("
    mug1 = "       ) )"
    mug2 = "    ........."
    mug3 = "    |       |___"
    mug4 = "    |       |_  |"
    mug5 = "    |  :-)  |_| |"
    mug6 = "    |       |___|"
    mug7 = "    |_______|"
    mug8 = "=== CAFE Vows Runner ==="

    print("\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}".format(
        mug0,
        mug1,
        mug2,
        mug3,
        mug4,
        mug5,
        mug6,
        mug7,
        mug8))

    print("-" * len(brew))
    print(brew)
    print("-" * len(brew))

if __name__ == '__main__':
    entry_point()
