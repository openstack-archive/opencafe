import sys
import unittest
from cafe.drivers.unittest.brew.parser import (
    _WriteOnceDict, _ImportablePathWrapper, DuplicateItemException,
    MalformedClassImportPathError, ModuleNotImportableError,
    ClassNotImportableError, _Brew, BrewMissingTestClassesError)


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
            MalformedClassImportPathError, _ImportablePathWrapper,
            'unittest/TestCase')

    def test_raises_ClassNotImportableError_on_non_existant_class(self):
        i = _ImportablePathWrapper("collections.aaaaDoesNotExistaaa")
        self.assertRaises(
            ClassNotImportableError, i.import_class)

    def test_raises_ModuleNotImportableError_on_non_existant_module(self):
        i = _ImportablePathWrapper("aaaa.aaaa.aaaa")
        self.assertRaises(
            ModuleNotImportableError, i.import_module)

    def test_import_module_happy_path(self):
        i = _ImportablePathWrapper("collections.OrderedDict")
        m = i.import_module()
        assert type(m.OrderedDict()).__name__ == 'OrderedDict'

    def test_import_class_happy_path(self):
        i = _ImportablePathWrapper("collections.OrderedDict")
        c = i.import_class()
        assert type(c()).__name__ == 'OrderedDict'


class Brew_Tests(unittest.TestCase):
    test_fixture = "unittest.TestCase"
    test_class = "collections.OrderedDict"
    dsl = "cafe.drivers.unittest.datasets.DatasetList"
    module_name = "FakeBrew"

    def test_init_raises_BrewMissingTestClassesError_empty_test_cases(self):
        self.assertRaises(
            BrewMissingTestClassesError, _Brew, "FakeBrew",
            "collections.OrderedDict", "collections.OrderedDict", [])

    def test_init_raises_BrewMissingTestClassesError_non_iterable(self):
        self.assertRaises(
            BrewMissingTestClassesError, _Brew, "FakeBrew",
            "collections.OrderedDict", "collections.OrderedDict", None)

    def test_init_BrewMissingTestClassesError_True_non_iterable(self):
        self.assertRaises(
            BrewMissingTestClassesError, _Brew, "FakeBrew",
            "collections.OrderedDict", "collections.OrderedDict", True)

    def test_generate_module(self):
        b = _Brew(
            self.module_name, self.test_fixture, self.dsl,
            [self.test_class])

        m = b._generate_module(self.module_name)
        assert type(m).__name__ == 'module', (
            "_generate_module did not return a module")

    def test_module_registration(self):
        b = _Brew(
            self.module_name, self.test_fixture, self.dsl,
            [self.test_fixture])

        m = b._generate_module(self.module_name)
        b._register_module(m)
        self.assertIn(
            self.module_name, sys.modules.keys(),
            "_register_module failed to register {} in sys.modules")
