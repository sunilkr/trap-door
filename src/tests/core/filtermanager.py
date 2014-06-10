from core.filtermanager import FilterManager
from filter.ipfilter import IPFilter
import util.datatypes as dt

import unittest

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

        self.assertEqual(child.sport,'\x00P')
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
