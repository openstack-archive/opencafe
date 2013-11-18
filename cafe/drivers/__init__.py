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
import argparse


def parse_runner_args(arg_parser):
    """ Generic CAFE args for external runners"""

    arg_parser.add_argument(
        "product",
        nargs=1,
        metavar="<product>",
        help="Product name")

    arg_parser.add_argument(
        "config",
        nargs=1,
        metavar="<config_file>",
        help="Product test config")

    arg_parser.add_argument(
        dest='cmd_opts',
        nargs=argparse.REMAINDER,
        metavar="<cmd_opts>",
        help="Options to pass to the test runner")

    return arg_parser.parse_args()


def print_mug(name, brewing_from):
    """ Generic CAFE mug """
    border = '-' * 40
    mug = """
    Brewing from {path}
              ( (
               ) )
            .........
            |       |___
            |       |_  |
            |  :-)  |_| |
            |       |___|
            |_______|
    === CAFE {name} Runner ===""".format(
        path=brewing_from, name=name)

    print border
    print mug
    print border
