from zope.interface import Interface

class Connector(Interface):
    def SetEventHandler(self,func): pass
    def GetResponseObject(self): pass
    def HandleResponse(self,response): pass
    def Start(self): pass
    def Stop(self): pass
    









#TODO: possibly add interfaces for plugin manager and response manager
