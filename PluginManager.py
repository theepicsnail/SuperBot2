import sys
from inspect import isclass, getmembers
from re import match
from Logging import LogFile
from Configuration import ConfigFile

log = LogFile("PluginManager")

class PluginManager:
    __services__={}
    __plugins__={}
    __hooks__=[] # list of (function, pluginname, functionname)

    AutoLoadDeps = True
    
    def __init__(self,providerPath):
        self.root = providerPath    

    def hasPlugin(self,plug):
        log.debug("hasPlugin %s"%plug)
        return self.__plugins__.has_key(plug)
    
    def checkRequirements(self,cls):
        log.debug("Check requirements",cls)

        req = getattr(cls,"sbreq",None)
        if not req:#no requirements, no problem!
            log.debug("No requirements.")
            return True
       
        for r in req: 
            for s in r:
                log.debug("Loading Requirement",s)
                serv = None
                if self.__services__.has_key(s):
                    log.debug("already have service",s,self.__services__)
                    serv = self.__services__[s]
                else:
                    log.debug("Loading service",s)
                    serv =self.loadService(s)
                    if not serv:
                        #we tried and it failed to load!
                        log.error("Loading service failed. failing")
                        return False
                sbservs = getattr(cls,"sbservs",[])
                sbservs.append(serv)
                cls.sbservs=sbservs
                log.debug("Service autoloaded",s)

        log.debug("Requirements met.")
        return True

    #preferences will try to load, but if not it's okay
    def checkPreferences(self,cls):
        log.debug("Check preferences",cls)

        pref = getattr(cls,"sbpref",None)
        if not pref:
            log.debug("No preferences.")
            return

        for p in pref:
            for s in p:
                if not self.__services__.has_key(s):
                    log.debug("Missing preference",s)
                    if self.AutoLoadDeps:
                        serv = self.loadService(s)
                        if serv:
                            sbservs = getattr(cls,"sbservs",[])
                            sbservs.append(serv)
                            cls.sbservs=sbservs
                            log.debug("Service autoloaded",s)
                        else:
                            log.debug("Loading service failed. skipping")
                    else:
                        log.debug("Autoload not enabled, skipping")
        
    
    def LoadHooks(self,inst):
        hookFuncs = filter(lambda x:hasattr(x[1],"sbhook"),getmembers(inst))
        for k,v in hookFuncs:
            self.addHook(inst,v)
        
    def addHook(self, inst, func):
        log.debug("Adding hook",inst,func)
        hookArgs = func.sbhook
        self.__hooks__.append((inst,func))
        

    def loadService(self,pname):
        try:
            log.debug("Loading service %s.Services.%s"%(self.root,pname))
            serv = __import__("%s.Services.%s"%(self.root,pname),globals(),locals(),pname)
            cls = getattr(serv,pname,None)
            if isclass(cls): #plugin has a self-titled class
                inst = cls() 
                self.__services__[pname]=inst
                log.debug("Service loaded",pname)
                """
                for i in inst.Plugins:
                    if not self.LoadPlugin(i):
                        log.error("Failed to load plugin while loading service",inst,i)
                        return False    """#"""
    
                self.LoadHooks(inst)
                return inst
            else:#No self-titled class?
                log.error("No self titled class for service %s"%pname)
        except:
            log.exception("Exception while loading service")
        return False

    def LoadPlugin(self,pname):
        log.debug("Loading plugin %s.Plugins.%s"%(self.root,pname))
        plug = __import__("%s.Plugins.%s"%(self.root,pname),globals(),locals(),pname)
        cls = getattr(plug,pname,None)
        if isclass(cls): #plugin has a self-titled class
            if not self.checkRequirements(cls):
                log.error("Requirements not met!")
                return False
            self.checkPreferences(cls)
            inst = cls() 
            
            #if we got here we have the requirements, get the hooks
            self.LoadHooks(inst)
            return inst
        else:#No self-titled class?
            log.error("No self titled class for plugin %s"%pname)
            return False

    def GetServices(self,inst):
        slist = getattr(inst,"sbservs",[])
        log.debug("Get services",inst,slist)
        return slist

    def GetMatchingFunctions(self,event):
        log.debug("Matching",event)
        matched = []
        for inst,func in self.__hooks__: 
            args = self.tryMatch(func,event)
            if args!=None:
                matched+=[(inst,func,args)]
        log.debug("Matched: %i"%len(matched))
        return matched


    def tryMatch(self,func,eventD):
        for hookD in func.sbhook:
            args = {}
            matched = True
            for key,pattern in hookD.items():
                value = eventD.get(key)
                if value == None:     
                    matched= False
                    break # plugin wanted to match something the event didn't have 
                
                m = match(pattern,value)
                if m == None:
                    matched = False
                    break # Didn't match

                for k,v in m.groupdict().items(): #named capture groups
                    args[k]=v
                for i,v in enumerate(m.groups()): #unnamed
                    args[key+str(i)]=v
            if matched:
               return args    
        return None

    def AutoLoad(self):        
        log.debug("Starting autoload", "Root:"+self.root)
        cf = ConfigFile(self.root,"Autoload")
        log.debug("Configuration:","val:"+str(cf))
        if cf:
            log.debug("Autoloading plugins and services.")

            names = cf["Plugins","Names"]
            log.debug("Autoloading plugins",names)
            if names:
                for name in names.split():
                    self.LoadPlugin(name)
        else:
            note.note("No Autoload configuration file")


    def Stop(self):
        if self.__services__:
            log.debug("Deleting services:",self.__services__)
            for name,module in self.__services__.items():
                log.debug("Removing service:",name)
                del module

        for name,module in self.__plugins__.items():
            log.debug("Removing plugin:",name)
            del module

