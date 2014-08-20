from core.controller import Controller
from util.cfgparser import CfgParser

from time import sleep
import signal
import os

CNF = 'config/config2.cfg'
trapd = None

def main():
    global trapd
    print "Creating and staring TrapDoor..."
    trapd = Controller()
    trapd.start()
    
    load_config(CNF, trapd)
    signal.signal(signal.SIGHUP, sighup_handler)
    fpid = open('controller.pid','w')
    fpid.write(str(os.getpid()))
    fpid.close()

    print "Started Monitoring..."
    try:
        while True:
            status = trapd.status()
            print "Filter Queue Size: {0}".format(status['filterq']['size'])
            print "Logger Queue Size: {0}".format(status['loggerq']['size'])
            print "--DNS Entries--"
            for name,ip in status['dnstable'].items():
                print "{0} --> {1}".format(name,ip)
            print "----"
            sleep(5)
    except KeyboardInterrupt:
        trapd.finish()

def load_config(cnf, ctrlr):
    print "Loading configurations from {0}".format(cnf)
    config = CfgParser().parse(cnf) 
    cfg = config['trapdoor']


    print "Adding interfaces..."
    for iface in cfg['iface']:
        print "Adding interface: {0}".format(iface)
        ctrlr.add_iface(iface)

    print "Adding filters..."
    for _filter in cfg['filters']:
        ctrlr.add_filter_chain(_filter)

    print "Adding Loggers..."
    for logger in cfg['loggers']:
        ctrlr.add_logger(logger)


def sighup_handler(signum, frame):
    print "Clearing old configurations..."
    trapd.reset()
    load_config(CNF, trapd)

if __name__ == "__main__":
    main()
