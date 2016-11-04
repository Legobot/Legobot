# Legobot
## Legobot is an ongoing project; currently, refactoring is taking place. If you wish to contribute, please do so in `develop`.

### Table of Contents

1. Installation
2. Connecting to IRC

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

## Installation

Installation is quite simple. Just run `pip install Legobot`. You can also easily install this as a non-privileged user by running `pip install --user Legobot` instead (this is recommended).

## Connecting to IRC

Legobot is intended to be simple, flexible, and painless; thereby allowing the user to control all functionality. Consequently, Legobot doesn't really *do* much on its own, other than monitor messages and manage connections. All triggers, responses, and functions are yours to create: this could range from an automated function to report Nginx monitoring info at a set interval, to a function for checking the weather, to a function that simply states "Hello, World!". The possibilities are endless, only bound by your imagination (and will to create). 

An example of a basic bot that is functional (connects to server, etc.) might look like this:

```python
import logging
import threading
from Legobot.Lego import Lego
from Legobot.Connectors import *

from Legobot.Legos.Help import Help
from Legobot.Legos.Roll import Roll
from Legobot.Connectors.IRC import IRC

# Initialize lock and baseplate
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add children
baseplate_proxy.add_child(IRC,
                          channel='#freenode',
                          nickname='legobot',
                          server='irc.freenode.net',
                          port=6697,
                          use_ssl=True,
                          username=None,
                          password=None)
baseplate_proxy.add_child(Roll)
baseplate_proxy.add_child(Help)
```
For the above example, we implemented the !roll Lego.. Now, to see this in action!

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

## Development

**Information will be added as becomes relevant**

When developing and running the development server or installing locally, you must install the requirment. To run the development server, just use vagrant! First, make sure you are in the Legobot directory. Then:

```
sudo $YourDistroPackageManager $install vagrant
```

Then, you just run: 

```
vagrant up
```
And finally, to access the VM via SSH, you just do:

```
vagrant ssh
```

And now, you have access to the development server! `cd` into `/legobot` for a folder that syncs with your Legobot folder on your base machine. Now you have access to the code you've changed/added/created! To get Legobot ready to run, do `sudo pip3 install -r requirements.txt`, let pip3 do it's thing, then run `python3 Legobot.py` and viola! You now have a working dev server at localhost (127.0.0.1), where the bot should be in `#social`!

[![PyPI](https://img.shields.io/pypi/pyversions/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/wheel/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/l/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/status/Django.svg?maxAge=2592000)]()

#### Build Status

| Master | Develop | 
|--------|---------|
| [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=master)](https://travis-ci.org/bbriggs/Legobot) | [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=develop)](https://travis-ci.org/bbriggs/Legobot)
>>>>>>> develop
