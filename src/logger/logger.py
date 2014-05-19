class Logger(object):

    __filter = None
    target = None

    def __init__(self, target=None, _filter=None):
        self.target = target
        self.__filter = _filter

    def set_filter(self,_filter):
        self.__filter = _filter

    def get_filter(self):
        return self.__filter

    def log(self,packet):
        pass

    def check(self,packet):
        if self.__filter is not None:
            return self.__filter.execute(packet)
        else:
            return True
        
    def close(self):
        pass
