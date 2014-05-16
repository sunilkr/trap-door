'''
An attempt to share data between multiprocess using direct manager 
'''


from time import sleep
from multiprocessing import Process, Manager
#from multiprocessing.managers import Manager
import random

class RunnerData:
    def __init__(self):
        self.manager = Manager()
        self.data = self.manager.dict()
        self.flags = self.manager.dict()

    def add_runner(self,name):
        self.data[name]=[]

    def add_data(self,runner,data):
        self.data[runner].append(data)
    
    def 

class Runner:
    def __init__(self,lst=[],name=None):
        self.lst = lst
        self.stop = False
        self.name = name

#    def add(self,obj):
#        self.lst.append(obj)

    def set_name(self,name):
        self.name = name

    def start(self):
        while not self.stop:
            print "\n[*]Contents of runner %s:" %self.name
            for i in self.lst:
                print str(i)+", " 
#                pass
            sleep(0.1)
#End Runner

class Controller:

    def __init__(self):
        self.runners=[]
        self.runner_procs=[]
        self.runner_data = RunnerData()
        
    def add_runner(self,runner):
        self.runners.append(runner)
        self.runner_data.add_runner(runner.name, runner)

    def add_runner_obj(self,name,obj):
        self.data.add_date(name,obj)

    def stop(self):
        for runner in self.runners:
            runner.stop()

    def start(self,count):
        for i in range(count):        
            runner = Runner()
            runner.set_name("Runner"+str(idx))
            self.add_runner(runner)
            proc = Process(target=start_runner, args=(runner,))
            self.runner_procs.append(proc)
            proc.start()
            print "\n[!] Created PID:%d" %proc.pid

    def join_all(self):
        for proc in self.runner_procs:
            proc.join()

    def add_randoms(self):
        for runner in self.runners:
            self.runner.add(random.randint(1,10000))
#End Controller

def start_runner(ctrlr,idx):
    runner.start()

def main():
    ctrlr = Controller()
    ctrlr.start(5)
    
    for i in range(10):
        print "[!] Iteration %d\n" %i
        ctrlr.add_randoms()
        sleep(1)

    ctrlr.stop()
    ctrlr.join_all()

if __name__ == "__main__":
    main()

