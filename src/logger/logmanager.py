class LogManager:

    __logger_q = None
    __loggers = {}

    def __init__(self,q_logger):
        self.__logger_q = q_logger
    
    def add_logger(self,name,logger):
        if self.__loggers.get(name) is None:
            self.__loggers[name] = logger

    def update_logger(self,name,logger):
        self.__logger[name] = logger

    def start(self):
