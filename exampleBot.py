#!/bin/python
import Legobot
import time
import sys

__author__ = "Bren Briggs and Kevin McCabe"
__copyright__ = "Copyright 2014"
__license__ = "GPL"
__version__ = "0.1"
__status__ = "Development"

##########################################################################################
#
# All Functions LegoBot will use go below
#
##########################################################################################

#All functions need to accept the message object as input

#simple function that simply prints hello world when called
def example(msgObj):
    return "hello World", ""

#slightly more complex def that prints back to the channel whatever it gets passed
def example2(msgObj):
    if msgObj.arg1:
        return "you told me to say: %s" % msgObj.arg1, ""
    else:
        return "you didn't tell me anything to say", ""

def myLogger(msgObj):
    #print "line from IRC: %s" % msgClass.splitMessage
    pass

def myRandomTimer():
    return "print this randomly!"

def test(msgObj):
    time.sleep(5)
    return "testing long wait", ""

def myTimerFunc():
    return "testing hello world"


##########################################################################################
#
# All config for your bot should be done in main()
#
##########################################################################################

def main():
    #parameters needed to allow bot to connect to IRC room:
    host = "irc.example.com"    #hostname we want to connect to, must be resolvable
    hostpw = ""                 #password for IRC server if needed
    port = 6667                 #port to connect on, standard IRC is typically 6667, SSL IRC is 6697
    nick = "examplebot"         #nick for bot
    room = [("#example","")]    #Rooms we wish the bot to join, Must be a list of tuples, even for one item.  tuple has items ("roomname","roompw") if you don't have a password, just pass a blank string
    isSSL = False               #whether or not the bot will be connecting via SSL

    #create bot object, note the logging function option and hostpw are optional
    myBot = Legobot.legoBot(host, port, nick, room, myLogger, hostpw)

    #add functions manually to the bot
    
    #for addFunc, the first param is the trigger, second is the name of the function to run on match
    myBot.addFunc("!hello", test, "This is a test function, it will sleep for 5 seconds and then return some text, takes no args. Usage !test")
    myBot.addFunc("!test", example2, "This is a hello world function and takes no args. Usage: !hello")
    
    #add in a bot that will run every 20 seconds, this func takes cron like options
    myBot.addTimerFunc(myTimerFunc, sec = "*/20")
    
    #add a random function, inputs are (function, minimumSeconds, maximumSeconds) min/max seconds provides a boundary of time the randomizer runs in
    myBot.addRandTimerFunc(myRandomTimer, 60, 1800)
    
    #have bot connect to IRC server and log into room(s) specified
    myBot.connect(isSSL)

if __name__ == '__main__':
    main()