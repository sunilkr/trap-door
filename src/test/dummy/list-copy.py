'''
    Sharing objects by copying into lists : FAIL
    
'''

import multiprocessing as mp
from time import sleep
import random

class Data:
    def __init__(self,a,b):
        self.value = a+b

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()

class Runner:
    def __init__(self,src,fd):
        self.lst = []
        self.fd = fd
        self.src = src
        self.name = "N/A"

    def set_name(self,name):
        self.name = name

    def run(self):
        self.name = mp.current_process().pid
        while not self.stop():
            self.update()
            msg = "[+] In Process:%s =>" %self.name
            for obj in self.lst:
                msg += str(obj) + ", "
#            print msg
#            sleep(0.1)

    def update(self):
#        print "[?] Checking update for %d: size %d" %(self.name,len(self.src))
        if len(self.src) > 0:
            self.lst.extend(self.src)
            del self.src[:]

    def stop(self):
        return self.fd[self.name]
#END Runner

class Controller:

    def __init__(self):
        self.lists = []
        self.rprocs = []
        self.manager = mp.Manager()

    def add_runner(self):
        self.data = self.manager.dict()
        self.stop = self.manager.dict()
        src = self.manager.list()
        src.append(Data(random.randint(0,1000),1))
        runner = Runner(src,self.stop)
        proc = mp.Process(target=runner.run)
        proc.start()
        print "[*] Process Started:%d" %proc.pid
        self.data[proc.pid] = src
        self.stop[proc.pid] = False
        self.rprocs.append(proc)
        
    def add_randoms(self):
        for key in self.data.keys():
            del self.data[key][:]
            for i in range(random.randint(0,10)):
                self.data[key].append(Data(random.randint(0,1000),5))
            print "[?] List updated for %d: Size %d" %(key, len(self.data[key]))


    def finish(self):
        for key in self.stop.keys():
            self.stop[key] = True

        print "[*] Flags set. Waiting for termination"

        for proc in self.rprocs:
            proc.join()

#END Controller

def main():
    ctrl = Controller()
    for i in range(5):
        ctrl.add_runner()

    for i in range(10):
        ctrl.add_randoms()
#        sleep(1)

    sleep(1)
    ctrl.finish()
    
if __name__ == "__main__":
    main()
