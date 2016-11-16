## Writing a Lego

### Intro

Legos are the most fundamental concept when working with Legobot. They are classes that function like individual, largely independent plugins. A Legobot instance (even how it talks to various chat protocols!) is simply a collection of Legos. 

Some things to remember:
 - Legos inherit from the Lego class. As such, we try to provide as many helpful things as we can without getting in your way.
 - The more protocol independent you make your Lego, the better. Remember, the aim is to write what matters, not spend your time in the weeds fighting a protocol.
 - Simplicity is valuable, but Legos can be incredibly powerful and flexible. They're fully functional Python scripts that can do whatever you need them to do.

### Bare minimum

At a minimum, your Lego needs to be a class that inherits from the `Lego` class and it should have two functions: `listening_for()` and `handle()`. Optionally (and we recommend it), you can include the `get_name` and `get_help` methods that our built-in `!help` lego will use. 

#### `listening_for`

This method alerts the master/parent that you are interested in whatever message is being boadcast. It takes the whole message, metadata included, as input and returns True if interested. Example of checking for just `!helloworld` at the beginning of the message:

```python
def listening_for(self, message):
    return message['text'].split()[0] == '!helloworld'
```

In the above example, we split the incoming message (what a person actually said) on spaces and return true if the first word was `!helloworld`. 

Given that you have the entire message at your disposal, you can match on incoming protocol, channels, who spoke, time since last message, a regex within the message, or more. All that matters is that you return a value of `True` if you want the lego to activate as a result of the message.


#### `handle`

Like the previous method, handle() takes only `self` and `message` as inputs. This is where the actual work of parsing and reacting to the message will take place. Also like `listening_for`, this method gets called automatically when the conditions are met. In this case, it is when `listening_for` returns `True`.

Since nothing consumes this method, it is not useful to return anything. Instead, you use the built-in `reply` method to route your message back to where it came from. Since the Lego that you are replying to must know where to send your message (ie, which IRC or Slack channel it goes to), you have to set that option in the metadata like so:

```python
def handle(self, message):
  target = message['metadata']['source_channel']
  opts = {'target':target}
  self.reply(message,"Hello, world!", opts)
```

This setup allows us a few advantages: 
1. Many instances of the same lego can run in parallel
1. A lego can send multiple responses using self.reply()
1. A lego can set any arbitrary metadata and send it back. For instance, messages received in one channel can be responded to on another or control messages can be sent between Legos to communite things that may not need to be said in the chat channels.

#### `get_name`

This may be the simplest of the functions in the skeleton. Simply return the name you want displayed when our built-in Help lego polls it.

```python
def get_name(self):
    return "helloworld"
```

#### `get_help`

Likewise, this is quite simple. Return a string with some information on how to use your lego. 

```python
def get_help(self):
    return "Say hello! Usage: !helloworld"
```

### Putting it all together

```python
from Legobot.Lego import Lego

class HelloWorld(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!helloworld'

    def handle(self, message):
        try:
            target = message['metadata']['source_channel']
            opts = {'target':target}
        except IndexError:
            logger.error('Could not identify message source in message: %s' % str(message))
        self.reply(message, "Hello, world!", opts)

    def get_name(self):
        return 'helloworld'

    def get_help(self):
        help_text = "Say hello! Usage: !helloworld"
        return help_text
```
