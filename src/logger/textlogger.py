from logger import Logger
from scapy.all import *
#from scapy.all import *

class TextLogger(Logger):
    '''    
    __format =  "{IP: IP,%IP.src%,%IP.dst%},"+
                "{TCP: TCP,%TCP.sport,%TCP.dport,%TCP.flags}"+
                "{UDP: UDP,%UDP.sport,%UDP.dport,-},"+
                "{Raw: %Raw.size%}"
    '''                

    def __init__(self, target, out_filter=None):
        super(TextLogger,self).__init__(target, out_filter)
        self.__target = target

    def log(self,packet):
        pkt = Ether(packet)
        self.__target.write(pkt.summary()+"\n")
        self.__target.flush()
#        os.fsync(self.__target.fileno())

