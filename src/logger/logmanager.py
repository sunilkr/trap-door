from util.logging import Log, syslog
import Queue

class LogManager:

    def __init__(self):
        self.__logger_q = None
        self.__loggers = {}
        self.__stop = False

    def add_logger(self,name,logger):
        if self.__loggers.get(name) is None:
            self.__loggers[name] = logger

    def update_logger(self,name,logger):
        self.__loggers[name] = logger

    def start(self,queue,comm):
        self.__logger_q = queue
        self.__comm = comm
        while not self.__stop:
            try:
                packet = queue.get(1)
            except Queue.Empty as e:
                syslog(Log.WARN, "Logger queue is empty")
            else:
                for logger in self.__loggers.values():
                    logger.log(packet)
            finally:
                self.check_comm()

    def check_comm(self):
        pass
