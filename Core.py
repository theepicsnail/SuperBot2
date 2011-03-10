from Interfaces import Connector
from ResponseManager import ResponseManager
from PluginManager import PluginManager
from PluginDispatcher import PluginDispatcher
from Configuration import ConfigFile
from re import match
from sys import path
from os import getcwd
from Util import dictJoin
from Logging import LogFile

path.append(getcwd())

log = LogFile("Core")

class Core:
    _PluginManager = None
    _PluginDispatcher = None
    _ResponseObject = None
    _Connector = None
    _Config = None
    def _LoadConnector(self):
        log.debug("Loading connector")
        if not self._Config: 
            log.critical("No Config file")
            return None
        ConName = self._Config["Core","Connector"]
        con = __import__("Connectors.%s"%ConName, globals(), locals(), ConName)
        cls = getattr(con,ConName,None)
        if cls:
            log.debug("Connector constructed")
            return cls()

        log.critical("No connector")
        return cls


    def HandleEvent(self,event):
        log.debug("HandleEvent",event)

        pm = self._PluginManager
        if not pm: 
            log.warning("No plugin manager")
            return
        
        pd = self._PluginDispatcher
        if not pd:
            log.warning("No plugin dispatcher") 
            return

        ro = self._ResponseObject
        if not ro:
            log.warning("no response object")
            pass
        
        
        matches = pm.GetMatchingFunctions(event)
        log.debug("Matched %i hook(s)."%len(matches))
        
        for inst,func,args in matches:
            newEvent = dictJoin(event,dictJoin(args,{"self":inst,"response":ro}))
            #service additions would be here
            pd.Enqueue((func,newEvent))
    
    def __init__(self):
        self._Config = ConfigFile("Core")
        if not self._Config: 
            log.critical("No log file loaded!")
            return

        self._PluginManager = PluginManager()
        self._PluginDispatcher = PluginDispatcher()
        self._Connector = self._LoadConnector()
        
        if self._Connector:
            self._Connector.SetEventHandler(self.HandleEvent)
            self._ResponseObject = self._Connector.GetResponseObject()
            self._PluginDispatcher.SetResponseHandler(self._Connector.HandleResponse)
            
    def Start(self):
        log.debug("Starting")
        cf = ConfigFile("Autoload")
        if cf:
            log.debug("Autoloading plugins and services.")

            names = cf["Plugins","Names"]
            log.debug("Autoloading plugins",names)
            if names:
                for name in names.split():
                    self._PluginManager.LoadPlugin(name)

            names = cf["Services","Names"]
            log.debug("Autoloading services",names)
            if names:
                for name in names.split():
                    self._PluginManager.LoadService(name)

        else:
            log.note("No Autoload configuration")

        if self._Connector:
            log.debug("Connector starting")
            self._Connector.Start()
        #else log error?

    def Stop(self):
        log.debug("Stopping")
        if self._PluginDispatcher: self._PluginDispatcher.Stop()
        if self._PluginManager: self._PluginManager.Stop()
        if self._Connector: self._Connector.Stop()

if __name__=="__main__":
    c = Core()
    c.Start()
    c.Stop()
    log.debug("End of core")
