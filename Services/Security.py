from Hook import bindFunction
from Logging import LogFile

log = LogFile("Security_Service")

class Security:
    sessions={} 
    def __init__(self):
        log.debug("Security service created.")
    def onEvent(self,event):#a plugin wants access to our stuff! 
        log.debug("onEvent")
        event["loggedIn"]=self.isLoggedIn
        #only give the the ability to check if a nick is logged in. 

    

    def logIn(self,nick,pswd):#plugin will make call back to here
        log.debug("logIn",nick, self.sessions)
        ses = self.sessions.get(nick,{"pswd":pswd})
        if pswd == ses["pswd"]:
            ses["LoggedIn"]=True
        else:
            return False
        self.sessions[nick]=ses
        return True
    def logOut(self,nick):
        log.debug("logOut",nick,self.sessions)
        ses = self.sessions.get(nick,{})
        ses["LoggedIn"]=False
        self.sessions[nick]=ses

    def isLoggedIn(self,nick):
        ses = self.sessions.get(nick,{})
        status = ses.get("LoggedIn",False)
        log.debug("isLoggedIn",status,self.sessions)
        return status



    #handle the login/logout stuff here 
    @bindFunction(prefix="(?P<nick>.*)!.*",message="login (?P<pswd>.*)")
    def login(self,response,nick,pswd):
        log.debug("Login called",nick,pswd,self.sessions)

        if(self.isLoggedIn(nick)):
            log.debug("Already logged in.")
            return response.msg(nick,"Already logged in")

        log.debug("Logging in.")

        if self.logIn(nick,pswd):
            return response.msg(nick,"Logged in")

        return response.msg(nick,"Login failed")


    
    @bindFunction(message="logout",prefix="(?P<nick>.*)!.*")
    def logout(self,response,nick):
        log.debug("Logout called",nick,self.sessions)
        if not self.isLoggedIn(nick):
            log.debug("Already logged out.")
            return response.msg(nick,"Already logged out")
        log.debug("Logging out")
        self.logOut(nick)
        return response.msg(nick,"Logged out")
