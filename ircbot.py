#!/usr/bin/python


"""
IRC bot using the Twisted framework

Features:
    -> SSL connections
    -> Logs channel events to stdout or file
    -> Responds with a random quote from a file when PM'ed
"""


from twisted.words.protocols import irc
from twisted.internet import reactor, protocol, ssl
from twisted.python import log
import time
import argparse
from random import choice

# this will hold the various irc networks that it can connect to
networks = {'freenode': 'irc.freenode.net'}


# bot description
prog_desc = """ ###### Twisted based IRC bot that logs channel messages
#####
"""

parser = argparse.ArgumentParser(description=prog_desc)
# add arg: network
parser.add_argument(
    '-n',
    choices = networks,
    help = 'Network / server name. Ex.: freenode',
    dest = 'irc_server',
    type = str,
    required=True
    )
# add arg: channel name
parser.add_argument(
    '-c',
    help = 'Channel name. Ex.: awesomechannel',
    dest = 'channel',
    type = str,
    required=True
    )
# add optional arg: log file
parser.add_argument(
    '-f',
    help = 'Name of the log file',
    dest = 'filename',
    type = str
    )


args = parser.parse_args()
argdict = vars(args)
try:
    for arg in argdict:
        for node in networks:
            if argdict[arg] == node:
                irc_server = networks[node]               
except:
    print ' No valid network found'
    parser.print_help()



channel = '#' + argdict['channel']


port = 6697 

# nickname formatting
def nickFormat(user_nick):
    nick = '<' + user_nick.split('!', 1)[0] + '>'
    return nick
    

# quote picker class
class PickQuote(object):
    def __init__(self, filename):
        with open(filename) as quotes_file:
            self.quote = quotes_file.readlines()
    def chooseQuote(self):
        return choice(self.quote).strip()
    

# this class defines the bot's behaviour
class ZeroBot(irc.IRCClient):

    def _get_nickname(self):
        return self.factory.nickname
    nickname = property(_get_nickname)
    
    def connectionMade(self):
        """
        Called when a connection is made.
        This may be considered the initializer of the protocol, because it is
        called when the connection is completed. For clients, this is called once
        the connection to the server has been established; for servers, this is
        called after an accept() call stops blocking and a socket has been
        received. If you need to send any greeting or initial message, do it here. 
        """
        irc.IRCClient.connectionMade(self)
        print "conected at " + str(time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        """
        Called when the connection is shut down.
        Clear any circular references here, and any external references to this
        Protocol. The connection has been closed.
        """
        irc.IRCClient.connectionLost(self, reason)
        print " disconnected at " + str(time.asctime(time.localtime(time.time())))

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)
        print "Successfully joined the server at " + irc_server

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        print self.factory.nickname + " " + "has joined " + self.factory.channel

    def left(self, channel):
        """Called when leaving a channel"""
        print self.factory.nickname + " " + "has left " + self.factory.channel 

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""     
        sender = user.split('!', 1)[0] 
        user = nickFormat(user)
    
        if channel == self.nickname: # if it's a PM
            # this is the PM
            print "[PM]: " + '[' + str(time.strftime("%I:%M:%S")) + ']' + " " + user + " " + msg

            answer = PickQuote('quotes.txt').chooseQuote()
            self.msg(sender, answer)            
            return        
        # log users' messages
        print '[' + str(time.strftime("%I:%M:%S")) + ']' + " " + user + " " + msg
        
        
    
    def userJoined(self, user, channel):
        """Called when I see another user joining a channel."""
        user = nickFormat(user)
        print '[' + str(time.strftime("%I:%M:%S")) + ']' + " " + user + " " + \
              'has joined ' + self.factory.channel

    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel."""
        user = nickFormat(user)
        print '[' + str(time.strftime("%I:%M:%S")) + ']' + " " + user + " " + \
              'has left ' + self.factory.channel

    def userQuit(self, user, quitMessage):
        """Called when I see another user disconnect from the network."""
        user = nickFormat(user)
        print '[' + str(time.strftime("%I:%M:%S")) + ']' + " " + user + " " + \
              'has quit for the reason: ' + quitMessage

    def kickedFrom(self, channel, kicker, message):
        kicker = nickFormat(user)
        print '[' + str(time.strftime("%I:%M:%S")) + ']' + " " + "I got kicked from " + \
              self.factory.channel + " " + "by " + kicker + " " + message
    

# this class creates instances of the bot
class ZeroBotFactory(protocol.ClientFactory):

    protocol = ZeroBot
    
    def __init__(self, channel, nickname="botster"):
        self.channel = channel
        self.nickname = nickname
       

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        """ Called when connection failed """
        print "connection failed:", reason
        reactor.stop()
        


if __name__ == '__main__':
    if argdict['filename'] != None:
        logfile = argdict['filename']
        log.startLogging(open(logfile, 'a'))
    reactor.connectSSL(irc_server, port, ZeroBotFactory(channel), ssl.ClientContextFactory())
    reactor.run()



