import threading
from types import GeneratorType
from Util import call
from time import sleep
from Logging import LogFile
pdLog = LogFile("PluginDispatcher")
pdwtLog = LogFile("PluginDispatcherWorkerThread")

class PluginDispatcherWorkerThread(threading.Thread):
    running = True
    produce = None
    consume = None 

    def run(self):
        pdwtLog.debug("Worker thread started.")
        while True:
            while self.produce==None or self.consume==None:
                pdwtLog.debug("Waiting on producer and consumer","P:"+str(self.produce), "C:"+str(self.consume))
                sleep(1)
                if not self.running:
                    pdwtLog.debug("Shutting down")
                    return
                if self.produce and self.consume:
                    pdwtLog.debug("Producer and consumer set.","P:"+str(self.produce),"C:"+str(self.consume))

            func,args = self.produce()
            pdwtLog.debug("Produced",func,args)

            if not self.running:
                pdwtLog.note("Shutting down")
                return
            try:
                pdwtLog.debug("Calling",func,args)
                response = call(func,args)
    
                if response and self.consume:
                    if isinstance(response,GeneratorType):
                        pdwtLog.debug("Generator",response)
                        for r in response:
                            pdwtLog.debug("Yielded",r)
                            self.consume(r)
                        pdwtLog.debug("End of generator",response)
                    else:
                        pdwtLog.debug("Returning",response)
                        self.consume(response)
                else:
                    pdwtLog.debug("Not returning.",response)
            except:
                pdwtLog.exception("Exception while evaluating plugin!")
    def Stop(self):
        pdwtLog.debug("Set stop flag")
        self.running = False
        
class PluginDispatcher:
    __queue__=[]
    __workerThreads__=[]
    __lock__ = threading.Condition()
    
    ResponseHandler=None
    def __init__(self):
        pdLog.debug("Creating worker threads.")
        for i in xrange(5):
            worker = PluginDispatcherWorkerThread()
            worker.produce = self.Dequeue
            self.__workerThreads__+=[worker]
            worker.start()

    def Dequeue(self):
        pdLog.debug("Dequeuing")
        self.__lock__.acquire()
        while not self.__queue__:
            pdLog.debug("Queue empty, waiting.")
            self.__lock__.wait()
            pdLog.debug("Notified.")

        out = self.__queue__[0]
        self.__queue__=self.__queue__[1:]
        self.__lock__.release()

        pdLog.debug("Dequeued",out)        
        return out
    
    def SetResponseHandler(self,resp):
        pdLog.debug("Response handler set to",resp)
        self.ResponseHandler = resp
        pdLog.debug("Switching workerthreads to new response handler")
        for worker in self.__workerThreads__:
            worker.consume=resp
        pdLog.debug("Complete")

    def Enqueue(self, t):
        pdLog.debug("Enqueuing",t)
        self.__lock__.acquire()
        self.__queue__.append(t)
        pdLog.debug("Notifying sleeping worker threads")
        self.__lock__.notify()
        self.__lock__.release()

    def Stop(self):
        pdLog.note("Stopping workers")
        del self.__queue__[:]
        for t in self.__workerThreads__:
            t.Stop()
        for t in self.__workerThreads__:
            self.Enqueue((None,None))

