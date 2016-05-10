import importlib
import sys
import unittest
from cafe.drivers.unittest.brew.parser import (
    _ImportablePathWrapper, MalformedClassImportPathError,
    ModuleNotImportableError, ClassNotImportableError, _Brew,
    BrewMissingTestClassesError)


class ImportablePathWrapper_Tests(unittest.TestCase):

    def test_raises_MalformedClassImportPathError_on_malformed_path(self):
        self.assertRaises(
            MalformedClassImportPathError, _ImportablePathWrapper,
            'unittest/TestCase')

    def test_raises_ClassNotImportableError_on_non_existant_class(self):
        i = _ImportablePathWrapper("collections.aaaaDoesNotExistaaa")
        self.assertRaises(ClassNotImportableError, i.import_class)

    def test_raises_ModuleNotImportableError_on_non_existant_module(self):
        i = _ImportablePathWrapper("aaaa.aaaa.aaaa")
        self.assertRaises(ModuleNotImportableError, i.import_module)

    def test_import_module_happy_path(self):
        i = _ImportablePathWrapper("collections.OrderedDict")
        m = i.import_module()
        self.assertEqual(type(m.OrderedDict()).__name__, 'OrderedDict')

    def test_import_class_happy_path(self):
        i = _ImportablePathWrapper("collections.OrderedDict")
        c = i.import_class()
        self.assertEqual(type(c()).__name__, 'OrderedDict')


class Brew_Tests(unittest.TestCase):
    test_fixture = "unittest.TestCase"
    test_class = "collections.OrderedDict"
    dsl = "cafe.drivers.unittest.datasets.DatasetList"
    module_name = "FakeBrew"

    def test_init_name_only(self):
        try:
            _Brew(self.module_name)
        except:
            self.fail("Unable to instantiate Brew with only a name")

    def test_call_brew_initialized_with_only_a_name(self):
        b = _Brew(self.module_name)
        module_ = b()
        new_name = "FakeBrew_automodule"
        self.assertEquals(module_.__name__, new_name)

    def test_init_raises_BrewMissingTestClassesError_non_iterable(self):
        self.assertRaises(
            BrewMissingTestClassesError, _Brew, "FakeBrew",
            "collections.OrderedDict", "collections.OrderedDict", 1)

    def test_init_raises_BrewMissingTestClassesError_string(self):
        self.assertRaises(
            BrewMissingTestClassesError, _Brew, "FakeBrew",
            "collections.OrderedDict", "collections.OrderedDict", "string")

    def test_init_BrewMissingTestClassesError_bool_non_iterable(self):
        self.assertRaises(
            BrewMissingTestClassesError, _Brew, "FakeBrew",
            "collections.OrderedDict", "collections.OrderedDict", True)

    def test_generate_module_correct_type(self):
        b = _Brew(
            self.module_name, self.test_fixture, self.dsl,
            [self.test_class])

        m = b._generate_module(self.module_name)
        self.assertEqual(
            type(m).__name__, 'module',
            "_generate_module did not return a module")

    def test_generate_module_correct_name(self):
        b = _Brew(
            self.module_name, self.test_fixture, self.dsl,
            [self.test_class])

        m = b._generate_module(self.module_name)
        self.assertEqual(
            m.__name__, self.module_name,
            "_generate_module did not return a module with the correct name")

    def test_module_registration(self):
        b = _Brew(
            self.module_name, self.test_fixture, self.dsl,
            [self.test_fixture])

        m = b._generate_module(self.module_name)
        b._register_module(m)
        self.assertIn(
            self.module_name, sys.modules.keys(),
            "_register_module failed to register {} in sys.modules")

    def test_registered_module_is_importable(self):
        b = _Brew(
            self.module_name, self.test_fixture, self.dsl,
            [self.test_fixture])

        m = b._generate_module(self.module_name)
        b._register_module(m)
        try:
            importlib.import_module(m.__name__)
        except ImportError:
            self.fail("Unable to import registered module")

    def test_generate_test_class_name_and_fixture_only(self):
        b = _Brew(self.module_name, fixture_class=self.test_fixture)
        gclass = b._generate_test_class()
        self.assertEqual(gclass.__name__, b.name)
        self.assertEqual(gclass.__name__, self.module_name)
        self.assertTrue(issubclass(gclass, unittest.TestCase))
