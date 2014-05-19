from filter.input.ipfilter import IPFilter
from core.trapdoor import TrapDoor
from core.netlistener import NetListener
from logger.textlogger import TextLogger
from logger.pcaplogger import PcapLogger
import pcapy

trapd = None

def init():
    global trapd
    trapd = TrapDoor()
    trapd.init_filters()
    fltr1 = IPFilter()
    trapd.mgr_filter.add_filter("Test-NO-IP", fltr1)

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
    trapd.stat(0.5)

init()
