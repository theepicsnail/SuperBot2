import threading
from Util import call

class WorkerThread(threading.Thread):
    running = True
    ID = -1
    pushResponse = None
    def __init__(self,producer,handler,ID):
        threading.Thread.__init__(self)
        self.ID = ID
        self.pushResponse = handler
        self.getFunc = producer


    def run(self):
        while True:
            func,args = self.getFunc()
            if not self.running:
                print "WorkerThread",self.ID,"Shuting down"
                return
            print "WorkerThread",self.ID,func,args
            print ""
            response = call(func,args)
            if response:
                self.pushResponse(response)

    def stop(self):
        self.running = False
        
class PluginQueue:
    __queue__=[]
    __workerThreads__=[]
    __lock__ = threading.Condition()
    def __init__(self,handler):
        for i in xrange(5):
            worker = WorkerThread(self.dequeueFunc,handler,i)
            #worker.setDaemon(True)
            self.__workerThreads__+=[worker]
            worker.start()

    def dequeueFunc(self):
        self.__lock__.acquire()
        while not self.__queue__:
            self.__lock__.wait()
        out = self.__queue__[0]
        self.__queue__=self.__queue__[1:]
        self.__lock__.release()
        return out
    
    def setResponseManager(self,manager):
        self.responseManager = manager

    def enqueueFunc(self, func, args):
        self.__lock__.acquire()
        self.__queue__.append((func,args))
        self.__lock__.notify()
        self.__lock__.release()

    def stop(self):
        del self.__queue__[:]
        for t in self.__workerThreads__:
            self.enqueueFunc(None,None)
            t.stop()
