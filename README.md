# Legobot

#### Table of Contents

1. [Usage](#usage)
2. [Installation](#installation)
3. [API Details](#api-details)
    * [Legobot](#legobot-class)
    * [The Message Object](#message)
4. [How to contribute](#how-to-contribute)
5. [Copyright](#copyright)

## Introduction
Legobot is an API around IRC to make interactive bots easy to build. The bot provides connectivity and the ability to listen and respond to users. 

## Usage

Legobot is intended to be simple in usage, flexible, and allow the user to drive all functionality. Therefore it is a given that it doesn't do much on its own outside of managing the IRC connection and watching conversations. Any triggers and responses are yours to build. 

Legobot's primary functionality centers around a few methods:

First, let's initialize our bot:

```python
import Legobot
HOST = 'irc.freenode.com'
PORT = 6667
NICK = 'legobot'
CHANS = [('#freenoode',''),('#bitcoin',''),('#legobot','')] #List of tuples. Format is (channel,password)
myBot = Legobot.legoBot(host=HOST,port=PORT,nick=NICK,chans=CHANS)
```

#### Great, now what?

Write a function, add it to Legobot, then connect!

```python
def helloWorld(msg):
    return "Hello, world!"

myBot.addFunc("!helloworld", helloWorld, "Ask your bot to say hello. Usage: !helloworld")
mybot.connect(isSSL=False)
```

Then watch your creation come to life:

```
<bbriggs> !helloworld
<legobot> Hello, world!
<bbriggs> !help
<legobot> Available functions: !helloworld, !help
<bbriggs> !help !helloworld
<legobot> Ask your bot to say hello. Usage: !helloworld
```

Congratulations, you just wrote an IRC bot!

## API details

### Legobot class

#### Legobot.legobot()

`Legobot.legobot(host,port,nick,chans, logfunc = "", hostpw = "", defaultFunc = None, defaultFuncChar = "")`

*Parameters:*

**host** _String._ IRC host to connect to.

**port** _Int._ IRCd port to connect to.

**nick** _String._ Nickname you want your bot to use. Also sets realname value in IRC. 

**chans** _List._ This is actually a list of tuples in the form of (channel,channel_password). Example: [('#admins'),('supersecretpassword'),('#social','')]

**logfunc** _Function.__ Function object (without parens). Instead of writing output to stdout, send output from Legobot as input to logfunc. Implements a custom logging within Legobot. 

**hostpw** _String._ Password for the IRCd, if necessary.

**defaultFunc** _Function.__ Function object (without parens). Supply a fallback function to trigger if your users ask for a function that doesn't exist. 

#### Legobot.addFunc()

`addFunc(self, name, function, helpText = "")`

*Parameters:*

**name** _String._ The word you want to trigger the function. Legobot only considers the first word in a message for this. Example: if name="!helloworld" and you say "!helloworld" in IRC, that will trigger the function. However, "will !helloworld work?" will not trigger the function.

**function** _Function._ Function object (without parens). It's usually helpful to name the function the same as the trigger. This is the function that gets called when the trigger word in the `name` parameter is seen.

**helpText** _String._ Describe in a few words what this function does. Gets displayed when user requests `!help !yourfunction` in IRC. 

#### `addDefaultFunc(self, func, char)`

*Parameters:*

**func** _Function._ Function object (without parens). Set the default, fallback function to trigger when users spam nonsense that starts with your trigger character. ie, `!xyzzy` could trigger `!help`. If you're not in the mood to be helpful, why not insult your users for being silly?

**char** _String._ Single character to serve as a trigger to let Legobot know we're talking to it. Example: setting `char` to `'!'` and just saying `!` in chat would trigger the default function. 

#### `connect(self, isSSL=False)`

*Parameters*

**isSSL** _Boolean._ Use SSL when connecting to the IRCd host

#### `sendMsg(self, msgToSend)`

*Parameters:*

**msgToSend** _String._ Line to send to IRC channel. 

### Message 

*Parameters:*

None.

Every line that comes in from the IRC connection generates a `Message` object in Legobot which is then parsed by the bot. Messages where the `Message.cmd` property (discussed below) matches a trigger will run the corresponding function. Legobot then passes the message object to the newly triggered function as a parameter. Example:

```python
def cointoss(msg):
    """
    Inputs:
      takes msg object

    Outputs:
      returns string to echo back to user in IRC

    Purpose:
      flip an imaginary coin or roll an imaginary N-sided die
      Usage:
      !roll [# of sides]
    """

    if not msg.arg1:
        toss = random.randint(0,1)
        if toss == 0:
            returnVal = "Heads"
        else:
            returnVal = "Tails"
    else:
        if not is_num(msg.arg1):
            returnVal = "Incorrect syntax. You must use a (sane) number"
        elif is_num(msg.arg1) and not int(msg.arg1) >= 2:
            returnVal = "Use at least two sides, weirdo."
        elif is_num(msg.arg1) and int(msg.arg1) == 2:
            toss = random.randint(1,2)
            if toss == 1:
                returnVal = "Heads"
            else:
                returnVal = "Tails"
        else:
            toss = random.randint(1,int(msg.arg1))
            returnVal = str(toss)
    return returnVal
```

Note: If you want your function to reply back to the channel or user the bot receieved from, return a just a string. To respond or forward to a specific channel, return a tuple of two strings in the form (message,channel_or_user)

**Properties:**

`Message.fullMessage`, _String._ full, raw IRC line. 

`Message.splitMessage`, _String._ IRC line split on whitespaces, truncated to 7 items. The 7th item is all remaining text, if it exists.

`Message.length`, _String._ The value of `len(self.splitMessage)`

`Message.userInfo`, _String._ The nick, realname, and host (or hostmask) of the IRC user who sent the message.

`Message.actualUserName`, _String._ Realname of IRC the user who sent the message. 

`Message.target`, _String._ where the message was addressed. ie, channel or individual user. Used to detect if message sent was a private message. 

`Message.cmd`, _String._ First word in user's actual message. In 'Hello world!', Message.cmd is 'Hello'

`Message.arg1`, `arg2`, and `arg3`, _String._ Additional positional arguments to evaluate when parsing a triggered command. May or may not be present depending on the length of the input line. 

`Message.isPM`, _Boolean._ False if message was sent to whole #channel, True if sent to just the bot.  

## How to contribute

Issues and pull requests welcome. Please send PRs to the development branch. 

## Copyright

Legobot
Copyright (c) 2016 Bren Briggs and Kevin McCabe

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.