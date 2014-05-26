from impacket.pcapfile import PcapFile
import struct
from logger import Logger
from util.logging import Log, syslog
import traceback

class PcapLogger(Logger):
    '''
        Log data in PCAP2.4 format, Defaults to EN10M DataLink
    '''
    #target is file name, not file object
    def __init__(self, name=None, target=None, dltype=1, _filter=None):    
        self.__struct = struct.Struct("<LLLL")
        self.dltype = dltype
        self.__dumper = None
        if target != None:
            self.__init_dumper(target)

        super(PcapLogger,self).__init__(name, target, _filter)

    def __init_dumper(self,target):
        if self.__dumper is not None:
            try:
                self.__dumper.close()
            except:
                pass

        self.__dumper = PcapFile(fileName=target, mode="wb")
        self.__dumper.setLinkType(self.dltype)        #  for ETH10M

    def __setattr__(self,name,value):
        if name == 'target':
            self.__init_dumper(value)

        super(PcapLogger,self).__setattr__(name,value)

    def log(self,packet):
        if super(PcapLogger,self).check(packet):
            hdr = self.__struct.pack(*packet[0])
            self.__dumper.write(hdr+packet[1])
            self.__dumper.file.flush()

    def close(self):
        self.__dumper.close()
