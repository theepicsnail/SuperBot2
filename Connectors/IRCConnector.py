from Configuration import ConfigFile
from Logging import LogFile
from twisted.words.protocols import irc
from twisted.internet import protocol,reactor
import sys,traceback
#these events get given to plugins to give back to the the ircconnector
log = LogFile("IRCConnector")
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
        if length:
            return "msg",user,message,length
        return "msg",user,message
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
    def stop(self):
        return "stop"

class IRCConnector(protocol.ClientFactory,irc.IRCClient,object):
    EventHandler = None
    reactor = None
    def HandleResponse(self,eventInfo):        
        if eventInfo=="stop":
            log.debug("Stopping reactor")
            self.reactor.stop()
            self.transport.doWrite()
            return 
        f = getattr(self,eventInfo[0],None)
        if f:
            try:
                log.debug("Calling",f,eventInfo[1:])
                f(*eventInfo[1:])
                self.transport.doWrite() #Coming from a different thread, we have to do this apparently
            except:
                traceback.print_exc(file=sys.stdout)

    def SetEventHandler(self,func):
        log.debug("Event handler set to",func)
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
            log.debug("Producing Event",event)
            self.EventHandler(event) 


    def __init__(self):
        log.note("Constructing.")
        self.eventObj  = IRCConnectorEvents()
        self.protocol = self
        self.config = ConfigFile("IRCConnector")
        
    def Start(self): 
        
        server = self.config["Connection","Server"]
        port = int(self.config["Connection","Port"])
        nick = self.config["Connection","Nick"]

        log.note("Connecting",server,port,nick)
        if not server:
            log.fatal("No 'Connection:Server' specified.")
            return
        if not port: 
            log.fatal("No 'Connection:Port' specified.")
            return
        if not nick: 
            log.fatal("No 'Connection:Nick' specified.")
            return

        self.nickname=nick
        reactor.connectTCP(server,port,self)
        log.note("Running reactor")
        self.reactor = reactor
        reactor.run()

    def Stop(self): 
        log.note("Nothing to do for stopping")

    def GetResponseObject(self):
        return self.eventObj

        

