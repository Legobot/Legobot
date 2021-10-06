# Connecting to Slack
1. Create a Slack app. Click [here](https://api.slack.com/apps?new_app=1)
to go to the new app page.
2. Configure your app's name and the workspace it will live in
3. Create a token for your bot
   After you configure the bot it should drop you at the "Basic Information"
   page. Click "Bot" and it'll jump to the App Home page where you can define
   the bot's scope and get a token. Legobot's scope is largely up to you, however
   at a minimum you'll want `channel:history`, `channel:read`,
   `chat:write` to give Legobot a minimal amount of interactability.
4. Go to "Install App" on the sidebar and then click "Install to Workspace".
   Legobot isn't setup for multi-workspace / OAuth, so we just can skip that
   stuff and go right to collecting our token.
5. Setup a basic `config.yaml` file and put the token in it.
   Here is a mimumal example config:
   ```yaml
connectors:
  Slack:
    enabled: true
    path: Legobot.Connectors.Slack.Slack
    kwargs:
      token: TOKEN-SECRET-GOES-HERE-1337
helpEnabled: true
legos:
  TestingConnector:
    enabled: true
    path: legos.TestingConnector
   ```
6. Setup a basic `chatbot.py` file and put the token in it.
   Here is a mimumal example:
   ```python
   from pathlib import Path
   from Legobot.Chatbot import Chatbot
   bot = Chatbot(Path(__file__).resolve().parent.joinpath('config.yaml'))
   bot.run()
   ```
7. Start the chatbot with `python chatbot.py`, you should see some init logs and then it ought to connect. You can test by going to your workspace, inviting your bot to a channel, and then watching as it echos everything you say.

Enjoy!
