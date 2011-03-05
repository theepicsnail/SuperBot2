from Interfaces import Connector
from ResponseManager import ResponseManager
from PluginManager import PluginManager
from PluginQueue import *
from re import match
from sys import path
from os import getcwd
from Util import dictJoin
path.append(getcwd())
print path
"""
#test descriptor
def requireConnection(func):
    def nfunc(self,*a,**b):
        if self.conn:
            return func(self,*a,**b)
        else:
            raise Exception("IRC Connection has not been defined yet!")
    return nfunc
"""


class Bot:
    def __init__(self):
        self.conn = None
        self.setPluginManager(PluginManager())
        self.setResponseManager(ResponseManager())

    def setPluginManager(self,pm):
        self.pluginManager = pm

    def setResponseManager(self,rm):
        self.responseManager=rm
        self.pluginQueue = PluginQueue(rm.addResponse)
    def setConnector(self, c):
        if Connector.providedBy(c):
            self.conn = c
            self.outbound = c.getEvents()
            c.setEventCallback(self.handleEvent)
            self.responseManager.setOutputHandler(c.pushEvent)
            return True
        return False


    def matchHook(self,eventD, hookD):
        args = {}
        for key,pattern in hookD.items():
            value = eventD.get(key)
            if value == None:
                return None
            
            m = match(pattern,value)
            if m == None:
                return None
            
            for k,v in m.groupdict().items():
                args[k]=v
            
            for i,v in enumerate(m.groups()):
                args[key+str(i)]=v
            
        return args
            

    def handleEvent(self, eventD):
        for inst,func in self.pluginManager.getHooks():
            for hook in func.sbhook:
                hookargs = self.matchHook(eventD,hook)
                if hookargs!=None:
                    args = dictJoin(eventD, hookargs)
                    args["response"]=self.outbound
                    args["self"]=inst
                    self.pluginQueue.enqueueFunc(func,args)
                    

    def start(self):
        self.conn.connect()

    def stop(self):
        print "Stopping"
        self.pluginQueue.stop()
b = Bot()

#hardcoded this should come from the config
from Connectors.IRCConnector import IRCConnector
ic = IRCConnector()
ic.configure(host="ssh.udderweb.com", port = 6667, nick="testbot")
b.setConnector(ic)
b.pluginManager.addSearchPath("Plugins")
b.pluginManager.loadPlugin("Test")
b.start()

b.stop()
