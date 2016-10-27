# Legobot
## Legobot is an ongoing project; currently, refactoring is taking place. If you wish to contribute, please do so in `develop`.

### Table of Contents

1. Installation
2. Connecting to IRC

***

## Introduction

Legobot is a platform that aims to make interactive IRC bots less of a chore and more of a simple pleasure. Legobot itself is a skeleton framework to be built upon; Legobot provides the basic connectivity and ability to listen to message object (called threads) and respond to users based on the content of the message. Legobot is extensible via writing simple functions called "Legos", which can be easily added, edited, modified, and removed based on the need. The bot provides an easy-to-use "message" object when needed, which eliminated the need to parse raw IRC strings; this allows faster, more efficient processing of message contents, and quicker response time. Currently, IRC is the bot's main function; however, the bot is easily extensible to work with other messaging applications, or whatever you might find a need for. Legobot itself is not an IRC bot, it is an extensible, easy to use bot framework for quick, painless deployment of different forms of chat bots (or other if you so choose). 

***

## Installation

Installation is quite simple. Just run `pip install Legobot`. You can also easily install this as a non-privileged user by running `pip install --user Legobot` instead (this is recommended).

## Connecting to IRC

Legobot is intended to be simple, flexible, and painless; thereby allowing the user to control all functionality. Consequently, Legobot doesn't really *do* much on its own, other than monitor IRC messages and manage connections. All triggers, responses, and functions are yours to create: this could range from an automated function to report Nginx monitoring info at a set interval, to a function for checking the weather, to a function that simply states "Hello, World!". The possibilities are endless, only bound by your imaginations (and will to create). 

To connect the bot to IRC, we must edit the config file. Here is an example using freenode:

```python
import Legobot
HOST = 'irc.freenode.com'
PORT = 6667
NICK = 'legobot'
CHANS = [('#freenoode', ''), ('#bitcoin', ''), ('#legobot', '')] # List of tuples. Format is (channel, password)
myBot = Legobot.legoBot(host=HOST, port=PORT, nick=NICK, nickpass="", chans=CHANS)
```

[![PyPI](https://img.shields.io/pypi/pyversions/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/wheel/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/l/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/status/Django.svg?maxAge=2592000)]()

#### Build Status

| Master | Develop | 
|--------|---------|
| [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=master)](https://travis-ci.org/bbriggs/Legobot) | [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=develop)](https://travis-ci.org/bbriggs/Legobot)
