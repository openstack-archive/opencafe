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
from cafe.drivers.base import print_mug, parse_runner_args


def entry_point():

    # Setup and parse arguments
    arg_parser = argparse.ArgumentParser(prog='specter-runner')
    args = parse_runner_args(arg_parser)

    config = str(args.config[0]) + '.config'
    product = str(args.product[0])
    cmd_opts = args.cmd_opts

    test_env_manager = TestEnvManager(product, config)
    test_env_manager.finalize()

    test_path = os.path.join(
        test_env_manager.test_repo_path, product)

    call_args = ['specter', '--search', test_path, '--no-art']

    if len(cmd_opts) > 0:
        call_args.extend(cmd_opts)

    print_mug(name='Specter', brewing_from=test_path)

    subprocess.call(call_args)
    exit(0)


if __name__ == '__main__':
    entry_point()
