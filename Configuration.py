#!/usr/bin/python
import os
import logging,logging.handlers



def listHandler(data):
    """ Custom handlers for data in the config file can return 'failure'
    by either raising an exception which will be caught, or returning
    None. Both of these flag the attribute as "Failed to convert"
    
    There is no way to specify that the attributes value should literally
    be None.
    """
    return data.split()

def boolHandler(data):
    """ Since bool("false") returns true, we should make a more intuative
    method for converting booleans.
    """    
    return data.lower() in ["true","1"]


#Generic object to store the config file information in
class Config(object): 
    def __getattr__(self,key):
        """Return None for all un-defined attributes
        This will allow code to use things like
        if config.something:
            x = config.something.else
        etc..."""
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        return None
    def __getitem__(self,key):
        return self.__getattr__(key)
    def __nonzero__(self):
        return True
    def __str__(self):
        """Returns a nicely formatted string that contains all the attributes in this config"""
        l = filter(lambda x:x[0]!="_",self.__dict__.keys())
        return "Config["+",".join(l)+"]"

    def __repr__(self):
        return str(self)
    def __iter__(self):
        for i in self.__dict__.keys():
            yield i

class ConfigFile:
    """The ConfigFile class does not read the file is was created with
        until getConfig is called. getConfig returns a Config object.

        The attributes that a Config object has (and thus what is looked
        for in the config file) are defined by the addAttr function.

        attributes but be addAttr'd then the next call to getConfig() 
        will reflect the additions (if the config file is valid) 
    """

    def __init__(self,filename="Superbot.cfg"):
        """This constructs the ConfigFile and adds the basic attributes that will be
        used in the basic SuperBot instance.

        Configurations should be in the ConfigParser format 
        http://docs.python.org/library/configparser.html

        The only fields required are server.host, and bot.nick. Thus:
        [server]
        host=example.com
        [bot]
        nick=MyBot

        is the minimal configuration.
        """
        self.configFile = filename
        self.attributeTree={}
        self.addAttr("server","host",str)        #required
        self.addAttr("server","port",int,6667)
        self.addAttr("server","reconnect",boolHandler,False)
        self.addAttr("bot","nick",str)          #required
        self.addAttr("bot","join",listHandler,[])
        self.addAttr("services","load",listHandler,[])
        self.addAttr("plugins","load",listHandler,[])
        self.addAttr("logger","filename",str,"Superbot.log")
        self.addAttr("logger","count",int,5)
        self.addAttr("logger","size",int,1024)
    
    def addAttr(self,section,entry,converter,default=None):
        """Add an attribute for the ConfigFile to parse for
            section  = the section of the attribute "server","bot",etc
            entry    = the name that is associated with the value
            converter= function to pass the string to, to convert it
                           to the desired format
            default  = If the argumen is required, this field should be None
                       otherwise it should store a defaul value
        """
        if not self.attributeTree.has_key(section):
            self.attributeTree[section]={}
        self.attributeTree[section][entry]=(converter,default)
       

 
    def getConfig(self):
        """
        This will parse the specified cnfig file and return an object that 
        has the config files information stored in it.
        The way the information is stored is as follows:
        [server]
        host=example.com

        would be accessed as such:

        cf = ConfigFile("example.cfg")
        config = cf.getConfig()
        print config.server.host

        if there is an error while reading the config file, this function
        returns None
        """

        #build the ConfigParser, and read the config file
        import ConfigParser
        configP = ConfigParser.ConfigParser()
        configP.optionxform=str
        try:
            configP.read(self.configFile)
        except Exception as E:
            print "Failed to parse config file!"
            print E
            return None
        

        #put the config file into a usable tree
        configFile={}
        for section in configP.sections():

            if not configFile.has_key(section):
                configFile[section]={}

            for key,val in configP.items(section):
                configFile[section][key]=val
    
        del configP
        del ConfigParser
    
        config = Config() #make a dummy object to put the attributes in
        for section,fields in self.attributeTree.items():
            if  getattr(config,section)==None:#we could hit a section more than once 
                setattr(config,section,Config())
            for key,value in fields.items():#get the (converter,default), for each requested argument
                converter,default = value
                if configFile.has_key(section) and configFile[section].has_key(key):#everythings good
                    cleaned = None
                    try:
                        cleaned = converter(configFile[section][key])
                    except:
                        print "Exception during conversion of",section,key
                        cleaned = None

                    if cleaned == None:
                        if default==None:
                            print "Invalid input in config file:"
                            print "Section:",section
                            print "Key:    ",key
                            print "Value:  ",configFile[section][key]
                            print "Handler:",converter
                            print "No default provided. Parser failed."
                            return None
                        cleaned = default
                    setattr(getattr(config,section),key,cleaned)
                else:#that field/section is missing from the config file
                    if default == None:
                        print "Unspecified value:"
                        print "Section:",section
                        print "Key    :",key
                        print "Handler:",converter
                        print "No default provided. Parser failed."
                        return None

                    setattr(getattr(config,section),key,default)
        return config


if __name__=="__main__":
    c = ConfigFile()
    i = c.getConfig()
    def dump(obj, level=0):
        if not obj:
            return 

        for i in obj:
            print "  "*level+str(i),
            if type(obj[i])==Config:
                print ""
                dump(obj[i],level+1)
            else:
                print obj[i]
    dump(i)
