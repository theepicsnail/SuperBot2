'''
Created on Jan 30, 2011

@author: snail
'''

from os.path import join
from os import getcwd
import logging, logging.handlers
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL
import sys,os
from pickle import dumps
LogPath = "Logs" 

#ensure the logging path exists.
try:
    from os import mkdir
    mkdir(join(getcwd(),LogPath))
    del mkdir
except:
    pass



def currentframe():
    """Return the frame object for the caller's stack frame."""
    try:
        raise Exception
    except:
        return sys.exc_info()[2].tb_frame.f_back


def CreateLogger(name,level=None):
    l = logging.getLogger(name)
    l.setLevel(DEBUG)
    if level!=None:
        l.setLevel(level)
    
    handler = logging.handlers.RotatingFileHandler(join(LogPath,"%s.log"%name), maxBytes=10240, backupCount=10)
    formatter = logging.Formatter("%(asctime)s|%(thread)d|%(levelno)s|%(module)s:%(funcName)s:%(lineno)d|%(message)s")
    handler.setFormatter(formatter)
    l.addHandler(handler) 
    return l

class LogFile:

    def __init__(self, output, minLevel=WARNING):
        self.minLevel = minLevel
        self._log = CreateLogger(output)
        self._log.findCaller = self.findCaller
    def findCaller(self):
        """
        Find the stack frame of the caller so that we can note the source
        file name, line number and function name.
        """
        f = currentframe()
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)"
        i=5
        while hasattr(f, "f_code") and i >0:
            i=i-1
            co = f.f_code
            rv = (co.co_filename, f.f_lineno, co.co_name)
            f = f.f_back
        return rv
 

    def debug(self,*vals, **kws):
        self.log(DEBUG,*vals,**kws)
    def note(self,*vals, **kws):
        self.log(INFO,*vals,**kws)
    def info(self,*vals, **kws):
        self.log(INFO,*vals,**kws)
    def warning(self,*vals, **kws):
        self.log(WARNING,*vals,**kws)
    def error(self,*vals, **kws):
        self.log(ERROR,*vals,**kws)
    def critical(self,*vals, **kws):
        self.log(CRITICAL,*vals,**kws)

    def dict(self,d):
        if d:
            lines = [lambda x,y:x+"\t"+y,d.items()]
        else:   
            lines = ["None"]

        self.log(DEBUG,*lines)
    
    def exception(self,*vals):
        lines = list(vals)
        import sys,traceback
        tb = sys.exc_info()
        tbLines=(traceback.format_exception(*tb))
        for l in tbLines:
            lines += l[:-1].split("\n")
        self.log(ERROR,*lines)
        
        global ExceptionLog
        ExceptionLog.log(ERROR,*lines)
    def log(self, level, *vals, **kws):
        self._log.log(level,"\t".join(map(str,vals)))

ExceptionLog = LogFile("Exceptions")
if __name__=="__main__":
    
    import threading, time, random
    class Worker(threading.Thread):
        log = None
        def run(self):
            for i in range(20):
                time.sleep(random.random()*.1)
                if self.log:
                    self.foo()
            self.log.debug("Exception time!")
            try:
                self.bar()
            except:
                self.log.exception("Exception while doing math!")
        def bar(self):
                i = 1/0
            
        def foo(self):
            self.log.warning(i,"abc","123")
    logger = LogFile("test")
    for i in range(20):
        w = Worker()
        w.log = logger
        w.start()
    


