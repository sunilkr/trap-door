class Filter(object):
    __next = None
   
    def __init__(self,_next=None):
        self.__next = _next

    '''
        return result of next filter or True by default
    '''
    def execute(self,packet):
        return self.__next.execute(packet) if self.__next else True
    
    def set_next(_filter):
        self.__next = _filter
