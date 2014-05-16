#from scapy.all import *
from util import logging as log
import traceback
import pcapy

'''
    Listens on a network interface and queues the packets
    to FilterQueue
'''
class NetListener:
    __iface = None
    __listen_ip = None
    __filter = None
    __stop = False
    
    def __init__(self, iface, ip=None, filter=None):
        self.__iface = iface
        self.__listen_ip = ip if ip else self.__get_ip(iface)
        self.__filter = filter

    def __get_ip(self,iface):
        pass

    def set_callback(self,call_back):
        self.__prn = call_back

    def stop(self):
        self.__stop = True

    def start(self,queue):
        self.queue = queue
        cap = pcapy.open_live(self.__iface, 65536, 1, 0)
        while not self.__stop:
            try:
                (header,pkt) = cap.next()
            except Exception, e:
                pass
            else:
                self.queue.put(pkt)

        '''
        sniff(iface=self.__iface, filter=self.__filter, 
                prn = lambda pkt: self.queue.put(pkt) if isinstance(pkt, scapy.packet.Packet) else 0, 
                store=0)
#                prn=lambda pkt:try_put(self.queue,pkt), store=0)
        '''

'''
def try_put(queue,packet):
    try:
        queue.put(packet)
    except Exception, e:
        log.syslog(log.WARN, traceback.format_exec())
'''
