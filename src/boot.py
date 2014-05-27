from core.trapdoor import TrapDoor
from util.cfgparser import CfgParser

CNF = 'config/config.cfg'

def main():
    config = CfgParser().parse(CNF) 
    cfg = config['trapdoor']
    
    print "Createing and staring TrapDoor..."
    trapd = TrapDoor()
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
    trapd.stat(5)
    

if __name__ == "__main__":
    main()
