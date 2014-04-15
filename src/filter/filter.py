class Filter:
    __next = None
   
    def __init__(self,next_filter=None):
        self.__next = next_filter

    '''
        return result of next filter or True by default
    '''
    def apply(self,packet):
        return self.__next.apply(packet) if self.__next else True

