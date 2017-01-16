## Slack Connector

Using the slack connector is actually simpler than even the IRC one. It takes a single argument, `token`, which is the bot token provided for you when you create a bot from the slack cusomization and integration page.

The slack connector uses the slackclient library and the RTM API, which in turn relies on websockets to do its thing. As the slack connector is very new, it currently only supports a single event type, `message`. Metadata is the same as with IRC, meaning that there are channels, sending users, text, and all the same fields you're used to. In upcoming patches, the Slack connector will be extended to support more event types and pass those directly to the Legos.

### Known bugs:
- For some reason it doesn't matter what you named the stupid bot, it always shows up in chat as `bot`.
- If using a slack client, the bot responds just fine to direct messages. If you're on IRC, the bot responds to the slack client but not your IRC client. Go figure.
- At this time it doesn't check to see if it lost connection or attempt to reestablish connection.


Yes, I do plan to address all these bugs in future releases.


### Usage

```
from Legobot import Lego
from Legobot.Connectors.Slack import Slack

SLACK_TOKEN = 'sometokenyougotfromslack'

# As usual, all the Pykka stuff to get us initialized
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Now we add the slack connector
baseplate_proxy.add_child(Slack,SLACK_TOKEN)
```

See? That was easy. Don't need to tell it what team, what its name is, etc etc. Just remember that on Slack, bots cannot join channels on their own--they have to be invited. Therefore, remember to invite your new legobot companion into appropriate channels once it's up and running.
