from util.logging import Log, syslog
import util.datatypes as dt
from util.factory import create_object, apply_attrs, create_chain
import Queue
import traceback
from multiprocessing import current_process
import signal

class LogManager(object):

    def __init__(self):
        self.__logger_q = None
        self.loggers = {}
        self.__stop = False

    def add_logger(self,name,logger):
        if self.loggers.get(name) is None:
            self.loggers[name] = logger

    def update_logger(self,name,logger):
        self.loggers[name] = logger

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
                    for logger in self.loggers.values():
                        logger.close()
                    self.comm.send([dt.STATUS_OK,'stopped'])
                    syslog(Log.INFO, "LogManager({0}):: Stopped".format(self.pid))
                    break
                else:
                    #syslog(Log.WARN, "LogManager({0}):: Logger queue is empty".format(self.pid))
                    pass
            except Exception, e:
                syslog(Log.ERR, traceback.format_exc())
                raise e
            else:
                for logger in self.loggers.values(): 
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
                self.comm.send(self._add(data))

            elif cmd == dt.CMD_UPDATE:
                self.comm.send(self._update(data))

            elif cmd == dt.CMD_DELETE:
                self.comm.send(self._delete(data))

            elif cmd == dt.CMD_GET_CONFIG:
                self.comm.send([dt.STATUS_OK, self.config()])

            else:
                self.cmd.send([dt.ERR_SEE_LOG, 'Unknown command: {0}'.format(cmd)])


    def _add(self, config):
        if config.has_key('name'):
            name = config['name']
        else:
            return [dt.ERR_NO_SUCH_ITEM, "'name' is required"]

        if self.loggers.has_key(name):
            return [dt.ERR_CONFLICT,"Logger {0} already exists".format(name)]
        else:
            logr = create_object(config['class'])
            logr = apply_attrs(logr,config)
            if config.has_key('filter'):
                _filter = create_chain(config['filter'])
                logr.set_filter(_filter)
            self.loggers[name] = logr
            return [dt.STATUS_OK, "Logger {0} added".format(name)]

    def _update(self, config):
        name = config['name']
        try:
            logger = self.loggers[name]
        except KeyError:
            return [dt.ERR_NO_SUCH_ITEM,'No such logger: {0}'.format(name)]
        else:
            self.loggers[name] = apply_attrs(logger,config)
            return [dt.STATUS_OK,"Logger {0} updated".format(name)]

    def _delete(self, config):
        name = config['name']
        if self.loggers.has_key(name):
            del self.loggers[name]
            return [dt.STATUS_OK, "Logger {0} deleted".format(name)]
        else:
            return [t.NO_SUCH_ITEM, "No such logger: {0}".format(name)]

    def _set_filter(self,config):
        if config.has_key('name'):
            name = config['name']
        else:
            return [dt.ERR_NO_SUCH_ITEM, "'name' is required"]

        if self.loggers.has_key(name):
            logger = self.loggers[name]
        else:
            return [dt.ERR_NO_SUCH_ITEM, "No such logger:{0} ".format(name)]

        if config.has_key('filter'):
            _filter = create_chain(config['filter'])
        else:
            return [dt.ERR_NO_SUCH_ITEM, "'filter' is required"]
        
        logger.set_filter(_filter)
        syslog(Log.INFO, "Filter:{0} added to logger:{1}".format(_filter.name, name))
        return [dt.STATUS_OK, "Filter:{0} added to logger:{1}".format(_filter.name,name)]

    def config(self):
        config=[]
        for logger in self.loggers.values():
            config.append(logger.attrs())
        return config


