import inspect
def dictJoin(src, addition):
    if src==None:
        return None

    a = src.copy()

    if addition==None:
        return a#return a copy so that this function always
                #returns a new dict and never a reference to src
    a.update(addition)
    return a


def call(func, args):
    reqArgs = inspect.getargspec(func).args[1:]
    passedArgs = map(args.get,reqArgs)
    r = func(*passedArgs)
    return r
