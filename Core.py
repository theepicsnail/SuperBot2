from Interfaces import Connector
from ResponseManager import ResponseManager
from PluginManager import PluginManager
from PluginDispatcher import PluginDispatcher
from Configuration import ConfigFile
from re import match
from sys import path
from os import getcwd
from Util import dictJoin

path.append(getcwd())




class Core:
    _PluginManager = None
    _PluginDispatcher = None
    _ResponseObject = None
    _Connector = None
    _Config = None
    def _LoadConnector(self):
        if not self._Config: return None
        ConName = self._Config["Core","Connector"]
        con = __import__("Connectors.%s"%ConName, globals(), locals(), ConName)
        cls = getattr(con,ConName,None)
        if cls:
            return cls()
        return cls


    def HandleEvent(self,event):
        pm = self._PluginManager
        if not pm: return #log a message here?
        
        pd = self._PluginDispatcher
        if not pd: return #log a message here?

        ro = self._ResponseObject
        if not ro: pass #log  message here?
        
        matches = pm.GetMatchingFunctions(event)

        print "-"*80
        print matches

        for inst,func,args in matches:
            newEvent = dictJoin(args,{"self":inst,"response":ro}) 
            #service additions would be here
            pd.Enqueue((func,newEvent))
    
    def __init__(self):
        self._Config = ConfigFile("Core")
        if not self._Config: return # log a message here?
        self._PluginManager = PluginManager()
        self._PluginDispatcher = PluginDispatcher()
        self._Connector = self._LoadConnector()
        
        if self._Connector:
            self._Connector.SetEventHandler(self.HandleEvent)
            self._ResponseObject = self._Connector.GetResponseObject()
            self._PluginDispatcher.SetResponseHandler(self._Connector.HandleResponse)
            
    def Start(self):
        cf = ConfigFile("Autoload")
        if cf:
            names = cf["Plugins","Names"]
            if names:
                for name in names.split():
                    self._PluginManager.LoadPlugin(name)
            names = cf["Services","Names"]
            if names:
                for name in names.split():
                    self._PluginManager.LoadService(name)

        if self._Connector:
            self._Connector.Start()
        #else log error?

    def Stop(self):
        if self._PluginDispatcher: self._PluginDispatcher.Stop()
        if self._PluginManager: self._PluginManager.Stop()
        if self._Connector: self._Connector.Stop()

if __name__=="__main__":
    c = Core()
    c.Start()
    c.Stop()





class Bot:

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
                    

