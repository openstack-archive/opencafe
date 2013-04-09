"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

'''
@summary: Generic Classes for test statistics
'''
import os
from datetime import datetime
from unittest2.result import TestResult

class TestRunMetrics(object):
    '''
    @summary: Generic Timer used to track any time span
    @ivar start_time: Timestamp from the start of the timer
    @type start_time: C{datetime}
    @ivar stop_time: Timestamp of the end of the timer
    @type stop_time: C{datetime}
    @todo: This is a stop gap. It will be necessary to override large portions
           of the runner and the default unittest.TestCase architecture to make
           this auto-magically work with unittest properly.
           This should be a child of unittest.TestResult  
    '''
    def __init__(self):
        self.total_tests = 0
        self.total_passed = 0
        self.total_failed = 0
        self.timer = TestTimer()
        self.result = TestResultTypes.UNKNOWN

class TestResultTypes(object):
    '''
    @summary: Types dictating an individual Test Case result
    @cvar PASSED: Test has passed
    @type PASSED: C{str}
    @cvar FAILED: Test has failed
    @type FAILED: C{str}
    @cvar SKIPPED: Test was skipped
    @type SKIPPED: C{str}
    @cvar TIMEDOUT: Test exceeded pre-defined execution time limit   
    @type TIMEDOUT: C{str}
    @note: This is essentially an Enumerated Type
    '''
    PASSED = "Passed"
    FAILED = "Failed"
    SKIPPED = "Skipped"    #Not Supported Yet
    TIMEDOUT = "Timedout"  #Not Supported Yet
    UNKNOWN = "UNKNOWN"

class TestTimer(object):
    '''
    @summary: Generic Timer used to track any time span
    @ivar start_time: Timestamp from the start of the timer
    @type start_time: C{datetime}
    @ivar stop_time: Timestamp of the end of the timer
    @type stop_time: C{datetime}
    '''
    def __init__(self):
        self.start_time = None
        self.stop_time = None

    def start(self):
        '''
        @summary: Starts this timer
        @return: None
        @rtype: None
        '''
        self.start_time = datetime.now()
        
    def stop(self):
        '''
        @summary: Stops this timer
        @return: None
        @rtype: None
        '''
        self.stop_time = datetime.now()
        
    def get_elapsed_time(self):
        '''
        @summary: Convenience method for total elapsed time
        @rtype: C{datetime}
        @return: Elapsed time for this timer. C{None} if timer has not started
        '''
        elapsedTime = None
        if (self.start_time != None):
            if (self.stop_time != None):
                elapsedTime = (self.stop_time - self.start_time)
            else:
                elapsedTime = (datetime.now() - self.start_time)
        else:
            ''' Timer hasn't started, error on the side of caution '''
            rightNow = datetime.now()
            elapsedTime = (rightNow - rightNow)
        return(elapsedTime)

class PBStatisticsLog(object):
    '''
    @summary: PSYCHOTICALLY BASIC Statistics logger
    @ivar: File: File Name of this logger
    @type File:  C{str}
    @ivar: FileMode: Mode this logger runs in. a or w
    @type FileMode:  C{str}
    @ivar: Errors: List of all error messages recorded by this logger
    @type Errors:  C{list}
    @ivar: Warnings: List of all warning messages recorded by this logger
    @type Warnings:  C{list}
    @ivar: IsDebugMode: Flag to turn Debug logging on and off
    @type IsDebugMode:  C{bool}
    @todo: Upgrade this astoundingly basic logger to Python or Twisted logger framework
    @attention: THIS LOGGER IS DESIGNED TO BE TEMPORARY. It will be replaced in the matured framework
    '''
    def __init__(self, fileName=None, log_dir='.', startClean=False):
        self.FileMode = 'a'
        if fileName is not None:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            self.File = os.path.normpath(os.path.join(log_dir, fileName))
            if startClean is True and os.path.exists(self.File) == True:
                ''' Force the file to be overwritten before any writing '''
                os.remove(self.File)
        else:
            self.File = None
            
        if os.path.exists(self.File) is False:
            ''' Write out the header to the stats log '''
            self.__write("Elapsed Time,Start Time,Stop Time,Result,Errors,Warnings")
        
    def __write(self, message):
        '''
        @summary: Writes a message to this log file
        @param formatted: Indicates if message applies standard formatting
        @type formatted: C{bool}  
        @return: None
        @rtype: None
        '''
        if self.File is not None:
            log = open(self.File, self.FileMode)
            log.write("%s\n" % message)
            log.close()
        return

    def report(self, test_result=TestRunMetrics()):
        self.__write("{0},{1},{2},{3}".format(test_result.timer.get_elapsed_time(), 
            test_result.timer.start_time,
            test_result.timer.stop_time,
            test_result.result))
