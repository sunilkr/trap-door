from dpkt import ethernet as L2
from dpkt.ip import IP as L3
from util.logging import syslog, Log
from util.datatypes import *

from abstractfilter import AbstractFilter
from struct import pack, unpack

class PortFilter(AbstractFilter):

    def __init__(self, name=None, sport=None, dport=None,  both = False, _next=None):
        self.sport = pack("!H",int(sport)) if sport else None
        self.dport = pack("!H",int(dport)) if dport else None
        self.both = both
        super(PortFilter, self).__init__(name,_next)

    def __setattr__(self,name,value):
        if name in ['sport','dport']:
            value = pack("!H",int(value)) if value else None
        elif name == 'both':
            value = to_bool(value) if value else False

        super(PortFilter,self).__setattr__(name,value)

    def match(self,l4pkt):
        result = 0
        if self.sport:
            if self.sport == l4pkt.sport or (self.both and self.sport == l4pkt.dport):
                result +=1
        else:
            result +=1

        if self.dport:
            if self.dst == l4pkt.dport or(self.both and self.dport == l4pkt.sport):
                result +=1
        else:
             result +=1

        return (result > 1)

    def execute(self,packet):
        return super(PortFilter,self).execute(packet)
    
    def attrs(self):
        attrs={ 'name':self.name,
                'sport':unpack("!H",self.sport)[0] if self.sport else None,
                'dport':unpack("!H",self.dport)[0] if self.dport else None,
                'both':self.both,
                'next':str(self.nxt)
                }
        return attrs

class TCPFilter(PortFilter):

    def __init__(self, name=None, sport=None, dport=None, flags=None, both=False, _next=None):
        self.flags = self._parse_flags(flags) if flags else None
        super(TCPFilter,self).__init__(name, sport, dport, both, _next)

    def __setattr__(self,name,value):
        if name == 'flags':
            value = self._parse_flags(value)

        super(TCPFilter, self).__setattr__(name,value)

    def execute(self,packet):
        l2pkt = L2.Ethernet(packet[1])
        l3pkt = None
        l4pkt = None

        if l2pkt.type == L2.ETH_TYPE_IP or l2pkt.type == L2.ETH_TYPE_IP6:
            l3pkt = l3pkt.data
        else:
            return False

        if l3pkt.v == 4 and l3pkt.p == L3.IP_PROTO_TCP:     #IPv4
            l4pkt = l3pkt.data
        elif l3pkt.v == 6 and l3pkt.nxt == L3.IP_PROTO_TCP: #IPv6
            l4pkt = l3pkt.data
        else:
            return False

        return (super(TCPFilter,self).match(l4pkt) and super(TCPFilter,self).execute(packet))

    def attrs(self):
        attrs = super(TCPFilter,self).attrs()
        attrs['flags'] = self.flags
        return attrs

    def _parse_flags(self, flags):
        return str(flags)

class UDPFilter(PortFilter):
    
    def execute(self, packet):
        pkt = L2.Ethernet(packet[1])
        
        if pkt.type == L2.ETH_TYPE_IP or ptk.type == L2.ETH_TYPE_IP6:
            pkt = pkt.data
        else:
            return False

        if pkt.v == 4 and pkt.p == L3.IP_PROTO_UDP:     #IPv4
            pkt = pkt.data
        elif pkt.v == 6 and pkt.nxt == L3.IP_PROTO_UDP: #IPv6
            pkt = pkt.data
        else:
            return False

        return (super(UDPFilter,self).match(self,pkt) and super(UDPFilter,self).execute(packet))

