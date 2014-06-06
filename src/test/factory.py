from util.factory import *
from util.datatypes import *
import unittest

class FactoryTest(unittest.TestCase):

    def test_create_object(self):
        cls = 'filter.ipfilter.IPFilter'
        obj = create_object(cls)
        self.assertEqual(obj.__class__.__name__, cls.split(".")[-1])

    def test_create_object_with_args(self):
        obj = create_object('filter.ipfilter.IPFilter',src='172.29.0.1',dst='127.0.0.1',both=True)
        self.assertEqual(obj.src,'\xac\x1d\x00\x01')
        self.assertEqual(obj.dst,'\x7f\x00\x00\x01')
        self.assertTrue(obj.both)
        self.assertEqual(obj.nxt,None)

    def test_apply_attrs(self):
        obj = create_object('filter.ipfilter.IPFilter')
        config = {'name':'IPFilter.TEST',
                'src':'172.29.0.1',
                'dst':'127.0.0.1',
                'both':'true',
                'bad':'raise_attr_error'
                }
        obj = apply_attrs(obj,config)

        self.assertEqual(obj.name, 'IPFilter.TEST')
        self.assertEqual(obj.src, '\xac\x1d\x00\x01')
        self.assertEqual(obj.dst, '\x7f\x00\x00\x01')
        self.assertTrue(obj.both)
        with self.assertRaises(AttributeError):
            bad = self.bad

    def test_apply_attrs_force(self):
        obj = create_object('filter.ipfilter.IPFilter')
        config = {'name':'IPFilter.TEST',
                'src':'172.29.0.1',
                'dst':'127.0.0.1',
                'both':'true',
                'forced':'forced_attr'
                }
        obj = apply_attrs(obj,config,force=True)
        self.assertEqual(obj.name, 'IPFilter.TEST')
        self.assertEqual(obj.src, '\xac\x1d\x00\x01')
        self.assertEqual(obj.dst, '\x7f\x00\x00\x01')
        self.assertEqual(obj.forced, 'forced_attr')

    def test_create_chain(self):
        config = {'class':'filter.bpffilter.BPFFilter',
                'name':'BPFilter.TEST',
                'expression':'ip.src == 127.0.0.1',
                'next':{
                    'class':'filter.portfilter.TCPFilter',
                    'name':'TCPFilter.HTTP/S',
                    'sport':'80',
                    'dport':'53',
                    'both':'true'
                    }
                }

        parent = create_chain(config)
        child = parent.nxt

        self.assertEqual(parent.__class__.__name__,'BPFFilter')
        self.assertEqual(parent.name,'BPFilter.TEST')
        self.assertEqual(parent.expression,'ip.src == 127.0.0.1')
        self.assertNotEqual(parent.nxt,None)

        self.assertEqual(child.__class__.__name__, 'TCPFilter')
        self.assertEqual(child.name, 'TCPFilter.HTTP/S')
        self.assertEqual(child.sport, '\x00P')
        self.assertEqual(child.dport, '\x005')
        self.assertEqual(child.nxt, None)


