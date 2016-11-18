# Legobot

[![PyPI](https://img.shields.io/pypi/pyversions/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/wheel/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/l/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/status/Django.svg?maxAge=2592000)]()

#### Build Status

| Master | Develop | 
|--------|---------|
| [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=master)](https://travis-ci.org/bbriggs/Legobot) | [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=develop)](https://travis-ci.org/bbriggs/Legobot)

### Table of Contents

1. Installation
2. Alternative (easier) install and run method

***

## Introduction

Legobot is a platform that aims to make interactive multi-protocol bots less of a chore and more of a simple pleasure. 

Legobot itself is: 
* a skeleton framework to be built upon 
* a multi-protocol API for bots (soon to include XMPP, Slack, Hipchat, etc.)
* a basic set of functions for managing connections and message objects
* extensible (easily)

Legobot is not:
* complete
* an IRC bot (it's bigger than all of us, Jim)
* an Apple product
* a Microsoft product
* made of LEGOS (yet...)

Currently, Legobot is "batteries included" when being used as an IRC bot; Legobot comes with connectors (Legos) and functions that make development for IRC simple. More protocols are on the roadmap for future builds, and would be quick and simple to develop. 

***

### Installation

Installation is quite simple. Since we are on python3, just run `pip3 install Legobot`. You can also easily install this as a non-privileged user by running `pip3 install --user Legobot` instead.

### Alternative installation

For things like Legobot, Docker might just be the greatest thing since sliced bread. If you want to run Legobot without installing the library on your host, you can always use a Virtualenv (gross) or use docker (fun!)

Here is the docker run command I've been using lately for my own instances: `docker run -d -it --name Legobot -v "$PWD":/usr/src/legobot -w /usr/src/legobot python:3 sh -c 'pip install -r requirements.txt && python chatbot.py'`

This of course assumes that you called your script "chatbot" and that you want to name the container 'Legobot', but I think you get the picture. It's easy to run in a Docker container and you can run multiple instances with possible conflicting libraries without having to set up a virtual env or pollute your host machine. 

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

# This is a local, user-developed lego
from Local import Roll

# Initialize lock and baseplate
lock = threading.Lock()
master = Lego.start(None, lock)
master_proxy = master.proxy()

# Add children
master_proxy.add_child(IRC,
                          channel='#freenode',
                          nickname='legobot',
                          server='chat.freenode.net',
baseplate_proxy.add_child(Roll)
baseplate_proxy.add_child(Help)
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

For a deeper dive into how Legobot works, see our [documentation](docs/into.md)
