import os
import time
from cafe.configurator.managers import TestEnvManager
from cafe.common.reporting import cclogging
from cafe.drivers.base import print_exception, get_error
from cafe.drivers.unittest.brew.arguments import ArgumentParser
from cafe.drivers.unittest.brew.parser import BrewFile
from cafe.drivers.unittest.runner_parallel import UnittestRunner
from cafe.drivers.unittest.suite_builder import SuiteBuilder


class BrewRunner(UnittestRunner):
    """OpenCafe BrewFile Runner"""
    def __init__(self):
        self.print_mug()
        self.cl_args = ArgumentParser().parse_args()
        self.test_env = TestEnvManager(
            "", self.cl_args.config, test_repo_package_name="")
        self.test_env.test_data_directory = self.test_env.test_data_directory
        self.test_env.finalize()
        cclogging.init_root_log_handler()

        # This is where things diverge from the regular parallel runner
        # Extract the runfile contents
        self._log = cclogging.getLogger(
            cclogging.get_object_namespace(self.__class__))
        self.datagen_start = time.time()
        self.run_file = BrewFile(self.cl_args.runfiles)

        # TODO: Once the parallel_runner is changed to a yielding model,
        #       change this to yielding brews instead of generating a list
        self.suites = SuiteBuilder(
            testrepos=self.run_file.brew_modules(),
            dry_run=self.cl_args.dry_run,
            exit_on_error=True).get_suites()

        self.print_configuration(self.test_env, runfile=self.run_file)

    def print_configuration(self, test_env, repos=None, runfile=None):
        """Prints the config/logs/repo/data_directory"""
        print("=" * 150)
        print("Percolated Configuration")
        print("-" * 150)
        if runfile:
            print("BREW FILES........:")
            print("\t\t    " + "\n\t\t    ".join(runfile.files))
            if self.cl_args.verbose == 3:
                print("BREWS............:")
                print "\t" + "\n\t".join(runfile.brews_to_strings())
        if repos:
            print("BREWING FROM: ....: {0}".format(repos[0]))
            for repo in repos[1:]:
                print("{0}{1}".format(" " * 20, repo))
        self._log.debug(str(runfile))
        print("ENGINE CONFIG FILE: {0}".format(test_env.engine_config_path))
        print("TEST CONFIG FILE..: {0}".format(test_env.test_config_file_path))
        print("DATA DIRECTORY....: {0}".format(test_env.test_data_directory))
        print("LOG PATH..........: {0}".format(test_env.test_log_dir))
        print("=" * 150)

    @staticmethod
    def print_mug():
        """Prints the cafe mug"""
        print("""
        /~~~~~~~~~~~~~~~~~~~~~~~/|
       /              /######/ / |
      /              /______/ /  |
     ========================= /||
     |_______________________|/ ||
      |  \****/     \__,,__/    ||
      |===\**/       __,,__     ||
      |______________\====/%____||
      |   ___        /~~~~\ %  / |
     _|  |===|===   /      \%_/  |
    | |  |###|     |########| | /
    |____\###/______\######/__|/
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
===      CAFE Brewfile Runner      ===""")


def entry_point():
    """setup.py script entry point"""
    try:
        runner = BrewRunner()
        exit(runner.run())
    except KeyboardInterrupt:
        print_exception(
            "BrewRunner", "run", "Keyboard Interrupt, exiting...")
        os.killpg(0, 9)
