import unittest

from util.datatypes import *

class DataTypesTest(unittest.TestCase):

    def test_to_bool(self):
        for value in ['yes', "Y", "True", "t", "1"]:
            self.assertTrue(to_bool(value))
        for value in ['no', 'N', 'False', 'f', '0']:
            self.assertFalse(to_bool(value))

        with self.assertRaises(ValueError):
            to_bool('TEST')

    def test_ip4_to_bytes(self):
        self.assertEqual(ip4_to_bytes('127.0.0.1'),'\x7f\x00\x00\x01')

    def test_bytes_to_ip4(self):
        self.assertEqual(bytes_to_ip4('\x7f\x00\x00\x0a'), '127.0.0.10')

    def test_tcp_flags_to_value(self):
        flags = ['SYN','ACK','FIN','URG', 'PSH', 'RST']
        self.assertEqual(tcp_flags_to_value(flags), 63)

    def test_bytes_to_tcp_flags(self):
        flags = set(['ACK','FIN','RST','URG','SYN','PSH'])
        self.assertEqual(len(flags - set(value_to_tcp_flags(63))), 0)

    def test_bytes_to_mac(self):
        value = '\x00\x90\xfb8\xb5H'
        self.assertEqual(bytes_to_mac(value), '00:90:fb:38:b5:48')

    def test_mac_to_bytes(self):
        mac = 'b8:ca:3a:83:73:6a'
        self.assertEqual(mac_to_bytes(mac), '\xb8\xca:\x83sj')

    def test_l3_proto_name(self):
        self.assertEqual(l3_proto_name(2048), "IP")
        self.assertEqual(l3_proto_name(0x1000), "INVALID")

    def test_l4_proto_name(self):
        self.assertEqual(l4_proto_name(6), 'TCP')
        self.assertEqual(l4_proto_name(150), "RESERVED")

if __name__ == "__main__":
    unittest.main()
