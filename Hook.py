#TODO: put checks in , requires/prefers should accept
#strings as the plugins and classes for cls
from Logging import LogFile
log = LogFile("Hook")

def requires(*plugins):
    def newClass(cls):
        log.debug("Requires",cls,*plugins)
        reqs = getattr(cls, "sbreq", [])
        reqs.extend(plugins)
        cls.sbreq = reqs
        return cls
    return newClass


def prefers(*plugins):
    def newClass(cls):
        log.debug("Prefers",cls,*plugins)
        prefs = getattr(cls, "sbpref", [])
        prefs.extend(plugins)
        cls.sbpref = prefs
        return cls
    return newClass


#TODO: the checking for this aswell, args should map to str->str
#and func should be a function
def bindFunction(**args):
    def newFunc(func):  # the actual descriptor
        log.debug("BindFunction",func)
        log.dict(args)

        attr = getattr(func, "hooks", [])
        attr.append(args)
        func.hooks=attr
        return func
    return newFunc


def dedicated(delay=1):
    def newFunc(func):
        log.debug("Dedicated",func,delay)
        func.delay = delay
        func.dedicated=True
        return func
    return newFunc
