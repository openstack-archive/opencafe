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
import datetime
import imp
import os
import platform
import sys
import textwrap
from ConfigParser import SafeConfigParser

if not platform.system().lower() == 'windows':
    import pwd


class EnvironmentManager(object):
    USING_WINDOWS = (platform.system().lower() == 'windows')
    USING_VIRTUALENV = hasattr(sys, 'real_prefix')

    @classmethod
    def get_current_user(cls):
        user = None

        if not cls.USING_WINDOWS:
            user = os.getenv("USER")

            if not cls.USING_VIRTUALENV:
                user = os.getenv("SUDO_USER") or user

        return user

    @classmethod
    def get_current_user_home_path(cls):
        if EnvironmentManager.USING_VIRTUALENV:
            return sys.prefix
        else:
            return os.path.expanduser("~{0}".format(cls.get_current_user()))

    @classmethod
    def get_current_user_ids(cls):
        if not EnvironmentManager.USING_WINDOWS:
            working_user = cls.get_current_user()
            uid = pwd.getpwnam(working_user).pw_uid
            gid = pwd.getpwnam(working_user).pw_gid
            return uid, gid


class TestEnvManager(object):

    def __init__(
            self, product_name, test_config_file_name,
            engine_config_path=None):

        engine_config_path = engine_config_path or \
            EngineConfigManager.ENGINE_CONFIG_PATH

        self.engine_config = EngineConfigManager.read_config_file(
            engine_config_path)

        self.product_name = product_name
        self.test_config_file_name = test_config_file_name

    @classmethod
    def set_engine_config_path(cls, engine_config_path=None):
        """
        Returns an engine config interface object for the engine.config file
        found at engine_config_path if provided, or the default location
        in .opencafe
        """
        os.environ["OPENCAFE_ENGINE_CONFIG_FILE"] = engine_config_path or \
            EngineConfigManager.ENGINE_CONFIG_PATH

    @classmethod
    def get_engine_config_interface(cls, engine_config_path=None):
        from cafe.engine.config import EngineConfig
        return EngineConfig(
            engine_config_path or EngineConfigManager.ENGINE_CONFIG_PATH)

    @classmethod
    def set_test_repo_path(cls, test_repo_path):
        os.environ["TEST_REPO_ROOT_DIR"] = test_repo_path

    @classmethod
    def set_test_repo_package_path(
            cls, test_repo_package=None, engine_config_path=None):
        """
        Sets the test repo path based on the location of the installed
        test repo package.  Uses the engine config default package if no
        package is provided, from either the default engine.config location, or
        the one provided in engine_config_path.
        Returns the path to the test repo package root directory on success.
        """
        if not test_repo_package:
            engine_config = cls.get_engine_config_interface(engine_config_path)
            test_repo_package = engine_config.default_test_repo

        module_info = None
        try:
            module_info = imp.find_module(test_repo_package)
        except ImportError as exception:
            print "Cannot find test repo '{0}'".format(test_repo_package)
            raise exception

        test_repo_path = module_info[1]
        os.environ["TEST_REPO_ROOT_DIR"] = test_repo_path
        return test_repo_path

    def set_test_log_dir(self, log_dir_path=None, create=True):
        """
        Creates a directory for the test to log to, and sets the
        "TEST_LOG_PATH" os environment variable.
        The default root_log_dir is .opencafe/logs, but is configurable
        in the engine.config file.
        The default path is:
        <root_log_dir>/<product_name>/<config_file_name>/<timestamp>
        """
        log_dir_name = str(datetime.now()).replace(" ", "_").replace(":", "_")
        log_dir_path = log_dir_path or os.path.join(
            self.engine_config.get('OPENCAFE_ENGINE', 'logging_directory'),
            self.product_name, self.test_config_file_name, log_dir_name)

        if not os.path.exists(log_dir_path) and create:
            os.makedirs(log_dir_path)

        os.environ["CAFE_LOG_PATH"] = log_dir_path

    def set_test_stats_log_dir(self, stats_log_dir_path=None, create=True):
        """
        Creates a directory for the test to log to, and sets the
        "TEST_LOG_PATH" os environment variable.
        The default root_log_dir is .opencafe/logs, but is configurable
        in the engine.config file.
        The default path is:
        <root_log_dir>/<product_name>/<config_file_name>/<timestamp>
        """
        stats_log_dir_name = 'statistics'
        stats_log_dir_path = stats_log_dir_path or os.path.join(
            self.engine_config.get('OPENCAFE_ENGINE', 'logging_directory'),
            self.product_name, self.test_config_file_name, stats_log_dir_name)

        if not os.path.exists(stats_log_dir_path) and create:
            os.makedirs(stats_log_dir_path)

        os.environ["CAFE_STATS_LOG_PATH"] = stats_log_dir_path

    def set_test_config_file(self, config_file_path=None):
        config_file_path = config_file_path or os.path.join(
            self.engine_config.get('OPENCAFE_ENGINE', 'config_directory'),
            self.product_name, self.test_config_file_name)

        os.environ["CAFE_CONFIG_FILE"] = config_file_path

    def set_test_data_directory(self, test_data_directory=None):
        test_data_directory = test_data_directory or os.path.join(
            self.engine_config.get('OPENCAFE_ENGINE', 'data_directory'),
            self.product_name, self.test_config_file_name)

        os.environ["CAFE_DATA_DIRECTORY"] = test_data_directory

    def set_test_logging_verbosity(self, logging_verbosity=None):
        """Currently supports STANDARD and VERBOSE.
        TODO: Implement 'OFF' option that adds null handlers to all loggers

        """
        logging_verbosity = logging_verbosity or self.engine_config.get(
            'OPENCAFE_ENGINE', 'logging_verbosity')

        os.environ["CAFE_LOGGING_VERBOSITY"] = logging_verbosity

    def set_test_master_log_file_name(self, master_log_file_name=None):
        os.environ["CAFE_MASTER_LOG_FILE_NAME"] = master_log_file_name


class _FlatNamespace(dict):
    """
    Converts the top-level keys of this dictionary into a namespace.
    Raises exception if any top-level keys collide with internal attributes.
    """
    def __init__(self, **kwargs):
        super(_FlatNamespace, self).__init__(**kwargs)
        collisions = set(kwargs) & set(dir(self))
        if bool(collisions):
            raise Exception(
                "Cannot set attribute {0}.  FlatNamespace cannot contain any "
                "keys that collide with internal attribute names.".format(
                    [c for c in collisions]))

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                "FlatNamespace has no attribute '{0}'".format(name))


class EngineDirectoryManager(object):
    wrapper = textwrap.TextWrapper(
        initial_indent="* ", subsequent_indent="  ", break_long_words=False)

    #Old .cloudcafe directories
    _OLD_ROOT_DIR = os.path.join(
        EnvironmentManager.get_current_user_home_path(), ".cloudcafe")
    _OLD_CAFE_DIRS = _FlatNamespace(
        LOG_DIR="{0}/logs".format(_OLD_ROOT_DIR),
        DATA_DIR="{0}/data".format(_OLD_ROOT_DIR),
        TEMP_DIR="{0}/temp".format(_OLD_ROOT_DIR))

    #Current .opencafe Directories
    OPENCAFE_ROOT_DIR = os.path.join(
        EnvironmentManager.get_current_user_home_path(), ".opencafe")

    OPENCAFE_SUB_DIRS = _FlatNamespace(
        LOG_DIR="{0}/logs".format(OPENCAFE_ROOT_DIR),
        DATA_DIR="{0}/data".format(OPENCAFE_ROOT_DIR),
        TEMP_DIR="{0}/temp".format(OPENCAFE_ROOT_DIR),
        CONFIG_DIR="{0}/configs".format(OPENCAFE_ROOT_DIR))

    @classmethod
    def update_existing_directories(cls):
        #Rename .cloudcafe to .opencafe
        if os.path.exists(cls._OLD_ROOT_DIR):
            if os.path.exists(cls.OPENCAFE_ROOT_DIR):
                print cls.wrapper.fill("* * ERROR * * *")
                print cls.wrapper.fill(
                    "Could not port .cloudcafe to .opencafe since .opencafe "
                    "already exists and is populated with files that the "
                    "config manager would need to overwrite.  This usually "
                    "means an attempt was made to install an older version "
                    "of opencafe on top of a newer version.  Delete either "
                    "the .opencafe or .cloudcafe directory in the user home "
                    "directory and try again.")
            else:
                os.rename(cls._OLD_ROOT_DIR, cls.OPENCAFE_ROOT_DIR)
                print cls.wrapper.fill(
                    "'{0} directory was successfully ported to {1}'".format(
                        cls._OLD_ROOT_DIR, cls.OPENCAFE_ROOT_DIR))

    @classmethod
    def create_default_directories(cls):
        print """* Creating default directories"""
        for _, directory_path in cls.OPENCAFE_SUB_DIRS.items():
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                if not EnvironmentManager.USING_WINDOWS:
                    uid, gid = EnvironmentManager.get_current_user_ids()
                    os.chown(directory_path, uid, gid)

    @classmethod
    def build_engine_directories(cls):
        if (os.path.exists(cls.OPENCAFE_ROOT_DIR) or
                os.path.exists(cls._OLD_ROOT_DIR)):
            cls.update_existing_directories()
        else:
            cls.create_default_directories()


class EngineConfigManager(object):
    wrapper = textwrap.TextWrapper(
        initial_indent="* ", subsequent_indent="  ", break_long_words=False)

    #Old Config Stuff for backwards compatability testing only
    _OLD_ENGINE_CONFIG_PATH = "{0}/configs/engine.config".format(
        EngineDirectoryManager.OPENCAFE_ROOT_DIR)

    #Openafe config defaults
    ENGINE_CONFIG_PATH = "{0}/engine.config".format(
        EngineDirectoryManager.OPENCAFE_ROOT_DIR)

    @staticmethod
    def rename_section(
            config_parser_object, current_section_name, new_section_name):

        items = config_parser_object.items(current_section_name)
        config_parser_object.add_section(new_section_name)

        for item in items:
            config_parser_object.set(new_section_name, item[0], item[1])

        config_parser_object.remove_section(current_section_name)

        return config_parser_object

    @staticmethod
    def rename_section_option(
            config_parser_object, section_name, current_option_name,
            new_option_name):

        current_option_value = config_parser_object.get(
            section_name, current_option_name)
        config_parser_object.set(
            section_name, new_option_name, current_option_value)
        config_parser_object.remove_option(section_name, current_option_name)

        return config_parser_object

    @staticmethod
    def read_config_file(path):
        config = SafeConfigParser()
        cfp = open(path, 'r')
        config.readfp(cfp)
        cfp.close()

        return config

    @classmethod
    def update_engine_config(cls):

        config = None
        _updated = False

        # Engine config moved from .opencafe/configs to .opencafe
        if os.path.exists(cls._OLD_ENGINE_CONFIG_PATH):
            _updated = True
            print cls.wrapper.fill(
                "Moving engine.config file from {0} to {1}".format(
                    cls._OLD_ENGINE_CONFIG_PATH, cls.ENGINE_CONFIG_PATH))

            config = cls.read_config_file(cls._OLD_ENGINE_CONFIG_PATH)

            #Move to new location
            os.rename(cls._OLD_ENGINE_CONFIG_PATH, cls.ENGINE_CONFIG_PATH)

        # Read config from current location ('.opencafe/engine.config)
        config = config or cls.read_config_file(cls.ENGINE_CONFIG_PATH)
        config_backup_location = "{0}{1}".format(
            cls.ENGINE_CONFIG_PATH, '.backup')
        print cls.wrapper.fill(
            "Creating backup of {0} at {1}".format(
                cls.ENGINE_CONFIG_PATH, config_backup_location))
        cls.write_and_chown_config(config, config_backup_location)

        # 'CCTNG_ENGINE' section name was changed to 'OPENCAFE_ENGINE'
        if 'CCTNG_ENGINE' in config.sections():
            _updated = True
            config = cls.rename_section(
                config, 'CCTNG_ENGINE', 'OPENCAFE_ENGINE')
            print cls.wrapper.fill(
                "Section name 'CCTNG_ENGINE' in the engine.config file was "
                "updated to'OPENCAFE_ENGINE'")

        # 'use_verbose_logging' option name changed to 'logging_verbosity'
        # value was changed from True or False to 'STANDARD', or 'VERBOSE',
        # respectively.
        config_keys = [key for key, _ in config.items('OPENCAFE_ENGINE')]
        if 'use_verbose_logging' in config_keys:
            _updated = True
            current_value = config.getboolean(
                'OPENCAFE_ENGINE', 'use_verbose_logging')
            new_value = 'VERBOSE' if current_value else 'STANDARD'
            config = cls.rename_section_option(
                config, 'OPENCAFE_ENGINE', 'use_verbose_logging',
                'logging_verbosity')
            config.set('OPENCAFE_ENGINE', 'logging_verbosity', new_value)
            print cls.wrapper.fill(
                "The 'use_verbose_logging' option in the OPENCAFE_ENGINE "
                "section of your engine.config has been renamed to "
                "'logging_verbosity'.  It's value has been changed from '{0}'"
                "to the new functional equivalent '{1}'".format(
                    current_value, new_value))

        #'default_test_repo' value changed from 'test_repo' to 'cloudroast'
        config_keys = [key for key, _ in config.items('OPENCAFE_ENGINE')]
        if ('default_test_repo' in config_keys and config.get(
                'OPENCAFE_ENGINE', 'default_test_repo') == 'test_repo'):
            _updated = True
            config.set(
                'OPENCAFE_ENGINE', 'default_test_repo', value='cloudroast')
            print cls.wrapper.fill(
                "The value of the 'default_test_repo' option in the "
                "OPENCAFE_ENGINE section of your engine.config has been "
                "changed from 'test_repo' to 'cloudroast'")

        #'config_dir' was added as a configurable option
        config_keys = [key for key, _ in config.items('OPENCAFE_ENGINE')]
        if 'config_dir' not in config_keys:
            _updated = True
            config.set(
                'OPENCAFE_ENGINE', 'config_dir',
                value=EngineDirectoryManager.OPENCAFE_SUB_DIRS.CONFIG_DIR)
            print cls.wrapper.fill(
                "'config_directory = {0}' has been added to the "
                "OPENCAFE_ENGINE section of your engine.config".format(
                    EngineDirectoryManager.OPENCAFE_SUB_DIRS.CONFIG_DIR))

        config_keys = [key for key, _ in config.items('OPENCAFE_ENGINE')]
        if 'master_log_file_name' not in config_keys:
            _updated = True
            config.set(
                'OPENCAFE_ENGINE', 'master_log_file_name', 'cafe-master')
            print cls.wrapper.fill(
                "'master_log_file_name = cafe-master' has been added to the "
                "OPENCAFE_ENGINE section of your engine.config")

        if not _updated:
            print cls.wrapper.fill(
                "No updates made, engine.config is newest version")

        return config

    @classmethod
    def default_engine_config(cls):
        config = SafeConfigParser()
        config.add_section('OPENCAFE_ENGINE')
        config.set(
            'OPENCAFE_ENGINE', 'config_directory',
            EngineDirectoryManager.OPENCAFE_SUB_DIRS.CONFIG_DIR)
        config.set(
            'OPENCAFE_ENGINE', 'data_directory',
            EngineDirectoryManager.OPENCAFE_SUB_DIRS.DATA_DIR)
        config.set(
            'OPENCAFE_ENGINE', 'log_directory',
            EngineDirectoryManager.OPENCAFE_SUB_DIRS.LOG_DIR)
        config.set(
            'OPENCAFE_ENGINE', 'temp_directory',
            EngineDirectoryManager.OPENCAFE_SUB_DIRS.TEMP_DIR)
        config.set(
            'OPENCAFE_ENGINE', 'master_log_file_name', 'cafe-master')
        config.set(
            'OPENCAFE_ENGINE', 'logging_verbosity', 'STANDARD')
        config.set(
            'OPENCAFE_ENGINE', 'default_test_repo', 'cloudroast')

        return config

    @staticmethod
    def write_and_chown_config(config_parser_object, path):
        cfp = open(path, 'w+')
        config_parser_object.write(cfp)
        cfp.close()

        if not EnvironmentManager.USING_WINDOWS:
            uid, gid = EnvironmentManager.get_current_user_ids()
            os.chown(path, uid, gid)

    @classmethod
    def build_engine_config(cls):
        config = None
        if os.path.exists(EngineDirectoryManager.OPENCAFE_ROOT_DIR):
            print '* Updating current config'
            config = cls.update_engine_config()
        else:
            print '* Writing new config'
            config = cls.default_engine_config()

        cls.write_and_chown_config(config, cls.ENGINE_CONFIG_PATH)


# TODO-jidar: Make this a report of what's actually there, not the defaults
def print_opencafe_config_install_report():
    config = EngineConfigManager.read_config_file(
        EngineConfigManager.ENGINE_CONFIG_PATH)
    print("========================================================")
    print("CAFE Core installed with the options:")
    print("Config File: {0}".format(
        EngineConfigManager.ENGINE_CONFIG_PATH))
    print("log_directory={0}".format(
        EngineDirectoryManager.OPENCAFE_SUB_DIRS.LOG_DIR))
    print("data_directory={0}".format(
        EngineDirectoryManager.OPENCAFE_SUB_DIRS.DATA_DIR))
    print("temp_directory={0}".format(
        EngineDirectoryManager.OPENCAFE_SUB_DIRS.TEMP_DIR))
    print("logging_verbosity={0}".format(
        config.get('OPENCAFE_ENGINE', 'logging_verbosity')))
    print("========================================================")

#class EnginePluginsManager(object):
#
#    @classmethod
#    def list_available_plugins(object):
#        pass


class EngineActions(object):

    class InitEngine(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            wrapper = textwrap.TextWrapper(
                initial_indent="", subsequent_indent="",
                break_long_words=False)
            print wrapper.fill("***Initializing Engine Install***")
            EngineDirectoryManager.build_engine_directories()
            EngineConfigManager.build_engine_config()

    class SomethingElse(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            print 'somethingelse_called'

#class PluginActions(object):
#
#    class ListPlugins(argparse.Action):
#        def __call__(self, parser, namespace, values, option_string=None):
#            print 'No current plugins'
#
#    class EnablePlugin(argparse.Action):
#        def __call__(self, parser, namespace, values, option_string=None):
#            print 'Enabling {0} Plugin'.format(values[0])
#
#    class DisablePlugin(argparse.Action):
#        def __call__(self, parser, namespace, values, option_string=None):
#            print 'Disbling {0} Plugin'.format(values[0])


class ConfiguratorCLI(object):

    @classmethod
    def run(cls):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest="subcommand")

        #Engine configuration subparser
        subparser_engine_config = subparsers.add_parser('engine')
        subparser_engine_config.add_argument(
            '--init', action=EngineActions.InitEngine, nargs=0)

        ##Plugins configuration subparser
        #subparser_engine_config = subparsers.add_parser('plugins')
        #subparser_engine_config.add_argument(
        #    '--list', action=PluginActions.ListPlugins, nargs=0)
        #subparser_engine_config.add_argument(
        #    '--enable', action=PluginActions.EnablePlugin, nargs=1)
        #subparser_engine_config.add_argument(
        #    '--disable', action=PluginActions.DisablePlugin, nargs=1)

        return parser.parse_args()


def entry_point():
    cli = ConfiguratorCLI()
    cli.run()
