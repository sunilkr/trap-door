import inputfilter
from scapy.all import *

class IPFilter(InputFilter):

    __src_ip = None
    __dst_ip = None
    __both = False # math src and dst in both direction?
    
    def __init(self,src = None, dst = None, both = False ,next_filter=None):
        super(next_filter)
        self.__src_ip = src
        self.__dst_ip = dst
        self.__both = both
    
    def apply(self,packet):
        result = False
        if packet[IP].src == self.__src_ip and packet[IP].dst == self.__dst_ip
            result = True
        elif self.__both and packet[IP].dst = self.__src_ip and packet[IP].src == self.__dst_ip
            result = True

        return (result and super.apply(packet))
