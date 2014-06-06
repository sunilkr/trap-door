from filter.abstractfilter import AbstractFilter
from util.logging import Log, syslog
from util.datatypes import *
from dpkt import ethernet as L2

class IPFilter(AbstractFilter):

    def __init__(self,name=None, src=None, dst=None, both=False ,_next=None):
        self.src = src
        self.dst = dst
        self.both = both
        super(IPFilter,self).__init__(name,_next)
    
    def __setattr__(self,name,value):
        if name == 'both':
            super(IPFilter,self).__setattr__(name, to_bool(value))
        elif name == 'src' or name == 'dst':
            super(IPFilter,self).__setattr__(name,ip4_to_bytes(value)) #Convert dotted to bytes
        else: 
            super(IPFilter,self).__setattr__(name,value)

    def execute(self,packet):
        result = 0
        packet = L2.Ethernet(packet[1])       #[hdr,data]
        if packet.type == L2.ETH_TYPE_IP:
            ip_packet = packet.data
            if self.src:
                if self.src == ip_packet.src or (self.both and self.src == ip_packet.dst):
                    result +=1
            else:
                result +=1

            if self.dst:
                if self.dst == ip_packet.dst or (self.both and self.dst == ip_packet.src):
                    result +=1
            else:
                result +=1

        if (result > 1) and super(IPFilter,self).execute(packet) :
            return True
        else:
            return False

    def attribs(self):
        return "name:%s, src:%s, dst:%s, both:%s" %(self.name,
                bytes_to_ip4(self.src), bytes_to_ip4(self.dst), self.both)

    def attrs(self):
        return {'name'  : self.name,
                'src'   : bytes_to_ip4(self.src),
                'dst'   : bytes_to_ip4(self.dst),
                'both'  : self.both,
                'next'  : str(self.nxt)
                }
