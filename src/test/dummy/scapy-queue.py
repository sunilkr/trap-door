from multiprocessing import Process, Queue, current_process
from Queue import Empty
import random
from time import sleep
from scapy.all import *
import traceback
import pcapy

def proc1(queue):
    print "started capture: %d" %current_process().pid
    cap = pcapy.open_live('eth0', 65536, 1,0)
    while True:
        try:
            (header,packet) = cap.next()
        except Exception, e:
#            print "[X] %s" % e.message
            pass
        else:
            queue.put(packet)
    '''
        queue.put(random.randint(1,1000))
        sleep(random.random() * 2)
    '''
def proc2(queue):
    print "started reader: %d" %current_process().pid
    while True:
       try:
           p = queue.get(False)
       except Empty, e:
           print "[!] Queue is empty"
           sleep(1)
       except Exception, e:
           traceback.print_exec()
       else:
           pkt = Ether(p)
           print "[*] Packet: %s" % pkt.summary()
#       finally:
#           sleep(random.random() * 2 )

def init():
    queue = Queue()
    p1 = Process(target = proc1, args=(queue,))
    p1.start()
    p2 = Process(target = proc2, args=(queue,))
    p2.start()
    
    while True:
        print "[*] Queue Size : % d" % queue.qsize()
        print "[*] captrue: %s" % ("alive" if p1.is_alive() else "dead")
        print "[*] reader : %s" % ("alive" if p2.is_alive() else "dead")
        sleep(5)
    p1.join()
    p2.join()

#RUN
init()

