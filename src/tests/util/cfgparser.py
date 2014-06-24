import unittest
from ConfigParser import SafeConfigParser
from StringIO import StringIO

from util.cfgparser import CfgParser

class CfgParserTest(unittest.TestCase):

    def setUp(self):
        self.parser = CfgParser()

    def test_parse(self):
        config = self.parser.parse('config/config-test.cfg')
        self.assertEqual(len(config), 1)
        self.assertTrue(config.has_key('trapdoor'))

        trap = config['trapdoor']
        self.assertEqual(len(trap),3)
        self.assertTrue(trap.has_key('filters'))
        self.assertEqual(len(trap['filters']), 2)
        self.assertTrue(trap.has_key('loggers'))
        self.assertEqual(len(trap['loggers']), 1)
        self.assertTrue(trap.has_key('iface'))
        self.assertEqual(len(trap['iface']), 1)
        self.assertEqual(trap['iface'][0], 'eth0')

        filter0 = trap['filters'][0]
        self.assertEqual(filter0['name'], 'IPFilter.GOOGLE')
        self.assertEqual(filter0['class'], 'filter.ipfilter.IPFilter')
        self.assertEqual(filter0['dst'], 'www.google.co.in')
        self.assertEqual(filter0['both'], 'True')
        self.assertNotEqual(filter0['next'], None)

        childf0 = filter0['next']
        self.assertEqual(childf0['name'], 'TCPFilter.HTTP_PORT')
        self.assertEqual(childf0['class'], 'filter.portfilter.TCPFilter')
        self.assertEqual(childf0['dst'], '80')
        self.assertEqual(childf0['both'], 'true')
        self.assertEqual(len(childf0['flags']), 3)
        self.assertEqual(childf0['flags'][0], 'SYN')
        self.assertEqual(childf0['flags'][1], 'ACK')
        self.assertEqual(childf0['flags'][2], 'PSH')

        filter1 = trap['filters'][1]
        self.assertEqual(filter1['name'], 'IPFilter.STACKOVERFLOW')
        self.assertEqual(filter1['class'], 'filter.ipfilter.IPFilter')
        self.assertEqual(filter1['src'], 'stackoverflow.com')
        self.assertEqual(filter1['both'], 'true')
        with self.assertRaises(KeyError):
            nxt = filter1['next']

        logger0 = trap['loggers'][0]
        self.assertEqual(logger0['name'], 'PCAP.cnf-test')
        self.assertEqual(logger0['target'], '../logs/cnf-test.pcap')
        self.assertEqual(logger0['class'], 'logger.pcaplogger.PcapLogger')

    def test_flatten(self):
        config={
                    'iface':['eth0'],
                    'filters':[{
                        'name':'IPFilter.TEST1',
                        'class':'filter.ipfilter.IPFilter',
                        'src':'google.co.in',
                        'both':'True',
                        'next':{
                            'name':'TCPFilter.TEST1',
                            'class':'filter.portfilter.TCPFilter',
                            'sport':'80',
                            'flags':['SYN', 'ACK', 'FIN']
                            }
                        },{
                        'name':'IPFilter.TEST2',
                        'class':'filter.ipfilter.IPFilter',
                        'src':'172.29.0.1',
                        'both':'False'
                        }],
                    'loggers':[{
                        'name':'PCAPLogger.TEST1',
                        'class':'logger.pcaplogger.PcapLogger',
                        'target':'/tmp/test.pcap',
                        }]
                    }
                
        io = StringIO()    
        f = open('/tmp/test.ini', 'w')
        data = self.parser.flatten(config, f)
        f.close()
        cfgparser = SafeConfigParser()
        cfgparser.read('/tmp/test.ini')
        sections = cfgparser.sections()
        self.assertEqual(len(sections), 5)

        self.assertTrue(cfgparser.has_section('trapdoor'))
        self.assertEqual(cfgparser.get('trapdoor', 'iface'), 'eth0,')
        self.assertEqual(cfgparser.get('trapdoor', 'filters'), 'IPFilter.TEST1,IPFilter.TEST2,')
        self.assertEqual(cfgparser.get('trapdoor', 'loggers'), 'PCAPLogger.TEST1,')

        self.assertTrue(cfgparser.has_section('IPFilter.TEST1'))
        self.assertEqual(cfgparser.get('IPFilter.TEST1', 'name'), 'IPFilter.TEST1')
        self.assertEqual(cfgparser.get('IPFilter.TEST1', 'class'), 'filter.ipfilter.IPFilter')
        self.assertEqual(cfgparser.get('IPFilter.TEST1', 'src'), 'google.co.in')
        self.assertEqual(cfgparser.get('IPFilter.TEST1', 'both').lower(), 'true')
        self.assertEqual(cfgparser.get('IPFilter.TEST1', 'next'), 'TCPFilter.TEST1')
        
        self.assertTrue(cfgparser.has_section('TCPFilter.TEST1'))
        self.assertEqual(cfgparser.get('TCPFilter.TEST1', 'name'), 'TCPFilter.TEST1')
        self.assertEqual(cfgparser.get('TCPFilter.TEST1', 'class'), 'filter.portfilter.TCPFilter')
        self.assertEqual(cfgparser.get('TCPFilter.TEST1', 'sport'), '80')
        self.assertEqual(cfgparser.get('TCPFilter.TEST1', 'flags'), 'SYN,,ACK,FIN')
        
        self.assertTrue(cfgparser.has_section('IPFilter.TEST2'))
        self.assertEqual(cfgparser.get('IPFilter.TEST2', 'name'), 'IPFilter.TEST2')
        self.assertEqual(cfgparser.get('IPFilter.TEST2', 'class'), 'filter.ipfilter.IPFilter')
        self.assertEqual(cfgparser.get('IPFilter.TEST2', 'src'), '172.29.0.1')
        self.assertEqual(cfgparser.get('IPFilter.TEST2', 'both').lower(), 'false')

        self.assertTrue(cfgparser.has_section('PCAPLogger.TEST1'))
        self.assertEqual(cfgparser.get('PCAPLogger.TEST1', 'name'), 'PCAPLogger.TEST1')
        self.assertEqual(cfgparser.get('PCAPLogger.TEST1', 'class'), 'logger.pcaplogger.PcapLogger')
        self.assertEqual(cfgparser.get('PCAPLogger.TEST1', 'target'), '/tmp/test.pcap')
        

if __name__ == "__main__":
    unittest.main()
