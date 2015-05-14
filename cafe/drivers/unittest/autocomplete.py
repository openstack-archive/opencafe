import os
import importlib
import pkgutil

from cafe.configurator.managers import EngineConfigManager
from cafe.engine.config import EngineConfig

ENGINE_CONFIG = EngineConfig(
    os.environ.get("CAFE_ENGINE_CONFIG_FILE_PATH") or
    EngineConfigManager.ENGINE_CONFIG_PATH)


def print_configs():
    config_dir = os.path.abspath(os.path.expanduser(
        ENGINE_CONFIG.config_directory))
    for path, dirs, files in os.walk(config_dir):
        for file_ in files:
            if file_.endswith(".config"):
                print os.path.join(path, file_)[len(config_dir) + len(os.sep):]


def print_imports(string):
    import_paths = string.strip().rsplit(".", 1)
    if len(import_paths) == 1:
        for _, module_name, _ in pkgutil.iter_modules():
            if module_name.startswith(import_paths[0]):
                print module_name
    else:
        try:
            base = importlib.import_module(import_paths[0])
            for _, name, _ in pkgutil.iter_modules(base.__path__):
                if name.startswith(import_paths[1]):
                    print "{0}.{1}".format(import_paths[0], name)
        except:
            return


def print_products():
    try:
        base = importlib.import_module(ENGINE_CONFIG.default_test_repo)
        for _, name, _ in pkgutil.iter_modules(base.__path__):
                print name
    except:
        return


def print_configs_by_product(product):
    config_dir = os.path.join(
        os.path.abspath(os.path.expanduser(ENGINE_CONFIG.config_directory)),
        product)
    for path, dirs, files in os.walk(config_dir):
        for file_ in files:
            if file_.endswith(".config"):
                print os.path.join(path, file_)[len(config_dir) + len(os.sep):]
