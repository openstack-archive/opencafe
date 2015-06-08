# Copyright 2015 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from datetime import datetime
import os
import errno
import csv
import six
import sys


class TestRunMetrics(object):
    """
    Contains test timing and results metrics for a test.
    """
    def __init__(self):
        self.total_tests = 0
        self.total_passed = 0
        self.total_errored = 0
        self.total_failed = 0
        self.timer = TestTimer()
        self.result = TestResultTypes.UNKNOWN


class TestResultTypes(object):
    """
    Types dictating an individual Test Case result
    @cvar PASSED: Test has passed
    @type PASSED: C{str}
    @cvar FAILED: Test has failed
    @type FAILED: C{str}
    @cvar SKIPPED: Test was skipped
    @type SKIPPED: C{str}
    @cvar TIMEDOUT: Test exceeded pre-defined execution time limit
    @type TIMEDOUT: C{str}
    @cvar ERRORED: Test has errored
    @type ERRORED: C{str}
    @note: This is essentially an Enumerated Type
    """

    PASSED = "Passed"
    FAILED = "Failed"
    SKIPPED = "Skipped"    # Not Supported Yet
    TIMEDOUT = "Timedout"  # Not Supported Yet
    UNKNOWN = "UNKNOWN"
    ERRORED = "ERRORED"


class TestTimer(object):
    """
    @summary: Generic Timer used to track any time span
    @ivar start_time: Timestamp from the start of the timer
    @type start_time: C{datetime}
    @ivar stop_time: Timestamp of the end of the timer
    @type stop_time: C{datetime}
    """

    def __init__(self):
        self.start_time = None
        self.stop_time = None

    def start(self):
        """
        @summary: Starts this timer
        @return: None
        @rtype: None
        """

        self.start_time = datetime.now()

    def stop(self):
        """
        @summary: Stops this timer
        @return: None
        @rtype: None
        """

        self.stop_time = datetime.now()

    def get_elapsed_time(self):
        """
        @summary: Convenience method for total elapsed time
        @rtype: C{datetime}
        @return: Elapsed time for this timer. C{None} if timer has not started
        """

        elapsedTime = None
        if self.start_time is not None:
            if self.stop_time is not None:
                elapsedTime = (self.stop_time - self.start_time)
            else:
                elapsedTime = (datetime.now() - self.start_time)
        else:
            # Timer hasn't started, error on the side of caution
            rightNow = datetime.now()
            elapsedTime = (rightNow - rightNow)
        return(elapsedTime)


class CSVWriter(object):
    """CSVWriter"""

    def __init__(self, headers, file_name, log_dir='.', start_clean=False):
        self.file_mode = 'a'
        self.headers = headers

        # create the dir if it does not exist
        try:
            os.makedirs(log_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

        # get full path
        self.full_path = os.path.normpath(os.path.join(log_dir, file_name))

        # remove file if you want a clean log file
        if start_clean:
            # Force the file to be overwritten before any writing
            try:
                os.remove(self.full_path)
            except OSError:
                sys.stderr.write('File not writable\n')

        if os.path.exists(self.full_path) is False:
            # Write out the header to the stats log
            self.writerow(self.headers)

    def writerow(self, row_list):
        if self.full_path:
            if six.PY2:
                fp = open(self.full_path, "ab")
            else:
                fp = open(self.full_path, "a", newline="")
            csv_writer = csv.writer(
                fp, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            try:
                csv_writer.writerow(row_list)
            except OSError:
                sys.stderr.write('File not writable\n')
            fp.close()


class PBStatisticsLog(CSVWriter):
    """extends the csv writer"""

    def __init__(self, file_name=None, log_dir='.', start_clean=False):
        headers = ["Elapsed", "Time", "Start Time", "Stop Time", "Result"]

        super(PBStatisticsLog, self).__init__(
            headers, file_name, log_dir, start_clean)

    def report(self, test_result=TestRunMetrics()):
        self.writerow([
            test_result.timer.get_elapsed_time(), test_result.timer.start_time,
            test_result.timer.stop_time, test_result.result])
