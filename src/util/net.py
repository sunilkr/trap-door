from socket import gethostbyname
from util.logging import Log, syslog
import traceback

def name_to_ip(name):
    try:
        ip = gethostbyname(name)
    except:
        syslog(Log.ERR, traceback.format_exc())
        ip = None
    finally:
        syslog(Log.DBG, "%s:%s"%(name,ip))
        return ip

