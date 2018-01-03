# Legobot
[![Travis CI](https://travis-ci.org/Legobot/Legobot.svg?branch=master)](https://travis-ci.org/Legobot/Legobot)
[![PyPI](https://img.shields.io/pypi/pyversions/Legobot.svg)](https://pypi.python.org/pypi/Legobot/)
[![PyPI](https://img.shields.io/pypi/l/Legobot.svg)](https://pypi.python.org/pypi/Legobot/)
[![PyPI](https://img.shields.io/pypi/v/Legobot.svg)](https://pypi.python.org/pypi/Legobot/)
[![PyPI](https://img.shields.io/pypi/status/Legobot.svg)](https://pypi.python.org/pypi/Legobot/)
[![PyPI](https://img.shields.io/pypi/wheel/Legobot.svg)](https://pypi.python.org/pypi/Legobot/)

### Table of Contents

1. [Introduction](#introduction)
1. [Supported Backends](#supported-backends)
1. [Installation](#installation)
1. [Alternative (easier) install and run method](#alternative-installation)
1. [Contributing](#contributing)

## Introduction

Legobot is a platform that aims to make interactive multi-protocol bots less of a chore and more of a simple pleasure. 

Legobot itself is: 
* a skeleton framework to be built upon 
* a multi-protocol API for bots
* a basic set of functions for managing connections and message objects
* extensible (easily)

### Supported backends 
_in planned order for support_
- [x] IRC
- [x] Slack
- [x] Discord (beta)
- [ ] XMPP
- [ ] Telegram
- [ ] FB Messenger
- [ ] Cisco Spark

### Installation

Installation is quite simple. Since we are on python3, just run `pip3 install Legobot`. You can also easily install this as a non-privileged user by running `pip3 install --user Legobot` instead.

### Alternative installation

For things like Legobot, Docker might just be the greatest thing since sliced bread. If you want to run Legobot without installing the library on your host, you can always use a Virtualenv (gross) or use docker (fun!)

Here is the docker run command I've been using lately for my own instances: `docker run -d -it --name Legobot -v "$PWD":/usr/src/legobot -w /usr/src/legobot python:3 sh -c 'pip install -r requirements.txt && python chatbot.py'`.

This of course assumes a couple things:
 - You called your script "chatbot"
 - You want to name the container "Legobot"
 - You are in the Legobot same directory as your chatbot script when running the command
 
But I think you get the picture. It's easy to run in a Docker container and you can run multiple instances with possible conflicting libraries without having to set up a virtual env or pollute your host machine. 

### Connecting to IRC

Legobot is intended to be simple, flexible, and painless; thereby allowing the user to control all functionality. Consequently, Legobot doesn't really *do* much on its own, other than monitor messages and manage connections. All triggers, responses, and functions are yours to create: this could range from an automated function to report Nginx monitoring info at a set interval, to a function for checking the weather, to a function that simply states "Hello, World!". The possibilities are endless, only bound by your imagination (and will to create). 

An example of a basic bot that is functional (connects to server, etc.) might look like this:

```python
import logging
import threading
from Legobot.Lego import Lego
from Legobot.Connectors import *

from Legobot.Legos.Help import Help
from Legobot.Connectors.IRC import IRC

# Another lego available on PyPi
from legos.dice import Roll

# Initialize lock and baseplate
lock = threading.Lock()
master = Lego.start(None, lock)
master_proxy = master.proxy()

# Add children
master_proxy.add_child(IRC,
                          channels=['#freenode'],
                          nickname='legobot',
                          server='chat.freenode.net')
master_proxy.add_child(Roll)
master_proxy.add_child(Help)
```
For the above example, we implemented the !roll Lego. Now, to see this in action!

```
<parsec> !help
<legobot> Available functions: roll
<parsec> !help roll
<legobot> Roll some dice. Usage: !roll 2d6t, !roll 6d6^3, !roll d20
<parsec> !roll 2d10
<legobot> You Rolled: 7, 3
<parsec> !roll d20
<legobot> You Rolled: 2
```

For a deeper dive into how Legobot works, see our [documentation](docs/intro.md)

### Contributing

We hang out and do our dev chat on the [0x00sec IRC](http://irc.0x00sec.org/) in `#legobot`. Drop by and say hey!

TO DO: Expand contributing docs
