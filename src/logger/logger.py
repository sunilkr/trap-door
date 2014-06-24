class Logger(object):

    def __init__(self, name=None, target=None, _filter=None):
        self.target = target
        self.__filter = _filter
        self.name = name

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

    def attrs(self):
        attrs ={'name':  self.name,
                'class': self.__module__ + "." + self.__class__.__name__,
                'target': self.target
                }
        if self.__filter:
            attrs['filter'] = self.__filter.attrs()

        return attrs

