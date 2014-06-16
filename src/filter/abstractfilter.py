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

    def __setattr__(self,name,value):
        if value == 'None':     # Explicitely set value to None
            value = None
        super(AbstractFilter,self).__setattr__(name,value)
