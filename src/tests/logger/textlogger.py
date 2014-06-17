import unittest

from logger.textlogger import TextLogger
from datetime import datetime
from util.factory import apply_attrs

class TextLoggerTest(unittest.TestCase):
    def setUp(self):
        self.logger = TextLogger()

    def test_log(self):
        hdr = [1402910019,205534,66,66]
        pkt = '\xb8\xca:\x83sj\x00\x90\xfb8\xb5H\x08\x00E\x00\x004\x00\x00@\x00@\x06\xf0\xfaC\xd4X\n\xac\x1d\x01\xce\x00P\x92l>\xfd\xd6\xe8\x04HI\x0b\x80\x12\x16\xd0\x18t\x00\x00\x02\x04\x05\xb4\x01\x01\x04\x02\x01\x03\x03\x05'
        config={'name':'TextLogger.TEST',
                'target':'/tmp/packet.log'
                }
        logger = apply_attrs(self.logger, config)
        logger.log([hdr,pkt])
        logger.close()
        
        log_f = open(config['target'], "r")

        self.assertEqual(log_f.readline().find("time"),0)
        parts = log_f.readline().strip().split("|")
        self.assertEqual(len(parts), 14)
        self.assertEqual(parts[0], '2014-06-16 14:43:39')
        self.assertEqual(parts[1], '205534')
        self.assertEqual(parts[2], '66')
        self.assertEqual(parts[3], 'ETH')
        self.assertEqual(parts[4], '00:90:fb:38:b5:48')
        self.assertEqual(parts[5], 'b8:ca:3a:83:73:6a')
        self.assertEqual(parts[6], 'IP')
        self.assertEqual(parts[7], '67.212.88.10')
        self.assertEqual(parts[8], '172.29.1.206')
        self.assertEqual(parts[9], 'TCP')
        self.assertEqual(parts[10], '80')
        self.assertEqual(parts[11], '37484')
        self.assertEqual(parts[12], "['ACK', 'SYN']")
        self.assertEqual(parts[13], '0')

    def tearDown(self):
        self.logger.close()


if __name__ == "__main__":
    unittest.main()
