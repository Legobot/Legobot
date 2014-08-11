#!/bin/python
import Legobot
import time
import sys

__author__ = "Bren Briggs and Kevin McCabe"
__copyright__ = "Copyright 2014"
__license__ = "GPL"
__version__ = "0.1"
__status__ = "Development"

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


def test(msgObj):
    time.sleep(5)
    return "testing long wait", ""

def myTimerFunc():
    return "testing hello world"

def main():
    #parameters needed to allow bot to connect to IRC room:
    host = "irc.cisco.com"
    hostpw = ""
    port = 6667
    nick = "EvilMrCase"
    room = [("#dcn-dev","")] #Must be a list of tuples, even for one item.  tuple is like ("roomname","roompw") if you don't have a password, just pass a blank string
    #isSSL = True

    #create bot object
    myBot = Legobot.legoBot(host,port,nick,room,myLogger,hostpw)

    #to-do: test with SSL (OpenSSL and GnuTLS)

    #add the functions manually to the bot
    #first param is the trigger, second is the name of the function to run on match
    myBot.addFunc("!hello", test)
    myBot.addFunc("!test", example2)
    myBot.addTimerFunc(myTimerFunc, sec = "*/20")
    
    #have bot connect to IRC server and log into room(s) specified
    myBot.connect()

if __name__ == '__main__':
    main()