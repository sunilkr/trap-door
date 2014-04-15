from multiprocessing import Queue

class FilterManager:

    __in_filters={}
    __filter_q = None
    __logger_q = None
    __stop = False

    def __init__(self,q_filter, q_logger):
        self.__filter_q = q_filter
        self.__logger_q = q_logger


    def process(self,packet):
        result = False

        for name,filter in self.__in_filters.items():
            result = filter.apply(packet)
            if result:
#                syslog(Log.DEBUG," Matched by "+name)
                break

        return result


    def add_filter(self,name,filter)
        if self.__in_filters.get(name) is not None:
            self.__in_filters[name] = filter
            return True
        else:
            return False

    def start(self):
        while not self.__stop:
            try:
                packet = self.__filter_q.get(timeout=1)
                if self.process(packet):
                    self.__logger_q.put(packet)
            except Queue.Empty as e:
#                syslog(Log.WARN,"Filter queue is empty")
    
    def stop(self):
        self.__stop = True;



