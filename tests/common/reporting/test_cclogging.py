import unittest
import mock
from uuid import uuid4
from requests import Response
import logging
from cafe.common.reporting.cclogging import getLogger as CC_getLogger
from cafe.common.reporting.cclogging import init_root_log_handler as IRLH


def mock_os_getenv_verbose(*args, **kwargs):
    return 'VERBOSE'

def mock_os_getenv_standard(*args, **kwargs):
    return 'STANDARD'

def mock_os_getenv_unconfigured(*args, **kwargs):
    return None

@mock.patch('os.getenv', side_effect=mock_os_getenv_verbose)
def get_verbose_logger(log_name, *args, **kwargs):
    return CC_getLogger(log_name)

@mock.patch('os.getenv', side_effect=mock_os_getenv_standard)
def get_standard_logger(log_name, *args, **kwargs):
    return CC_getLogger(log_name)

@mock.patch('os.getenv', side_effect=mock_os_getenv_unconfigured)
def get_unconfigured_logger(log_name, *args, **kwargs):
    return CC_getLogger(log_name)


class BaseLoggerTestMixin(object):

    def call_getLogger(self, logger_func, calls=1):
        logger_name = str(uuid4())
        logger = None
        for n in range(0,calls):
            logger = logger_func(logger_name)
        return logger

    def assertHandlerCount(self, logger, expected_handler_count, msg=None):
        handler_count = len(logger.handlers)
        std_msg = "Logger had {0} handlers but should have had {1}".format(
                handler_count, expected_handler_count)

        if handler_count != expected_handler_count:
            self.fail(self._formatMessage(msg, std_msg))


class getLogger_Tests(object):

    def test_new_logger_verbose_env_1_handler(self):
        global get_verbose_logger
        logger = self.call_getLogger(get_verbose_logger, 1)
        self.assertHandlerCount(logger, 1)

    def test_existing_logger_verbose_env_1_handler_after_2_calls(self):
        global get_verbose_logger
        logger = self.call_getLogger(get_verbose_logger, 2)
        self.assertHandlerCount(logger, 1)


class Normal_getLogger_Tests(
    unittest.TestCase, getLogger_Tests, BaseLoggerTestMixin):

    def test_new_logger_unconfigured_env_0_handlers(self):
        global get_unconfigured_logger
        logger = self.call_getLogger(get_unconfigured_logger, 1)
        self.assertHandlerCount(logger, 0)

    def test_new_logger_standard_env_0_handlers(self):
        global get_standard_logger
        logger = self.call_getLogger(get_standard_logger, 1)
        self.assertHandlerCount(logger, 0)

    def test_existing_logger_standard_env_0_handlers_after_2_calls(self):
        global get_standard_logger
        logger = self.call_getLogger(get_standard_logger, 2)
        self.assertHandlerCount(logger, 0)

    def test_existing_logger_unconfigured_env_0_handlers_after_2_calls(self):
        global get_unconfigured_logger
        logger = self.call_getLogger(get_unconfigured_logger, 2)
        self.assertHandlerCount(logger, 0)


class Root_getLogger_Tests(
    unittest.TestCase, getLogger_Tests, BaseLoggerTestMixin):
    '''TODO: Change the verbose root logger tests to just make sure
    init_root_log_handler() gets called (mock it out) instead of checking
    for number of handlers.  (Do this after tests have been added for
    init_root_log_handler)
    '''

    def call_getLogger(self, logger_func, calls=1):
        #Always returns root log
        logger = None
        for n in range(0,calls):
            logger = logger_func(None, )
        return logger

    def init_handler_for_root_logger(self):
        logging.getLogger().addHandler(logging.NullHandler())

    def setUp(self):
        logging.getLogger().handlers = []

    def test_new_logger_unconfigured_env_0_handlers(self):
        global get_unconfigured_logger
        logger = self.call_getLogger(get_unconfigured_logger, 1)
        self.assertHandlerCount(logger, 0)

    def test_new_logger_standard_env_0_handlers(self):
        global get_standard_logger
        logger = self.call_getLogger(get_standard_logger, 1)
        self.assertHandlerCount(logger, 0)

    def test_initialized_root_logger_unconfigured_env_1_handlers_after_2_calls(
            self):
        global get_unconfigured_logger
        self.init_handler_for_root_logger()
        logger = self.call_getLogger(get_unconfigured_logger, 2)
        self.assertHandlerCount(logger, 1)

    def test_initialized_root_logger_standard_env_1_handlers_after_2_calls(
            self):
        global get_standard_logger
        self.init_handler_for_root_logger()
        logger = self.call_getLogger(get_standard_logger, 2)
        self.assertHandlerCount(logger, 1)

    def test_initialized_root_logger_verbose_env_1_handlers_after_2_calls(
            self):
        global get_verbose_logger
        self.init_handler_for_root_logger()
        logger = self.call_getLogger(get_verbose_logger, 2)
        self.assertHandlerCount(logger, 1)
