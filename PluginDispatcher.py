import threading
from Util import call
from time import sleep

class PluginDispatcherWorkerThread(threading.Thread):
    running = True
    ID = -1
    produce = None
    consume = None 
    def __init__(self,ID):
        threading.Thread.__init__(self)
        self.ID = ID


    def run(self):
        while True:
            while self.produce==None or self.consume==None:
                sleep(1)

            func,args = self.produce()
            if not self.running:
                print "WorkerThread",self.ID,"Shuting down"
                return
            print "WorkerThread",self.ID,func,args
            print ""
            response = call(func,args)
            if response:
                self.consume(response)

    def Stop(self):
        self.running = False
        
class PluginDispatcher:
    __queue__=[]
    __workerThreads__=[]
    __lock__ = threading.Condition()
    
    ResponseHandler=None
    def __init__(self):
        for i in xrange(5):
            worker = PluginDispatcherWorkerThread(i)
            #worker.setDaemon(True)
            worker.produce = self.Dequeue
            self.__workerThreads__+=[worker]
            worker.start()

    def Dequeue(self):
        self.__lock__.acquire()
        while not self.__queue__:
            self.__lock__.wait()
        out = self.__queue__[0]
        self.__queue__=self.__queue__[1:]
        self.__lock__.release()
        return out
    
    def SetResponseHandler(self,resp):
        self.ResponseHandler = resp
        for worker in self.__workerThreads__:
            worker.consume=resp

    def Enqueue(self, t):
        self.__lock__.acquire()
        self.__queue__.append(t)
        self.__lock__.notify()
        self.__lock__.release()

    def Stop(self):
        del self.__queue__[:]
        for t in self.__workerThreads__:
            self.enqueueFunc(None,None)
            t.Stop()
