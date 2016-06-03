import argparse
import sys
from cafe.drivers.unittest.arguments import ConfigAction, VerboseAction
from cafe.drivers.base import print_exception, get_error


class ArgumentParser(argparse.ArgumentParser):
    """
        Parses all arguments.
    """
    def __init__(self):
        desc = "Open Common Automation Framework Engine BrewFile Runner"
        usage_string = """
            cafe-brew <config> <runfile(s)>...
                [--failfast]
                [--dry-run]
                [--parallel=(class|test)]
                [--result=(json|xml)] [--result-directory=RESULT_DIRECTORY]
                [--verbose=VERBOSE]
                [--exit-on-error]
                [--workers=NUM]
                [--help]
            """

        super(ArgumentParser, self).__init__(
            usage=usage_string, description=desc)

        self.prog = "Argument Parser"

        self.add_argument(
            "config",
            action=ConfigAction,
            metavar="<config>",
            help="test config.  Looks in the .opencafe/configs directory."
                 "Example: bsl/uk.json")

        self.add_argument(
            "runfiles",
            nargs="*",
            default=[],
            metavar="<runfiles>...",
            help="A list of paths to opencafe runfiles.")

        self.add_argument(
            "--dry-run",
            action="store_true",
            help="dry run.  Don't run tests just print them.  Will run data"
                 " generators.")

        self.add_argument(
            "--failfast",
            action="store_true",
            help="fail fast")

        self.add_argument(
            "--verbose", "-v",
            action=VerboseAction,
            choices=[1, 2, 3],
            default=2,
            type=int,
            help="Set unittest output verbosity.")

        self.add_argument(
            "--parallel",
            choices=["class", "test"],
            help="Runs test in parallel by class grouping or test")

        self.add_argument(
            "--result",
            choices=["json", "xml", "subunit"],
            help="Generates a specified formatted result file")

        self.add_argument(
            "--result-directory",
            default="./",
            metavar="RESULT_DIRECTORY",
            help="Directory for result file to be stored")

        self.add_argument(
            "--workers",
            nargs="?",
            default=10,
            type=int,
            help="Set number of workers for --parallel option")

    def error(self, message):
        self.print_usage(sys.stderr)
        print_exception("Argument Parser", message)
        exit(get_error())

    def parse_args(self, *args, **kwargs):
        args = super(ArgumentParser, self).parse_args(*args, **kwargs)
        args.all_tags = False
        return args
