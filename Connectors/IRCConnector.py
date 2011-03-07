from Interfaces import Connector
from Configuration import ConfigFile
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
    EventHandler = None

    def HandleResponse(self,eventInfo):        
        f = getattr(self,eventInfo[0],None)
        if f:
            f(*eventInfo[1:])
    def SetEventHandler(self,func):
        self.EventHandler=func
    def buildProtocol(self,addr):
        return self

    def handleCommand(self,cmd,prefix,params):
        super(IRCConnector, self).handleCommand(cmd,prefix,params)

        if self.EventHandler:
            event = {}
            event["command"]=cmd
            event["prefix"]=prefix
            event["target"]=params[0]
            if len(params)==2:
                event["message"]=params[1]
            self.EventHandler(event) 


    def __init__(self):
        self.eventObj  = IRCConnectorEvents()
        self.protocol = self
        self.config = ConfigFile("IRCConnector")

    def Start(self): 
        print "Connect", self.config
        
        server = self.config["Connection","Server"]
        port = int(self.config["Connection","Port"])
        nick = self.config["Connection","Nick"]

        if not server:
            print "No 'Connection:Server' specified."
            return
        if not port: 
            print "No 'Connection:Port' specified."
            return
        if not nick: 
            print "No 'Connection:Nick' specified."
            return

        self.nickname=nick
        reactor.connectTCP(server,port,self)
        reactor.run()

    def Stop(self): 
        print "Disconnect"

    def GetResponseObject(self):
        return self.eventObj

        

