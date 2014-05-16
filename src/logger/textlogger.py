import logger
#from scapy.all import *

class TextLogger(Logger):
    '''    
    __format =  "{IP: IP,%IP.src%,%IP.dst%},"+
                "{TCP: TCP,%TCP.sport,%TCP.dport,%TCP.flags}"+
                "{UDP: UDP,%UDP.sport,%UDP.dport,-},"+
                "{Raw: %Raw.size%}"
    '''                

    def __init__(self,target, filter=None):
        super(target,filter)

    def log(self,packet):
        self.__target.write(packet.summary()+"\n")
        self.__target.flush()
#        os.fsync(self.__target.fileno())

