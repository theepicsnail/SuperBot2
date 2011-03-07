from Hook import bindFunction
class Test:
    @bindFunction(command="PRIVMSG",prefix="(?P<nick>.*)!.*")
    def foo(self,response,nick,message):
        print "== foo"
        return response.msg(nick,message)
        
    @bindFunction(command="INVITE")
    def joiner(self,response,message):
        print "== joiner"
        return response.join(message)


