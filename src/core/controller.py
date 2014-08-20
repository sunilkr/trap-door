## STDLIB imports
import multiprocessing as mp
from threading import Thread
from time import sleep, time, strftime, localtime
import re
import sys
import socket
import signal

## Package Imports
from .netlistener import NetListener
from util.logging import Log, syslog
import util.datatypes as dt
from .filtermanager import FilterManager
from .logmanager import LogManager

class Controller(object):
    
    instance = None

    def __init__(self):
        self.ifaces = {}
        self.loggermgr = {}
        self.loggermgr['queue'] = mp.Queue()    
        self.loggermgr['obj']   = LogManager()
        self._init_loggers()

        self.filtermgr = {}
        self.filtermgr['queue'] = mp.Queue()
        self.filtermgr['obj']   = FilterManager()
        self._init_filters()

        self.dnsmanager = DNSUpdater()
        self.__running = False

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
    
    # Return 0:STATUS_OK on success
    def add_iface(self,iface):
        if self.ifaces.has_key(iface):
            syslog(Log.WARN, "Already listening on {0}".format(iface))
            return dt.ERR_CONFLICT
        
        listener = NetListener(iface)
        local,remote = mp.Pipe()
        proc = mp.Process(target=listener.start, args=(self.filtermgr['queue'],remote))
        if self.__running:
            proc.start()
            syslog(Log.INFO, "Listener for {2}:{0} started. PID: {1}".format(
                listener.getip(), proc.pid, iface))
        
        self.ifaces[iface] = {}
        self.ifaces[iface]['comm'] = local
        self.ifaces[iface]['proc'] = proc
        syslog(Log.INFO, "Listener added for {0}".format(iface))
        return dt.STATUS_OK

    # Returns 0:STATUS_OK on success
    def remove_iface(self, iface):
        if not self.ifaces.has_key(iface):
            return dt.ERR_NO_SUCH_ITEM
        
        proc = self.ifaces[iface]['proc']   # Need improvements...
        if not proc.is_alive():
            syslog(Log.WARN, "Listener for {0} is not running".format(iface))
            del self.ifaces[iface]
            return dt.STATUS_OK

        comm = self.ifaces[iface]['comm']
        comm.send([dt.CMD_STOP,0])
        result = comm.recv()
        comm.close()
        proc.join()
        
        del self.ifaces[iface]
        return dt.STATUS_OK

    # Start all processes....    
    def start(self):
        syslog(Log.INFO, "Starting Filter Manager...")
        self.filtermgr['proc'].start()
        syslog(Log.INFO, "FilterManager PID: {0} ".format(self.filtermgr['proc'].pid))

        syslog(Log.INFO, "Staring Logger Manager...")
        self.loggermgr['proc'].start()
        syslog(Log.INFO, "LogManager PID: {0}".format(self.loggermgr['proc'].pid))

        syslog(Log.INFO, "Starting Listeners...")
        for iface in self.ifaces.keys():
            proc = self.ifaces[iface]['proc']
            if not proc.is_alive():
                proc.start()
                syslog(Log.INFO, "Started Listener for {1}, PID: {0}".format(proc.pid, iface))

        syslog(Log.INFO, "Starting DNS Manager...")
        self.dnsmanager.set_comm(self.filtermgr['comm'])
        self.dnsmanager.deamon = True
        self.dnsmanager.start()
        self.__running = True

    def stat(self, delay=2):
        try:
            while True:
                syslog(Log.DBG, "Filter Queue Size {0}".format(self.filtermgr['queue'].qsize()))
                syslog(Log.DBG, "Logger Queue Size {0}".format(self.loggermgr['queue'].qsize()))
                sleep(delay)
        except KeyboardInterrupt, e:
            self.finish()
    
    def status(self,dns=True):
        status={'filterq':{'size':self.filtermgr['queue'].qsize()},
                'loggerq':{'size':self.loggermgr['queue'].qsize()},
                'dnstable': self.dnsmanager.entries()}
        return status 

    def finish(self):
        syslog(Log.INFO,"Stopping DNS Manager...")
        self.dnsmanager.stop()

        # Stopping Listeners...
        syslog(Log.INFO,"Stopping Listeners...")
        for iface in self.ifaces.keys():
            proc = self.ifaces[iface]['proc']
            if not proc.is_alive():
                continue
            comm = self.ifaces[iface]['comm']
            comm.send([dt.CMD_STOP,None])
            result = comm.recv()
            comm.close()
            proc.join()
        
        # Stopping FilterManager...
        syslog(Log.INFO, "Stopping FilterManager...")
        if self.filtermgr['proc'].is_alive():
            self.filtermgr['comm'].send([dt.CMD_STOP,None])
            self.filtermgr['proc'].join()
        self.filtermgr['comm'].close()

        # Stopping LogManager...
        syslog(Log.INFO, "Stopping LogManager...")
        if self.loggermgr['proc'].is_alive():
            self.loggermgr['comm'].send([dt.CMD_STOP,None])
            self.loggermgr['proc'].join()
        self.loggermgr['comm'].close()
        self.__running = False

        syslog(Log.INFO, "DONE")
        
    # Add single Filter in middle/end of chain
    def add_filter(self,config):
        if config.has_key('src'):
            config['src'] = self.dnsmanager.add_target(config['src'],config['name'],'src')
        if config.has_key('dst'):
            config['dst'] = self.dnsmanager.add_target(config['dst'],config['name'],'dst')
        
        self.filtermgr['comm'].send([dt.CMD_ADD, config])
        result = self.filtermgr['comm'].recv()
        syslog(Log.INFO, result)
        return result

    # Add Logger
    def add_logger(self, config):
        self.loggermgr['comm'].send([dt.CMD_ADD, config])
        result = self.loggermgr['comm'].recv()
        syslog(Log.INFO,result)
        return result
    
    # Add new filter chain
    def add_filter_chain(self,config):
        config = self._resolve_names(config)
        self.filtermgr['comm'].send([dt.CMD_FILTER_ADD_CHAIN, config])
        result = self.filtermgr['comm'].recv()
        syslog(Log.INFO, result)
        return result

    # Convert all src & dst fields to IP
    def _resolve_names(self,config):
        conf = {}
        for name, value in config.items():
            if isinstance(value, dict):
                conf[name]=self._resolve_names(value)
            elif name in ['src','dst']:
                conf[name] = self.dnsmanager.add_target(value, config['name'], name)
            else:
                conf[name]=value
        return conf

    # Get current configuration
    def get_config(self):
        config={'iface':self.ifaces.keys()}

        self.filtermgr['comm'].send([dt.CMD_GET_CONFIG, 0])
        result = self.filtermgr['comm'].recv()
        config['filters'] = self._resolve_ip(result[1])

        self.loggermgr['comm'].send([dt.CMD_GET_CONFIG, 0])
        result = self.loggermgr['comm'].recv()
        config['loggers'] = result[1]

        return config

    # Covert IP to domain name if possible.
    def _resolve_ip(self,value):
        data = None
        if isinstance(value, dict):
            data = {}
            for k , v in value.items():
                data[k] = self._resolve_ip(v)
        elif isinstance(value, list):
            data = []
            for v in value:
                data.append(self._resolve_ip(v))
        else:
            data = self.dnsmanager.get_domain(value)

        return data

    # Reset all systems. For RELOAD
    # Return: 0:STATUS_OK
    def reset(self):
        # Stop listeners
        for iface in self.ifaces.keys():
            self.remove_iface(iface)

        # Clear filters
        self.filtermgr['comm'].send([dt.CMD_CLEAR, None])
        result = self.filtermgr['comm'].recv()
        syslog(Log.INFO, "Clearing filters... {0}".format(result[1]))

        # Clear loggers
        self.loggermgr['comm'].send([dt.CMD_CLEAR, None])
        result = self.loggermgr['comm'].recv()
        syslog(Log.INFO, "Clearing loggers... {0}".format(result[1]))
        
        # Restart dnsmanager
        # self.dnsmanager.stop()
        self.dnsmanager.clear()
        #self.dnsmanager.start()
        syslog(Log.INFO, "Cleared DNS Entries.")
        
        return dt.STATUS_OK

# TODO: Move it to a new file
#  Manage Name resolutions
class DNSUpdater(Thread):
    def __init__(self,table = {}, comm=None, wait=1):
        self.table = table
        self.comm = comm
        self.wait = wait * 60
        self.__t_last = time() + self.wait
        self.__stop = False
        self.log = open("../logs/dns.log","a")

        Thread.__init__(self)

    def add_target(self,name,target,attr):
        ip = None

        if name != None:
            #if self.re_ip.match(name) != None:
            #    return name

            if self.table.has_key(name):
                self.table[name][1].append([target,attr])
            else:
                data = [self.__resolve(name),[[target,attr]]]
                self.table[name] = data

            ip = self.table[name][0]
        return ip

    def get_ip(self,name):
        return self.table[name][0]
    
    def get_domain(self, target):
        domain = target
        for name, ip in self.table.items():
            if ip[0] == target:
                domain = name
                break

        return domain

    def __resolve(self,name):
        try:
            ip = socket.gethostbyname(name)
        except socket.gaierror:
            self.log_dns(name,'DNS_ERR_NOT_RESOLVED')
            return None
        else:
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
                            config = {'name':target[0], target[1]:ip}
                            try:
                                self.comm.send([dt.CMD_UPDATE,config])
                                syslog(Log.INFO, self.comm.recv())            
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
            
    def entries(self):
        entries = {}
        for name,data in self.table.items():
            entries[name] = data[0]
        return entries

    def clear(self):
        self.table = {}
        return True
