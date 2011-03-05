'''
Created on Jan 30, 2011

@author: snail
'''
from os.path import join
import logging, logging.handlers
from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

LogPath = "Logs"

#ensure the logging path exists.
try:
    from os import mkdir
    mkdir(LogPath)
    del mkdir
except:
    pass

#this could probably be much better
def getLogger(name,level=None):
    l = logging.getLogger(name)
    if level!=None:
        l.setLevel(level)
    handler = logging.handlers.RotatingFileHandler(join(LogPath,name), maxBytes=10240, backupCount=5)
    l.addHandler(handler)
    return l






from os import linesep
from time import time
class Logger:
    recordSeparator = linesep
    def __init__(self, output, minLevel=WARNING):
        self.minLevel = minLevel
        self.output = output
    def debug(self,*vals, **kws):
        self.log(DEBUG,*vals,**kws)
    def info(self,*vals, **kws):
        self.log(INFO,*vals,**kws)
    def warning(self,*vals, **kws):
        self.log(WARNING,*vals,**kws)
    def error(self,*vals, **kws):
        self.log(ERROR,*vals,**kws)
    def critical(self,*vals, **kws):
        self.log(CRITICAL,*vals,**kws)
    def log(self, level, *vals, **kws):
        pass



