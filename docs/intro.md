## Intro to Legobot

### Quickstart

Installing Legobot is pretty simple. Since it's written in Python 3, you'll want to use pip3 to install it: `pip3 install -U Legobot`

From there, you can build a simple bot in just a few lines: 

```python
# Libs to initialize the bot
import threading
from Legobot.Lego import Lego

# A few plugins
from Legobot.Connectors.IRC import IRC
from Legobot.Legos.Help import Help

# Create the "parent" lego that owns all the plugins
# This will get boiled down into a one-liner soon
lock = threading.Lock()
master = Lego.start(None, lock)
master_proxy = master.proxy()

# Add some functionality
master_proxy.add_child(IRC,
                          channels=['#social'],
                          nickname='mybot',
                          server='chat.freenode.net')
master_proxy.add_child(Help)
```

This one doesn't do much. It just connects to IRC and, should you ask, will tell you about other Legos that are plugged in (if there are any). In this case, since there aren't, it will just sit there. Doing nothing. Beacuse you gave it nothing to do. You monster.

### What is Leogbot?

Legobot is an engine/framework/magical mystery box for developing eaily developing chatbots. Written in python3 and driven by plugins (which we lovingly call Legos), this is a multi-protocol, extendable, lightweight framework. 

### How does it work?

By shamelessly taking advantage of Pykka, everything in Legobot is a plugin (or Lego, as mentioned above). Legobot connects to chat protocols by way of special Legos called Connectors. These Connectors are responsible for knowing how to communicate with their given protocol. Other legos don't need to know or care. 

Legos (that aren't connetors) simply have to handle a Message and `reply()` to it as they see fit (or not reply. Whatever. It's your lego, dude.) Legos don't need to be aware of the ins and outs of each protocol, just how to respond to incoming text and occasionally metadata. The result is that a Lego can respond equally well to messages inbound from IRC, Slack, XMPP, or more so long as the connectors are properly built.

### Principles

- Flexible
- Multi-protocol
- Powered by plugins
- Simple API
- Small

Our vision for Legobot is to keep the codebase small, the dependency count low, the API simple, and the protocol-specific crut abstracted out of plugins.

#### Multi-protocol

Because the primary object each Lego consumes is a Message, any connector for any protocol can in theory produce one. The connectors are responsible for interfacing with the protocol and handing the specifics of maintaining that connection as well as sending and receiving data. As a message is received, a connector packages it up as a Message with corresponding metadata and forwards it up to the master/parent. Therefore, any properly written connector can produce a message that any Lego can consume, regardless of protocol.

#### Powered by plugins

In Legobot, every bit of functionality is a plugin. Everything, connectors and functions alike, are all plugins. Some are shipped with Legobot (such as the IRC connector and the Help lego), but many will be written by and for the end user, which is the whole point. If the Lego that you want to use is already published as a library on PyPi, just `pip install` it and `import` it! If not, my favorite way to add local Legos is to add a `Local/` directory wherever my bot script is located and then toss my homegrown legos in there.

#### Simple API

In our quest to put a powerful bot in the hands of every script kiddie on Earth, we have decided to make the API as simple as possible. This means that you won't have to spend hours reading docs, outputs will be predictable (as will inputs), and most of the time your Lego will simply need to do a `reply()` with the what you want to say in order to talk back to someone. 

#### Flexible

Should you find that the API is missing what you need or that the base classes (like Lego or Message) are lacking functionality you require, it will be easy to extend and override them. 

We also believe that while it should be easy to use a single method to do a job, it should also be easy to have full view and control over the entire message, connector, or bot behavior itself.

#### Small

Legobot is focused on doing just one thing: Being the engine and framework for plugins that allow people to connect their desired functionality into a chat protocol. To that end, we vow to keep the codebase as small as possible. This includes dependencies.

