from filter.abstractfilter import AbstractFilter
from scapy.all import *
from util.logging import Log, syslog
from util.datatypes import to_bool 

class IPFilter(AbstractFilter):

    def __init__(self,name=None, src=None, dst=None, both=False ,_next=None):
        self.src = src
        self.dst = dst
        self.both = both
        super(IPFilter,self).__init__(name,_next)
    
    def __setattr__(self,name,value):
        if name == 'both':
            super(IPFilter,self).__setattr__(name, to_bool(value))
        else:
            super(IPFilter,self).__setattr__(name,value)

    def execute(self,packet):
        result = 0
        packet = Ether(packet[1])       #[hdr,data]
        if packet.haslayer("IP"):
            if self.src:
                if self.src == packet[IP].src or (self.both and self.src == packet[IP].dst):
                    result +=1
            else:
                result +=1

            if self.dst:
                if self.dst == packet[IP].dst or (self.both and self.dst == packet[IP].src):
                    result +=1
            else:
                result +=1

        if (result > 1) and super(IPFilter,self).execute(packet) :
            return True
        else:
            return False

    def attribs(self):
        return "name:%s, src:%s, dst:%s, both:%s" %(self.name,self.src,self.dst,self.both)
