'''
@summary: Generic Data Generators for fuzzing
@copyright: Copyright (c) 2013 Rackspace US, Inc.
'''
import sys

from cafe.common.generators.base import BaseDataGenerator



class SecDataGeneratorString(BaseDataGenerator):
    '''
    @summary: Used for reading data from a file
    '''
    def __init__(self, count=-1, disallow='',
                 filename="../data/fuzz/fuzz_data"):
        '''
        @summary: Data generator for opening files and sending line at a time
        @param count: number of lines to send
        @type count: int
        @param disallow: Characters not allowed
        @type disallow: string
        @param filename: path to the filename starting from bin directory
        @type filename: string
        @return: None
        @note: ints are stored in twos compliment so negative numbers return
               positive numbers with unexpected results (-1,0) returns 255
        '''
        #Tests to ensure inputs are correct
        try:
            file_pointer = open(filename)
        except Exception as exception:
            sys.stderr.write("Check filename in data generator "
                             "SecDataGeneratorString.\n")
            raise exception
        if type(count) != int:
            count = -1
        if type(disallow) != str:
            disallow = ''
        #generates data
        self.test_records = []
        for j, i in enumerate(file_pointer):
            if j == count:
                break
            i = i.rstrip('\r\n')
            for k in disallow:
                i = i.replace(k, "")
            self.test_records.append({"fuzz_data": i, "result": "unknown"})


class SecDataGeneratorCount(BaseDataGenerator):
    '''
    @summary: Used for generating a count
    '''
    def __init__(self, start, stop):
        '''
        @summary: Data generator for counting int returned
        @param start: start int
        @type start: int
        @param stop: stop int
        @type stop: int
        @return: int
        '''
        self.test_records = []
        for i in range(start, stop):
            self.test_records.append({"fuzz_data": i})

