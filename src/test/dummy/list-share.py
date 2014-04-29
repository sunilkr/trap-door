'''
    Sharing list among processes: PASS
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
    def __init__(self,lst):
        self.lst = lst
        self.name = "Runner"

    def set_name(self,name):
        self.name = name

    def run(self):
        self.name = mp.current_process().pid
        while len(self.lst) > 0:
            msg = "[+] In Process:%s =>" %self.name
            for obj in self.lst:
                msg += str(obj) + ", "
            print msg
#            sleep(0.1)

#END Runner

class Controller:

    def __init__(self):
        self.lists = []
        self.rprocs = []
        self.manager = mp.Manager()

    def add_runner(self):
        lst = self.manager.list()
        lst.append(Data(random.randint(1,1000),1))
        self.lists.append(lst)
        runner = Runner(lst)
        proc = mp.Process(target=runner.run)
        proc.start()
        print "[*] Process Started:%d" %proc.pid
        self.rprocs.append(proc)
        
    def add_randoms(self):
        for lst in self.lists:
            lst.append(Data(random.randint(1,1000),1))

    def clear(self):
        for lst in self.lists:
            del lst[:]

    def finish(self):
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
    ctrl.clear()
    ctrl.finish()
    
if __name__ == "__main__":
    main()
