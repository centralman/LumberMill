import extendSysPath
import unittest2
import Queue
import BaseQueue
import Utils

class ModuleBaseTestCase(unittest2.TestCase):

    def setUp(self, test_object):
        self.input_queue = BaseQueue.BaseQueue()
        self.output_queue = BaseQueue.BaseQueue()
        self.test_object = test_object
        self.test_object.setInputQueue(self.input_queue)
        self.test_object.addOutputQueue(self.output_queue, filter=False)

    def testQueueCommunication(self, config = {}):
        self.test_object.configure(config)
        self.test_object.start()
        self.input_queue.put(Utils.getDefaultDataDict({}))
        queue_emtpy = False
        try:
            self.output_queue.get(timeout=1)
        except Queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy != True)

    def testWorksOnOriginal(self, config = {}):
        config['work-on-copy'] = {'value': False, 'contains_placeholder': False}
        data_dict = Utils.getDefaultDataDict({})
        self.test_object.configure(config)
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        try:
            returned_data_dict = self.output_queue.get(timeout=1)
        except Queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == False and returned_data_dict is data_dict)

    def testWorksOnCopy(self, config = {}):
        config['work-on-copy'] = {'value': True, 'contains_placeholder': False}
        data_dict = Utils.getDefaultDataDict({})
        self.test_object.configure(config)
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        try:
            returned_data_dict = self.output_queue.get(timeout=1)
        except Queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == False and returned_data_dict is not data_dict)

    def testOutputQueueFilterNoMatch(self, config = {}):
        output_queue = BaseQueue.BaseQueue()
        data_dict = Utils.getDefaultDataDict({})
        data_dict['Johann'] = 'Gambolputty'
        self.test_object.configure(config)
        self.test_object.addOutputQueue(output_queue, filter='Johann == "Gambolputty de von ausfern" or Johann != "Gambolputty"')
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        try:
            item = output_queue.get(timeout=1)
        except Queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == True)

    def testOutputQueueFilterMatch(self,config = {}):
        output_queue = BaseQueue.BaseQueue()
        data_dict = Utils.getDefaultDataDict({})
        data_dict['Johann'] = 'Gambolputty'
        self.test_object.configure(config)
        self.test_object.addOutputQueue(output_queue, filter='Johann in ["Gambolputty", "Blagr"] or Johan not in ["Gambolputty", "Blagr"]')
        self.test_object.start()
        self.input_queue.put(data_dict)
        queue_emtpy = False
        returned_data_dict = {}
        try:
            returned_data_dict = output_queue.get(timeout=1)
        except Queue.Empty:
            queue_emtpy = True
        self.assert_(queue_emtpy == False and 'Johann' in returned_data_dict)

    def tearDown(self):
        pass