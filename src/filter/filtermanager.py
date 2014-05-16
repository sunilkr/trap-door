#from multiprocessing import Queue
from util.logging import syslog, Log
#from util import logging as log
from scapy.all import *
import Queue
#import multiprocessing
import traceback

class FilterManager:

    def __init__(self):
       self.__in_filters={}
       self.__filter_q = None
       self.__logger_q = None
       self.__comm = None
       self.__stop = False
    '''
    def __init__(self,q_filter, q_logger):
        self.__filter_q = q_filter
        self.__logger_q = q_logger
    '''

    def process(self,packet):
#        syslog(Log.DBG, "Processing: %s" %packet.summary())
        result = False
        for name,filter in self.__in_filters.items():
            result = filter.apply(packet)
            if result:
                syslog(Log.DBG," Matched by "+name)
                break

        return result


    def add_filter(self,name,filter):
        if self.__in_filters.get(name) is not None:
            self.__in_filters[name] = filter
            return True
        else:
            return False

    def start(self,q_filter,q_logger, comm):
        self.__filter_q = q_filter
        self.__logger_q = q_logger
        self.__comm = comm
        while not self.__stop:
            try:
                pkt = self.__filter_q.get(timeout=1)
                packet = Ether(pkt)
            except Queue.Empty, e:
                syslog(Log.WARN,"Filter queue is empty")
            except Exception, e:
                syslog(Log.WARN,traceback.format_exec())
            else:
#                log.syslog(log.DBG, "Got packet : %s" %packet.summary())
                if self.process(packet):
                    self.__logger_q.put(pkt) # type scapy.packet.Packet throws pickling error
                    print "+",
                else:
                    self.__logger_q.put(pkt)
                    print "-",
            finally:
                self.check_comm()
    
    def stop(self):
        self.__stop = True;

    def check_comm(self):
        if self.__comm.poll():
            cmd = self.__comm.recv()
            self.__stop = True if cmd == 'stop' else False



