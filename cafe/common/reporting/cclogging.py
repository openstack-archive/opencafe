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

import sys
import logging
import os

# When raising warnings in the module, only print them once, and don't
# show any line numbers or stacktraces (simply print the messages to stderr)
import warnings
warnings.simplefilter('once', Warning)
warnings.showwarning = \
    lambda msg, category, filename, lineno: sys.stderr.write(str(msg))

try:
    from collections import OrderedDict
except ImportError:
    # python 2.6 or earlier, use backport
    from ordereddict import OrderedDict


def logsafe_str(data):
    return "{0}".format(data).decode('utf-8', 'replace')


def get_object_namespace(obj):
    """Attempts to return a dotted string name representation of the general
    form 'package.module.class.obj' for an object that has an __mro__ attribute

    Designed to let you to name loggers inside objects in such a way
    that the engine logger organizes them as child loggers to the modules
    they originate from.

    So that logging doesn't cause exceptions, if the namespace cannot be
    extracted from the object's mro attribute, the actual name returned is set
    to a probably-unique string, the id() of the object passed,
    and is then further improved by a series of functions until
    one of them fails.
    The value of the last successful name-setting method is returned.
    """

    try:
        return parse_class_namespace_string(str(obj.__mro__[0]))
    except:
        pass

    # mro name wasn't availble, generate a unique name
    # By default, name is set to the memory address of the passed in object
    # since it's guaranteed to work.

    name = str(id(obj))
    try:
        name = "{0}_{1}".format(name, obj.__name__)
    except:
        pass

    return name


def parse_class_namespace_string(class_string):
    """
    Parses the dotted namespace out of an object's __mro__. Returns a string
    """

    class_string = str(class_string)
    class_string = class_string.replace("'>", "")
    class_string = class_string.replace("<class '", "")
    return str(class_string)


def getLogger(log_name=None, log_level=None):
    """Convenience function to create a logger and set it's log level at the
    same time. Log level defaults to logging.DEBUG
    Note: If the root log is accesed via this method in VERBOSE mode, the root
    log will be initialized and returned, if it hasn't been initialized
    already.
    """

    # Create requested log
    requested_log = logging.getLogger(name=log_name)
    verbosity = os.getenv('CAFE_LOGGING_VERBOSITY')

    if verbosity == 'VERBOSE':
        # By default, logs don't get handlers when they're created.
        # Setting the logger to 'VERBOSE' will add handlers for every log
        # that gets created.
        if not log_name:
            # Only init the handler on the root logger if mode is VERBOSE
            return init_root_log_handler()
        if requested_log.handlers == []:
            requested_log.setLevel(log_level or logging.DEBUG)
            requested_log.addHandler(setup_new_cchandler(log_name))

    return requested_log


def setup_new_cchandler(
        log_file_name, log_dir=None, encoding=None, msg_format=None):
    """Creates a log handler named <log_file_name> configured to save the log
    in <log_dir> or <os environment variable 'CAFE_TEST_LOG_PATH'>,
    in that order or precedent.
    File handler defaults: 'a+', encoding=encoding or "UTF-8", delay=True
    """

    log_dir = log_dir or os.getenv('CAFE_TEST_LOG_PATH')

    try:
        log_dir = os.path.expanduser(log_dir)
    except Exception as exception:
        warnings.warn(
            "\nUnable to verify existence of log directory: "
            "{0}\nError: {1}".format(log_dir, exception.message), Warning)

    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as exception:
        warnings.warn(
            "\nError creating log directory: "
            "{0}\nError: {1}".format(log_dir, exception.message), Warning)

    log_path = os.path.join(log_dir, "{0}.log".format(log_file_name))

    # Set up handler with encoding and msg formatter in log directory
    log_handler = logging.FileHandler(
        log_path, "a+", encoding=encoding or "UTF-8", delay=True)

    fmt = msg_format or "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
    log_handler.setFormatter(logging.Formatter(fmt=fmt))

    return log_handler


def init_root_log_handler(override_handler=None):
    """Setup root log handler if the root logger doesn't already have one"""

    root_log = logging.getLogger()
    if override_handler:
        root_log.addHandler(override_handler)
    elif not root_log.handlers:
        master_log_file_name = os.getenv('CAFE_MASTER_LOG_FILE_NAME')
        if master_log_file_name is None:
            warnings.warn(
                "Environment variable 'CAFE_MASTER_LOG_FILE_NAME' is not "
                "set. A null root log handler will be used, no logs will be "
                "written.", Warning)
            root_log.addHandler(logging.NullHandler())
        else:
            root_log.addHandler(setup_new_cchandler(master_log_file_name))
            root_log.setLevel(logging.DEBUG)
    return root_log


def log_info_block(
        log, info, separator=None, heading=None, log_level=logging.INFO,
        one_line=False):
    """Expects info to be a list of tuples or an OrderedDict
    Logs info in blocks surrounded by a separator:
    ====================================================================
    A heading will print here, with another separator below it.
    ====================================================================
    Items are logged in order................................: Info
    And are separated from their info........................: Info
    By at least three dots...................................: Info
    If no second value is given in the tuple, a single line is logged
    Lower lines will still line up correctly.................: Info
    The longest line dictates the dot length for all lines...: Like this
    ====================================================================
    if one_line is true, info block will be logged as a single line, formatted
    using newlines.  Otherwise, each line of the info block will be logged
    as seperate log lines (with seperate timestamps, etc.)
    """

    output = []
    try:
        info = info if isinstance(info, OrderedDict) else OrderedDict(info)
    except:
        # Something went wrong, log what can be logged
        output.append(str(info))
        return

    separator = str(separator or "{0}".format('=' * 56))
    max_length = \
        len(max([k for k in list(info.keys()) if info.get(k)], key=len)) + 3

    output.append(separator)
    if heading:
        output.append(heading)
        output.append(separator)

    for k in info:
        value = str(info.get(k, None))
        if value:
            output.append(
                "{0}{1}: {2}".format(k, "." * (max_length - len(k)), value))
        else:
            output.append("{0}".format(k))
    output.append(separator)

    if one_line:
        log.log(log_level, "\n{0}".format("\n".join(output)))
    else:
        [log.log(log_level, line) for line in output]
