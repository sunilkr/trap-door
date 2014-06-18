import unittest

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


if __name__ == "__main__":
    unittest.main()
