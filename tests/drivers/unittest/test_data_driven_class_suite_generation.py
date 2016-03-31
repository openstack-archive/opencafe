import os
import unittest

from cafe.drivers.unittest import decorators# import FauxDSLFixture


class DSLSuiteBuilderTests(unittest.TestCase):

    def test_FauxDSLFixture_raises_Exception(self):
        """Check that the FauxDSLFixture raises an exception as expected."""

        faux_fixture = type(
            'FauxDSLFixture',
            (object,),
            dict(decorators.FauxDSLFixture.__dict__))

        # Check that the fixture raises an exception
        with self.assertRaises(decorators.EmptyDSLError) as e:
            faux_fixture().setUpClass()

        # If it does, let's make sure the exception generates the correct
        # message.
        msg = (
            "The Dataset list used to generate this Data Driven Class was "
            "empty. No Fixtures or Tests were generated. Review the Dataset "
            "used to run this test.\n"
            "DatasetlList location: None\n\n"
            "The following 0 tests were not run\n\t")

        self.assertEquals(msg, e.exception.message)
