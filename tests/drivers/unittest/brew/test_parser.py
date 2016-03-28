import unittest
from cafe.drivers.unittest.brew.parser import (
    _WriteOnceDict, _Importable, DuplicateItemException,
    MalformedClassImportPathError)


class WriteOnceDict_Tests(unittest.TestCase):

    def test_assigning_a_key_the_first_time_passes(self):
        wod = _WriteOnceDict()
        try:
            wod['key'] = 'value'
        except Exception:
            self.fail(
                "_WriteOnceDict unexpectedly raised an exception on "
                "initial aassignment.")

    def test_reassigning_a_key_raises_DuplicateItemException(self):
        wod = _WriteOnceDict()
        wod['key'] = 'value'
        try:
            wod['key'] = 'value2'
        except DuplicateItemException:
            return
        except Exception:
            self.fail(
                "_WriteOnceDict raised an incorrect exception on "
                "reassignment")


class Importable_Tests(unittest.TestCase):

    def test_raises_MalformedClassImportPathError_on_malformed_path(self):
        self.assertRaises(
            MalformedClassImportPathError, _Importable, 'unittest/TestCase')
