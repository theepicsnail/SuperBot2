import threading
from types import GeneratorType
from Util import call
from time import sleep,time
from Logging import LogFile
pdLog = LogFile("PluginDispatcher")
pdwtLog = LogFile("PluginDispatcherWorkerThread")
pddtLog = LogFile("PluginDispatcherDedicatedThread")

class PluginDispatcherDedicatedThread(threading.Thread):
    callback = None
    recover  = True
    active = True
    connectorInfo = (None, None)
    def __init__(self,callback, responseObject= None, consumer= lambda x:None ):
        super(PluginDispatcherDedicatedThread,self).__init__()
        self.connectorInfo=responseObject,consumer 
        self.callback = callback
        pddtLog.note("New PDDT",callback,responseObject,consumer)

    def run(self):
        args = {}
        crashProtection=[0]*30
        while self.active:
            try:
                crashProtection=crashProtection[1:]+[time()]
                if crashProtection[-1]-crashProtection[0]<5:
                    pdLog.error("A static thread has returned 30 times in 5 seconds. Killing process.")
                    return 
                
                args.update({"response":self.connectorInfo[0]})
                pddtLog.dict(args,"Calling callback.",self.callback)
                response = call(self.callback,args)
                if response and self.connectorInfo[1]:
                    if isinstance(response, GeneratorType):
                        pddtLog.debug("Generator", response)
                        for r in response:
                            if not self.active:
                                pddtLog.debug("No longer active. Shutting down.")
                                self.Stop()
                                return 
                            pddtLog.debug("Yielded", r)
                            self.connectorInfo[1](r)
                        pddtLog.debug("End of generator", response)
                    else:
                        pddtLog.debug("Returning", response)
                        self.connectorInfo[1](response)
                elif response:
                    pddtLog.warning("No consumer to consume response",response)
                else:
                    pddtLog.debug("Didn't return")
            except:
                if not self.active:
                    pdLog.exception("No longer active. Shutting down.")
                    self.Stop()
                    return

                if self.recover:
                    pdLog.exception("Recovering",crashProtection[-1]-crashProtection[0])
                else:
                    pdLog.exception("Not recovering. Shuttind down.")
                    self.Stop()
                    return
    def Stop(self):
        pddtLog.note("Stopping.")
        self.active = False            
        
class PluginDispatcherWorkerThread(threading.Thread):
    running = True
    produce = None
    consume = None
    active  = False
    def run(self):
        pdwtLog.debug("Worker thread started.")
        while True:
            self.active = False
            while self.produce == None or self.consume == None:
                pdwtLog.debug("Waiting on producer and consumer",
                        "P:" + str(self.produce), "C:" + str(self.consume))
                sleep(1)
                if not self.running:
                    pdwtLog.debug("Shutting down")
                    return
                if self.produce and self.consume:
                    pdwtLog.debug("Producer and consumer set.",
                            "P:" + str(self.produce), "C:" + str(self.consume))
            func, args = self.produce()
            self.active = True

            pdwtLog.debug("Produced", func)
            pdwtLog.dict(args)

            if not self.running:
                pdwtLog.note("Shutting down")
                return
            try:
                pdwtLog.debug("Calling", func)
                pdwtLog.dict(args)
                response = call(func, args)

                if response and self.consume:
                    if isinstance(response, GeneratorType):
                        pdwtLog.debug("Generator", response)
                        for r in response:
                            pdwtLog.debug("Yielded", r)
                            self.consume(r)
                        pdwtLog.debug("End of generator", response)
                    else:
                        pdwtLog.debug("Returning", response)
                        self.consume(response)
                else:
                    pdwtLog.debug("Not returning.", response)
            except NameError,n:
                pdwtLog.exception("NameError while evaluating plugin!", n.message)
            except:
                pdwtLog.exception("Exception while evaluating plugin!")
    def Stop(self):
        pdwtLog.debug("Set stop flag")
        self.running = False


class PluginDispatcher:
    __queue__ = []
    __workerThreads__ = []
    __dedicatedThreads__ = {}
    __lock__ = threading.Condition()

    ResponseHandler = None

    def __init__(self):
        pdLog.debug("Creating worker threads.")
        for i in xrange(5):
            self.CreateWorkerThread()
    
    def CreateWorkerThread(self):
        worker = PluginDispatcherWorkerThread()
        worker.produce = self.Dequeue
        self.__workerThreads__ += [worker]
        worker.consume = self.ResponseHandler
        worker.start()

    def CreateDedicatedThread(self,callback, responseObject, consumer):
        t = PluginDispatcherDedicatedThread(callback,responseObject,consumer)
        self.__dedicatedThreads__[callback] = t
        t.start()
    def EnsureDedicated(self,funcList,responseObject,callback):
        #should this remove plugins that are not in funcList?
        pdLog.debug("Ensure dedicated",funcList,responseObject,callback)
        for func in funcList:
            if not self.__dedicatedThreads__.has_key(func):
                self.CreateDedicatedThread(func,responseObject, callback)
            elif not self.__dedicatedThreads__[func].active:
                del self.__dedicatedThreads__[func]
                pdLog.debug("Restarting dead dedicated thread.")
                self.CreateDedicatedThread(func,responseObject, callback)
                

    def Dequeue(self):
        pdLog.debug("Dequeuing")
        self.__lock__.acquire()
        while not self.__queue__:
            pdLog.debug("Queue empty, waiting.")
            self.__lock__.wait()
            pdLog.debug("Notified.")

        out = self.__queue__[0]
        self.__queue__ = self.__queue__[1:]
        self.__lock__.release()

        pdLog.debug("Dequeued")
        pdLog.debug(out[0])
        pdLog.dict(out[1])
        return out

    def SetResponseHandler(self, resp):
        pdLog.debug("Response handler set to", resp)
        self.ResponseHandler = resp
        pdLog.debug("Switching workerthreads to new response handler")
        for worker in self.__workerThreads__:
            worker.consume = resp
        pdLog.debug("Complete")
    def GetResponseHandler(self):
        return self.ResponseHandler
    def Enqueue(self, t):
        pdLog.debug("Enqueuing")
        pdLog.debug(t[0])
        pdLog.dict(t[1])
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
            self.Enqueue((None, None))
        for name,t in self.__dedicatedThreads__.items():
            t.Stop()
