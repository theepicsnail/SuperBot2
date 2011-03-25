#!/usr/bin/python
import os.path, os, ConfigParser 
import inspect
from Logging import LogFile
log = LogFile("ConfigFiles")

class ConfigFile:
    _Valid = False
    _Config = None
    def __init__(self,*parts):
        log.debug("__init__",*parts)
        #get the parent's directory
        stk = inspect.stack()
        path = stk[1][0].f_code.co_filename
        base = os.path.sep.join(path.split(os.path.sep)[:-1])
        #join it with the provided parts
        path = os.path.join(base,*parts)+".cfg"
        log.debug("path",path)
        
        config = ConfigParser.ConfigParser()
        if not config.read(path):
            log.critical("Failed to load logfile:",path)
            return

        
        self._Config = config
        self._Valid = True
 
    def __getitem__(self,arg):
        log.debug("GetItem",self._Config,arg)
        if not self._Valid: return None
        try:
            if type(arg)==tuple:
                if len(arg)==2:
                    return self._Config.get(*arg)
                elif len(arg)==1:
                    return self._Config.items(*arg)
                elif len(arg)==3:
                    exp = arg[2]
                    narg = arg[:2]
                    if exp==str:    return self._Config.get(*narg)
                    elif exp==bool: return self._Config.getboolean(*narg)
                    elif exp==int:  return self._Config.getint(*narg)
                    elif exp==float:return self._Config.getfloat(*narg)
                    else: 
                         return exp(self._Config.get(*narg))
            elif type(arg)==str:
                return self._Config.items(arg)
            else: 
                return None # log error
        except:
            return None
    def __iter__(self):
        log.debug("__Iter__ started",self._Config)
        if not self._Valid: return
        for i in self._Config.sections():
            log.debug("__Iter__ yield",self._Config,i)
            yield i
        log.debug("__Iter__ stopped",self._Config)

if __name__=="__main__":
    cf = ConfigFile("Foo")
    for section in cf:
        print section
        for item in cf[section]:
            print item

    def converter(read):
        return map(int,read.split())
    print cf["Section1","arg1",converter]

    print cf["Section1","arg2",bool]
    print cf["Section2","arg1",str]


