from util.logging import Log, syslog
import util.datatypes as dt
import traceback
import pcapy
from multiprocessing import current_process
import socket 
import signal

class NetListener:
    
    """
        Listens on a network interface and queues the packets
        to FilterQueue
    """
    def __init__(self, iface, ip=None, _filter=None):
        self.__iface = iface
        self.__filter = _filter
        self.pcap = pcapy.open_live(self.__iface, 65536, 1, 0)
        self.__stop = False
        self.ip = self.getip()
        self.netmask = self.getmask()

    def getip(self):
        return self.pcap.getnet()
    
    def getmask(self):
         self.pcap.getmask()

    def stop(self):
        self.__stop = True

    def getpcap(self):
        return self.pcap

    def start(self,queue,comm):
        self.queue = queue
        self.comm = comm
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        while not self.__stop:
            try:
                (phdr,pkt) = self.pcap.next()
            except socket.timeout:
                pass
            except:
                syslog(Log.WARN, traceback.format_exc())
            else:
                ts = phdr.getts()
                hdr = (ts[0],ts[1], phdr.getcaplen(), phdr.getlen())
                data = (hdr, pkt)
                self.queue.put(data)

            self.check_comm()

    def check_comm(self):
        if self.comm.poll():
            cmd,data = self.comm.recv()
            if cmd == dt.CMD_STOP:
                self.__stop = True
                self.comm.send("stopped")
                self.comm.close()
                syslog(Log.INFO, "NetListener(%d)::STOP:: Stopped" %current_process().pid)

