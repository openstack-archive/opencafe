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

from unittest2.suite import TestSuite


class BaseParameterizedLoader(object):    
    '''
    Instantiate this class with a data generator object(DataGenerator subclass)
    Then use that instance to add your tests like you add your tests into the suite.
    e.g. data_generator = LavaAPIDataGenerator()
         custom_loader =  BaseParameterizedLoader(data_generator)
         custom_loader.addTest(TestClass("test-1"))
         custom_loader.addTest(TestClass("test-2"))
         custom_loader.addTest(TestClass("test-3"))
         custom_loader.getSuite()
    '''
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.tests = []
    
    def addTest(self,testcase):
        '''
        Add tests to this loader. This takes a test case object as a parameter
        See e.g. above
        '''
        self.tests.append(testcase)
    
    def getSuite(self):
        '''
        returns a test suite used by the unittest to run packages.
        load_tests function can return this. 
        '''
        if len(self.tests) != 0:
            '''
            Port all the jsons to instance variables of the class
            '''
            suite = TestSuite()
            for test_record in self.data_provider.generate_test_records():
                for test in self.tests:
                    test_to_be_mod = test
                    if test.__dict__.has_key(test_record.keys()[0]):
                        test_to_be_mod = test.__copy__()
                    else:
                        test_to_be_mod = test
                    for key in test_record.keys():
                        setattr(test_to_be_mod, key, test_record[key])
                    setattr(test_to_be_mod, "test_record", test_record)
                    suite.addTest(test_to_be_mod)
            return suite
        else:
            raise Exception,"No tests added to the parameterized loader"
                    
        