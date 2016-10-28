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

To connect the bot to IRC, we must create the config file. To add a server here is an example using freenode:

```python
	channel='#freenode',
	nickname='legobot',
	server='irc.freenode.net',
	port=6697,
	use_ssl=True,
	username='legobot',
	password=

```

[![PyPI](https://img.shields.io/pypi/pyversions/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/wheel/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/l/Legobot.svg?maxAge=2592000)]() [![PyPI](https://img.shields.io/pypi/status/Django.svg?maxAge=2592000)]()

#### Build Status

| Master | Develop | 
|--------|---------|
| [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=master)](https://travis-ci.org/bbriggs/Legobot) | [![Build Status](https://travis-ci.org/bbriggs/Legobot.svg?branch=develop)](https://travis-ci.org/bbriggs/Legobot)
