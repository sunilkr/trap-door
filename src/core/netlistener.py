from scapy.all import *

class NetworkListener:
    '''
    Listens on a network interface and queues the packets
    to FilterQueue
    '''
    __iface = None
    __listen_ip = None
    __filter = None
    __stop = False
    
    def __init__(self, iface=None, ip=None, filter=None):
        self.__iface = iface
        self.__listen_ip = ip if ip else __get_ip(iface)
        self.__filter = filter

    def __get_ip(self,iface):
        pass

    def set_callback(self,call_back):
        self.__prn = call_back

    def stop(self):
        self.__stop = True

    def start(self):
        sniff(iface=self.__iface, filter=self.__filter, prn=self.__prn, store=0)

