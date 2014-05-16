class Logger(object):

    __filter = None
    __target = None

    def __init__(self,target=None, out_filter=None):
        self.__target = target
        self.__filter = out_filter

    def set_filter(self,out_filter):
        self.__filter = out_filter

    def get_filter(self):
        return self.__filter

    def log(self,packet):
        pass

