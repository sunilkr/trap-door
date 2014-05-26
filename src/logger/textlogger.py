from util.logging import Log, syslog
from logger import Logger
from scapy.all import *

class TextLogger(Logger): 
    """
        Logs packet information to a text file.
        Uses the summary from scapy Packet.
        Packet data treated as EN10MB
    """

    def __init__(self, name=None, target=None,  _filter=None):
        super(TextLogger,self).__init__(name, target, _filter)
        if target is not None:
            self.__init_target(target)

    def log(self,packet):
        if super(TextLogger,self).check(packet):
            pkt = Ether(packet[1])  #packet = [hdr,data]
            self.target.write(pkt.summary()+"\n")
            self.target.flush()

    def __init_target(self, name):
        self.target = open(name,'w')

    def __setattr__(self,name,value): 
#        syslog(Log.DBG,"LOGGER.__setattr__ {0}:{1}".format(name,value))
        if name == 'target':
            self.__init_target(value)
        else:
            super(TextLogger,self).__setattr__(name,value)

    def close(self):
        self.target.close()
