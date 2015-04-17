from util.datatypes import *
from util.factory import *

from dpkt import ethernet

import unittest

class NoDNSFilterTest(unittest.TestCase):

    def setUp(self):
        self.tcp80 = 'UD3"\x11\x00\x00\x11"3DU\x08\x00E\x00\x00(\x00\x01\x00\x00@\x06\xf6\xa6\xac\x1c\r\'\x93\xde7\x07\x00P\x00\x89\x00\x00\x00\x00\x00\x00\x00\x00P\x02 \x00\n\xe1\x00\x00'

    def test_pkt(self):
        pkt = ethernet.Ethernet(self.tcp80)
        self.assertTrue(hasattr(pkt, 'ip'))
        self.assertEqual(bytes_to_ip4(pkt.data.src), '172.28.13.39')
        self.assertTrue(hasattr(pkt.data, 'tcp'))
        self.assertEqual(pkt.data.data.sport, 80)

    def test_nodns(self):
        config = {  'class': 'filter.ipfilter.IPFilter',
                    'name' : 'L1IPF',
                    'src'  : '147.222.55.7',
                    'both' : 'true',
                    'next' : {
                        'class' : 'filter.portfilter.TCPFilter',
                        'name'  : 'L2TCP',
                        'sport' : '80',
                        'both'  : 'true',
                        'next'  : {
                            'class' : 'filter.ipfilter.IPFilter',
                            'name'  : 'L3IPFx',
                            'src'   : '147.222.55.7',
                            'both'  : 'true',
                            #'inverse' : 'true',
                            'next' : {
                                'class' : 'filter.ipfilter.IPFilter',
                                'name'  : 'L4IPFx',
                                'dst'   : '172.28.13.39',
                                'both'  : 'true',
                                'inverse' : 'true'
                            }
                        }
                    }
                }
        _filter = create_chain(config)
        self.assertEqual(_filter.name, 'L1IPF')
        self.assertEqual(_filter.nxt.name, 'L2TCP')
        self.assertEqual(_filter.nxt.nxt.name, 'L3IPFx')
        self.assertEqual(_filter.nxt.nxt.nxt.name, 'L4IPFx')

        self.assertFalse(_filter.execute([0,self.tcp80]))

