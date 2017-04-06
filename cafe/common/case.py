import time
import unittest
from cafe.drivers.unittest.fixtures import BaseTestFixture


class TimedTestCase(BaseTestFixture):
    def run(self, result=None):
        self.startTime = time.time()
        super(TimedTestCase, self).run(result)


class TimedTextTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        # Supplement the constructor with a list of successful tests, which the
        # original code does not do.
        super(TimedTextTestResult, self).__init__(stream, descriptions, verbosity)
        self.successes = []

    def _setElapsedTime(self, test):
        # If the test cases have timing information, include it.
        if self.showAll:
            if hasattr(test, 'startTime') and not hasattr(test, 'stopTime'):
                test.stopTime = time.time()
                test.elapsedTime = test.stopTime - test.startTime

            if hasattr(test, 'elapsedTime'):
                self.stream.write('%0.3fs ' % test.elapsedTime)
            else:
                self.stream.write('- ')

    def addSuccess(self, test):
        self._setElapsedTime(test)
        # Add the test to the list of successes.  The original code does not track
        # successful tests, only errors.
        self.successes.append(test)
        super(TimedTextTestResult, self).addSuccess(test)

    def addError(self, test, err):
        self._setElapsedTime(test)
        super(TimedTextTestResult, self).addError(test, err)

    def addFailure(self, test, err):
        self._setElapsedTime(test)
        super(TimedTextTestResult, self).addFailure(test, err)

    def addSkip(self, test, reason):
        self._setElapsedTime(test)
        super(TimedTextTestResult, self).addSkip(test, reason)

    def addExpectedFailure(self, test, err):
        self._setElapsedTime(test)
        super(TimedTextTestResult, self).addExpectedFailure(test, err)

    def addUnexpectedSuccess(self, test):
        self._setElapsedTime(test)
        super(TimedTextTestResult, self).addUnexpectedSuccess(test)


# Replace the default TestResult with one that displays timing information
unittest.TextTestRunner.resultclass = TimedTextTestResult
