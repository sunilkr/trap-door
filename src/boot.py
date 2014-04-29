import ConfigParser

from core import trapdoor,netlistener
from filter import filtermanager
from logger import loggermanager

def main():
    global config
    global trapd

    config = load_config('config/config.cfg')

    try:
        # Create trapdoor object
        tdopts = config['trapdoor']
        trapd = TrapDoor()
        ifaces = tdopts['ifaces']
        for ifs in ifaces:
            netl = NetListener(iface=ifs)
            trapd.add_listener(netl)
        
        # Create filter chains
        for filter in tdopts['filters']:
            trapd.add_filter(create_filter(filter))
        
        # Create loggers
        for cfg_logger in tdopts['loggers']:
            trapd.add_logger(create_logger(cfg_logger))


    except e as Exception:
        raise e

'''
 input: 'filter' => (Filter config chained with next)
 output: chain of 'filter' objects
'''
def create_filter(cfg_filter)
    filter = get_object(cfg_filter['class'], cfg_filter['options'])
    if cfg_filter["next"] is not None:
        cfg_filter = cfg_filter["next"]
        filter.set_next(create_filter(cfg_filter))

    return fltr

'''
'''
def create_logger(cfg_logger):
    logger = get_object(cfg_logger['class'], cfg_logger['options'])

