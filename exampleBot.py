#!/bin/python
import Legobot

#simple def that simply prints hello world when called
def fcnsTest(msgClass):
	return "hello World", ""

#slightly more complex def that prints back to the user whatever it gets passed
def fcnsTest2(msgClass):
  if msgClass.arg1:
    return "you told me to say: %s" % msgClass.arg1, "kmccabe2"
  else:
    return "you didn't tell me anything to say", "kmccabe2"


if __name__ == '__main__':
  #parameters needed to allow bot to connect to IRC room:
  host = "your.irc.server"
  port = 6667
  nick = "mybot"
  room = ["#room-a","#room-b"]

  #create bot object
  myBot = Legobot.Listener(host,port,nick,room)
  
  #add the functions manually to the bot
  myBot.addFcns("!hello", fcnsTest)
  myBot.addFcns("!test", fcnsTest2)

  #have bot connect to IRC server and log into room specified
  myBot.connect()

  #have bot listen to incoming messages. This is required, because he needs to respond to pings to stay alive
  myBot.listen()

