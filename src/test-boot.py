from filter.ipfilter import IPFilter
from core.trapdoor import TrapDoor
from core.netlistener import NetListener
from logger.textlogger import TextLogger
from logger.pcaplogger import PcapLogger
import pcapy
from util.factory import create_object
import inspect 
import socket

trapd = None

def init():
    global trapd
    trapd = TrapDoor()
    trapd.init_filters()
#    fltr = IPFilter()
    name = "SSDPAddress"
    ipfcfg = {
            'class':"filter.input.ipfilter.IPFilter",
            'name':"SSDP",
            'dst':'239.255.255.250',
            'both':'false'
            }

#    name,fltr1 = get_object(ipfcfg)
#    trapd.mgr_filter.add_filter(name, fltr)

    ytfcfg = {
            'class':'filter.input.dnsfilter.DNSFilter',
            'name':'YouTubeFilter',
            'both':'true',
            'ddomain':'youtube.com'
            }
            
    print "[*] YouTube IP:%s"%socket.gethostbyname(ytfcfg['ddomain'])
    ytip = socket.gethostbyname("youtube.com")
#    name,fltr = get_object(ytfcfg)
    name,fltr = "Youtube",IPFilter(dst=ytip,both=True)
    trapd.mgr_filter.add_filter(name,fltr)

    netl = NetListener('eth0')
    trapd.add_listener(netl)
    print "[*] LinkType:%d, IP: %s, MASK: %s" %(netl.getpcap().datalink(), netl.getip(), netl.getmask())

    f_log = '../logs/packet.log'
    txtlog = TextLogger(f_log,'w')
    trapd.init_loggers()
    caplog = PcapLogger('../logs/test.pcap',dltype=pcapy.DLT_EN10MB)
    trapd.mgr_logger.add_logger("Text",txtlog)
    trapd.mgr_logger.add_logger("Pcap", caplog)

    trapd.start()
    trapd.stat(1)

def get_object(config):
    name = config['name']
    fltr = create_object(config['class'])
    for key in (set(config.keys()) - set(['name','class'])):
        try:
            getattr(fltr,key)
        except:
            pass
        else:
            setattr(fltr,key,config[key])

    print inspect.getmembers(fltr)
    return (name,fltr)

def test_factory(name):
    obj = create_object(name)
    config = {'src':'172.29.0.1', 'dst':'www.google.com', 'both':'True'}
    print obj.__class__.__name__
    for k,v in config.items():
#        try:
#            print type(getattr(obj,k))
#        except:
#            pass
#        else:
        setattr(obj,k,v)
#    setattr(obj,'src','172.29.0.1')
#    setattr(obj,'dst','www.google.com')
#    setattr(obj,'both',True)
#    print getattr(obj,'both')
    print inspect.getmembers(obj)
init()

#test_factory('test.tc1.TC1')
#test_factory('test.tc2.TC2')
