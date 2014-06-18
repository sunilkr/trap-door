import unittest
import dpkt

from logger.pcaplogger import PcapLogger
from util.factory import apply_attrs

class PcapLoggerTest(unittest.TestCase):
    def setUp(self):
        self.logger = PcapLogger()

    def test_log(self):
        config={'name':'PCAPLogger.TEST',
                'target':'/tmp/test.pcap',
                }
        logger = apply_attrs(self.logger, config)
        pkt = '\xb8\xca:\x83sj\x00\x90\xfb8\xb5H\x08\x00E\x00\x004\x00\x00@\x00@\x06\xf0\xfaC\xd4X\n\xac\x1d\x01\xce\x00P\x92l>\xfd\xd6\xe8\x04HI\x0b\x80\x12\x16\xd0\x18t\x00\x00\x02\x04\x05\xb4\x01\x01\x04\x02\x01\x03\x03\x05'
        hdr=[0,0,66,66]

        self.logger.log([hdr,pkt])
        self.logger.close()

        pcap = dpkt.pcap.Reader(open('/tmp/test.pcap'))
        count = 0
        pkt = None
        for ts,buf in pcap:
            count +=1
            pkt = dpkt.ethernet.Ethernet(buf)

        self.assertEqual(count,1)
        self.assertEqual(pkt.ip.tcp.sport,80)
        self.assertEqual(pkt.ip.tcp.dport,37484)
        
    def tearDown(self):
        self.logger.close()


if __name__ == "__main__":
    unittest.main()
