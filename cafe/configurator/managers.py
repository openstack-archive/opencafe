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

import compileall
import os
import platform
import sys
import textwrap
import getpass
import shutil
from subprocess import Popen, PIPE

from six.moves.configparser import SafeConfigParser

import cafe

if not platform.system().lower() == 'windows':
    import pwd


class _NamespaceDict(dict):
    """
    A dict-like object that allows dotted access via its top-level keys.

    Raises an Exception if any keys in self.keys() collide with reserved
    (internal to dict()) attributes.
    """

    def __init__(self, **kwargs):
        super(_NamespaceDict, self).__init__(self, **kwargs)
        collisions = set(kwargs) & set(dir(self))
        if bool(collisions):
            # Construct proper grammar for Exception message
            collisions = list(collisions)
            collisions_string = "key {0} as an attribute".format(collisions[0])
            if len(collisions) > 1:
                collisions_string = ", ".join(
                    ["'{0}'".format(c) for c in collisions[:-1]])
                collisions_string = "keys {0} or '{1}' as attributes".format(
                    collisions_string, str(collisions[-1]))
            raise Exception(
                "Cannot set {0}.  NamespaceDict cannot "
                "contain any keys that collide with attribute names internal "
                "to a dict-like object.".format(collisions_string))

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                "NamespaceDict has no accessible attribute '{0}'".format(name))


class PlatformManager(object):
    """
    Methods for dealing with the OS cafe is running on
    """

    USING_WINDOWS = (platform.system().lower() == 'windows')
    USING_VIRTUALENV = hasattr(sys, 'real_prefix')

    @classmethod
    def get_current_user(cls):
        """Returns the name of the current user.  For Linux, always tries to
        return a user other than 'root' if it can.
        """

        real_user = os.getenv("SUDO_USER")
        effective_user = os.getenv("USER")

        if not cls.USING_WINDOWS and not cls.USING_VIRTUALENV:
            if effective_user == 'root' and real_user not in ['root', None]:
                # Running 'sudo'.
                return real_user
        elif cls.USING_WINDOWS:
            return getpass.getuser()

        # Return the effective user, or root if all else fails
        return effective_user or 'root'

    @classmethod
    def get_user_home_path(cls):
        if cls.USING_VIRTUALENV:
            return sys.prefix
        else:
            return os.path.expanduser("~{0}".format(cls.get_current_user()))

    @classmethod
    def get_user_uid(cls):
        if not cls.USING_WINDOWS:
            working_user = cls.get_current_user()
            return pwd.getpwnam(working_user).pw_uid

    @classmethod
    def get_user_gid(cls):
        if not cls.USING_WINDOWS:
            working_user = cls.get_current_user()
            return pwd.getpwnam(working_user).pw_gid

    @classmethod
    def safe_chown(cls, path):
        if not cls.USING_WINDOWS:
            uid = cls.get_user_uid()
            gid = cls.get_user_gid()
            os.chown(path, uid, gid)

    @classmethod
    def safe_create_dir(cls, directory_path):
        if not os.path.exists(directory_path):
            os.makedirs(directory_path)

# .opencafe Directories
OPENCAFE_ROOT_DIR = os.path.join(
    PlatformManager.get_user_home_path(), ".opencafe")

OPENCAFE_SUB_DIRS = _NamespaceDict(
    LOG_DIR=os.path.join(OPENCAFE_ROOT_DIR, 'logs'),
    DATA_DIR=os.path.join(OPENCAFE_ROOT_DIR, 'data'),
    TEMP_DIR=os.path.join(OPENCAFE_ROOT_DIR, 'temp'),
    CONFIG_DIR=os.path.join(OPENCAFE_ROOT_DIR, 'configs'),
    PLUGIN_CACHE=os.path.join(OPENCAFE_ROOT_DIR, 'plugin_cache'),
    ENGINE_CONFIG_PATH=os.path.join(OPENCAFE_ROOT_DIR, 'engine.config'))


class EngineDirectoryManager(object):

    wrapper = textwrap.TextWrapper(
        initial_indent="* ", subsequent_indent="  ", break_long_words=False)

    @classmethod
    def create_engine_directories(cls):
        print(cls.wrapper.fill('Creating default directories in {0}'.format(
            OPENCAFE_ROOT_DIR)))

        # Create the opencafe root dir and sub dirs
        PlatformManager.safe_create_dir(OPENCAFE_ROOT_DIR)
        print(cls.wrapper.fill('...created {0}'.format(OPENCAFE_ROOT_DIR)))
        for _, directory_path in list(OPENCAFE_SUB_DIRS.items()):
            PlatformManager.safe_create_dir(directory_path)
            print(cls.wrapper.fill('...created {0}'.format(directory_path)))

    @classmethod
    def set_engine_directory_permissions(cls):
        """Recursively changes permissions default engine directory so that
        everything is user-owned
        """

        PlatformManager.safe_chown(OPENCAFE_ROOT_DIR)
        for root, dirs, files in os.walk(OPENCAFE_ROOT_DIR):
            for d in dirs:
                PlatformManager.safe_chown(os.path.join(root, d))
            for f in files:
                PlatformManager.safe_chown(os.path.join(root, f))

    @classmethod
    def build_engine_directories(cls):
        """Updates, creates, and owns (as needed) all default directories"""

        cls.create_engine_directories()
        cls.set_engine_directory_permissions()


class EngineConfigManager(object):
    wrapper = textwrap.TextWrapper(
        initial_indent="* ", subsequent_indent="  ", break_long_words=False)

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
            OPENCAFE_SUB_DIRS.ENGINE_CONFIG_PATH, '.backup')
        print(cls.wrapper.fill(
            "Creating backup of {0} at {1}".format(
                OPENCAFE_SUB_DIRS.ENGINE_CONFIG_PATH, config_backup_location)))
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
        # Read config from current default location ('.opencafe/engine.config)
        config = config or cls.read_config_file(
            OPENCAFE_SUB_DIRS.ENGINE_CONFIG_PATH)

        # UPDATE CODE GOES HERE

        if not update_tracker._updated:
            wrapper = textwrap.TextWrapper(initial_indent="  ")
            print(wrapper.fill(
                "...no updates applied, engine.config is newest version"))

        return config

    @classmethod
    def generate_default_engine_config(cls):
        config = SafeConfigParser()
        config.add_section('ENGINE')
        config.set('ENGINE', 'config_directory', OPENCAFE_SUB_DIRS.CONFIG_DIR)
        config.set('ENGINE', 'data_directory', OPENCAFE_SUB_DIRS.DATA_DIR)
        config.set('ENGINE', 'log_directory', OPENCAFE_SUB_DIRS.LOG_DIR)
        config.set('ENGINE', 'temp_directory', OPENCAFE_SUB_DIRS.TEMP_DIR)
        config.set('ENGINE', 'master_log_file_name', 'cafe.master')
        config.set('ENGINE', 'logging_verbosity', 'STANDARD')
        config.set('ENGINE', 'default_test_repo', 'cloudroast')
        config.set('ENGINE', 'root_log_dir', '{test_config}')
        config.set('ENGINE', 'test_log_dir', '{timestamp}')
        config.set('ENGINE', 'test_config', os.devnull)
        return config

    @staticmethod
    def write_and_chown_config(config_parser_object, path):
        cfp = open(path, 'w+')
        config_parser_object.write(cfp)
        cfp.close()
        PlatformManager.safe_chown(path)

    @classmethod
    def build_engine_config(cls):
        config = None
        if os.path.exists(OPENCAFE_SUB_DIRS.ENGINE_CONFIG_PATH):
            print(cls.wrapper.fill('Checking for updates to engine.config...'))
            config = cls.update_engine_config()
        else:
            print(cls.wrapper.fill(
                "Creating default engine.config at {0}".format(
                    OPENCAFE_SUB_DIRS.ENGINE_CONFIG_PATH)))
            config = cls.generate_default_engine_config()

        cls.write_and_chown_config(
            config, OPENCAFE_SUB_DIRS.ENGINE_CONFIG_PATH)

    @classmethod
    def install_optional_configs(cls, source_directory, print_progress=True):
        if print_progress:
            twrap = textwrap.TextWrapper(
                initial_indent='* ', subsequent_indent='  ',
                break_long_words=False)
            print(twrap.fill(
                'Installing reference configuration files in ...'.format(
                    OPENCAFE_ROOT_DIR)))
            twrap = textwrap.TextWrapper(
                initial_indent='  ', subsequent_indent='  ',
                break_long_words=False)

        _printed = []
        for root, sub_folders, files in os.walk(source_directory):
            for file_ in files:
                source = os.path.join(root, file_)
                destination_dir = os.path.join(OPENCAFE_ROOT_DIR, root)
                destination_file = os.path.join(destination_dir, file_)
                PlatformManager.safe_create_dir(destination_dir)
                PlatformManager.safe_chown(destination_dir)

                if print_progress:
                    'Installing {0} at {1}'.format(source, destination_dir)

                shutil.copyfile(source, destination_file)

                if print_progress:
                    if destination_dir not in _printed:
                        print(twrap.fill('{0}'.format(destination_dir)))
                        _printed.append(destination_dir)

                PlatformManager.safe_chown(destination_file)


class EnginePluginManager(object):

    @classmethod
    def copy_plugin_to_cache(
            cls, plugins_src_dir, plugins_dest_dir, plugin_name):
        """ Copies an individual plugin to the .opencafe plugin cache """
        src_plugin_path = os.path.join(plugins_src_dir, plugin_name)
        dest_plugin_path = os.path.join(plugins_dest_dir, plugin_name)

        if os.path.exists(dest_plugin_path):
            shutil.rmtree(dest_plugin_path)

        shutil.copytree(src_plugin_path, dest_plugin_path)

    @classmethod
    def populate_plugin_cache(cls, plugins_src_dir):
        """ Handles moving all plugin src data from package into the user's
        .opencafe folder for installation by the cafe-config tool.
        """

        default_dest = OPENCAFE_SUB_DIRS.PLUGIN_CACHE
        plugins = next(os.walk(plugins_src_dir))[1]

        for plugin_name in plugins:
            cls.copy_plugin_to_cache(
                plugins_src_dir, default_dest, plugin_name)

    @classmethod
    def list_plugins(cls):
        """ Lists all plugins currently available in user's .opencafe cache"""

        plugin_cache = OPENCAFE_SUB_DIRS.PLUGIN_CACHE
        plugin_folders = os.walk(plugin_cache).next()[1]
        wrap = textwrap.TextWrapper(initial_indent="  ",
                                    subsequent_indent="  ",
                                    break_long_words=False).fill

        for plugin_folder in plugin_folders:
            print(wrap('... {name}'.format(name=plugin_folder)))

    @classmethod
    def install_plugins(cls, plugin_names):
        """ Installs a list of plugins into the current environment"""

        for plugin_name in plugin_names:
            cls.install_plugin(plugin_name)
        compileall.compile_dir(
            cafe.__path__[0], maxlevels=1000, force=1, quiet=1)

    @classmethod
    def install_plugin(cls, plugin_name):
        """ Install a single plugin by name into the current environment"""

        plugin_cache = OPENCAFE_SUB_DIRS.PLUGIN_CACHE
        plugin_dir = os.path.join(plugin_cache, plugin_name)
        wrap = textwrap.TextWrapper(initial_indent="  ",
                                    subsequent_indent="  ",
                                    break_long_words=False).fill

        # Pretty output of plugin name
        print(wrap('... {name}'.format(name=plugin_name)))

        # Verify that the plugin exists
        if not os.path.exists(plugin_dir):
            print(wrap('* Failed to install plugin: {0}'.format(plugin_name)))
            return

        # Install Plugin
        process, standard_out, standard_error = None, None, None
        cmd = 'pip install {name} --upgrade'.format(name=plugin_dir)

        try:
            process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
            standard_out, standard_error = process.communicate()
        except Exception as e:
            msg = '* Plugin install failed {0}\n{1}\n'.format(cmd, e)
            print(wrap(msg))

        # Print failure if we receive an error code
        if process and process.returncode != 0:
            print(wrap(standard_out))
            print(wrap(standard_error))
            print(wrap('* Failed to install plugin: {0}'.format(plugin_name)))
