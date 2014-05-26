import pcapy

class BPFFilter(AbstractFilter):

    def __init__(self, name=None, expr=None, _next=None):
        self.expression = expr
        if expr:
            self._bpf = pcapy.compile(pcapy.DLT_EN10MB,65535, expr,0,1)
        super(BPFFilter,self).__init__(name,_next)

    def __steattr__(self,name,value):
        if name == 'expression':
            self._bpf = pcapy.compile(pcapy.DLT_EN10MB, 65535, value, 0, 1)
        super(BPFFilter, self).__setattr__(name,value)

    def execute(self,packet):
        raw = packet[1]
        
        if self._bpf.filter(raw) == 0:
            return super(BPFFilter,self).execute(packet)
        return False
            
    def attribs(self):
        return "name:{0}, expression:{1}".format(self.name, self.expression)
