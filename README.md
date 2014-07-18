#Legobot
=======
##Authors
Bren Briggs and Kevin McCabe developed this IRC Bot framework starting in late 2013.

##Introduction
Legobot is a python IRC bot framework.  The bot provides connectivity and the ability to listen and respond to users.

An example .py file exists for how to create a simple IRC Bot.

##Functions
###Logging function
This function gets called anytime we receive anything on our socket.  It gets passed a message object. Logging functions can't return anything to Legobot.

###FCNS Function
FCNS functions are associated with a calling parameter.  For example "!hello" could be the way to call a fcns, Legobot checks to see if a user puts any of those calling parameters at the beginning of their irc message.  It must be called at the beginning, eg: "!hello" would work "call !hello" would not.  FCNS functions MUST return a tuple, first value is the value to be returned back and sent to IRC, the other value is where the value should be sent. If the first value is blank, nothing will be printed (no blank line either), if the value exists, it should be of type string, although if it isn't a string casting will be attempted so lists and dicts should work as well.  If the second value is blank, the output will be sent to the same context which it received an input.  So if you sent your bot a message in #myroom, the bot will return the output back to #myroom.  If you PM the bot and the second message is blank, the output will be PM'd back.  You can also specify a username instead of a room for this value, meaning every output from that fcns would be sent to a user instead of the room.

##Message Object
Both the Logging function and FCNS's recieve must accept one and only one variable. It's a message object with these values that can be accessed:
splitMessage, this is a list of the incoming message which was delimited by spaces
length, len of splitMessage
userInfo, IRC user info for who sent the message, eg: :username!~username
actualUserName, an attempt to grab out the username from userInfo, should grab everything between the : and !
target, context this was sent to, either room name or user for PM's
cmd, this is the first word typed in the chat, typically this would be what command a user wants to run.  This is what Legobot will use to check against the calling parameters.

arg1, second word typed

arg2, third word typed

arg3, fourth word typed

If any of the above parameters do not exist, the value will contain None.

##Instantiating legoBot
###Required Parameters:
host, type string, server IP or FQDN eg: irc.example.com

port, type integer, port server is listening on

nick, type string, value you wish to use for the bot's nickname

room, type list of strings, rooms that you wish to join, at least one room required

###Optional Parameter:
loggingFcns type function, function you wish run on every line sent to IRC
 
##Utilizing LegoBot (Methods)
###connect
No inputs, after defining a legoBot object, you can use this to connect to the IRC room
		
###sendMsg
Raw string input, this method is used to send a message to the server.  Typically this shouldn't be used to provide output for users and should only be used if your fcns function needs to join a room or grab op or something.
		
###addFcns
input: name as string, this would be the command that users would run to call the fcns; fcns as function which is the function that will be run.
		
###batchAddFunc
input d ad dictionary; used to add a bunch of fcns's at the same time.  dictionary keys should be the string you want used to call your fcns and the value should be a fcns
		
