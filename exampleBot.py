#!/bin/python
import Legobot

#All functions need to accept the message object as input

#simple function that simply prints hello world when called
def example(msgObj):
	return "hello World", ""

#slightly more complex def that prints back to the user whatever it gets passed
def example2(msgObj):
  if msgClass.arg1:
    return "you told me to say: %s" % msgClass.arg1, "kmccabe2"
  else:
    return "you didn't tell me anything to say", "kmccabe2"

def myLogger(msgObj):
  #print "line from IRC: %s" % msgClass.splitMessage
  pass

if __name__ == '__main__':
  #parameters needed to allow bot to connect to IRC room:
  host = "your.irc.server"
  port = 6667
  nick = "mybot"
  room = ["#social","#test"] #Must be list, even for one item

  #create bot object
  myBot = Legobot.legoBot(host,port,nick,room,myLogger)
  
  #add the functions manually to the bot
  #first param is the trigger, second is the name of the function to run on match
  myBot.addFcns("!hello", example)
  myBot.addFcns("!test", example2)

  #have bot connect to IRC server and log into room(s) specified
  myBot.connect()