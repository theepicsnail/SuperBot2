from Hook import bindFunction
class Test:
    @bindFunction(command="PRIVMSG",prefix="(?P<nick>.*)!.*")
    def foo(self,response,nick,message):
        print "== foo"
        if message=="stop":
            return response.stop()
        return response.msg(nick,message)
        
    @bindFunction(command="INVITE")
    def joiner(self,response,message):
        print "== joiner"
        return response.join(message)


