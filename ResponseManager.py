from Logging import getLogger
from threading import Thread
from time import sleep, time

log = getLogger("ResponseManager")
#This acts as a buffering mechanism for queing up and pushing out
#events. 
class ResponseManager(Thread):
    __queue__ = []
    __maxLen__ = None
    __running__ = False
    __delay__ = None
    handleOutput = None
    def setOutputHandler(self,h):
        self.handleOutput=h
    def __init__(self):
        pass    

    def addResponse(self,resp):
        if self. __maxLen__!=None:
            if len(self.__queue__)>=self.__maxlen__:
                log.warning("Ignoring response because queue length hit max.")
                log.warning("Skipped response [[[")
                log.warning("%s",resp)
                log.warning("]]]")
                return 
        log.debug("Adding response:")
        log.debug("%s",resp)
        self.__queue__.append(resp)
        if not self.__running__:
            Thread.__init__(self)
            self.start()
    
    def setAutoDelay(self,seconds):
        self.__delay__=seconds
        

    def setMaxRate(self,count,timeperiod): #not implemented yet
        pass

    def setQueueLength(self,length):
        self.__maxLen__ = length
        

    def clearMessages(self):
        self.__queue__=[]
        

    def run(self):
        self.__running__=True
        while self.__queue__:
            print "Dequeue"
            event,self.__queue__=self.__queue__[0],self.__queue__[1:]
            self.handleOutput(event)
            if self.__delay__:
                sleep(self.__delay__)
            #implement the count/timeperiod here
        self.__running__=False 
        


if __name__=="__main__":
    
    def foo(arg):
        print "Foo",arg

    rm = ResponseManager()
    rm.handleOutput=foo
    rm.setAutoDelay(2)
    print "Adding a,b,c"
    rm.addResponse("a")
    rm.addResponse("b")
    rm.addResponse("c")
    sleep(4)
    print "Adding d"
    rm.addResponse("d")
    sleep(3)
    print "Adding e"
    rm.addResponse("e")
    sleep(2)
    print "Adding f"
    rm.addResponse("f")
    sleep(1)
    print "Adding g"
    rm.addResponse("g")
