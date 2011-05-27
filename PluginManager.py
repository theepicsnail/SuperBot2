import sys
from inspect import isclass, getmembers
from re import match
from Logging import LogFile
from Configuration import ConfigFile
import os
log = LogFile("PluginManager")
"""
 SFunc1   SFunc2   SFunc3  SFunc4
     \         \  /         |
  Service1   Service2   Service3   Service4  __services__
        \     /    \     /            |        
        Plugin1    Plugin2         Plugin3   __plugins__
       /   |  \       |            /     \      These connections are made from
  Func1 Func2 Func3 Func4       Func5   Func6      the call to bindFunction
                                                hooks are located at foo.Hooks

  Each service has a reference count. When a plugin is removed this number is
  decremented. When that hits 0 the service is removed. All the associated 
  functions are also removed.
  

  __services__ maps the services name to a (module,instance,references) tuple.
  __plugins__ maps the plugins name to a (module,instance,[servicelist],[funclist])
  servicelist: ["Service1","Service2","Service3","Service4"] updated as plugins
                                                         require or prefer them.
  funcmap:    {"Plugin1":[Func1,Func2,Func3], "Plugin2"...} 
  the funclist is a list of functions that have sbhook attributes
"""

class PluginManager: #we really only need the function and ref count
    __services__ = {}#map of name to (module,instance, [service names], [func list], reference count)
    __plugins__ = {} #map of name to (module,instance, [service names], [func list])
    root = None # This should be the providers name (and the directory its in)
    def rmPyc(self,mod):
#        print "rm:",os.getcwd()+"/"+path
#        os.remove(os.path.join(os.getcwd(),path))
#        for i in sys.modules.items():
#            print i[0]
        f = mod.__file__
        if f[-1]!="c":
            f+="c"
        log.debug("Remove Module:",mod.__name__,"Deleting:",f)
        del sys.modules[mod.__name__]
        try:
            os.remove(f)
        except:
            pass

    def __init__(self, providerPath):
        log.debug("Creating PluginManager for provider <%s>"%providerPath)
        self.root = providerPath
    def HasService(self, serv):
        return self.__services__.has_key(serv)

    def HasPlugin(self, plug):
        return self.__plugins__.has_key(plug)

    def GetService(self,servName):
        s = self.__services__.get(servName,[None,None,1])[1]
        return s

    def CheckRequirements(self, cls):
        """
        Check the passed class object for an sbreq attribute. If it exits
        then look though each of the requirements and try to load it.
        """
        log.debug("Check requirements", cls)

        requirements = getattr(cls, "sbreq", None)
        if not requirements:  # no requirements, no problem!
            log.debug("No requirements.")
            return []

        loaded = []
        for req in requirements:
            log.debug("Loading Requirement", req)
            serv = None
            serv = self.LoadService(req)
            if not serv:
                #we tried and it failed to load!
                log.error("Loading requirement failed. Failing")
                del loaded #This needs to be properly unloaded
                return False
            log.debug("Requirement autoloaded")
            loaded+=[req]

        log.debug("Requirements met.")
        return loaded

    #preferences will try to load, but if not it's okay
    def CheckPreferences(self, cls):
        log.debug("Check preferences", cls)

        preferences = getattr(cls, "sbpref", None)
        if not preferences:
            log.debug("No preferences.")
            return []

        loaded=[]
        for pref in preferences:
            log.debug("Loading Preference", pref)
            serv = self.LoadService(pref)
            if not serv:
                log.warning("Preference loading failed.")
            else:
                loaded+=[pref]
                log.debug("Preference autoloaded")
        log.debug("Preferences loaded.");
        return loaded
    
    def LoadService(self, pname):
        """Called whenever a plugin is being loaded and it requires/prefers
        a service. This will update the reference count if the module exists
        if successful, this returns True, otherwise it returns False."""
        s = self.__services__.get(pname)
        log.debug("Loading service","%s.Services.%s" % (self.root, pname))
        if s:
            s[-1]+=1
            log.debug("Service found","Adding reference",*s)
            log.dict(self.__services__,"Services:")
            return s[1]

        try:
            mod = __import__("%s.Services.%s" % (self.root, pname),
                    globals(), locals(), pname)
            cls = getattr(mod, pname, None)
            if isclass(cls):  # plugin has a self-titled class
                services = self.CheckRequirements(cls)
                if services == False:
                    log.error("Requirements not met!")
                    return False
                services +=self.CheckPreferences(cls)
 #               print pname,"Services:",services
                inst = cls()#any exceptions get caught higher up in the stack
    
                #if we got here we have the requirements, get the hooks
                
                funcList= self.LoadHooks(inst)
                log.note("Plugin loaded.","%s.Plugins.%s" % (self.root, pname))

                self.__services__[pname] = [mod,inst,services,funcList,1]
                log.debug("Service loaded", pname)
                log.dict(self.__services__,"Services:")
                return inst
            else:  # No self-titled class?
                log.error("No self titled class for service" , pname)
        except:
            log.exception("Exception while loading service",pname)
            log.dict(self.__services__,"Services:")
        return False

    def LoadPlugin(self, pname):
        log.note("Loading plugin %s.Plugins.%s" % (self.root, pname))
        mod = __import__("%s.Plugins.%s" % (self.root, pname),
                globals(), locals(), pname)
#        print "Before loadplugin";self.tmp()
        #plugin classes should be put into some dict
        #and the associated services should be removed
        #if no other plugins are using it.
        cls = getattr(mod, pname, None)
        if isclass(cls):  # plugin has a self-titled class
            services = self.CheckRequirements(cls)
            if services == False:
                log.error("Requirements not met!")
             #   print "Requirements not met.";self.tmp()
                return False
            services +=self.CheckPreferences(cls)
            inst = cls()#any exceptions get caught higher up in the stack

            #if we got here we have the requirements, get the hooks
            
            funcList= self.LoadHooks(inst)
            log.note("Plugin loaded.","%s.Plugins.%s" % (self.root, pname))
            self.__plugins__[pname]=(mod,inst,services,funcList)
            #print "Plugin loaded";self.tmp()
            return inst
        else:  # No self-titled class?
            log.error("No self titled class for plugin %s" % pname)
            #print "PluginLoad failed";self.tmp()
            return False

    def LoadHooks(self,inst):
        #inst.hooks
        def filter(memb):
            if callable(memb):
                return hasattr(memb,"hooks")
            return False

        hookFuncs = getmembers(inst,filter)
        funcs = []
        for name,func in hookFuncs:
            log.debug("Adding hook",inst,func)
            funcs.append(func)
        return funcs
    def UnloadPlugin(self, pname):
        """Given the plugin name, this will attempt to unload the plugin.
        unloading a plugin consists of removing all the hooks from this
        deleting the resources associated with the plugin. And ultimatly
        it should unload services too, if they aren't needed by anyone else
        """
        log.debug("Unloading plugin %s.Plugins.%s" % (self.root, pname))
        if not self.HasPlugin(pname):
            log.debug("Plugin wasn't loaded.",pname)
            return
        servs = self.__plugins__[pname][2]
        self.rmPyc(self.__plugins__[pname][0])
        del self.__plugins__[pname]
        log.debug("Plugin Unloaded",pname,"Unloading services:",*servs)
        for i in servs:
            self.UnloadService(i)
        return

    def UnloadService(self,sname):
        log.debug("Unloading service %s.Service.%s"%(self.root,sname))
        if not self.HasService(sname):
            log.debug("Service wasn't loaded.",sname)
            return

        serv = self.__services__[sname]
        log.debug("Service found:",sname,*serv)
        serv[-1]-=1
        if not serv[-1]:
            log.debug("No more references, deleting")
            self.rmPyc(self.__services__[sname][0]) 
            del self.__services__[sname]

    def GetServices(self, inst):
        slist = getattr(inst, "sbservs", [])
        log.debug("Get services", inst, slist)
        return slist

    def GetMatchingFunctions(self, event):
        """
        For each plugin:
            For each hook in that plugin:
                tryMatch(hook,event)
        """
        
        log.debug("Matching", event)
        matched = []
        for name,(cls,inst,servs,funcs,ref) in self.__services__.items():
            for f in funcs:
                args = self.tryMatch(f,event)
                if args != None:
                    matched += [(inst, f, args, servs)]

        for name,(cls,inst,servs,funcs) in self.__plugins__.items():#class instance services functions
            for f in funcs:
                args = self.tryMatch(f, event)
                if args != None:
                    matched += [(inst, f, args, servs)]
        if matched:
            log.debug("Matched:",*matched)
            return matched
        return []

    def tryMatch(self, func, eventD):
        for hookD in func.hooks:
            args = {}
            matched = True
            for key, pattern in hookD.items():
                value = eventD.get(key)
                if value == None:
                    matched = False
                    # plugin wanted to match something the event didn't have
                    break

                m = match(pattern, value)
                if m == None:
                    matched = False
                    break  # Didn't match

                for k, v in m.groupdict().items():  # named capture groups
                    args[k] = v
                for i, v in enumerate(m.groups()):  # unnamed
                    args[key + str(i)] = v
            if matched:
                return args
        return None

    def AutoLoad(self):        
        log.debug("Starting autoload", "Root:" + self.root)
        cf = ConfigFile(self.root, "Autoload")
        lines = ["Configuration:"]
        for i in cf:
            lines.append(i)
            for j in cf[i]:
                lines.append("  %s=%s"%(j,cf[i,j]))
        log.debug(*lines)

        if cf:
            log.debug("Autoloading plugins and services.")

            names = cf["Plugins", "Names"]
            log.debug("Autoloading plugins", names)
            if names:
                for name in names.split():
                    self.LoadPlugin(name)
        else:
            note.note("No Autoload configuration file")

    def Stop(self):
        log.note("Stopping PluginManager")
        for name, module in self.__services__.items():
            self.UnloadService(name)

        for name, module in self.__plugins__.items():
            self.UnloadPlugin(name)
