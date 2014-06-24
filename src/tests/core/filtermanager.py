from core.filtermanager import FilterManager
from filter.ipfilter import IPFilter
import util.datatypes as dt

import unittest
from multiprocessing import Process, Queue, Pipe
from time import sleep

class FilterManagerTest(unittest.TestCase):

    def setUp(self):
        self.fm = FilterManager()

    def test_add_filter(self):
        _filter = IPFilter(name='IPFilter.TEST', src='127.0.0.1')
        self.fm.add_filter(_filter.name,_filter)

        self.assertEqual(len(self.fm.filters),1)
        self.assertTrue(self.fm.filters.has_key('IPFilter.TEST'))
        self.assertEqual(self.fm.filters['IPFilter.TEST'],_filter)

    def test_add(self):
        _filter = IPFilter(name='IPFilter.PARENT', src='127.0.0.1')
        self.fm.add_filter(_filter.name,_filter)
        config={'name':'IPFilter.CHILD',
                'class':'filter.ipfilter.IPFilter',
                'src':'127.0.0.1',
                'parent':'IPFilter.PARENT'
                }
        status = self.fm._add(config)
       
        print status
        self.assertEqual(status[0],dt.STATUS_OK)
        self.assertEqual(len(self.fm.filters),2)
        self.assertTrue(self.fm.filters.has_key('IPFilter.CHILD'))
        
        child = self.fm.filters['IPFilter.PARENT'].nxt
        self.assertNotEqual(child, None)
        self.assertEqual(child.name, 'IPFilter.CHILD')
        self.assertEqual(child.nxt, None)

    def test_new_chain(self):
        config={'class':'filter.ipfilter.IPFilter',
                'name':'IPFilter.PARENT',
                'src':'127.0.0.1',
                'next':{
                    'class':'filter.portfilter.UDPFilter',
                    'name':'UDPFilter.CHILD',
                    'sport':'53',
                    'both':'true'
                    }
                }
        self.fm._new_chain(config)
        
        self.assertEqual(len(self.fm.filters),2)
        self.assertTrue(self.fm.filters.has_key('IPFilter.PARENT'))
        self.assertTrue(self.fm.filters.has_key('UDPFilter.CHILD'))
        self.assertEqual(len(self.fm.chains),1)

        child = self.fm.chains[0].nxt

        self.assertNotEqual(child, None)
        self.assertEqual(child.name, 'UDPFilter.CHILD')
       
    def test_new_chain_2(self):
        self.test_new_chain()
        config={'class':'filter.ipfilter.IPFilter',
                'name':'IPFilter.PARENT2',
                'next':{
                    'class':'filter.portfilter.TCPFilter',
                    'name':'TCPFilter.CHILD2',
                    'sport':'80',
                    'both':'false'
                    }
                }
        self.fm._new_chain(config)

        self.assertEqual(len(self.fm.filters),4)
        self.assertEqual(len(self.fm.chains),2)
        self.assertTrue(self.fm.filters.has_key('IPFilter.PARENT2'))
        self.assertTrue(self.fm.filters.has_key('TCPFilter.CHILD2'))

        child = self.fm.chains[1].nxt
        self.assertEqual(child.name, 'TCPFilter.CHILD2')
        self.assertEqual(child.nxt,None)

    def test_new_chain_3(self):
        self.test_new_chain_2()

        config={'class':'filter.ipfilter.IPFilter',
                'name':'IPFilter.PARENT3',
                'next':{
                    'class':'filter.portfilter.TCPFilter',
                    'name':'TCPFilter.CHILD2',
                    'sport':'81',
                    'both':'true'
                    }
                }
        status = self.fm._new_chain(config)

        self.assertEqual(status[0], dt.ERR_CONFLICT)
        self.assertFalse(self.fm.filters.has_key('IPFilter.PARENT3'))
        self.assertTrue(self.fm.filters.has_key('TCPFilter.CHILD2'))
        self.assertEqual(len(self.fm.chains), 2)
        
        child = self.fm.filters['TCPFilter.CHILD2']

        self.assertEqual(child.sport,80)
        self.assertFalse(child.both)

    def test_update(self):
        self.test_add_filter()
        config={'name':'IPFilter.TEST',
                'src':'172.29.0.10',
                'dst':'8.8.8.8',
                'both':'true'
                }
        self.fm._update(config)

        self.assertTrue(self.fm.filters.has_key('IPFilter.TEST'))
        self.assertEqual(self.fm.filters['IPFilter.TEST'].src, '\xac\x1d\x00\n')
        self.assertEqual(self.fm.filters['IPFilter.TEST'].dst, '\x08\x08\x08\x08')
        self.assertTrue(self.fm.filters['IPFilter.TEST'].both)

    def test_delete_in_chain(self):
        self.test_new_chain_2()
        config={'name':'UDPFilter.CHILD'}
        self.fm._delete(config)

        self.assertFalse(self.fm.filters.has_key('UDPFilter.CHILD'))
        self.assertTrue(self.fm.filters.has_key('IPFilter.PARENT'))
        self.assertTrue(self.fm.filters.has_key('IPFilter.PARENT2'))
        self.assertTrue(self.fm.filters.has_key('TCPFilter.CHILD2'))

        self.assertEqual(len(self.fm.chains),2)
        self.assertEqual(self.fm.chains[0].nxt, None)
        self.assertNotEqual(self.fm.chains[1].nxt, None)

    def test_delete_chain(self):
        self.test_new_chain_2()
        config={'name':'IPFilter.PARENT2'}
        self.fm._delete(config)

        self.assertFalse(self.fm.filters.has_key('IPFilter.PARENT2'))
        self.assertFalse(self.fm.filters.has_key('TCPFilter.CHILD2'))
        self.assertTrue(self.fm.filters.has_key('IPFilter.PARENT'))
        
        self.assertEqual(len(self.fm.chains),1)
        self.assertNotEqual(self.fm.chains[0].nxt, None)

    def test_config(self):
        config = [{
                    'name':'IPFilter.P1',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'172.29.0.1',
                    'next':{
                        'name':'TCPFilter.P1CH1',
                        'class':'filter.portfilter.TCPFilter',
                        'sport':'80',
                        }
                    },
                    {'name':'IPFilter.P2',
                    'class':'filter.ipfilter.IPFilter',
                    'dst':'127.0.0.1',
                    'both':'true'},
                    {'name':'IPFilter.P3',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'127.0.0.1',
                    'next':{
                        'name':'UDPFilter.P2CH1',
                        'class':'filter.portfilter.UDPFilter',
                        'dport':'53'
                        }
                    }
                ]

        for _filter in config:
            res = self.fm._new_chain(_filter)
            self.assertEqual(res[0], dt.STATUS_OK)

        chains = self.fm.config()
        self.assertEqual(len(chains), 3)

        chain = chains[0]
        self.assertEqual(chain['name'], config[0]['name'])
        self.assertEqual(chain['class'], config[0]['class'])
        self.assertEqual(chain['src'], config[0]['src'])
        self.assertEqual(chain['next']['name'], config[0]['next']['name'])
        self.assertEqual(chain['next']['class'], config[0]['next']['class'])
        self.assertEqual(chain['next']['sport'], config[0]['next']['sport'])
        with self.assertRaises(KeyError):
            nxt = chain['next']['next']

        chain = chains[1]
        self.assertEqual(chain['name'], config[1]['name'])
        self.assertEqual(chain['class'], config[1]['class'])
        self.assertEqual(chain['dst'], config[1]['dst'])
        self.assertEqual(chain['both'].lower(), config[1]['both'])
        with self.assertRaises(KeyError):
            nxt = chain['next']

        chain = chains[2]
        self.assertEqual(chain['name'], config[2]['name'])
        self.assertEqual(chain['class'], config[2]['class'])
        self.assertEqual(chain['src'], config[2]['src'])
        self.assertEqual(chain['next']['name'], config[2]['next']['name'])
        self.assertEqual(chain['next']['class'], config[2]['next']['class'])
        self.assertEqual(chain['next']['dport'], config[2]['next']['dport'])

    def test_start(self):
        fq = Queue()
        lq = Queue()
        l,r = Pipe()
        proc = Process(target=self.fm.start, args=(fq,lq,r))
        proc.start()
        
        config = [{
                    'name':'IPFilter.P1',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'198.252.206.140',
                    'both':'true',
                    'next':{
                        'name':'TCPFilter.P1CH1',
                        'class':'filter.portfilter.TCPFilter',
                        'sport':'80',
                        'both':'true'
                        }
                    },
                    {'name':'IPFilter.P2',
                    'class':'filter.ipfilter.IPFilter',
                    'dst':'127.0.0.1',
                    'both':'true'},
                    {'name':'IPFilter.P3',
                    'class':'filter.ipfilter.IPFilter',
                    'src':'127.0.0.1',
                    'next':{
                        'name':'UDPFilter.P2CH1',
                        'class':'filter.portfilter.UDPFilter',
                        'dport':'53'
                        }
                    }
                ]
            
        for chain in config:
            l.send([dt.CMD_FILTER_ADD_CHAIN, chain])
            res = l.recv()
            self.assertEqual(res[0], dt.STATUS_OK)

        pkt1 = [0, '\x00\x90\xfb\x38\xb5\x48\xb8\xca\x3a\x83\x73\x6a\x08\x00\x45\x00\x00\x3c\xbb\x72\x40\x00\x40\x06\x35\x80\xac\x1d\x01\xce\x43\xd4\x58\x0a\x92\x6c\x00\x50\x04\x48\x49\x0a\x00\x00\x00\x00\xa0\x02\x72\x10\x49\xf8\x00\x00\x02\x04\x05\xb4\x04\x02\x08\x0a\x00\x62\xf2\x78\x00\x00\x00\x00\x01\x03\x03\x07']
        fq.put(pkt1)
        sleep(0.5)
        self.assertEqual(fq.qsize(), 0)
        self.assertEqual(lq.qsize(), 0)

        pkt2 = [0, '\x00\x90\xfb8\xb5H\xb8\xca:\x83sj\x08\x00E\x00\x00<\x06\xea@\x00@\x06\xf2\x17\xac\x1d\x00\x14\xc6\xfc\xce\x8c\xd9_\x00P+o\xe1{\x00\x00\x00\x00\xa0\x02r\x10A\xe9\x00\x00\x02\x04\x05\xb4\x04\x02\x08\n\x00+\xe7\x91\x00\x00\x00\x00\x01\x03\x03\x07']
        fq.put(pkt2)
        sleep(0.5)
        l.send([dt.CMD_STOP, 0])

        self.assertEqual(fq.qsize(), 0)
        self.assertEqual(lq.qsize(), 1)
        proc.join()


if __name__ == "__main__":
    unittest.main()
