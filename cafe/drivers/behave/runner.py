import argparse
import os
import subprocess
import sys
from cafe.configurator.managers import TestEnvManager

def entry_point():
 
    # Set up arguments
    argparser = argparse.ArgumentParser(prog='behave-runner')

    argparser.add_argument(
        "product",
        nargs=1,
        metavar="<product>",
        help="Product name")

    argparser.add_argument(
        "config",
        nargs=1,
        metavar="<config_file>",
        help="Product test config")
    
    argparser.add_argument(
        dest='behave_opts',
        nargs=argparse.REMAINDER,
        metavar="<behave_opts>",
        help="Options to pass to Behave")

    args = argparser.parse_args()
    config = str(args.config[0])
    product = str(args.product[0])
    behave_opts = args.behave_opts
    
    test_env_manager = TestEnvManager(product, config)
    test_env_manager.finalize()
            
    product_root_test_path = os.path.join(test_env_manager.test_repo_path, product)
    
    """
    Attempts to use first positional argument after product config as a sub-path to the test repo path.
    If not a sub-path, raise exception.
    """
    if behave_opts and not behave_opts[0].startswith('-'):
        user_provided_path = behave_opts[0]
        attempted_sub_path = os.path.join(product_root_test_path, user_provided_path.lstrip(os.path.sep))

        if os.path.exists(attempted_sub_path):
            behave_opts[0] = attempted_sub_path
        else:
            raise Exception("{directory} is not a sub-path in the {repo} repo.".format(directory=behave_opts[0], repo=test_env_manager.test_repo_package))
    else:
        behave_opts.insert(0, product_root_test_path)

    print_mug(behave_opts[0])
    behave_opts.insert(0, "behave")
    
    proc = subprocess.call(behave_opts) 
    
    exit(0)

def print_mug(base_dir):
    brew = "Brewing from {0}".format(base_dir)

    mug0 = "      ( ("
    mug1 = "       ) )"
    mug2 = "    ........."
    mug3 = "    |       |___"
    mug4 = "    |       |_  |"
    mug5 = "    |  :-)  |_| |"
    mug6 = "    |       |___|"
    mug7 = "    |_______|"
    mug8 = "=== CAFE Behave Runner ==="

    print "\n{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}".format(
        mug0,
        mug1,
        mug2,
        mug3,
        mug4,
        mug5,
        mug6,
        mug7,
        mug8)

    print "-" * len(brew)
    print brew
    print "-" * len(brew)

if __name__ == '__main__':
    entry_point()
