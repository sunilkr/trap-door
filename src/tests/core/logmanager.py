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
                    'both':'true',
                    'inverse': 'true'
                    }
                }
        status = self.lm._set_filter(config)
        
        self.assertTrue(self.lm.loggers.has_key('PCAPLogger.TEST'))
        _filter = self.lm.loggers['PCAPLogger.TEST'].get_filter()
        self.assertTrue(_filter.both)
        self.assertEqual(_filter.src, '\x7f\x00\x00\x01')
        self.assertTrue(_filter.inverse)
        
    def test_add_with_filter_chain(self):
        config={'name':'PCAPLogger.TEST',
                'class':'logger.pcaplogger.PcapLogger',
                'target':'/tmp/test.pcap',
                'filter':{
                    'name':'IPFilter.TEST',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'127.0.0.1',
                    'inverse': 'true',
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
        self.assertTrue(_filter.inverse)
        self.assertEqual(_filter.__class__.__name__, 'IPFilter')
        self.assertEqual(_filter.nxt.__class__.__name__, 'TCPFilter')
        self.assertEqual(_filter.nxt.sport, 80)

    def test_config(self):
        config=[{'name':'PCAPLogger.TEST',
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
                        'both':'true',
                        'inverse' : 'true' 
                        }
                    }
                },
                {'name':'TextLogger.TEST',
                'class':'logger.textlogger.TextLogger',
                'target':'/tmp/test.log'
                }
            ]
        
        for logger in config:
            self.lm._add(logger)

        attrs = self.lm.config()
        self.assertEqual(len(attrs), 2)

        logger = attrs[1]
        #self.assertEqual(logger['name'], config[0]['name'])
        self.assertEqual(logger['name'], 'PCAPLogger.TEST')
        self.assertEqual(logger['class'], config[0]['class'])
        self.assertEqual(logger['target'], config[0]['target'])
        
        fltr = logger['filter']
        cfltr = config[0]['filter']
        self.assertEqual(fltr['name'], cfltr['name'])
        self.assertEqual(fltr['class'], cfltr['class'])
        self.assertEqual(fltr['next']['class'], cfltr['next']['class'])
        self.assertEqual(fltr['next']['inverse'].lower(), 'true')

        logger = attrs[0]
        self.assertEqual(logger['name'], config[1]['name'])
        self.assertEqual(logger['class'], config[1]['class'])
        self.assertEqual(logger['target'], config[1]['target'])
        with self.assertRaises(KeyError):
            self.assertEqual(logger['filter'], None)
        
    def test_clear(self):
        self.test_add_with_filter_chain()
        self.lm._clear()
        self.assertEqual(len(self.lm.loggers), 0)

if __name__ == "__main__":
    unittest.main()
