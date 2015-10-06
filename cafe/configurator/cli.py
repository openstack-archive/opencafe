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


class EngineActions(object):

    class Init(object):
        def __init__(self, args):
            print("=================================")
            print("* Initializing Engine Install")
            EngineDirectoryManager.build_engine_directories()
            EngineConfigManager.build_engine_config()
            print("=================================")

    class InitInstall(argparse.Action):
        def __call__(
                self, parser, namespace, values,
                option_string=None):
            print("=================================")
            print("* Initializing Engine Install")
            EngineDirectoryManager.build_engine_directories()
            EngineConfigManager.build_engine_config()
            print("=================================")


class PluginActions(object):

    class InstallPlugin(argparse.Action):
        def __call__(
                self, parser, namespace, values,
                option_string=None):
            print("=================================")
            print("* Installing Plugins")
            EnginePluginManager.install_plugins(values)
            print("=================================")

    class ListPlugins(argparse.Action):
        def __call__(
                self, parser, namespace, values,
                option_string=None):
            print("=================================")
            print("* Available Plugins")
            EnginePluginManager.list_plugins()
            print("=================================")


class ConfiguratorCLI(object):
    """CLI for future engine management and configuration
    options."""

    @classmethod
    def run(cls):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")

        # Engine configuration subparser
        subparser_engine_config = subparsers.add_parser(
            'engine')
        subparser_engine_config.add_argument(
            '--init-install',
            action=EngineActions.InitInstall,
            nargs=0,
            help="Deprecated. Please use 'cafe-config init' instead.")

        subparser_init = subparsers.add_parser('init')
        subparser_init.set_defaults(func=EngineActions.Init)

        # Plugin argument subparser
        subparser_plugins = subparsers.add_parser('plugins')
        plugin_args = subparser_plugins.add_subparsers(
            dest='plugin_args')

        plugins_list_parser = plugin_args.add_parser('list')
        plugins_list_parser.add_argument(
            'list_plugins',
            action=PluginActions.ListPlugins,
            nargs=0)

        plugins_install_parser = plugin_args.add_parser('install')
        plugins_install_parser.add_argument(
            'plugin-name',
            action=PluginActions.InstallPlugin,
            type=str,
            nargs='*')

        # parse args and trigger actions
        args = parser.parse_args()

        try:
            args.func(args)
        except AttributeError:
            return args


def entry_point():
    cli = ConfiguratorCLI()
    cli.run()
