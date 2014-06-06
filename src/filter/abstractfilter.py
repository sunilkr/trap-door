class AbstractFilter(object):
   
    def __init__(self,name=None,_next=None):
        self.nxt = _next
        self.name = name

    '''
        return result of next filter or True by default
    '''
    def execute(self,packet):
        return self.nxt.execute(packet) if self.nxt else True
    
    def set_next(self,_filter):
        self.nxt = _filter
