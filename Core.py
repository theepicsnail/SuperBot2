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
    def _LoadConnector(self,ConName):
        try:
            con = __import__("%s.Connector"%ConName, globals(), locals(), "Connector")
            log.debug("Got connector:",con)
            cls = getattr(con,"Connector",None)
        except:
            log.exception("Exception while loading connector")
            cls = None
        log.debug("Connectors class",cls)
        if cls:
            c = cls()
            log.debug("Connector constructed")
            return c

        log.critical("No connector")
        return cls


    def HandleEvent(self,event):
        log.debug("HandleEvent")
        log.dict(event)

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
            log.debug("Getting services for:",inst)
            servs = pm.GetServices(inst)
            log.debug("Services found for plugin:",servs)
            if servs:
                log.debug("Event before processing:",newEvent)

            for serv in servs:
                log.debug("Processing service",serv)
                serv.onEvent(newEvent)
            if servs:
                log.debug("Event after processing:",newEvent)
            #issue 5 fix goes here
            pd.Enqueue((func,newEvent))
    
    def __init__(self):
        self._Config = ConfigFile("Core")
        if not self._Config: 
            log.critical("No log file loaded!")
            return
        ConName = self._Config["Core","Provider"]
        if ConName == None:
            log.critical("No Core:Provider in Core.cfg")
            del self._Connector
            return 
            
        self._Connector=self._LoadConnector(ConName) 
	if self._Connector:
	        self._PluginManager = PluginManager(ConName)
	        self._PluginDispatcher = PluginDispatcher()
	        self._Connector.SetEventHandler(self.HandleEvent)
	        self._ResponseObject = self._Connector.GetResponseObject()
	        self._PluginDispatcher.SetResponseHandler(self._Connector.HandleResponse)    
                
    def Start(self):
        if not self._Connector:
            log.warning("Could not start, no connector.")
            return

        log.debug("Starting")
        log.debug("Auto loading plugins")
        self._PluginManager.AutoLoad()
        log.debug("Auto load complete")

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
    try:
        c = Core()
        try:
            c.Start()
        except:
            log.exception("Exception while starting.")
        c.Stop()
    except:
        log.exception("Exception while stopping.")
    log.debug("End of core")
