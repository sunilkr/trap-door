from util.logging import Log, syslog
from util.datatypes import *
from logger import Logger
#from scapy.all import *
from datetime import datetime
from dpkt.ethernet import Ethernet

class TextLogger(Logger): 
    """
        Logs packet information to a text file.
        Uses the summary from scapy Packet.
        Packet data treated as EN10MB
    """

    def __init__(self, name=None, target=None,  _filter=None):
        super(TextLogger,self).__init__(name, target, _filter)
        self.__file = None
        if target is not None:
            self.__init_target(target)

    def log(self,packet):
        if super(TextLogger,self).check(packet):
            #pkt = Ether(packet[1])  #packet = [hdr,daata]
            #self.target.write(pkt.summary()+"\n")
            self.__file.write(self._format(packet)+"\n")
            self.__file.flush()

    def _format(self, packet):
        phdr = packet[0]
        hdr = "{0}|{1}|{2}|".format(datetime.fromtimestamp(phdr[0]),phdr[1],phdr[2])
        pdata = hdr+"ETH|"
        pkt = Ethernet(packet[1])
        pdata += bytes_to_mac(pkt.src)+"|"
        pdata += bytes_to_mac(pkt.dst)+"|"
        if hasattr(pkt,'ip'):
            pkt = pkt.ip
            pdata += "IP|{0}|{1}|".format(bytes_to_ip4(pkt.src), bytes_to_ip4(pkt.dst))
            if hasattr(pkt,"tcp"):
                pkt = pkt.tcp
                pdata += "TCP|{0}|{1}|{2}|".format(pkt.sport, pkt.dport, 
                        value_to_tcp_flags(pkt.flags))
            elif hasattr(pkt,"udp"):
                pkt = pkt.udp
                pdata += "UDP|{0}|{1}|".format(pkt.sport, pkt.dport)
            else:
                pdata += l4_proto_name(pkt.p) + "|"
        else:
            pdata += l3_proto_name(pkt.type) + "|"
        
        pdata += str(len(pkt.data))
        return pdata

    def __init_target(self, name):
        if name is not None:
            self.__file = open(name,'w')
            hdr = "time|msec|len|proto.l2|eth.src|eth.dst|proto.l3|ip.src|ip.dst|proto.l4|l4.sport|l4.dport|tcp.flags|payload.len\n"

            self.__file.write(hdr)
            self.__file.flush()
        else:
            self.__file = None

    def __setattr__(self,name,value): 
#        syslog(Log.DBG,"LOGGER.__setattr__ {0}:{1}".format(name,value))
        if name == 'target':
            self.__init_target(value)
        super(TextLogger,self).__setattr__(name,value)

    def close(self):
        if self.__file is not None:
            self.__file.close()
            self.__file = None
