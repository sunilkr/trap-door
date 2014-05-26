class Log:
    DBG=0
    INFO=1
    ERR=-1
    WARN=-2

def syslog(lvl,msg):
    if lvl == Log.DBG:
        print("[?] {0}".format(msg))
    elif lvl == Log.INFO:
        print("[*] {0}".format(msg))
    elif lvl == Log.ERR:
        print("[X] {0}".format(msg))
    elif lvl == Log.WARN:
        print("[!] {0}".format(msg))
    else:
        print("[%] {0}".format(msg))
