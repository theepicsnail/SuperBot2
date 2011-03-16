from Hook import bindFunction,requires

@requires("Security")
class Test:
    @bindFunction(command="PRIVMSG",prefix="(?P<nick>.*)!.*")
    def foo(self,response,nick,message,loggedIn):
        if loggedIn(nick):
            return response.msg(nick,message);
            
        if message=="stop":
            return response.stop()
        


