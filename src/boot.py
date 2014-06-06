from core.controller import Controller
from util.cfgparser import CfgParser
from time import sleep

CNF = 'config/config.cfg'

def main():

    config = CfgParser().parse(CNF) 
    cfg = config['trapdoor']
    
    print "Createing and staring TrapDoor..."
    trapd = Controller()
    trapd.start()
    
    print "Adding interfaces..."
    for iface in cfg['iface']:
        trapd.add_iface(iface)


    print "Adding filters..."
    for _filter in cfg['filters']:
        trapd.add_filter(_filter)

    print "Adding Loggers..."
    for logger in cfg['loggers']:
        trapd.add_logger(logger)

    print "Started Monitoring..."
#    trapd.stat(5)
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

if __name__ == "__main__":
    main()
