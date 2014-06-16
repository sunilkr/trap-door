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

