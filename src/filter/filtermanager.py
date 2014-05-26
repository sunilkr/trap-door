from util.logging import syslog, Log
from util.factory import apply_attrs,create_object
import util.datatypes as dt
import Queue
import traceback
from multiprocessing import current_process
import signal

class FilterManager:

    def __init__(self):
       self.filters={}
       self.__filter_q = None
       self.__logger_q = None
       self.__comm = None
       self.stop_req = False 
       self.__stop = False

    def process(self,packet):
        result = False
        for name,_filter in self.filters.items():
            if _filter.execute(packet):
                result = True
                break

        return result


    def add_filter(self,name,_filter):
        if self.filters.get(name) is None:
            self.filters[name] = _filter
            return True
        else:
            return False

    def start(self,q_filter,q_logger, comm):
        self.__filter_q = q_filter
        self.__logger_q = q_logger
        self.__comm = comm
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        self.pid = current_process().pid
        while True:
            try:
                packet = self.__filter_q.get(timeout=1)
            except Queue.Empty, e:
                if self.__stop:
                    syslog(Log.INFO, "FilterManager({0})::STOP:: Stopped".format(self.pid))
                    self.__comm.send([dt.STATUS_OK,"stopped"])
                    self.__comm.close()
                    break
                else:
                    syslog(Log.WARN,"FilterManager({0}):: Filter queue is empty".format(self.pid))
            except Exception, e:
                syslog(Log.ERR,traceback.format_exc())
                raise e
            else:
                if self.process(packet):      
                    self.__logger_q.put(packet) 
            finally:
                self.check_comm()
    
    def __add(self,config):
        name = config['name']
        try:
            _filter = self.filters[name]
        except KeyError:
            _filter = create_object(config['class'])
            _filter = apply_attrs(_filter,config)
            self.filters[name]=_filter
            return [dt.STATUS_OK,"Filter {0} added".format(name)]
        else:
            return [dt.ERR_CONFLICT,"Filter {0} already exists".format(name)]


    def __update(self,config):
        name = config['name']
        try:
            _filter = self.filters[config['name']]
        except KeyError:
            return [dt.ERR_NO_SUCH_ITEM,"No such filter {0}".format(name)]
        else:
            self.filters[name] = apply_attrs(_filter,config)
            return [dt.STATUS_OK,"Filter {0} updated".format(name)]

    def __delete(self,config):
        if self.__filters.has_key(config['name']):
            del self.filters[config['name']]
            return [dt.STATUS_OK,"Filter {0} deleted".format(name)]
        else:
            return [dt.ERR_NO_SUCH_ITEM,"No such filter: {0}".format(name)]
           

    def check_comm(self):
        if self.__comm.poll():
            cmd,data = self.__comm.recv()

            if cmd == dt.CMD_STOP:
                self.__stop = True
                syslog(Log.INFO, "FilterManager({0})::STOP:: Clearing queue...".format(self.pid))

            elif cmd == dt.CMD_UPDATE:
                self.__comm.send(self.__update(data))

            elif cmd == dt.CMD_ADD:
                self.__comm.send(self.__add(data))

            elif cmd == dt.CMD_DELETE:
                self.__comm.send(self.__delete(data))
