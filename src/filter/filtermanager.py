from util.logging import syslog, Log
import Queue
import traceback


class FilterManager:

    def __init__(self):
       self.__in_filters={}
       self.__filter_q = None
       self.__logger_q = None
       self.__comm = None
       self.__stop = False 

    def process(self,packet):
        result = False
        for name,_filter in self.__in_filters.items():
            result = _filter.execute(packet)
            if result:
                break

        return result


    def add_filter(self,name,_filter):
        if self.__in_filters.get(name) is None:
            self.__in_filters[name] = _filter
            return True
        else:
            return False

    def start(self,q_filter,q_logger, comm):
        self.__filter_q = q_filter
        self.__logger_q = q_logger
        self.__comm = comm
        while not self.__stop:
            try:
                packet = self.__filter_q.get(timeout=1)
            except Queue.Empty, e:
                syslog(Log.WARN,"Filter queue is empty")
            except Exception, e:
                syslog(Log.WARN,traceback.format_exec())
            else:
                if self.process(packet):      
                    self.__logger_q.put(packet) 
            finally:
                self.check_comm()
    
    def stop(self):
        self.__stop = True;

    def create_filter(self,config):
        pass

    def check_comm(self):
        if self.__comm.poll():
            cmd = self.__comm.recv()
            self.__stop = True if cmd == 'stop' else False
            
