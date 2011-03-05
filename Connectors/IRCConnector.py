from Interfaces import Connector
from zope.interface import implements
from twisted.words.protocols import irc
from twisted.internet import protocol,reactor

#these events get given to plugins to give back to the the ircconnector
class IRCConnectorEvents:

    def __init__(self): pass

    def join(self,channel, key=None):
        return "join",channel,key
    def part(self,channel, message=None): 
        return "part",channel,messages
    def kick(self,channel, user, message=None): 
        return "kick",channel,user,message
    def topic(self,channel, message=None):
        return "topic",channel,message
    def say(self, channel, message, length=None):
        return "say",channel,message, length
    def msg(self, user, message, length=None):
        return "msg",user,message,length
    def notice(self,user, message):
        return "notice",user, message
    def away(self,message=""):
        return "away",message
    def back(self):
        return "back"
    def setNick(self,nickname):
        return "setNick",nickname
    def quit(self,message=""):
        return "quit",message
    def me(self,channel,message):
        return "action",channel,message
    def ping(self,user,message=""):
        return "ping",user,message


class IRCConnector(protocol.ClientFactory,irc.IRCClient,object):
    implements(Connector)


    def pushEvent(self,eventInfo):        
        f = getattr(self,eventInfo[0],None)
        if f:
            f(*eventInfo[1:])
   
 
    onEvent      = None
    onConnect    = None
    onDisconnect = None
    onError      = None

    configuration = {}
    def buildProtocol(self,addr):
        return self

    def handleCommand(self,cmd,prefix,params):
        super(IRCConnector, self).handleCommand(cmd,prefix,params)

        if self.onEvent:
            event = {}
            event["command"]=cmd
            event["prefix"]=prefix
            event["target"]=params[0]
            if len(params)==2:
                event["message"]=params[1]
            self.onEvent(event) 


    def __init__(self):
        self.eventObj  = IRCConnectorEvents()
        self.protocol = self
        
    def connect(self): 
        print "Connect"
        if not self.configuration.has_key("host"): return
        if not self.configuration.has_key("port"): return
        if not self.configuration.has_key("nick"): return

        self.nickname=self.configuration["nick"]
        reactor.connectTCP(
                self.configuration["host"],
                self.configuration["port"],
                self)
        reactor.run()

    def disconnect(self): 
        print "Disconnect"
        if self.onDisconnect: self.onDisconnect()

    def getEvents(self):
        return self.eventObj

        

    def configure(self,*a,**b):
        self.configuration=b


    #Client Factory stuff 
    #TODO: eventually override this with reconnection stuff
    #def clientConnectionFailed(self, connector, reason):
    #def clientConnectionLost(self,connector, reason):

    #call backs
    def setConnectCallback(self,c):
        self.onConnect = c

    def setDisconnectCallback(self,c):
        self.onDisconnect = c

    def setErrorCallback(self,c):
        self.onError = c

    def setEventCallback(self,callback): 
        self.onEvent = callback

