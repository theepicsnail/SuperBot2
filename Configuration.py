#!/usr/bin/python
import os.path, os, ConfigParser 
import inspect

class ConfigFile:
    _Valid = False
    _Config = None
    def __init__(self,*parts):
        #get the parent's directory
        stk = inspect.stack()
        path = stk[1][0].f_code.co_filename
        base = os.path.sep.join(path.split(os.path.sep)[:-1])
        #join it with the provided parts
        path = os.path.join(base,*parts)+".cfg"
        
        
        config = ConfigParser.ConfigParser()
        if not config.read(path): return; # log an error?

        
        self._Config = config
        self._Valid = True
 
    def __getitem__(self,arg):
        if not self._Valid: return None
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
    def __iter__(self):
        if not self._Valid: return
        for i in self._Config.sections():
            yield i

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


