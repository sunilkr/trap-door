import multiprocessing as mp
from time import sleep

#import netlistener
from util.logging import Log, syslog
import util.datatypes as dt
from filter.filtermanager import FilterManager
from logger.logmanager import LogManager
from filter.ipfilter import IPFilter
from threading import Thread
from time import sleep

class TrapDoor:
    
    listeners = []
    net_procs = []
    instance = None
    dns_table = {}

    def __init__(self):
        self.loggermgr = {}
        self.loggermgr['queue'] = mp.Queue()    
        self.loggermgr['obj'] = LogManager()
        
        self.filtermgr = {}
        self.filtermgr['queue'] = mp.Queue()
        self.filtermgr['obj'] = FilterManager()
        
        self.pipe_net = []
#        self.dnsmanager = DNSUpdater(self.dns_table)
    
    def init_loggers(self):
        local, remote = mp.Pipe() 
        self.loggermgr['proc'] = mp.Process(target=self.loggermgr['obj'].start, 
                args=(self.loggermgr['queue'],remote))
        self.loggermgr['comm'] = local

    
    def init_filters(self):
        local, remote = mp.Pipe()
        self.filtermgr['comm'] = local
        self.filtermgr['proc'] = mp.Process(target=self.filtermgr['obj'].start, 
                args=(self.filtermgr['queue'], self.loggermgr['queue'], remote))
    
    def add_listener(self,listener):
        local,remote = mp.Pipe()
        self.pipe_net.append(local)
        self.listeners.append(listener)
        proc = mp.Process(target=listener.start, args=(self.filtermgr['queue'],remote))
        self.net_procs.append(proc)

    def start(self):
        syslog(Log.INFO, "Starting Filter Manager...")
        self.filtermgr['proc'].start()
        syslog(Log.INFO, "FilterManager PID: {0} ".format(self.filtermgr['proc'].pid))

        syslog(Log.INFO, "Staring Logger Manager...")
        self.loggermgr['proc'].start()
        syslog(Log.INFO, "LogManager PID: {0}".format(self.loggermgr['proc'].pid))

        syslog(Log.INFO, "Starting Listeners...")
        for proc in self.net_procs:
            proc.start()
            syslog(Log.INFO, "Listener PID: {0}".format(proc.pid))

        syslog(Log.INFO, "Starting DNS Manager...")
        #self.dnsmanager.set_comm(self.filtermgr['comm'])
        #self.dnsmanager.deamon = True
        #self.dnsmanager.start()

    def stat(self, delay):
        try:
            while True:
                syslog(Log.DBG, "Filter Queue Size {0}".format(self.filtermgr['queue'].qsize()))
                syslog(Log.DBG, "Logger Queue Size {0}".format(self.loggermgr['queue'].qsize()))
                sleep(delay)
        except KeyboardInterrupt, e:
            self.finish()

    def finish(self):
        syslog(Log.INFO,"Stoppng DNS Manager...")
#        self.dnsmanager.stop()

        syslog(Log.INFO,"Stoppng Listeners...")
        for comm in self.pipe_net:
            comm.send([dt.CMD_STOP,None])
            comm.close()
#            syslog(Log.INFO,comm.recv())
        for proc in self.net_procs:
            proc.join()

        syslog(Log.INFO, "Stopping FilterManager...")
        self.filtermgr['comm'].send([dt.CMD_STOP,None])
#        syslog(Log.INFO, self.pipe_filter.recv())
        self.filtermgr['proc'].join()
        self.filtermgr['comm'].close()

        syslog(Log.INFO, "Stopping LogManager...")
        self.loggermgr['comm'].send([dt.CMD_STOP,None])
#        syslog(Log.INFO,self.pipe_logger.recv())
        self.loggermgr['proc'].join()
        self.loggermgr['comm'].close()

        syslog(Log.INFO, "DONE")
        
    def add_ipfilter(self, config):
        self.filtermgr['comm'].send([dt.CMD_ADD, config])
        syslog(Log.INFO,self.filtermgr['comm'].recv())

    def add_dnsfilter(self, config):
#        src = self.dnsmanager.add_target(config['source'],config['name'],'src')
#        dst = self.dnsmanager.add_target(config['destin'],config['name'],'dst')
#        config['src']=src
#        config['dst']=dst
        self.filtermgr['comm'].send([dt.CMD_ADD, config])
        del config['src']
        del config['dst']
        syslog(Log.INFO,self.filtermgr['comm'].recv())

    def add_logger(self, config):
        self.loggermgr['comm'].send([dt.CMD_ADD, config])
        syslog(Log.INFO,self.loggermgr['comm'].recv())
        

class DNSUpdater(Thread):
    def __init__(self,table,comm=None, wait=300):
        self.table = table
        self.comm = comm
        self.wait = wait
        self.__stop = False
        Thread.__init__(self)

    def add_target(self,name,target,attr):
        ip = None

        if name != None:
            try:
                self.table[name][1].append((target,attr))
            except KeyError:
                data = (gethostbyname(name),[(target,attr)])
                self.table[name] = data
            finally:
                ip = self.table[name][0]

        return ip

    def get_ip(self,name):
        return self.table[name][0]

    def set_comm(self,comm):
        self.comm = comm

    def run(self):
        if self.comm is None:
            raise AttributeError, "comm must not be None"
        while not self.__stop:
            for name in self.table.keys():
                ip,targets = self.table[name]
                ip = gethostbyname(name)
                self.table[name][0]=ip
                for target in targets:
                    config = {'name':target[0],attr:ip}
                    try:
                        comm.send([dt.CMD_UPDATE,config])
                        syslog(Log.INFO, comm.recv())            
                    except IOError:
                        pass
            sleep(self.wait)

    def stop(self):
        self.__stop = True
    
