#!/usr/bin/env python
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

import os
import imp
import sys
import time
import fnmatch
import inspect
import logging
import argparse
import platform
import threading
import traceback
import unittest2 as unittest
from datetime import datetime

from cafe.drivers.unittest.parsers import ParseResult

'''@todo: This needs to be configurable/dealt with by the install '''
import test_repo

# Default Config Options
if platform.system().lower() == 'windows':
    DIR_SEPR = '\\'
else:
    DIR_SEPR = '/'

BASE_DIR = "{0}{1}.cloudcafe".format(os.path.expanduser("~"), DIR_SEPR)
DATA_DIR = os.path.expanduser('{0}{1}data'.format(BASE_DIR, DIR_SEPR))
LOG_BASE_PATH = os.path.expanduser('{0}{1}logs'.format(BASE_DIR, DIR_SEPR))
YELLOW = '\033[1;33m'
GREEN = '\033[1;32m'
WHITE = '\033[1;37m'
RED = '\033[0;31m'
HIGHLIGHTED_RED = '\033[1;41m'
END = '\033[1;m'


class _WritelnDecorator: 
    """Used to decorate file-like objects with a handy 'writeln' method""" 
    
    def __init__(self,stream): 
        self.stream = stream 
   
    def __getattr__(self, attr): 
        return getattr(self.stream,attr) 

    def writeln(self, arg=None): 
        if arg:
            self.write(arg)
        self.write('\n') 


class CCParallelTextTestRunner(unittest.TextTestRunner):
    
    def __init__(self, stream=sys.stderr, descriptions=1, verbosity=1): 
        self.stream = _WritelnDecorator(stream)
        self.descriptions = descriptions 
        self.verbosity = verbosity
        
    def run(self, test): 
        """Run the given test case or test suite."""
        result = self._makeResult() 
        startTime = time.time() 
        test(result) 
        stopTime = time.time() 
        timeTaken = stopTime - startTime 
        result.printErrors() 
        run = result.testsRun 
        return result

    
class CCRunner(object):
    '''
    Cloud Cafe Runner
    '''

    def __init__(self):
        self.log = logging.getLogger('RunnerLog')

    def get_cl_args(self):
        '''
        collects and parses the command line args
        creates the runner's help msg
        '''

        export_path = os.path.join(BASE_DIR, 'lib')

        help1 = ' '.join(['runner.py', '<product>', '<config>', '-m',
                            '<module pattern>', '-M', '<test method>', '-t',
                            '[tag tag...]'])
        help2 = ' '.join(['runner.py', '<product>', '<config>', '-p',
                            '[package package...]', '-M',
                            '<method name pattern>'])
        help3 = ' '.join(['runner.py', '<product>', '<config>', '-p',
                            '[package package...]', '-M',
                            '<method name pattern>', '-t', '[tag tag...]'])
        help4 = ' '.join(['runner.py', '<product>', '<config>', '-p',
                            '[package package...]', '-m', '<module pattern>',
                            '-M', '<test method>', '-t', '[tag tag...]'])

        usage_string = """
        *run all the tests for a product
        runner.py <product> <config>

        *run all the tests for a product with matching module name pattern
        runner.py <product> <config> -m <module pattern>

        *run all the tests for a product with matching the method name pattern
        runner.py <product> <config> -M <method name pattern>

        *run all the tests for a product with matching tag(s)
        runner.py <product> <config> -t [tag tag...]

        *run all the tests for a product with matching the method name pattern
        and matching tag(s)
        runner.py <product> <config> -M <method name pattern> -t [tag tag...]

        *run all the tests for a product with matching module name pattern,
        method name pattern and matching tag(s)
        %s

        **run all modules in a package(s) for a product
        runner.py <product> <config> -p [package package...]

        **run all modules in a package(s) for a product matching a name pattern
        runner.py <product> <config> -p [package package...] -m <module pattern>

        **run all modules in a package(s) for a product with matching the method
        name pattern
        %s

        **run all modules in a package(s) for a product with matching tag(s)
        runner.py <product> <config> -p [package package...] -t [tag tag...]

        **run all modules in a package(s) for a product with matching the method
        name pattern and matching tag(s)
        %s

        **run all modules in a package(s) for a product with matching module
        name pattern, method name pattern and matching tag(s)
        %s

        *list tests for a product
        runner.py <product> -l <tests>

        *list configs for a product
        runner.py <product> -l <configs>

        *list tests and configs for a product
        runner.py <product> -l <tests> <configs>

        notes:
        SET YOUR PYTHON PATH!
        export PYTHONPATH=$PYTHONPATH:%s

        TAGS:
        format: -t [+] tag1 tag2 tag3 key1=value key2=value
        By default tests with that match any of the tags will be returned.
        Sending a '+' as the first character in the tag list will only
        returned all the tests that match all the tags.

        config file and optional module name given on the command line
        do not have .config and .py extensions respectively.

        by default if no packages are specified, all tests under the
        product's test repo folder will be run.

        runner will search under the products testrepo folder for the
        package so full dotted package paths are not necessary on the
        command line.

        if a module is specified, all modules matching the name pattern
        will be run under the products test repo folder or packages (if
        specified).
        """ % (help1, help2, help3, help4, export_path)

        desc = "Cloud Common Automated Engine Framework"

        argparser = argparse.ArgumentParser(usage=usage_string,
                                            description=desc)

        argparser.add_argument('product',
                               metavar='<product>',
                               help='product name')
        argparser.add_argument('config',
                               nargs='?',
                               default=None,
                               metavar='<config_file>',
                               help='product test config')
        argparser.add_argument('-q', '--quiet',
                               default=2,
                               action='store_const',
                               const=1,
                               help="quiet")
        argparser.add_argument('-f', '--fail-fast',
                               default=False,
                               action='store_true',
                               help="fail fast")
        argparser.add_argument('-s', '--supress-load-tests',
                               default=False,
                               action='store_true',
                               dest='supress_flag',
                               help="supress load tests method")
        argparser.add_argument('-p', '--packages',
                               nargs='*',
                               default=None,
                               metavar='[package(s)]',
                               help="test package(s) in the product's "
                                    "test repo")
        argparser.add_argument('-m', '--module',
                               default=None,
                               metavar='<module>',
                               help="test module regex - defaults to '*.py'")
        argparser.add_argument('-M', '--method-regex',
                               default=None,
                               metavar='<method>',
                               help="test method regex defaults to 'test_'")
        argparser.add_argument('-t', '--tags',
                               nargs='*',
                               default=None,
                               metavar='tags',
                               help="tags")
        argparser.add_argument('-l', '--list',
                               nargs='+',
                               choices=['tests', 'configs'],
                               metavar='<tests> <configs>',
                               help='list tests and or configs')
        argparser.add_argument('--generateXML',
                               help="generates and xml of the testsuite run")
        argparser.add_argument('--parallel',
                               action="store_true",
                               default=False)
        argparser.add_argument('--data-directory',
                               help="directory for tests to get data from")

        args = argparser.parse_args()
        return args

    def log_results(self, result):
        '''
            @summary: Replicates the printing functionality of unittest's
            runner.run() but log's instead of prints
        '''
        expected_fails = unexpected_successes = skipped = 0
        try:
            results = map(len, (result.expectedFailures,
                                result.unexpectedSuccesses,
                                result.skipped))
            expected_fails, unexpected_successes, skipped = results
        except AttributeError:
            pass
        infos = []

        if not result.wasSuccessful():
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                infos.append("failures=%d" % failed)
            if errored:
                infos.append("errors=%d" % errored)
            self.log_errors('ERROR', result, result.errors)
            self.log_errors('FAIL', result, result.failures)
            self.log.info("Ran %d Tests" % result.testsRun)
            self.log.info('FAILED ')
        else:
            self.log.info("Ran %d Tests" % result.testsRun)
            self.log.info("Passing all tests")

        if skipped:
            infos.append("skipped=%d" % skipped)
        if expected_fails:
            infos.append("expected failures=%d" % expected_fails)
        if unexpected_successes:
            infos.append("unexpected successes=%d" % unexpected_successes)
        if infos:
            self.log.info(" (%s)\n" % (", ".join(infos),))
        else:
            self.log.info("\n")
        
        # Write out the log dir at the end so it's easy to find                    
        print(self.colorize('=', WHITE) * 150)
        print(self.colorize("Detailed logs: {0}".format(os.getenv("CLOUDCAFE_LOG_PATH")), WHITE))
        print(self.colorize('-', WHITE) * 150)
        

    def log_errors(self, label, result, errors):
        border1 = ''.join(['\n', '=' * 45, '\n'])
        border2 = ''.join(['-' * 45, '\n'])

        for test, err in errors:
            msg = "%s: %s\n" % (label, result.getDescription(test))
            self.log.info(''.join([border1, msg, border2, err]))

    def tree(self, directory, padding, print_files=False):
        '''
        creates an ascii tree for listing files or configs
        '''

        files = []

        #dir_token = '+-'
        #file_token = '>'

        print self.colorize(''.join([padding[:-1], '+-']), WHITE),
        print self.colorize(os.path.basename(os.path.abspath(directory)), RED),
        print self.colorize('/', WHITE)

        padding = ''.join([padding, ' '])

        if print_files:
            try:
                files = os.listdir(directory)
            except OSError:
                print self.colorize('Config directory: {0} Does Not Exist'.format(directory), HIGHLIGHTED_RED)
        else:
            files = [x for x in os.listdir(directory) if
                     os.path.isdir(DIR_SEPR.join([directory, x]))]
        count = 0
        for file_name in files:
            count += 1
            path = DIR_SEPR.join([directory, file_name])
            if os.path.isdir(path):
                if count == len(files):
                    self.tree(path, ''.join([padding, ' ']), print_files)
                else:
                    self.tree(path, ''.join([padding, '|']), print_files)
            else:
                if file_name.find('.pyc') == -1 and \
                file_name != '__init__.py':
                    print self.colorize(''.join([padding, file_name]), WHITE)

    def set_env(self, config_path, log_path, data_dir):
        '''
        sets an environment var so the tests can find their respective
        product config path
        '''
        os.environ['CCTNG_CONFIG_FILE'] = "{0}{1}configs{1}engine.config".format(BASE_DIR, DIR_SEPR)
        os.environ['OSTNG_CONFIG_FILE'] = config_path
        os.environ['CLOUDCAFE_LOG_PATH'] = log_path
        os.environ['CLOUDCAFE_DATA_DIRECTORY'] = data_dir
        print
        print self.colorize('=', WHITE) * 150
        print(self.colorize("Percolated Configuration", WHITE)) 
        print self.colorize('-', WHITE) * 150
        print(self.colorize("CCTNG_CONFIG_FILE.......: {0}{1}configs{1}engine.config".format(BASE_DIR, DIR_SEPR), WHITE))
        print(self.colorize("OSTNG_CONFIG_FILE.......: {0}".format(config_path), WHITE))
        print(self.colorize("CLOUDCAFE_DATA_DIRECTORY: {0}".format(data_dir), WHITE))
        print(self.colorize("CLOUDCAFE_LOG_PATH......: {0}".format(log_path), WHITE))
        print self.colorize('=', WHITE) * 150

    def get_safe_file_date(self):
        '''
        @summary: Builds a date stamp that is safe for use in a file path/name
        @return: The safely formatted datetime string
        @rtype: C{str}
        '''
        return str(datetime.now()).replace(' ', '_').replace(':', '_')

    def get_repo_path(self, product):
        '''
        returns the base string for the test repo directory
        '''

        repo_path = ''

        if product is not None:
            repo_path = os.path.join("{0}".format(test_repo.__path__[0]),
                                     product)

        return repo_path

    def get_config_path(self, parent_path, product, cfg_file_name):
        '''
        returns the base string for the config path
        '''

        cfg_path = ''

        if product is not None and cfg_file_name is not None:
            if cfg_file_name.find('.config') == -1:
                cfg_file_name = '.'.join([cfg_file_name, 'config'])

            cfg_path = os.path.join(parent_path,
                                    'configs',
                                    product,
                                    cfg_file_name)

        return cfg_path

    def get_dotted_path(self, path, split_token):
        '''
        creates a dotted path for use by unittest's loader
        '''
        try:
            position = len(path.split(split_token)) - 1
            temp_path = "{0}{1}".format(split_token,
                                        path.split(split_token)[position])
            split_path = temp_path.split(DIR_SEPR)
            dotted_path = '.'.join(split_path)

        except AttributeError:
            return None
        except Exception:
            return None
        return dotted_path

    def find_root(self, path, target):
        '''
        walks the path searching for the target root folder.
        '''
        root_path = None
        for root, _, _ in os.walk(path):
            if os.path.basename(root).find(target) != -1:
                root_path = root
                break
            else:
                continue
        return root_path

    def find_file(self, path, target):
        '''
        walks the path searching for the target file. the full to the target
        file is returned
        '''
        file_path = None
        for root, _, files in os.walk(path):
            for file_name in files:
                if file_name.find(target) != -1 \
                and file_name.find('.pyc') == -1:
                    file_path = DIR_SEPR.join([root, file_name])
                    break
                else:
                    continue
        return file_path

    def find_subdir(self, path, target):
        '''
        walks the path searching for the target subdirectory.
        the full to the target subdirectory is returned
        '''
        subdir_path = None
        for root, dirs, _ in os.walk(path):
            for dir_name in dirs:
                if dir_name.find(target) != -1:
                    subdir_path = DIR_SEPR.join([root, dir_name])
                    break
                else:
                    continue
        return subdir_path

    #this may be used later
    def drill_path(self, path, target):
        '''
        walks the path searching for the last instance of the target path.
        '''
        return_path = {}
        for root, _, _ in os.walk(path):
            if os.path.basename(root).find(target) != -1:
                return_path[target] = root
        return return_path

    def colorize(self, msg, color):
        '''
        colorizes a string
        '''
        end = '\033[1;m'
        colorized_msg = ''.join([color, str(msg), end])
        return colorized_msg

    def error_msg(self, e_type, e_msg):
        '''
        creates an error message
        '''
        err_msg = ' '.join(['<[ WARNING', str(e_type), 'ERROR:', str(e_msg),
                            ']>'])
        return err_msg

    def load_module(self, module_path):
        '''
        uses imp to load a module
        '''
        loaded_module = None

        module_name = os.path.basename(module_path)
        package_path = os.path.dirname(module_path)

        pkg_name = os.path.basename(package_path)
        root_path = os.path.dirname(package_path)

        if module_name.find('.py') != -1:
            module_name = module_name.split('.')[0]

        f, p_path, description = imp.find_module(pkg_name, [root_path])
        loaded_pkg = imp.load_module(pkg_name, f, p_path, description)

        f, m_path, description = imp.find_module(module_name,
                                                 loaded_pkg.__path__)

        try:
            mod = '.'.join([loaded_pkg.__name__, module_name])
            loaded_module = imp.load_module(mod, f, m_path, description)
        except ImportError:
            raise

        return loaded_module

    def get_class_names(self, loaded_module):
        '''
        gets all the class names in an imported module
        '''
        class_names = []
        # This has to be imported here as runner sets an environment variable
        # That will be required by the BaseTestFixture
        from cafe.drivers.unittest.fixtures import BaseTestFixture

        for _, obj in inspect.getmembers(loaded_module, inspect.isclass):
            temp_obj = obj
            try:
                while temp_obj.__base__ != object:
                    if temp_obj.__base__ == unittest.TestCase \
                        or temp_obj.__base__ == BaseTestFixture \
                        and temp_obj != obj.__base__:
                        class_names.append(obj.__name__)
                        break
                    else:
                        temp_obj = temp_obj.__base__
            except AttributeError:
                continue

        return class_names

    def get_class(self, loaded_module, test_class_name):
        to_return = None
        try:
            to_return = getattr(loaded_module, test_class_name)
        except AttributeError, e:
            print e
            return to_return
        return to_return

    def get_modules(self, rootdir, module_regex):
        '''
        generator yields modules matching the module_regex
        '''
        for root, _, files in os.walk(rootdir):
            for name in files:
                if fnmatch.fnmatch(name, module_regex) \
                    and name.find('init') == -1 \
                    and name.find('.pyc') == -1:
                    file_name = name.split('.')[0]
                    full_path = '/'.join([root, file_name])
                    yield full_path

    def check_attrs(self, method, attrs, attr_keys, token=None):
        '''
        checks to see if the method passed in has matching key=value
        attributes. if a '+' token is passed only method that contain
        foo and bar will be match
        '''
        truth_values = []
        for attr_key in attr_keys:
            if method.__dict__.has_key(attr_key):
                method_val = method.__dict__[attr_key]
                attr_val = attrs[attr_key]
                truth_values[len(truth_values):] = [method_val == attr_val]
            else:
                truth_values[len(truth_values):] = [False]
        temp = ''
        if token == '+':
            temp = 'False not in'
        else:
            temp = 'True in'
        eval_string = ' '.join([temp, 'truth_values'])
        return eval(eval_string)

    def check_tags(self, method, tags, token):
        '''
        checks to see if the method passed in has matching tags.
        if the tags are (foo, bar) this method will match foo or
        bar. if a '+' token is passed only method that contain
        foo and bar will be match
        '''
        truth_values = []
        for tag in tags:
            if hasattr(method, tag):
                truth_values[len(truth_values):] = [True]
            else:
                truth_values[len(truth_values):] = [False]

        temp = ''
        if token == '+':
            temp = 'False not in'
        else:
            temp = 'True in'
        eval_string = ' '.join([temp, 'truth_values'])
        return eval(eval_string)

    def _parse_tags(self, tags):
        '''
        tags sent in from the command line are sent in as a string.
        returns a list of tags and a '+' token if it is present.
        '''
        token = None
        tag_list = []
        attrs = {}

        if tags[0] == '+':
            token = tags[0]
            tags = tags[1:]

        for tag in tags:
            tokens = tag.split('=')
            if len(tokens) > 1:
                attrs[tokens[0]] = tokens[1]
            else:
                tag_list[len(tag_list):] = [tag]

        return tag_list, attrs, token

    def build_suite(self, loaded_module, method_regex, cl_tags, supress_flag):
        '''
        loads the found tests and builds the test suite
        '''
        tag_list = []
        attrs = {}
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        class_names = self.get_class_names(loaded_module)

        module_path = os.path.dirname(loaded_module.__file__)
        module_name = loaded_module.__name__.split('.')[1]
        base_dotted_path = self.get_dotted_path(module_path, test_repo.__name__)

        if cl_tags is not None:
            tag_list, attrs, token = self._parse_tags(cl_tags)

        attr_keys = attrs.keys()
        a_len = len(attr_keys)
        t_len = len(tag_list)

        if hasattr(loaded_module, 'load_tests') and \
            supress_flag is False and \
            method_regex == 'test_*' and cl_tags is None:
            load_tests = getattr(loaded_module, 'load_tests')
            suite.addTests(load_tests(loader, None, None))
            return suite

        for test_class_name in class_names:
            class_ = self.get_class(loaded_module, test_class_name)

            for method_name in dir(class_):
                load_test_flag = False
                attr_flag = False
                tag_flag = False

                if fnmatch.fnmatch(method_name, method_regex):
                    if cl_tags is None:
                        load_test_flag = True
                    else:
                        method = getattr(class_, method_name)
                        if dict(method.__dict__):
                            if t_len != 0 and a_len == 0:
                                tag_flag = self.check_tags(method,
                                                           tag_list,
                                                           token)
                                load_test_flag = tag_flag
                            elif t_len == 0 and a_len != 0:
                                attr_flag = self.check_attrs(method,
                                                             attrs,
                                                             attr_keys,
                                                             token)
                                load_test_flag = attr_flag
                            elif t_len != 0 and a_len != 0:
                                tag_flag = self.check_tags(method,
                                                           tag_list,
                                                           token)
                                attr_flag = self.check_attrs(method,
                                                             attrs,
                                                             attr_keys,
                                                             token)
                                load_test_flag = attr_flag and tag_flag
                        else:
                            continue

                    if load_test_flag is True:
                        try:
                            dotted_path = '.'.join([base_dotted_path,
                                                    module_name,
                                                    test_class_name,
                                                    method_name])
                            suite.addTest(loader.loadTestsFromName(
                                dotted_path))
                        except ImportError:
                            raise
                        except AttributeError:
                            raise
                        except Exception:
                            raise
        return suite

    def print_traceback(self):
        '''
        formats and prints out a minimal stack trace
        '''
        info = sys.exc_info()
        excp_type, excp_value = info[:2]
        err_msg = self.error_msg(excp_type.__name__,
                                 excp_value)
        print self.colorize(err_msg, HIGHLIGHTED_RED)
        for file_name, lineno, function, text in \
            traceback.extract_tb(info[2]):
            print ">>>", file_name
            print "  > line", lineno, "in", function, \
                repr(text)
        print "-" * 100

    def run(self):
        '''
        loops through all the packages, modules, and methods sent in from
        the command line and runs them
        '''
        test_classes = []
        cl_args = self.get_cl_args()
        module_regex = None

        if os.path.exists(BASE_DIR) is False:
            err_msg = self.error_msg("{0} does not exist - Exiting".
                                        format(BASE_DIR))
            print self.colorize(err_msg, HIGHLIGHTED_RED)
            exit(1)

        if cl_args.module is None:
            module_regex = '*.py'
        else:
            if cl_args.module.find('.py') != -1:
                module_regex = cl_args.module
            else:
                module_regex = '.'.join([cl_args.module, 'py'])

        if cl_args.method_regex is None:
            method_regex = 'test_*'
        else:
            if cl_args.method_regex.find('test_') != -1:
                method_regex = cl_args.method_regex
            else:
                method_regex = ''.join(['test_', cl_args.method_regex])

        parent_path = BASE_DIR

        config_path = self.get_config_path(parent_path,
                                           cl_args.product,
                                           cl_args.config)

        repo_path = self.get_repo_path(cl_args.product)

        if os.path.exists(repo_path) is False:
            err_msg = self.error_msg('Repo', ' '.join([cl_args.product,
                                     repo_path,
                                     'does not exist - Exiting']))
            print self.colorize(err_msg, HIGHLIGHTED_RED)
            exit(1)

        if cl_args.list is not None:
            for arg in cl_args.list:
                if arg == 'tests':
                    banner = ''.join(['\n', '<[TEST REPO]>', '\n'])
                    path = repo_path
                else:
                    banner = ''.join(['\n', '<[CONFIGS]>', '\n'])
                    path = os.path.join(parent_path, 'configs', cl_args.product)

                print self.colorize(banner, WHITE)
                self.tree(path, ' ', print_files=True)
        else:
            suite = unittest.TestSuite()
            master_suite = unittest.TestSuite()
            
            #Use the parallel runner if needed so the console logs look correct
            if cl_args.parallel:
                test_runner = CCParallelTextTestRunner(verbosity=cl_args.quiet)
            else:
                test_runner = unittest.TextTestRunner(verbosity=cl_args.quiet)
                
            test_runner.failfast = cl_args.fail_fast

            #-----------------------Debug Logger-----------------------------
            #this is for the debug logger. its breaking right now
            #test_runner = LogCaptureRunner(verbosity=cl_args.quiet)
            #-----------------------Debug Logger-----------------------------

            try:
                stats_log_path  = '/'.join(
                                   [LOG_BASE_PATH,
                                   cl_args.product,
                                   cl_args.config,
                                   "statistics"])
 
                product_log_path = '/'.join(
                                   [LOG_BASE_PATH,
                                   cl_args.product,
                                   cl_args.config,
                                   self.get_safe_file_date()])

            except TypeError:
                print 'Config was not set on command line - Exiting'
                exit(1)

            if os.path.isdir(stats_log_path) is not True:
                os.makedirs(stats_log_path)
            if os.path.isdir(product_log_path) is not True:
                os.makedirs(product_log_path)

            #Get and then ensure the existence of the cc data directory
            data_dir = None
            user_data_dir = getattr(cl_args, 'data_directory', None)
            if user_data_dir is not None:
                #Quit if the data directory is user-defined and doesn't exist,
                #otherwise it uses the user defined data dir
                user_data_dir = os.path.expanduser(user_data_dir)
                if os.path.isdir(user_data_dir):
                    data_dir = user_data_dir
                else:
                    print "Data directory '{0}' does not exist. Exiting."\
                            .format(user_data_dir)
                    exit(1)
            else:
                #Make and use the default directory if it doesn't exist
                '''
                @TODO:  Make this create a sub-directory based on the product
                        name like the log_dir does (minus timestamps and config
                        file name)
                '''
                data_dir = DATA_DIR
                if not os.path.isdir(data_dir):
                    os.makedirs(data_dir)

            self.set_env(config_path, product_log_path, data_dir)

            if cl_args.packages is None:
                for module in self.get_modules(repo_path, module_regex):
                    try:
                        loaded_module = self.load_module(module)
                    except ImportError:
                        self.print_traceback()
                        continue

                    try:
                        suite = self.build_suite(loaded_module,
                                                 method_regex,
                                                 cl_args.tags,
                                                 cl_args.supress_flag)
                        master_suite.addTests(suite)
                        test_classes.append(suite)
                    except ImportError:
                        self.print_traceback()
                        continue
                    except AttributeError:
                        self.print_traceback()
                        continue
                    except Exception:
                        self.print_traceback()
                        continue
            else:
                for package_name in cl_args.packages:

                    test_path = self.find_subdir(repo_path, package_name)

                    if test_path is None:
                        err_msg = self.error_msg('Package', package_name)
                        print self.colorize(err_msg, HIGHLIGHTED_RED)
                        continue

                    for module_path in self.get_modules(test_path,
                                                        module_regex):
                        try:
                            loaded_module = self.load_module(module_path)
                        except ImportError:
                            self.print_traceback()
                            continue

                        try:
                            suite = self.build_suite(loaded_module,
                                                     method_regex,
                                                     cl_args.tags,
                                                     cl_args.supress_flag)
                            master_suite.addTests(suite)
                            test_classes.append(suite)
                        except ImportError:
                            self.print_traceback()
                            continue
                        except AttributeError:
                            self.print_traceback()
                            continue
                        except Exception:
                            self.print_traceback()
                            continue

            if cl_args.parallel:
                unittest.installHandler()
                threads = []
                results = []
                start = time.time()
                for test in test_classes:
                    t = ThreadedRunner(test_runner, test, results)
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
                finish = time.time()
                print '=' * 71
                print 'Tests Complete.'
                print '=' * 71

                run = 0
                errors = 0
                failures = 0
                for result in results:
                    run += result.testsRun
                    errors += len(result.errors)
                    failures += len(result.failures)

                print ("Ran %d test%s in %.3fs" % (run, run != 1 and "s" or "", finish - start))
                if failures:
                    print("Failures=%d" % failures)
                if errors:
                    print("Errors=%d" % errors)
                if failures or errors:
                    exit(1)
            else:
                unittest.installHandler()
                start_time = time.time()
                result = test_runner.run(master_suite)
                total_execution_time = time.time() - start_time

                if cl_args.generateXML is not None:
                    xml_path = ''.join([parent_path, cl_args.generateXML])
                    parse_res = ParseResult(vars(result), master_suite, xml_path,
                                            total_execution_time)

                    parse_res.generate_xml_report()

                self.log_results(result)
                if not result.wasSuccessful():
                    exit(1)

                
class ThreadedRunner(threading.Thread):
    def __init__(self, runner, test, results):
        super(ThreadedRunner, self).__init__()
        self.runner = runner
        self.test = test
        self.results = results

    def run(self):
        self.results.append(self.runner.run(self.test))


def entry_point():
    print('\n'.join(["\t\t     ( (",
                     "\t\t        ) )",
                     "\t\t     .........    ",
                     "\t\t     |       |___ ",
                     "\t\t     |       |_  |",
                     "\t\t     |  :-)  |_| |",
                     "\t\t     |       |___|",
                     "\t\t     |_______|",
                     "\t\t === CAFE Runner ==="]))
    print("\t\t--------------------------------------------------------")
    print("\t\tBrewing from {0}".format(BASE_DIR))
    print("\t\t--------------------------------------------------------")
    print
    runner = CCRunner()
    runner.run()
    exit(0)
