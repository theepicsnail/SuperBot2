import sys
from inspect import isclass, getmembers
from re import match
from Logging import LogFile


log = LogFile("PluginManager")

class PluginManager:
    __services__={}
    __plugins__={}
    __hooks__=[] # list of (function, pluginname, functionname)

    AutoLoadDeps = False
    
    def hasService(self,serv):
        log.debug("hasService %s",serv)
        return self.__services__.has_key(serv)
    
    def hasPlugin(self,plug):
        log.debug("hasPlugin %s",plug)
        return self.__plugins__.has_key(plug)
    
    def LoadService(self,serv):
        log.error("Unimplemented")
        return False
    
    def checkRequirements(self,cls):
        log.debug("Check requirements",cls)

        req = getattr(cls,"sbreq",None)
        if not req:#no requirements, no problem!
            log.debug("No requirements.")
            return True
       
        for s in req:
            if not self.hasService(s):#a dep is missing!
                log.warning("Missing requirement",s)
                if not self.AutoLoadDeps:
                    #and we don't load them automatically
                    log.error("Autoload not enabled, failing")
                    return False
                if not self.loadService(s):
                    #we tried and it failed to load!
                    log.error("Loading service failed. failing")
                    return False

        log.debug("Requirements met.")
        return True

    #preferences will try to load, but if not it's okay
    def checkPreferences(self,cls):
        log.debug("Check preferences",cls)

        pref = getattr(cls,"sbpref",None)
        if not pref:
            log.debug("No preferences.")
            return

        for s in pref:
            if not self.hasService(s):
                log.debug("Missing preference",s)
                if self.AutoLoadDeps:
                    if self.loadService(s):
                        log.debug("Service autoloaded")
                    else:
                        log.debug("Loading service failed. skipping")
                else:
                    log.debug("Autoload not enabled, skipping")
        
    
    def addHook(self, inst, func):
        log.debug("Adding hook",inst,func)
        hookArgs = func.sbhook
        self.__hooks__.append((inst,func))
        


    def LoadPlugin(self,pname):
        plug = __import__("Plugins.%s"%pname,globals(),locals(),pname)
        cls = getattr(plug,pname,None)
        if isclass(cls): #plugin has a self-titled class
            if not self.checkRequirements(cls):
                print "Requirements not met!"#TODO Logger this
                return False
            self.checkPreferences(cls)
            inst = cls() 
            
            
            #if we got here we have the requirements, get the hooks
            hookFuncs = filter(lambda x:hasattr(x[1],"sbhook"),getmembers(inst))
            for k,v in hookFuncs:
                self.addHook(inst,v)
                
        else:#No self-titled class?
            print "No self titled class?"
            pass


    def GetMatchingFunctions(self,event):
        matched = []
        for inst,func in self.__hooks__: 
            print "Trying match:"
            print inst
            print func, func.sbhook
            print event
            args = self.tryMatch(func,event)
            print "Try match returned: ", args
            if args!=None:
                print "PM: Matched function:"
                print inst
                print func
                print args
                matched+=[(inst,func,args)]
        return matched


    def tryMatch(self,func,eventD):
        for hookD in func.sbhook:
            print "  ",hookD
            args = {}
            for key,pattern in hookD.items():
                print "     ",key,pattern
                value = eventD.get(key)
                if value == None:     
                    print "---- 1"
                    break # plugin wanted to match something the event didn't have 
                
                m = match(pattern,value)
                if m == None:
                    print "---- 2"
                    break # Didn't match

                for k,v in m.groupdict().items(): #named capture groups
                    args[k]=v
                for i,v in enumerate(m.groups()): #unnamed
                    args[key+str(i)]=v
                print "---- 3"
                return args

    def Stop(self):
        for name,module in self.__services__:
            print "Removing service:",name
            del module
        for name,module in self.__plugins__:
            print "Removing plugin:",name
            del module
