'''
An attempt to share data between multiprocess using direct object access
'''


from time import sleep
from multiprocessing import Process
import random


class Runner:
    def __init__(self):
        self.list = []
        self.stop = False
        self.name=""

    def add(self,obj):
        self.list.append(obj)

    def set_name(self,name):
        self.name = name

    def start(self):
        while not self.stop:
#            print "\n[*]Contents of runner %s:" %self.name
            for i in self.list:
#                print str(i)+", " 
                pass
            sleep(0.1)
#End Runner

class Controller:

    def __init__(self):
        self.runners=[]
        self.runner_procs=[]
        
    def add_runner(self,runner):
        self.runners.append(runner)

    def add_runner_obj(self,index,obj):
        self.runners[i].add(obj)

    def stop(self):
        for runner in self.runners:
            runner.stop()

    def start(self,count):
        for i in range(count):
            proc = Process(target=start_runner, args=(self,i))
            self.runner_procs.append(proc)
            proc.start()
            print "\n[!] Created PID:%d" %proc.pid

    def join_all(self):
        for proc in self.runner_procs:
            proc.join()

    def add_randoms(self):
        for runner in self.runners:
            runner.add(random.randint(1,10000))
#End Controller

def start_runner(ctrlr,idx):
    runner = Runner()
    runner.set_name("Runner"+str(idx))
    ctrlr.add_runner(runner)
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

