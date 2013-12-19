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
from cafe.configurator.managers import (
    EngineDirectoryManager, EngineConfigManager, EnginePluginManager)


class EngineActions(object):

    class InitInstall(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print "================================="
            print "* Initializing Engine Install"
            EngineDirectoryManager.build_engine_directories()
            EngineConfigManager.build_engine_config()
            print "================================="

    class InstallPluginCache(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print "================================="
            print "* Installing Plugin Cache"
            EnginePluginManager.populate_plugin_cache(values)
            print "================================="

    class InstallPlugin(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print "================================="
            print "* Installing Plugin {0}".format(values)
            EnginePluginManager.install_plugin(values)
            print "================================="


class ConfiguratorCLI(object):
    """CLI for future engine management and configuration options."""

    @classmethod
    def run(cls):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")

        #Engine configuration subparser
        subparser_engine_config = subparsers.add_parser('engine')
        subparser_engine_config.add_argument(
            '--init-install', action=EngineActions.InitInstall, nargs=0)
        subparser_engine_config.add_argument(
            '--install-plugin-cache', action=EngineActions.InstallPluginCache,
            type=str)
        subparser_engine_config.add_argument(
            '--install-plugin', action=EngineActions.InstallPlugin,
            type=str)

        return parser.parse_args()


def entry_point():
    cli = ConfiguratorCLI()
    cli.run()
