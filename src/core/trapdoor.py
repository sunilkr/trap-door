import multiprocessing as mp

import netlistener
from util.logging import Log, syslog

from filter.filtermanager import FilterManager
#from logger.logmanager import LogManager

from time import sleep


class TrapDoor:
    
    __listeners = []
    __net_procs = []
    filter_queue = None
    logger_queue = None
    instance = None
    mgr_logger = None
    mgr_filter = None
    pipe_logger = None
    pipe_filter = None
    proc_mgr_logger = None
    proc_mgr_filter = None

    def __init__(self):
        self.filter_queue = mp.Queue()
        self.logger_queue = mp.Queue()    
#        self.mgr_logger = LogManager()
        self.mgr_filter = FilterManager()
    '''
    def init_loggers(self):
        self.pipe_logger, remote = mp.Pipe() 
        self.proc_mgr_logger = mp.Process(self.mgr_logger.start, arg=(self.logger_queue,remote))
   ''' 
    def init_filters(self):
        self.pipe_filter, remote = mp.Pipe()
#        self.proc_mgr_filter = mp.Process(target=start_filter, arg=self)
        self.proc_mgr_filter = mp.Process(target=self.mgr_filter.start, 
                args=(self.filter_queue, self.logger_queue, remote))
    
    def add_listener(self,listener):
#        listener.set_callback(capture)
        self.__listeners.append(listener)
        proc = mp.Process(target=listener.start, args=(self.filter_queue,))
        self.__net_procs.append(proc)

    def start(self):
        syslog(Log.INFO, "Starting Filter Manager...")
        self.proc_mgr_filter.start()
        syslog(Log.INFO, "FilterManager PID: %d" %self.proc_mgr_filter.pid)
#        self.proc_mgr_logger.start()
        syslog(Log.INFO, "Starting Listeners...")
        for proc in self.__net_procs:
            proc.start()
            syslog(Log.INFO, "Listener PID: %d" % proc.pid)

    def stat(self):
        while True:
            syslog(Log.DBG, "Filter Queue Size %d " %self.filter_queue.qsize())
            syslog(Log.DBG, "Logger Queue Size %d" %self.logger_queue.qsize())
            sleep(.2)

