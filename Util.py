import inspect


def dictJoin(src, addition):
    if src == None:
        return None

    a = src.copy()

    if addition == None:
        #return a copy so that this function always
        #returns a new dict and never a reference to src
        return a
    a.update(addition)
    return a


def call(func, args):
    reqArgs = inspect.getargspec(func).args[1:]
    defaults = inspect.getargspec(func).defaults
    if defaults:
        defArgs = reqArgs[-len(defaults):]
        defaults = dict(zip(defArgs, defaults))
        for key, val in defaults.items():
            if not args in key:
                args[key] = val
    passedArgs = map(args.get, reqArgs)
    r = func(*passedArgs)
    return r

if __name__ == "__main__":
    #default parameter test
    class Test():
        def foo(self, a, b=123):
            print self, a, b

        def bar(self, a):
            print self, a
    t = Test()
    d = {}
    call(t.foo, d)  # None, 123

    d["a"] = 2
    call(t.foo, d)  # 2, 123

    d["b"] = 3
    call(t.foo, d)  # 2, 3

    del d["a"]
    call(t.foo, d)  # None, 3

    call(t.bar, {})  # None

    call(t.bar, {"a": "a"})  # a
