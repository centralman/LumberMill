import ModuleBaseTestCase
import sys
import time
import mock
import socket
import ssl

import lumbermill.utils.DictUtils as DictUtils
from lumbermill.input import TcpServer


class TestTcpServer(ModuleBaseTestCase.ModuleBaseTestCase):

    def setUp(self):
        super(TestTcpServer, self).setUp(TcpServer.TcpServer(mock.Mock()))

    def testTcpConnection(self):
        self.test_object.configure({})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(.1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s.connect(('localhost', self.test_object.getConfigurationValue('port')))
            for _ in range(0, 1500):
                s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.\n")
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ( 'localhost', self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        expected_ret_val = DictUtils.getDefaultEventDict({'data': "Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever."})
        expected_ret_val.pop('lumbermill')
        event = False
        time.sleep(2)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertTrue(event != False)
        self.assertEqual(counter, 1500)
        event.pop('lumbermill')
        self.assertDictEqual(event, expected_ret_val)

    def testATlsTcpConnection(self):
        self.test_object.configure({'port': 5252,
                                    'tls': True,
                                    'key': './test_data/gambolputty_ca.key',
                                    'cert': './test_data/gambolputty_ca.crt',
                                    'timeout': 1})
        self.checkConfiguration()
        self.test_object.initAfterFork()
        self.startTornadoEventLoop()
        # Give server process time to startup.
        time.sleep(1)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            s = ssl.wrap_socket(s, ssl_version=ssl.PROTOCOL_TLSv1)
            s.connect((self.test_object.getConfigurationValue('interface'), self.test_object.getConfigurationValue('port')))
            for _ in range(0, 1500):
                s.sendall("Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever.\n")
            s.close()
            connection_succeeded = True
        except:
            etype, evalue, etb = sys.exc_info()
            print "Could not connect to %s:%s. Exception: %s, Error: %s" % ( self.test_object.getConfigurationValue("interface"),
                                                                            self.test_object.getConfigurationValue("port"), etype, evalue)
            connection_succeeded = False
        self.assertTrue(connection_succeeded)
        expected_ret_val =  DictUtils.getDefaultEventDict({'data': "Beethoven, Mozart, Chopin, Liszt, Brahms, Panties...I'm sorry...Schumann, Schubert, Mendelssohn and Bach. Names that will live for ever."})
        expected_ret_val.pop('lumbermill')
        event = False
        time.sleep(2)
        counter = 0
        for event in self.receiver.getEvent():
            counter += 1
        self.assertTrue(event != False)
        self.assertEqual(counter, 1500)
        event.pop('lumbermill')
        self.assertDictEqual(event, expected_ret_val)

    def tearDown(self):
        self.test_object.shutDown()
        ModuleBaseTestCase.ModuleBaseTestCase.tearDown(self)