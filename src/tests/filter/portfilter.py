import unittest

from util.factory import *

class PortFilterTest(unittest.TestCase):

    def test_match(self):
        pass

class TCPFilterTest(PortFilterTest):
    def setUp(self):
        self._filter = create_object('filter.portfilter.TCPFilter')

    def test_execute_no_flags(self):
        config={'name':'TCPFilter.TEST',
                'sport':'37484',
                'dport':'80',
                'both':'false'
                }
        _filter = apply_attrs(self._filter, config)

        pkt = '\xb8\xca:\x83sj\x00\x90\xfb8\xb5H\x08\x00E\x00\x004\x00\x00@\x00@\x06\xf0\xfaC\xd4X\n\xac\x1d\x01\xce\x00P\x92l>\xfd\xd6\xe8\x04HI\x0b\x80\x12\x16\xd0\x18t\x00\x00\x02\x04\x05\xb4\x01\x01\x04\x02\x01\x03\x03\x05'

        self.assertFalse(self._filter.execute([0,pkt]))

        setattr(self._filter,'both','true')
        self.assertTrue(self._filter.execute([0,pkt]))

    def test_execute_with_flags(self):
        config={'name':'TCPFilter.TEST',
                'sport':'80',
                'dport':'37484',
                'both':'true',
                'flags':['FIN']
                }
        _filter = apply_attrs(self._filter,config)

        pkt = '\xb8\xca:\x83sj\x00\x90\xfb8\xb5H\x08\x00E\x00\x004\x00\x00@\x00@\x06\xf0\xfaC\xd4X\n\xac\x1d\x01\xce\x00P\x92l>\xfd\xd6\xe8\x04HI\x0b\x80\x12\x16\xd0\x18t\x00\x00\x02\x04\x05\xb4\x01\x01\x04\x02\x01\x03\x03\x05'

        self.assertFalse(_filter.execute([0,pkt]))

        setattr(_filter, 'flags',['SYN','ACK','PSH'])
        self.assertTrue(_filter.execute([0,pkt]))

    def test_attrs(self):
        config={'name':'TCPFilter.TEST',
                'sport':'80',
                'dport':'443',
                'both':'true',
                'flags':['SYN','ACK']
                }
        _filter = apply_attrs(self._filter,config)
        attrs = _filter.attrs()
        self.assertEqual(attrs['name'],config['name'])
        self.assertEqual(attrs['sport'],80)
        self.assertTrue(attrs['both'])
        self.assertTrue('SYN' in attrs['flags'])
        self.assertTrue('ACK' in attrs['flags'])
        self.assertFalse('FIN' in attrs['flags'])

    def test_setattr(self):
        setattr(self._filter,'flags',['SYN','ACK'])
        self.assertEqual(self._filter.flags, 18)
        setattr(self._filter,'flags','None')
        self.assertEqual(self._filter.flags, None)


class UDPFilterTest(PortFilterTest):
    def setUp(self):
        self._filter = create_object('filter.portfilter.UDPFilter')

    def test_execute(self):
        config={'name':'UDPFilter.TEST',
                'sport':'53',
                'both':'true'
                }
        _filter = apply_attrs(self._filter, config)
        pkt = '33\x00\x00\x00\x0c\xe8@\xf2\x06\x17\x0f\x86\xdd`\x00\x00\x00\x00\x83\x11\x01\xfe\x80\x00\x00\x00\x00\x00\x00\x00\xe0g[\xae\x0b\x06m\xff\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0c\xd0\x94\x07l\x00\x83\x95@M-SEARCH * HTTP/1.1\r\nHost:[FF02::C]:1900\r\nST:urn:schemas-wifialliance-org:device:WFADevice:1\r\nMan:"ssdp:discover"\r\nMX:3\r\n\r\n'
        self.assertFalse(_filter.execute([0,pkt]))

        setattr(_filter, 'sport','1900')
        self.assertEqual(_filter.sport, 1900)
        self.assertTrue(_filter.execute([0,pkt]))


if __name__ == "__main__":
    unittest.main()
