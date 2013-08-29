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

import datetime
import imp
import os
import platform
import sys
import textwrap
from ConfigParser import SafeConfigParser
from cafe.engine.config import EngineConfig

if not platform.system().lower() == 'windows':
    import pwd


class PlatformManager(object):
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
        if PlatformManager.USING_VIRTUALENV:
            return sys.prefix
        else:
            return os.path.expanduser("~{0}".format(cls.get_current_user()))

    @classmethod
    def get_current_user_ids(cls):
        if not PlatformManager.USING_WINDOWS:
            working_user = cls.get_current_user()
            uid = pwd.getpwnam(working_user).pw_uid
            gid = pwd.getpwnam(working_user).pw_gid
            return uid, gid


class UnittestRunnerTestEnvManager(object):
    """DO NOT USE
    Supports the current unittest runner until it can be refactored to use
    the regular TestEnvManager, at which time this class will be deleted"""

    @staticmethod
    def set_engine_config_path():
        os.environ['OPENCAFE_ENGINE_CONFIG_FILE_PATH'] = \
            EngineConfigManager.ENGINE_CONFIG_PATH
        return EngineConfigManager.ENGINE_CONFIG_PATH

    @staticmethod
    def get_engine_config_interface():
        return EngineConfig(EngineConfigManager.ENGINE_CONFIG_PATH)

    @staticmethod
    def set_test_repo_package_path():
        eng_conf = EngineConfig(EngineConfigManager.ENGINE_CONFIG_PATH)
        test_repo_package = eng_conf.default_test_repo

        os.environ["CAFE_TEST_REPO_PACKAGE"] = test_repo_package

        module_info = None
        try:
            module_info = imp.find_module(test_repo_package)
        except ImportError as exception:
            print "Cannot find test repo '{0}'".format(test_repo_package)
            raise exception

        test_repo_path = module_info[1]
        os.environ["CAFE_TEST_REPO_PATH"] = test_repo_path
        return test_repo_path


class TestEnvManager(object):
    """
    Manages setting all required and optional environment variables used by
    the engine and it's implementations.
    Usefull for writing bootstrappers for runners and scripts.
    """

    def __init__(
            self, product_name, test_config_file_name,
            engine_config_path=None):

        self.product_name = product_name
        self.test_config_file_name = test_config_file_name
        self.engine_config_path = engine_config_path or \
            EngineConfigManager.ENGINE_CONFIG_PATH
        os.environ['OPENCAFE_ENGINE_CONFIG_FILE_PATH'] = \
            self.engine_config_path
        self.engine_config_interface = EngineConfig(self.engine_config_path)

        #Property value vars
        self._test_repo_path = None
        self._test_repo_package = None
        self._test_data_directory = None
        self._test_root_log_dir = None
        self._test_log_dir = None
        self._test_logging_verbosity = None
        self._test_config_file_path = None
        self._test_master_log_file_name = None

    def finalize(self, create_missing_dirs=True, set_defaults=True):
        """
        Checks that all set paths exists, and creates them if they don't.
        (create_missing_dirs=False overrides the dir creation behavior)

        Sets all non-configured values to the defaults in the engine.config
        file.  (set_defaults=False overrides this behavior)

        """
        def _check_and_create(path, create=create_missing_dirs):
            if not os.path.exists(path):
                if create:
                    os.makedirs(path)
                else:
                    raise Exception('{0} does not exist'.format(path))

        if set_defaults:
            self.test_repo_path = self.test_repo_path
            self.test_repo_package = self.test_repo_package
            self.test_data_directory = self.test_data_directory
            self.test_root_log_dir = self.test_root_log_dir
            self.test_log_dir = self.test_log_dir
            self.test_logging_verbosity = self.test_logging_verbosity
            self.test_config_file_path = self.test_config_file_path
            self.test_master_log_file_name = self.test_master_log_file_name

        _check_and_create(self.test_repo_path, create_missing_dirs)
        _check_and_create(self.test_data_directory, create_missing_dirs)
        _check_and_create(self.test_root_log_dir, create_missing_dirs)
        _check_and_create(self.test_log_dir, create_missing_dirs)
        _check_and_create(self.test_logging_verbosity, create_missing_dirs)
        _check_and_create(self.test_config_file_path, create_missing_dirs)

    @property
    def test_repo_path(self):
        return self._test_repo_path

    @test_repo_path.setter
    def test_repo_path(self, test_repo_path=None):
        """NOTE:  There is no default for test_repo_path because we don't
        officially support non-package test repos yet, even though every
        runner just gets the path to the test repo package.

        This is set by the test_repo_package.
        """

        self._test_repo_path = test_repo_path
        os.environ["CAFE_TEST_REPO_PATH"] = self._test_repo_path

    @property
    def test_repo_package(self):
        return self._test_repo_package

    @test_repo_package.setter
    def test_repo_package(self, test_repo_package=None):
        """NOTE: The actual test repo package is never used by any current
        runners, instead they reference the root path to the tests.  For that
        reason, it sets the CAFE_TEST_REPO_PATH directly.
        """
        self._test_repo_package = test_repo_package or \
            self.engine_config_interface.default_test_repo

        os.environ["CAFE_TEST_REPO_PACKAGE"] = self._test_repo_package

        #Also set test repo package path
        module_info = None
        try:
            module_info = imp.find_module(self.test_repo_package)
        except ImportError as exception:
            print "Cannot find test repo '{0}'".format(self.test_repo_package)
            raise exception

        self.test_repo_path = module_info[1]
        os.environ["CAFE_TEST_REPO_PATH"] = self.test_repo_path

    @property
    def test_data_directory(self):
        return self._test_data_directory

    @test_data_directory.setter
    def test_data_directory(self, test_data_directory=None):
        self._test_data_directory = test_data_directory or os.path.join(
            self.engine_config_interface.data_directory,
            self.product_name, self.test_config_file_name)

        os.environ["CAFE_DATA_DIR_PATH"] = self._test_data_directory

    @property
    def test_root_log_dir(self):
        return self._test_root_log_dir

    @test_root_log_dir.setter
    def test_root_log_dir(self, test_root_log_dir=None):
        self.test_root_log_dir = test_root_log_dir or os.path.join(
            self.engine_config_interface.log_directory, self.product_name,
            self.test_config_file_name)

        os.environ["CAFE_ROOT_LOG_PATH"] = self._test_root_log_dir

    @property
    def test_log_dir(self):
        return self._test_log_dir

    @test_log_dir.setter
    def test_log_dir(self, test_log_dir=None):
        log_dir_name = str(datetime.now()).replace(" ", "_").replace(":", "_")

        self._test_root_log_dir = self.test_root_log_dir or \
            self.engine_config_interface.log_directory

        self._test_log_dir = test_log_dir or os.path.join(
            self.test_root_log_dir, log_dir_name)

        os.environ["CAFE_TEST_LOG_PATH"] = self._test_log_dir

    @property
    def test_config_file_path(self):
        return self._test_config_file_path

    @test_config_file_path.setter
    def test_config_file_path(self, test_config_file_path=None):
        self._test_config_file_path = test_config_file_path or os.path.join(
            self.engine_config_interface.config_directory, self.product_name,
            self.test_config_file_name)

        os.environ["CAFE_CONFIG_FILE_PATH"] = self._test_config_file_path

    @property
    def test_logging_verbosity(self):
        return self._test_logging_verbosity

    @test_logging_verbosity.setter
    def test_logging_verbosity(self, test_logging_verbosity=None):
        """Currently supports STANDARD and VERBOSE.
        TODO: Implement 'OFF' option that adds null handlers to all loggers

        """
        self._test_logging_verbosity = test_logging_verbosity or \
            self.engine_config_interface.logging_verbosity

        os.environ["CAFE_LOGGING_VERBOSITY"] = self._test_logging_verbosity

    @property
    def test_master_log_file_name(self, test_master_log_file_name=None):
        self._test_master_log_file_name = test_master_log_file_name or \
            self.engine_config_interface.master_log_file_name

        os.environ["CAFE_MASTER_LOG_FILE_NAME"] = \
            self._test_master_log_file_name


class EngineDirectoryManager(object):

    class _Namespace(dict):
        """
        Converts the top-level keys of this dictionary into a namespace.
        Raises exception if any self.keys() collide with internal attributes.
        """
        def __init__(self, **kwargs):
            dict.__init__(self, **kwargs)
            collisions = set(kwargs) & set(dir(self))
            if bool(collisions):
                raise Exception(
                    "Cannot set attribute {0}.  Namespace cannot contain "
                    "any keys that collide with internal attribute "
                    "names.".format([c for c in collisions]))

        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(
                    "Namespace has no attribute '{0}'".format(name))

    wrapper = textwrap.TextWrapper(
        initial_indent="* ", subsequent_indent="  ", break_long_words=False)

    #Old .cloudcafe directories
    _OLD_ROOT_DIR = os.path.join(
        PlatformManager.get_current_user_home_path(), ".cloudcafe")
    _OLD_CAFE_DIRS = _Namespace(
        LOG_DIR="{0}/logs".format(_OLD_ROOT_DIR),
        DATA_DIR="{0}/data".format(_OLD_ROOT_DIR),
        TEMP_DIR="{0}/temp".format(_OLD_ROOT_DIR))

    #Current .opencafe Directories
    OPENCAFE_ROOT_DIR = os.path.join(
        PlatformManager.get_current_user_home_path(), ".opencafe")

    OPENCAFE_SUB_DIRS = _Namespace(
        LOG_DIR="{0}/logs".format(OPENCAFE_ROOT_DIR),
        DATA_DIR="{0}/data".format(OPENCAFE_ROOT_DIR),
        TEMP_DIR="{0}/temp".format(OPENCAFE_ROOT_DIR),
        CONFIG_DIR="{0}/configs".format(OPENCAFE_ROOT_DIR))

    @classmethod
    def update_existing_directories(cls):
        """
        Applies to an existing .cloudcafe (old) or .opencafe (new) directory
        all changes made to the default .opencafe directory structure since
        opencafe's release.
        """
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
        print cls.wrapper.fill(
            'Creating default directories in {0}'.format(
                cls.OPENCAFE_ROOT_DIR))

        for _, directory_path in cls.OPENCAFE_SUB_DIRS.items():
            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                if not PlatformManager.USING_WINDOWS:
                    uid, gid = PlatformManager.get_current_user_ids()
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
    def write_config_backup(cls, config):
        config_backup_location = "{0}{1}".format(
            cls.ENGINE_CONFIG_PATH, '.backup')
        print cls.wrapper.fill(
            "Creating backup of {0} at {1}".format(
                cls.ENGINE_CONFIG_PATH, config_backup_location))
        cls.write_and_chown_config(config, config_backup_location)

    @classmethod
    def update_engine_config(cls):
        """
        Applies to an existing engine.config file all modifications made to
        the default engine.config file since opencafe's release in the order
        those modification where added.
        """

        class _UpdateTracker(object):
            def __init__(self):
                self._updated = False
                self._backed_up = False

            def register_update(self, config=None, backup=True):
                if not self._backed_up and backup:
                    EngineConfigManager.write_config_backup(config)
                    self._backed_up = True
                self._updated = True

        config = None
        update_tracker = _UpdateTracker()

        # Engine config moved from .opencafe/configs/engine.conf
        # to .opencafe/engine.conf
        if os.path.exists(cls._OLD_ENGINE_CONFIG_PATH):
            update_tracker.register_update(backup=False)
            print cls.wrapper.fill(
                "Moving engine.config file from {0} to {1}".format(
                    cls._OLD_ENGINE_CONFIG_PATH, cls.ENGINE_CONFIG_PATH))
            config = cls.read_config_file(cls._OLD_ENGINE_CONFIG_PATH)
            #Move to new location
            os.rename(cls._OLD_ENGINE_CONFIG_PATH, cls.ENGINE_CONFIG_PATH)

        # Read config from current default location ('.opencafe/engine.config)
        config = config or cls.read_config_file(cls.ENGINE_CONFIG_PATH)

        # 'CCTNG_ENGINE' section name was changed to 'OPENCAFE_ENGINE'
        if 'CCTNG_ENGINE' in config.sections():
            update_tracker.register_update(config)
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
            update_tracker.register_update(config)
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
            update_tracker.register_update(config)
            config.set(
                'OPENCAFE_ENGINE', 'default_test_repo', value='cloudroast')
            print cls.wrapper.fill(
                "The value of the 'default_test_repo' option in the "
                "OPENCAFE_ENGINE section of your engine.config has been "
                "changed from 'test_repo' to 'cloudroast'")

        #'config_dir' was added as a configurable option
        config_keys = [key for key, _ in config.items('OPENCAFE_ENGINE')]
        if 'config_directory' not in config_keys:
            update_tracker.register_update(config)
            config.set(
                'OPENCAFE_ENGINE', 'config_directory',
                value=EngineDirectoryManager.OPENCAFE_SUB_DIRS.CONFIG_DIR)
            print cls.wrapper.fill(
                "'config_directory = {0}' has been added to the "
                "OPENCAFE_ENGINE section of your engine.config".format(
                    EngineDirectoryManager.OPENCAFE_SUB_DIRS.CONFIG_DIR))

        config_keys = [key for key, _ in config.items('OPENCAFE_ENGINE')]
        if 'master_log_file_name' not in config_keys:
            update_tracker.register_update(config)
            config.set(
                'OPENCAFE_ENGINE', 'master_log_file_name', 'cafe.master')
            print cls.wrapper.fill(
                "'master_log_file_name = cafe-master' has been added to the "
                "OPENCAFE_ENGINE section of your engine.config")

        if not update_tracker._updated:
            wrapper = textwrap.TextWrapper(initial_indent="  ")
            print wrapper.fill(
                "...no updates applied, engine.config is newest version")

        return config

    @classmethod
    def generate_default_engine_config(cls):
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
            'OPENCAFE_ENGINE', 'master_log_file_name', 'cafe.master')
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

        if not PlatformManager.USING_WINDOWS:
            uid, gid = PlatformManager.get_current_user_ids()
            os.chown(path, uid, gid)

    @classmethod
    def build_engine_config(cls):
        config = None
        if os.path.exists(cls.ENGINE_CONFIG_PATH) or \
                os.path.exists(cls._OLD_ENGINE_CONFIG_PATH):
            print cls.wrapper.fill('Checking for updates to engine.config...')
            config = cls.update_engine_config()
        else:
            print cls.wrapper.fill(
                "Creating default engine.config at {0}".format(
                    cls.ENGINE_CONFIG_PATH))

            config = cls.generate_default_engine_config()

        cls.write_and_chown_config(config, cls.ENGINE_CONFIG_PATH)
