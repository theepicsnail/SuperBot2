import sys
from inspect import isclass, getmembers

from Logging import getLogger


log = getLogger("PluginManager")

class PluginManager:
    __services__={}
    __plugins__={}
    __hooks__=[] # list of (function, pluginname, functionname)

    AutoLoadDeps = False
    
    def hasService(self,serv):
        log.error("hasService %s",serv)
        return self.__services__.has_key(serv)
    
    def hasPlugin(self,plug):
        log.error("hasPlugin %s",plug)
        return self.__plugins__.has_key(plug)
    
    def addSearchPath(self,path):
        sys.path.append(path)
    
    def loadService(self,serv):
        return True
    
    def checkRequirements(self,cls):
        req = getattr(cls,"sbreq",None)

        if not req:#no requirements, no problem!
            return True
        
        for s in req:
            if not self.hasService(s):#a dep is missing!
                if not self.AutoLoadDeps:
                    #and we don't load them automatically
                    return False
                if not self.loadService(s):
                    #we tried and it failed to load!
                    return False
        
        return True

    #preferences will try to load, but if not it's okay
    def checkPreferences(self,cls):
        pref = getattr(cls,"sbpref",None)

        if not pref:
            return
        for s in pref:
            if not self.hasService(s) and self.AutoLoadDeps:
                self.loadService(s)
        
    def getHooks(self):
        return self.__hooks__    
    
    def addHook(self, inst, func):
        hookArgs = func.sbhook
        self.__hooks__.append((inst,func))
        


    def loadPlugin(self,pname):
        plug = __import__(pname,fromlist=(pname,))
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



