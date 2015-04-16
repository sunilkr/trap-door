from filter.abstractfilter import AbstractFilter
from util.logging import Log, syslog
from util.datatypes import *
from dpkt import ethernet as L2

class IPFilter(AbstractFilter):

    def __init__(self, name=None, src=None, dst=None, both=False, inverse=False ,_next=None):
        self.src = src
        self.dst = dst
        self.both = both
        self.inverse = inverse
        super(IPFilter,self).__init__(name,_next)
    
    def __setattr__(self,name,value):
        if name == 'both':
            value = to_bool(value)
        elif name == 'src' or name == 'dst':
            value = ip4_to_bytes(value) #Convert dotted-decimal to bytes
        elif name == 'inverse':
            value = to_bool(value)
        
        super(IPFilter,self).__setattr__(name,value)

    def execute(self,packet):
        result = 0
        pkt = L2.Ethernet(packet[1])       #[hdr,data]
        if hasattr(pkt,'ip'):
            ip_packet = pkt.data
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
        
        final =  ((result > 1) and super(IPFilter,self).execute(packet))
        return final ^ self.inverse

    def attribs(self):
        return "name:%s, src:%s, dst:%s, both:%s, inverse:%s" %(self.name,
                bytes_to_ip4(self.src), bytes_to_ip4(self.dst), self.both, self.inverse)

    def attrs(self):
        config = super(IPFilter, self).attrs()
        if self.src:
            config['src'] = bytes_to_ip4(self.src)
        if self.dst:
            config['dst'] = bytes_to_ip4(self.dst)

        config['inverse'] = str(self.inverse)
        config['both'] = str(self.both)

        return config
