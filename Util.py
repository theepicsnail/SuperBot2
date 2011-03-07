def dictJoin(src, addition):
    if src==None:
        return None

    a = src.copy()

    if addition==None:
        return a#return a copy so that this function always
                #returns a new dict and never a reference to src

    for k,v in addition.items():
        a[k]=v
    return a


def call(func, args):
     
    reqArgs = func.func_code.co_varnames[1:]
    passedArgs = map(args.get,reqArgs)
    print "----- call -----"
    print "  ",func
    print "  ",args
    print "  ",reqArgs
    print "  ",passedArgs    
    r = func(*passedArgs)
    print "  ",r
    print "----------------"
    return r
