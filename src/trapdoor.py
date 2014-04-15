import multiprocessing

import netlistener
'''
import filtermanager
import logmanager
'''
class TrapDoor:
    
    __listeners = []
    filter_queue = None
    logger_queue = None
    instance = None

    def __init__(self,iface):
        
