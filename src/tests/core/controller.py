import unittest

from core.controller import Controller, DNSUpdater
import util.datatypes as dt

from socket import gethostbyname
import multiprocessing as mp

class ControllerTest(unittest.TestCase):
    def setUp(self):
        self.ctrlr = Controller()
        #self.ctrlr.start()
        pass

    def test_add_iface(self):      # Requires sudo
        self.ctrlr.add_iface('lo')
        self.assertEqual(len(self.ctrlr.pipe_net), 1)
        self.assertEqual(len(self.ctrlr.listeners), 1)
        self.assertEqual(len(self.ctrlr.net_procs), 1)

    def test_add_logger(self):
        self.ctrlr.start()
        config={'name':'TextLogger.TEST',
                'class':'logger.textlogger.TextLogger',
                'target':'/tmp/test.log',
                'filter':{
                    'class':'filter.ipfilter.IPFilter',
                    'name':'IPFilter.TEST',
                    'src':'172.29.0.1'
                    }
                }
        res = self.ctrlr.add_logger(config)
        self.assertEqual(res[0], dt.STATUS_OK)

    def test_add_filter_chain(self):
        self.ctrlr.start()
        config={'class':'filter.ipfilter.IPFilter',
                'name':'IPFilter.TEST',
                'src':'google.com',
                'next':{
                    'class':'filter.portfilter.UDPFilter',
                    'name':'UDPFilter.TEST',
                    'dport':'53',
                    'both':'true'
                    }
                }

        res = self.ctrlr.add_filter_chain(config)
        self.assertEqual(res[0],dt.STATUS_OK)

    def test_resolve_names(self):
        config={'src':'ubuntu.com',
                'dst':'172.29.0.1',
                'both':True,
                'name':'TestFilter.P',
                'next':{
                    'src':'stackoverflow.com',
                    'both':'true',
                    'name':'TestFilter.C'
                    }
                }
        ips = { 'p.src': gethostbyname(config['src']),
                'p.dst': gethostbyname(config['dst']),
                'c.src': gethostbyname(config['next']['src'])
                }

        cnf = self.ctrlr._resolve_names(config)

        self.assertEqual(len(cnf), 5)
        self.assertEqual(cnf['src'], ips['p.src'])
        self.assertEqual(cnf['dst'], ips['p.dst'])
        self.assertTrue(cnf['both'])
        self.assertEqual(cnf['name'], 'TestFilter.P')
        self.assertEqual(cnf['next']['src'], ips['c.src'])
        self.assertEqual(cnf['next']['name'], 'TestFilter.C')
        self.assertEqual(cnf['next']['both'], 'true')

    def test_add_filter(self):
        self.ctrlr.start()
        config={'name':'IPFilter.TEST',
                'class':'filter.ipfilter.IPFilter',
                'src':'www.google.com'
                }
        res = self.ctrlr.add_filter(config)
        self.assertEqual(res[0], dt.ERR_NO_SUCH_ITEM)
        
        res = self.ctrlr.add_filter_chain(config)
        self.assertEqual(res[0], dt.STATUS_OK)

        config['parent'] = 'IPFilter.TEST'
        res = self.ctrlr.add_filter(config)
        self.assertEqual(res[0], dt.ERR_CONFLICT)
        
        config['name'] = 'IPFilter.TEST.CHILD'
        config['dst'] = '172.29.0.1'
        res = self.ctrlr.add_filter(config)
        self.assertEqual(res[0], dt.STATUS_OK)

    def tearDown(self):
        self.ctrlr.finish()
        

class DNSUpdaterTest(unittest.TestCase):

    def setUp(self):
        self.table = {}
        self.dns = DNSUpdater(self.table,wait=0.1)

    def test_add_target(self):
        res = self.dns.add_target('ubuntu.com', 'TEST', 'src')
        ip = gethostbyname('ubuntu.com')
        
        self.assertEqual(res, ip)   # may fail if IP changes.
        self.assertEqual(len(self.table), 1)
        self.assertTrue(self.table.has_key('ubuntu.com'))
        entry = self.table['ubuntu.com']
        self.assertEqual(len(entry[1]), 1)
        self.assertEqual(entry[0], ip)
        self.assertEqual(entry[1][0][0], 'TEST')
        self.assertEqual(entry[1][0][1], 'src')

        res = self.dns.add_target('ubuntu.com', 'TEST2', 'dst')
        self.assertEqual(res, ip)
        self.assertEqual(len(self.table), 1)

        entry = self.table['ubuntu.com']
        self.assertEqual(len(entry[1]), 2)
        self.assertEqual(entry[1][1][0], 'TEST2')
        self.assertEqual(entry[1][1][1], 'dst')

    def test_get_ip(self):
        ip = self.dns.add_target('ubuntu.com', 'TEST', 'src')
        self.assertEqual(self.dns.get_ip('ubuntu.com'), ip)

    def test_entries(self):
        ip = self.dns.add_target('ubuntu.com', 'TEST', 'src')
        entries = self.dns.entries()

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries['ubuntu.com'], ip)

    def _test_run(self):    #test individually. can have INFINITE delay before msg
        l,r = mp.Pipe()

        self.dns.set_comm(r)
        self.dns.start()        #Thread.start()->run()
        ip = self.dns.add_target('ubuntu.com', 'TEST', 'src')
        l.send('OK')
        msg = l.recv()
        self.assertEqual(msg[0], dt.CMD_UPDATE)
        self.assertEqual(msg[1]['name'], 'TEST')
        self.assertEqual(msg[1]['src'], ip)

    def tearDown(self):
        self.dns.stop()

if __name__ == "__main__":
    unittest.main()
