from util.logging import Log, syslog
import traceback
import pcapy
from struct import pack

'''
    Listens on a network interface and queues the packets
    to FilterQueue
'''
class NetListener:
    
    def __init__(self, iface, ip=None, _filter=None):
        self.__iface = iface
        self.__filter = _filter
        self.pcap = pcapy.open_live(self.__iface, 65536, 1, 0)
        self.__stop = False
        self.ip = self.getip()
        self.netmask = self.getmask()

    def getip(self):
        return self.pcap.getnet()
    
    def getmask(self):
         self.pcap.getmask()

    def stop(self):
        self.__stop = True

    def getpcap(self):
        return self.pcap

    def start(self,queue):
        self.queue = queue
        while not self.__stop:
            try:
                (phdr,pkt) = self.pcap.next()
            except Exception, e:
                pass
            else:
                ts = phdr.getts()
                hdr = (ts[0],ts[1], phdr.getcaplen(), phdr.getlen())
                data = (hdr, pkt)
                self.queue.put(data)

