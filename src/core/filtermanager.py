from util.logging import syslog, Log
from util.factory import apply_attrs,create_object, create_chain
import util.datatypes as dt
import Queue
import traceback
from multiprocessing import current_process
import signal

class FilterManager(object):

    def __init__(self):
       self.filters={}
       self.chains=[]
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

    def _process(self,packet):
        for chain in self.chains:
            if chain.execute(packet): # return true if any chain returns True.
                return True
        return False

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
                    #syslog(Log.WARN,"FilterManager({0}):: Filter queue is empty".format(self.pid))
                    pass
            except Exception, e:
                syslog(Log.ERR,traceback.format_exc())
                raise e
            else:
                if self._process(packet):      
                    self.__logger_q.put(packet) 
            finally:
                self.check_comm() 

    def _add(self,config):
        parent = config['parent'] if config.has_key('parent') else None
        if config.has_key('name') :
            name = config['name'] 
        else: 
            return [dt.ERR_NO_SUCH_ITEM,"'name' is required attrubute"]

        if self.filters.has_key(name):
            return [dt.ERR_CONFLICT, 'Filter "{0}" already added'.format(name)]
        if parent is None:
            return [dt.ERR_NO_SUCH_ITEM, "Parent is required to add filter:{0}".format(name)]
        elif not self.filters.has_key(parent):
            return [dt.ERR_NO_SUCH_ITEM, 
                    "Invalid parent:{0}. Try adding a new chain.".format(parent)]
        else:
            parent = self.filters[parent]
            
        try:
            _filter = create_object(config['class'])
            _filter = apply_attrs(_filter,config)
        except:
            return [dt.ERR_SEE_LOG,
                    'Error while creating filter {0}. See logs.'.format(config['class'])]
        else:
            tail = parent.nxt   #TODO: Append the tail to new filter if required
            parent.set_next(_filter)
            self.filters[_filter.name] = _filter
            if tail == None:
                return [dt.STATUS_OK, "Filter added with no tail."]
            else:
                return [dt.STATUS_OK, "Filter added, tail removed ({0}).".format(tail.name)]


    def _update(self,config):
        name = config['name']
        try:
            _filter = self.filters[config['name']]
        except KeyError:
            return [dt.ERR_NO_SUCH_ITEM,"No such filter {0}".format(name)]
        else:
            try:
                self.filters[name] = apply_attrs(_filter,config)
            except:
                syslog(Log.ERR, traceback.format_exc())
                return [dt.ERR_APPLY_ATTR, 
                        "Error while applying attributes to '{0}' type {1}".format(name, 
                            _filter.__class__.__name__)]
            else:
                return [dt.STATUS_OK,"Filter {0} updated".format(name)]

    def _delete(self,config):
        name = config['name']
        if self.filters.has_key(name):
            for chain in self.chains:       #TODO: Can do better than this
                done = False
                if chain.name == name:
                    self.chains.remove(chain)
                    self._remove_tail(chain)
                    return [dt.STATUS_OK, 'Remove filter chain with root:{0}'.format(name)]
                else:
                    node = chain
                    parent = node
                    while node is not None:
                        if node.name == name:
                            self._remove_tail(node)
                            parent.set_next(None)
                            done = True
                            break
                        else:
                            parent = node
                            node = node.nxt

                if done:
                    break

            return [dt.STATUS_OK,"Filter {0} deleted".format(name)]
        else:
            return [dt.ERR_NO_SUCH_ITEM,"No such filter: {0}".format(name)]
           
    def _remove_tail(self,node):
        if node.nxt is not None:
            self._remove_tail(node.nxt)
        del self.filters[node.name]
        

    def _new_chain(self,config):
        _filter = create_chain(config)
        self.chains.append(_filter)
        while _filter is not None:
            name = _filter.name
            if self.add_filter(name, _filter):      # FIXME: Can add non filter types
                _filter = _filter.nxt
            else:
                syslog(Log.ERR, "Filter {0} already exists. Rolling Back".format(name))
            
                _filter = self.chains.pop(-1)
                while _filter is not None:
                    if _filter in self.filters.values():
                        del self.filters[_filter.name]
                    _filter = _filter.nxt

                return [dt.ERR_CONFLICT, "Filter {0} already exists".format(name)]

        return [dt.STATUS_OK, "Filter chain added successfully"]

    def config(self):
        filters = []
        for chain in self.chains:
            filters.append(chain.attrs())
        return filters

    def _clear(self):
        self.chains = []
        self.filters = {}
        return [dt.STATUS_OK, 'All filters cleared']

    def check_comm(self):
        if self.__comm.poll():
            cmd,data = self.__comm.recv()

            if cmd == dt.CMD_STOP:
                self.__stop = True
                syslog(Log.INFO, "FilterManager({0})::STOP:: Clearing queue...".format(self.pid))

            elif cmd == dt.CMD_UPDATE:
                self.__comm.send(self._update(data))

            elif cmd == dt.CMD_ADD:
                self.__comm.send(self._add(data))

            elif cmd == dt.CMD_DELETE:
                self.__comm.send(self._delete(data))

            elif cmd == dt.CMD_FILTER_ADD_CHAIN:
                self.__comm.send(self._new_chain(data))
            
            elif cmd == dt.CMD_GET_CONFIG:
                self.__comm.send([dt.STATUS_OK, self.config()])

            elif cmd == dt.CMD_CLEAR:
                self.__comm.send(self._clear())

            else:
                self.__comm.send([dt.ERR_SEE_LOG, "Unknown command: {0}".format(cmd)])
