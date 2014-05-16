#from logger import textlogger
from filter.ipfilter import IPFilter
from core.trapdoor import TrapDoor
from core.netlistener import NetListener
from logger.textlogger import TextLogger

trapd = None

def init():
    global trapd
    trapd = TrapDoor()
    trapd.init_filters()
    fltr1 = IPFilter()
    trapd.mgr_filter.add_filter("Test-NO-IP", fltr1)

    netl = NetListener('eth0')
    trapd.add_listener(netl)

    f_log = open('../logs/packet.log','w')
    txtlog = TextLogger(f_log)
    trapd.init_loggers()
    trapd.mgr_logger.add_logger("Text",txtlog)

    trapd.start()
    trapd.stat()

init()
