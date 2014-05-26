class AbstractFilter(object):
   
    def __init__(self,name=None,_next=None):
        self._next = _next
        self.name = name

    '''
        return result of next filter or True by default
    '''
    def execute(self,packet):
        return self._next.execute(packet) if self._next else True
    
    def set_next(self,_filter):
        self._next = _filter
