from zope.interface import Interface

class Connector(Interface):
    def connect(self):
        """
This should signal the connector to start the connection.
The connection information will be given from the configuration call"""


    def disconnect(self):
        """
Signal the connector to disconnect/stop
"""


    def getEvents(self): 
        """
This should return an object a response/events object that will be passed
to plugins for a plugin to pass events back to this connector.
"""


    def setEventCallback(self,func): 
        """
This callback is how the connector feeds information back to the core.
The connector should call this whenever it wants to pass an event to plugins
"""


    def pushEvent(self,eventInfo):
        """
This is called by the core (or response manager) when there is an event
that the connector should handle (usually pushing something down the network).
"""


    def configure(self,configuration):
        """
This is possibly the first point of interaction. This will
provide the details to the connetor for server/port/etc
TODO: Figure out a good configuation structure (possibly the already built one i made)
"""


    def setConnectCallback(self,func):
        """
This is a way for the connector to notify the core it's been connected.
This callback can be called to tell plugins that were ready to send responses
"""

    def setDisconnectCallback(self,func):
        """
This gives the connector a way to notify everything that we are nolonger
connected and that they should not send more responses.
"""

    def setErrorCallback(self,func):
        """
If the connector wants to notify plugins and the core of an error it should
call this callback.
TODO: Figure out how to send the error and possible stack trace etc in a nice way
"""



#TODO: possibly add interfaces for plugin manager and response manager
