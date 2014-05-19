from impacket.pcapfile import PcapFile
import struct
from logger import Logger

'''
    Logs data in PCAP2.4 format, Defaults to EN10M DataLink
'''

class PcapLogger(Logger):

    def __init__(self,target, dltype=1, _filter=None):    #target is file name, not file object
        super(PcapLogger,self).__init__(target, _filter)
        self.__dumper = PcapFile(fileName=target, mode="wb")
        self.__dumper.setLinkType(dltype)        #  for ETH10M
        self.__struct = struct.Struct("<LLLL")

    def log(self,packet):
        if super(PcapLogger,self).check(packet):
            hdr = self.__struct.pack(*packet[0])
            self.__dumper.write(hdr+packet[1])
            self.__dumper.file.flush()

    def close(self):
        self.__dumper.close()
