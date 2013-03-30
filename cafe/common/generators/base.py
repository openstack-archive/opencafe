class BaseDataGenerator(object):
    '''
    Any Data Generator should extend this class.
    It should just define a self.test_records which is a list of dictionaries that you want the tests to run with.
    '''
    def __init__(self):
        self.test_records = []
        
    def generate_test_records(self):
        for test_record in self.test_records:
            yield test_record
        
        