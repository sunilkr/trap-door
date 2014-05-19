from logger import Logger
from scapy.all import *



class TextLogger(Logger): 
    def __init__(self, target, mode, _filter=None):
        super(TextLogger,self).__init__(target, _filter)
        self.target = open(target,mode)

    def log(self,packet):
        if super(TextLogger,self).check(packet):
            pkt = Ether(packet[1])  #packet = [hdr,data]
            self.target.write(pkt.summary()+"\n")
            self.target.flush()
    
    def close(self):
        self.target.close()
