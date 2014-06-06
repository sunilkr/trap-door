from util.logging import Log, syslog
import util.datatypes as dt
from util.factory import create_object, apply_attrs
import Queue
import traceback
from multiprocessing import current_process
import signal

class LogManager(object):

    def __init__(self):
        self.__logger_q = None
        self.__loggers = {}
        self.__stop = False

    def add_logger(self,name,logger):
        if self.__loggers.get(name) is None:
            self.__loggers[name] = logger

    def update_logger(self,name,logger):
        self.__loggers[name] = logger

    def start(self,queue,comm):
        self.__logger_q = queue
        self.comm = comm
        self.pid = current_process().pid
        signal.signal(signal.SIGINT, signal.SIG_IGN)

        while True:
            try:
                packet = self.__logger_q.get(timeout=1)
            except Queue.Empty as e:
                if self.__stop:
                    syslog(Log.INFO, "LogManager({0}):: Stopping Loggers...".format(self.pid))
                    for logger in self.__loggers.values():
                        logger.close()
                    self.comm.send([dt.STATUS_OK,'stopped'])
                    syslog(Log.INFO, "LogManager({0}):: Stopped".format(self.pid))
                    break
                else:
                    syslog(Log.WARN, "LogManager({0}):: Logger queue is empty".format(self.pid))
            except Exception, e:
                syslog(Log.ERR, traceback.format_exc())
                raise e
            else:
                for logger in self.__loggers.values(): 
                    logger.log(packet)
            finally:
                self.check_comm()

    def check_comm(self):
        if self.comm.poll():
            cmd,data = self.comm.recv()

            if cmd == dt.CMD_STOP:
                syslog(Log.INFO, "LogManager({0})::STOP:: Clearing queue...".format(self.pid))
                self.__stop = True

            elif cmd == dt.CMD_ADD:
                self.comm.send(self.__add(data))

            elif cmd == dt.CMD_UPDATE:
                self.comm.send(self.__update(data))

            elif cmd == dt.CMD_DELETE:
                self.comm.send(self.__delete(data))

    def __add(self, config):
        name = config['name']
        if self.__loggers.has_key(name):
            return [dt.ERR_CONFLICT,"Logger {0} already exists".format(name)]
        else:
            logr = create_object(config['class'])
            logr = apply_attrs(logr,config)
            self.__loggers[name] = logr
            return [dt.STATUS_OK, "Logger {0} added".format(name)]

    def __update(self, config):
        name = config['name']
        try:
            logger = self.__loggers[name]
        except KeyError:
            return [dt.ERR_NO_SUCH_ITEM,'No such logger: {0}'.format(name)]
        else:
            self.__loggers[name] = apply_attrs(logger,config)
            return [dt.STATUS_OK,"Logger {0} updated".format(name)]

    def __delete(self, config):
        name = config['name']
        if self.__loggers.has_key(name):
            del self.__loggers[name]
            return [dt.STATUS_OK, "Logger {0} deleted".format(name)]
        else:
            return [t.NO_SUCH_ITEM, "No such logger: {0}".format(name)]


