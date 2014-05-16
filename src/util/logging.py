class Log:
    DBG=0
    INFO=1
    ERR=-1
    WARN=-2

def syslog(lvl,msg):
    if lvl == Log.DBG:
        print("[?] %s" %msg)
    elif lvl == Log.INFO:
        print("[*] %s" %msg)
    elif lvl == Log.ERR:
        print("[X] %s" %msg)
    elif lvl == Log.WARN:
        print("[!] %s" %msg)
    else:
        print("[%] %s" %msg) 
