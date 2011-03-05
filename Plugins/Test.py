from Hook import bindFunction
class Test:
    @bindFunction(command="PRIVMSG",prefix="(?P<nick>.*)!.*")
    def foo(self,response,nick,message):
        return response.msg(nick,message)
        

    @bindFunction(command="(.*)")
    def bar(self):
        print "BAR"


