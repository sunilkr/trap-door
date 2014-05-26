import multiprocessing as mp
from threading import Thread
from time import sleep, time, strftime, localtime
import re
import sys
import socket
from netlistener import NetListener
from util.logging import Log, syslog
import util.datatypes as dt
from filter.filtermanager import FilterManager
from logger.logmanager import LogManager
from filter.ipfilter import IPFilter

class TrapDoor:
    
    listeners = []
    net_procs = []
    instance = None
    dns_table = {}

    def __init__(self):
        self.loggermgr = {}
        self.loggermgr['queue'] = mp.Queue()    
        self.loggermgr['obj'] = LogManager()
        self._init_loggers()

        self.filtermgr = {}
        self.filtermgr['queue'] = mp.Queue()
        self.filtermgr['obj'] = FilterManager()
        self._init_filters()

        self.pipe_net = []
        self.dnsmanager = DNSUpdater(self.dns_table)
        
    def _init_loggers(self):
        local, remote = mp.Pipe() 
        self.loggermgr['proc'] = mp.Process(target=self.loggermgr['obj'].start, 
                args=(self.loggermgr['queue'],remote))
        self.loggermgr['comm'] = local

    
    def _init_filters(self):
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
        self.dnsmanager.set_comm(self.filtermgr['comm'])
        self.dnsmanager.deamon = True
        self.dnsmanager.start()

    def stat(self, delay):
        try:
            while True:
                syslog(Log.DBG, "Filter Queue Size {0}".format(self.filtermgr['queue'].qsize()))
                syslog(Log.DBG, "Logger Queue Size {0}".format(self.loggermgr['queue'].qsize()))
                sleep(delay)
        except KeyboardInterrupt, e:
            self.finish()

    def finish(self):
        syslog(Log.INFO,"Stopping DNS Manager...")
        self.dnsmanager.stop()

        syslog(Log.INFO,"Stopping Listeners...")
        for comm in self.pipe_net:
            comm.send([dt.CMD_STOP,None])
            comm.close()
        for proc in self.net_procs:
            proc.join()

        syslog(Log.INFO, "Stopping FilterManager...")
        self.filtermgr['comm'].send([dt.CMD_STOP,None])
        self.filtermgr['proc'].join()
        self.filtermgr['comm'].close()

        syslog(Log.INFO, "Stopping LogManager...")
        self.loggermgr['comm'].send([dt.CMD_STOP,None])
        self.loggermgr['proc'].join()
        self.loggermgr['comm'].close()

        syslog(Log.INFO, "DONE")
        
    def add_ipfilter(self, config):
        self.filtermgr['comm'].send([dt.CMD_ADD, config])
        syslog(Log.INFO,self.filtermgr['comm'].recv())

    def add_filter(self,config):
        if config.has_key('src'):
            config['src'] = self.dnsmanager.add_target(config['src'],config['name'],'src')
        if config.has_key('dst'):
            config['dst'] = self.dnsmanager.add_target(config['dst'],config['name'],'dst')
        
        self.filtermgr['comm'].send([dt.CMD_ADD, config])
        syslog(Log.INFO, self.filtermgr['comm'].recv())

    def add_logger(self, config):
        self.loggermgr['comm'].send([dt.CMD_ADD, config])
        syslog(Log.INFO,self.loggermgr['comm'].recv())

    def add_iface(iface):
        netl = NetListener(iface)
        self.add_listener(netl)
        

class DNSUpdater(Thread):
    def __init__(self,table,comm=None, wait=1):
        self.table = table
        self.comm = comm
        self.wait = wait * 60
        self.__t_last = time() + self.wait
        self.__stop = False
        self.log = open("../logs/dns.log","a")

        self.re_ip = re.compile('^([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])\\.([01]?\\d\\d?|2[0-4]\\d|25[0-5])$')

        Thread.__init__(self)

    def add_target(self,name,target,attr):
        ip = None

        if name != None:
            if self.re_ip.match(name) != None:
                return name

            if self.table.has_key(name):
                self.table[name][1].append(target,attr)
            else:
                data = (self.__resolve(name),[target,attr])
                self.table[name] = data

            ip = self.table[name][0]
        return ip

    def get_ip(self,name):
        return self.table[name][0]

    def __resolve(self,name):
        ip = socket.gethostbyname(name)
        self.log_dns(name,ip)
        return ip

    def set_comm(self,comm):
        self.comm = comm
    def run(self):
        if self.comm is None:
            raise AttributeError, "comm must not be None"
        while not self.__stop:
            if self.__t_last - time() < 0:
                for name in self.table.keys():
                    ip,targets = self.table[name]
                    ip = self.__resolve(name)
                    if self.table[name][0] != ip:
                        self.table[name][0] = ip
                        self.log_dns(name,ip)
                        for target in targets:
                            config = {'name':target[0],attr:ip}
                            try:
                                comm.send([dt.CMD_UPDATE,config])
                                syslog(Log.INFO, comm.recv())            
                            except IOError:
                                pass
                self.__t_last = time() + self.wait
            sleep(2)

    def stop(self):
        self.__stop = True
        self.log.close()
    
    def log_dns(self,name,ip):
        try:
            syslog(Log.DBG,"Resolved {0}:{1}".format(name,ip))
            sys.stdout.flush()    
            self.log.write("{0}|{1}|{2}\n".format(strftime("%Y/%m/%d-%X",localtime()),
                name,ip))
            self.log.flush()
        except:
            syslog(Log.WARN, "DNSUpdater::Failed to log DNS")
        
            

