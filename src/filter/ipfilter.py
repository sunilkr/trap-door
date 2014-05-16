from filter import Filter

#from scapy.all import *

class IPFilter(Filter):

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

        if packet.has_layer("IP"):
            if self.__src_ip and self.__dst_ip:
                if packet[IP].src == self.__src_ip and packet[IP].dst == self.__dst_ip:
                    result = True
                elif self.__both and packet[IP].dst == self.__src_ip and packet[IP].src == self.__dst_ip:
                    result = True
            elif self.__src_ip and packet[IP].src == self.__src_ip: # Only SRC IP
                result = True
            elif self.__dst_ip and packet[IP].dst == self.__dst_ip: # Only DST IP
                result = True
            elif not (self.__src_ip or self.__dst_ip):
                result = True

        return (result and super.apply(packet))
