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

import logging
import os
import sys
from collections import OrderedDict

log = logging.getLogger('RunnerLog')


def get_object_namespace(obj):
    '''Attempts to return a dotted string name representation of the general
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
    '''

    try:
        return parse_class_namespace_string(str(obj.__mro__[0]))
    except:
        pass

    #mro name wasn't availble, generate a unique name
    #By default, name is set to the memory address of the passed in object
    #since it's guaranteed to work.

    name = str(id(obj))
    try:
        name = "{0}_{1}".format(name, obj.__name__)
    except:
        pass

    return name


def parse_class_namespace_string(class_string):
    '''Parses the dotted namespace out of an object's __mro__.
    Returns a string
    '''
    class_string = str(class_string)
    class_string = class_string.replace("'>", "")
    class_string = class_string.replace("<class '", "")
    return str(class_string)


def getLogger(log_name, log_level=None):
    '''Convenience function to create a logger and set it's log level at the
    same time.
    Log level defaults to logging.DEBUG
    '''

    #Create new log
    new_log = logging.getLogger(name=log_name)
    new_log.setLevel(log_level or logging.DEBUG)
    verbosity = os.getenv('CAFE_LOGGING_VERBOSITY')

    if verbosity == 'VERBOSE':
        if logging.getLogger(log_name).handlers == []:
            #Special case for root log handler
            if log_name == "":
                log_name = os.getenv('CAFE_MASTER_LOG_FILE_NAME')
            #Add handler by default for all new loggers
            new_log.addHandler(setup_new_cchandler(log_name))

    # Add support for adding null log handlers by default when
    # logging_verbosity == 'OFF'

    return new_log


def setup_new_cchandler(
        log_file_name, log_dir=None, encoding=None, msg_format=None):
    '''Creates a log handler named <log_file_name> configured to save the log
    in <log_dir> or <os environment variable 'CAFE_TEST_LOG_PATH'>,
    in that order or precedent.
    File handler defaults: 'a+', encoding=encoding or "UTF-8", delay=True
    '''

    log_dir = log_dir or os.getenv('CAFE_TEST_LOG_PATH')

    try:
        log_dir = os.path.expanduser(log_dir)
    except Exception as exception:
        sys.stderr.write(
            "\nUnable to verify log directory: {0}\n".format(exception))

    try:
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
    except Exception as exception:
        sys.stderr.write(
            "\nError creating log directory: {0}\n".format(exception))

    log_path = os.path.join(log_dir, "{0}.log".format(log_file_name))

    #Set up handler with encoding and msg formatter in log directory
    log_handler = logging.FileHandler(log_path, "a+",
                                      encoding=encoding or "UTF-8", delay=True)

    fmt = msg_format or "%(asctime)s: %(levelname)s: %(name)s: %(message)s"
    log_handler.setFormatter(logging.Formatter(fmt=fmt))

    return log_handler


def log_results(result):
    """
        @summary: Replicates the printing functionality of unittest's
        runner.run() but log's instead of prints
    """
    infos = []
    expected_fails = unexpected_successes = skipped = 0

    try:
        results = map(len, (result.expectedFailures,
                            result.unexpectedSuccesses,
                            result.skipped))
        expected_fails, unexpected_successes, skipped = results
    except AttributeError:
        pass

    if not result.wasSuccessful():
        failed, errored = map(len, (result.failures, result.errors))

        if failed:
            infos.append("failures={0}".format(failed))
        if errored:
            infos.append("errors={0}".format(errored))

        log_errors('ERROR', result, result.errors)
        log_errors('FAIL', result, result.failures)
        log.info("Ran {0} Tests".format(result.testsRun))
        log.info('FAILED ')
    else:
        log.info("Ran {0} Tests".format(result.testsRun))
        log.info("Passing all tests")

    if skipped:
        infos.append("skipped={0}".format(str(skipped)))
    if expected_fails:
        infos.append("expected failures={0}".format(expected_fails))
    if unexpected_successes:
        infos.append("unexpected successes={0}".format(
            str(unexpected_successes)))
    if infos:
        log.info(" ({0})\n".format((", ".join(infos),)))
    else:
        log.info("\n")

    print '=' * 150
    print "Detailed logs: {0}".format(
        os.getenv("CAFE_TEST_LOG_PATH"))
    print '-' * 150


def log_errors(label, result, errors):
    border1 = '=' * 45
    border2 = '-' * 45

    for test, err in errors:
        msg = "{0}: {1}\n".format(label, result.getDescription(test))
        log.info('{0}\n{1}\n{2}\n{3}'.format(border1, msg, border2, err))


def init_root_log_handler():
    #Setup root log handler if the root logger doesn't already have one
    if not getLogger('').handlers:
        master_log_file_name = os.getenv('CAFE_MASTER_LOG_FILE_NAME')
        getLogger('').addHandler(
            setup_new_cchandler(master_log_file_name))


def log_info_block(
        log, info, separator=None, heading=None, log_level=logging.INFO):
    """Expects info to be a list of tuples or an OrderedDict
    Logs info as individual lines in blocks surrounded by a separator:
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
    """
    try:
        info = info if isinstance(info, OrderedDict) else OrderedDict(info)
    except:
        #Something went wrong, log what can be logged
        log.log(log_level, str(info))
        return

    separator = str(separator or "{0}".format('=' * 56))
    max_length = len(max([k for k in info.keys() if info.get(k)], key=len))+3

    log.log(log_level, separator)
    if heading:
        log.info(heading)
        log.log(log_level, separator)

    for k in info:
        value = str(info.get(k, None))
        if value:
            log.log(log_level, "{0}{1}: {2}".format(
                k, "." * (max_length-len(k)), value))
        else:
            log.log(log_level, "{0}".format(k))

    log.log(log_level, separator)
