from dpkt.ethernet import Ethernet

from util.logging import syslog, Log
from util.datatypes import *
from abstractfilter import AbstractFilter

from struct import pack, unpack

class PortFilter(AbstractFilter):

    def __init__(self, name=None, sport=None, dport=None,  both = False, inverse=False ,_next=None):
        self.sport = pack("!H",int(sport)) if sport else None
        self.dport = pack("!H",int(dport)) if dport else None
        self.both = both
        self.inverse = False
        super(PortFilter, self).__init__(name,_next)

    def __setattr__(self,name,value):
        if name in ['sport','dport']:
            value = int(value) if value else None
        elif name == 'both':
            value = to_bool(value) if value else False
        elif name == 'inverse':
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
            if self.dport == l4pkt.dport or(self.both and self.dport == l4pkt.sport):
                result +=1
        else:
             result +=1

        return (result > 1) ^ self.inverse

    def execute(self,packet):
        return super(PortFilter,self).execute(packet)
    
    def attrs(self):
        config = super(PortFilter, self).attrs()
        if self.sport:
            config['sport'] = str(self.sport)
        if self.dport:
            config['dport'] = str(self.dport)
        
        config['both'] = str(self.both)
        config['inverse'] = str(self.inverse)
        return config

class TCPFilter(PortFilter):

    def __init__(self, name=None, sport=None, dport=None, flags=None, both=False, inverse=False, _next=None):
        self.flags = tcp_flags_to_value(flags) if flags else None
        super(TCPFilter,self).__init__(name, sport, dport, both, _next)

    def __setattr__(self,name,value):
        if name == 'flags':
            value = tcp_flags_to_value(value)

        super(TCPFilter, self).__setattr__(name,value)

    def execute(self,packet): #FIXME: Might have some edge cases
        ethpkt = Ethernet(packet[1])

        if hasattr(ethpkt,'ip'):
            ippkt = ethpkt.ip
        elif hasattr(ethpacket,'ip6'):
            ippkt = ethpkt.ip6
        else:
            return False

        if hasattr(ippkt,'tcp'):
            tcppkt = ippkt.tcp
        else:
            return False

        #Check Flags: Supprted: FLAG1|FLAG2|..., Not Supported: FLAG1&FLAG2&...
        if self.flags is not None and (tcppkt.flags & self.flags) == 0:
            return False ^ self.inverse     #FIXME: Inverse filter with flags and next??

        return (super(TCPFilter,self).match(tcppkt) and super(TCPFilter,self).execute(packet))

    def attrs(self):
        attrs = super(TCPFilter,self).attrs()
        if self.flags:
            attrs['flags'] = str(value_to_tcp_flags(self.flags))
        return attrs

class UDPFilter(PortFilter):
    
    def execute(self, packet):
        pkt = Ethernet(packet[1])
        
        if hasattr(pkt,'ip'):
            ippkt = pkt.ip
        elif hasattr(pkt,'ip6'):
            ippkt = pkt.ip6
        else:
            return False

        if hasattr(ippkt,'udp'):
            udppkt = ippkt.udp
        else:
            return False

        return (super(UDPFilter,self).match(udppkt) and super(UDPFilter,self).execute(packet))

