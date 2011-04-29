import sys
from inspect import isclass, getmembers
from re import match
from Logging import LogFile
from Configuration import ConfigFile

log = LogFile("PluginManager")
"""
  Service1   Service2   Service3   Service4
        \     /    \     /            |        
        Plugin1    Plugin2         Plugin3
       /   |  \       |            /     \      These connections are made from
  Func1 Func2 Func3 Func4       Func5   Func6      the call to bindFunction

  Each service has a reference count. When a plugin is removed this number is
  decremented. When that hits 0 the service is removed. All the associated 
  functions are also removed.
  

  __services__ maps the services name to a (object,references) tuple.
  __plugins__ maps the plugins name to a (object,[servicelist],[funclist])
  a service list is a list of service names
  the funclist is a list of functions that have sbhook attributes
"""

class PluginManager:
    __services__ = {}#map of name to (module,instance, reference count)
    __plugins__ = {} #map of name to (class,instance, [service names], [func list])
    root = None # This should be the providers name (and the directory its in)

    def __init__(self, providerPath):
        log.debug("Creating PluginManager for provider <%s>"%providerPath)
        self.root = providerPath

    def HasPlugin(self, plug):
        log.debug("HasPlugin",plug)
        return self.__plugins__.has_key(plug)

    def CheckRequirements(self, cls):
        """
        Check the passed class object for an sbreq attribute. If it exits
        then look though each of the requirements and try to load it.
        """
        log.debug("Check requirements", cls)

        requirements = getattr(cls, "sbreq", None)
        if not requirements:  # no requirements, no problem!
            log.debug("No requirements.")
            return True

        loaded ={} # a buffer for whats going into __services__
        for req in requirements:
            log.debug("Loading Requirement", req)
            serv = None
            if self.__services__.has_key(req):
                log.debug("Requirement already loaded")
            else:
                serv = self.LoadService(req)
                if not serv:
                    #we tried and it failed to load!
                    log.error("Loading requirement failed. Failing")
                    del loaded
                    return False
                loaded[req]=serv
                log.debug("Requirement autoloaded")

        self.__services__.update(loaded)
        del loaded
        log.debug("Requirements met.")
        return True

    #preferences will try to load, but if not it's okay
    def CheckPreferences(self, cls):
        log.debug("Check preferences", cls)

        preferences = getattr(cls, "sbpref", None)
        if not preferences:
            log.debug("No preferences.")
            return True

        loaded={}
        for pref in preferences:
            log.debug("Loading Preference", pref)

            if  self.__services__.has_key(pref):
                log.debug("Preference already loaded")
            else:
                serv = self.LoadService(pref)
                if not serv:
                    log.warning("Preference loading failed.")
                else:
                    loaded[pref]=serv
                    log.debug("Preference autoloaded")
        self.__services__.update(loaded)
        del loaded
        log.debug("Preferences loaded.");
        return True
    
    def LoadService(self, pname):
        try:
            log.debug("Loading service","%s.Services.%s" % (self.root, pname))
            serv = __import__("%s.Services.%s" % (self.root, pname),
                    globals(), locals(), pname)
            cls = getattr(serv, pname, None)
            if isclass(cls):  # plugin has a self-titled class
                inst = cls()
                self.__services__[pname] = (serv,inst,1)
                log.debug("Service loaded", pname)
                return inst
            else:  # No self-titled class?
                log.error("No self titled class for service" , pname)
        except:
            log.exception("Exception while loading service")
        return False

    def LoadPlugin(self, pname):
        log.debug("Loading plugin %s.Plugins.%s" % (self.root, pname))
        plug = __import__("%s.Plugins.%s" % (self.root, pname),
                globals(), locals(), pname)
        #plugin classes should be put into some dict
        #and the associated services should be removed
        #if no other plugins are using it.
        cls = getattr(plug, pname, None)
        if isclass(cls):  # plugin has a self-titled class
            if not self.CheckRequirements(cls):
                log.error("Requirements not met!")
                return False
            self.CheckPreferences(cls)
            inst = cls()

            #if we got here we have the requirements, get the hooks
            
            self.LoadHooks(inst)
            return inst
        else:  # No self-titled class?
            log.error("No self titled class for plugin %s" % pname)
            return False
    def LoadHooks(self,inst):
        #inst.hooks
        
    def UnloadPlugin(self, pname):
        """Given the plugin name, this will attempt to unload the plugin.
        unloading a plugin consists of removing all the hooks from this
        deleting the resources associated with the plugin. And ultimatly
        it should unload services too, if they aren't needed by anyone else
        """
        log.debug("Unloading plugin %s.Plugins.%s" % (self.root, pname))
        

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
        for name,(cls,inst,servs,funcs) in self.__plugins__.items:#class instance services functions
            for f in funcs:
                args = self.tryMatch(f, event)
                if args != None:
                    matched += [(inst, f, args)]
        if matched:
            log.debug("Matched: %i" % len(matched))
            return matched
        return False

    def tryMatch(self, func, eventD):
        for hookD in func.sbhook:
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
        if self.__services__:
            log.debug("Deleting services:", self.__services__)
            for name, module in self.__services__.items():
                log.debug("Removing service:", name)
                del module

        for name, module in self.__plugins__.items():
            log.debug("Removing plugin:", name)
            del module
