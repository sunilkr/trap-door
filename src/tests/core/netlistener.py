import unittest

from core.netlistener import NetListener
import util.datatypes as dt
from multiprocessing import Queue, Process, Pipe
from os import system
from time import sleep

class NetListenerTest(unittest.TestCase):
    
    def test_getip(self):
        netl = NetListener('lo')
        self.assertEqual(netl.getip(), '127.0.0.0')

    def test_getmask(self):
        netl = NetListener('lo')
        self.assertEqual(netl.getmask(), None)

    def test_getpcap(self):
        netl = NetListener('lo')
        self.assertEqual(netl.getpcap().getnet(), '127.0.0.0')

    def test_start(self):
        netl = NetListener('lo')
        q = Queue()
        l,r = Pipe()
        proc = Process(target=netl.start, args=(q,r))
        proc.start()
        system('ping -c 1 localhost')
        sleep(1)        # Avoid race-condition
        l.send([dt.CMD_STOP, 0])
        res = l.recv()
        proc.join()

        self.assertGreater(q.qsize(), 0)
        self.assertEqual(res[0], dt.STATUS_OK)


if __name__ == "__main__":
    unittest.main()
