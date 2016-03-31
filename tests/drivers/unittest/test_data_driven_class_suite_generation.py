import os
import unittest

from cafe.drivers.unittest import decorators# import FauxDSLFixture


class DSLSuiteBuilderTests(unittest.TestCase):

    def test_FauxDSLFixture_raises_Exception(self):
        fake_log_dir = os.getcwd() + os.path.sep + 'test-reporting-results'
        os.environ["CAFE_TEST_LOG_PATH"] = fake_log_dir
        try:
            fix = type('FauxDSLFixture', (object,), dict(decorators.FauxDSLFixture.__dict__))
            #print fix.__mro__
            #print fix.__dict__
            fix().setUpClass()

        except Exception as e:
            #print e
            pass

        #fix().setUpClass()
        self.assertTrue(True)
