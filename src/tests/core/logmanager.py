from core.logmanager import LogManager
import util.datatypes as dt
from util.factory import *

import unittest

class LogManagerTest(unittest.TestCase):

    def setUp(self):
        self.lm = LogManager()

    def test_add_logger(self):
        logger = create_object('logger.pcaplogger.PcapLogger')
        logger.target = '/tmp/test.pcap'
        logger.name = 'PCAPLogger.TEST'

        self.lm.add_logger(logger.name, logger)

        self.assertEqual(len(self.lm.loggers), 1)
        self.assertTrue(self.lm.loggers.has_key('PCAPLogger.TEST'))
        self.assertEqual(self.lm.loggers['PCAPLogger.TEST'],logger)

    def test_add(self):
        config={'name':'PCAPLogger.TEST',
                'class':'logger.pcaplogger.PcapLogger',
                'target':'/tmp/test.pcap'
                }
        status = self.lm._add(config)

        self.assertEqual(status[0],dt.STATUS_OK)
        self.assertEqual(len(self.lm.loggers), 1)
        self.assertTrue(self.lm.loggers.has_key('PCAPLogger.TEST'))
        self.assertEqual(self.lm.loggers['PCAPLogger.TEST'].target,'/tmp/test.pcap')

        status = self.lm._add(config)
        self.assertEqual(status[0],dt.ERR_CONFLICT)
        self.assertEqual(len(self.lm.loggers), 1)
        

    def test_delete(self):
        self.test_add()
        status = self.lm._delete({'name':'PCAPLogger.TEST'})
        
        self.assertEqual(status[0], dt.STATUS_OK)
        self.assertFalse(self.lm.loggers.has_key('PCAPLogger.TEST'))
        
    def test_update(self):
        self.test_add()
        config = {  'name':'PCAPLogger.TEST',
                    'target':'/tmp/test2.pcap',
                    }
        status = self.lm._update(config)

        self.assertEqual(status[0],dt.STATUS_OK)
        self.assertEqual(len(self.lm.loggers), 1)
        self.assertTrue(self.lm.loggers.has_key('PCAPLogger.TEST'))
        self.assertEqual(self.lm.loggers['PCAPLogger.TEST'].target,'/tmp/test2.pcap')

    def test_set_filter(self):
        self.test_add()
        config={'name':'PCAPLogger.TEST',
                'filter':{
                    'name':'IPFilter.TEST',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'127.0.0.1',
                    'both':'true'
                    }
                }
        status = self.lm._set_filter(config)
        
        self.assertTrue(self.lm.loggers.has_key('PCAPLogger.TEST'))
        _filter = self.lm.loggers['PCAPLogger.TEST'].get_filter()
        self.assertTrue(_filter.both)
        self.assertEqual(_filter.src, '\x7f\x00\x00\x01')
        
    def test_add_with_filter_chain(self):
        config={'name':'PCAPLogger.TEST',
                'class':'logger.pcaplogger.PcapLogger',
                'target':'/tmp/test.pcap',
                'filter':{
                    'name':'IPFilter.TEST',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'127.0.0.1',
                    'next':{
                        'name':'TCPFilter.TEST',
                        'class':'filter.portfilter.TCPFilter',
                        'sport':'80',
                        'both':'true'
                        }
                    }
                }
        status = self.lm._add(config)

        self.assertTrue(self.lm.loggers.has_key('PCAPLogger.TEST'))
        self.assertNotEqual(self.lm.loggers['PCAPLogger.TEST'].get_filter, None)
        
        _filter = self.lm.loggers['PCAPLogger.TEST'].get_filter()
        self.assertNotEqual(_filter.nxt, None)
        self.assertEqual(_filter.src,'\x7f\x00\x00\x01')
        self.assertEqual(_filter.__class__.__name__, 'IPFilter')
        self.assertEqual(_filter.nxt.__class__.__name__, 'TCPFilter')
        self.assertEqual(_filter.nxt.sport, 80)


