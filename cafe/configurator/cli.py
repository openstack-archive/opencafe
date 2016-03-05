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
from cafe.configurator.managers import (
    EngineDirectoryManager, EngineConfigManager, EnginePluginManager)


def engine_config_init(namespace):
    print vars(namespace)
    if hasattr(namespace, "init_install") and not namespace.init_install:
        return
    print("=================================")
    print("* Initializing Engine Install")
    EngineDirectoryManager.build_engine_directories()
    EngineConfigManager.build_engine_config()
    print("=================================")


def add_plugins_subparser(subparsers):
    def install_plugin(namespace):
        print("=================================")
        print("* Installing Plugins")
        EnginePluginManager.install_plugins(namespace.plugins)
        print("=================================")

    def list_plugins(namespace):
        print("=================================")
        print("* Available Plugins")
        EnginePluginManager.list_plugins()
        print("=================================")

    subparser_plugins = subparsers.add_parser('plugins')
    plugin_args = subparser_plugins.add_subparsers(dest='subcommand')

    plugins_list_parser = plugin_args.add_parser('list')
    plugins_list_parser.set_defaults(func=list_plugins)

    plugins_install_parser = plugin_args.add_parser('install')
    plugins_install_parser.set_defaults(func=install_plugin)
    plugins_install_parser.add_argument("plugins", nargs="*", default=[])


def add_engine_subparser(subparsers):
    # Engine configuration subparser
    subparsers.add_parser('engine')
    # engine_subparsers = engine_parser.add_subparsers(dest='subcommand')


class ConfiguratorCLI(object):
    """CLI for future engine management and configuration
    options."""

    @classmethod
    def run(cls):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")

        # Plugin argument subparser
        add_plugins_subparser(subparsers)

        # add engine subparser
        add_engine_subparser(subparsers)

        # add init command
        subparser_init = subparsers.add_parser('init')
        subparser_init.set_defaults(func=engine_config_init)

        # parse args and trigger actions
        args = parser.parse_args()

        try:
            args.func(args)
        except AttributeError:
            return args


def entry_point():
    cli = ConfiguratorCLI()
    cli.run()
