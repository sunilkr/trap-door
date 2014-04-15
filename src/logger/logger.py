class Logger:

    __filter = None
    __target = None

    def __init__(self,target=None, filter=None):
        self.__target = target
        self.__filter = filter

    def set_filter(self,filter):
        self.__filter = filter

    def get_filter(self):
        return self.__filter

    def log(self,packet):
        pass

