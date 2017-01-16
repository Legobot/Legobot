'''
.. module:: Legobot.Connectors.Slack
  :synopsis: A backend for connecting Legobot to Slack

.. moduleauthor:: Bren Briggs

Module lovingly built with inspiration from slackhq's RtmBot
'''
import sys
import time
import logging
import threading

from slackclient import SlackClient

from Legobot.Message import Message, Metadata
from Legobot.Lego import Lego

logger = logging.getLogger(__name__)

sys.dont_write_bytecode = True


class RtmBot(threading.Thread, object):
    '''
    Create slack bot instance using SlackClient
    '''

    def __init__(self, baseplate, token, *args, **kwargs):
        '''
        Initialize the bot.

        :param baseplate: The baseplate/parent lego. Typically passed in from
        Legobot.Connectors.Slack.Slack

        :param token: The Slack API token you generated
        :param args: Reserved for future use
        :param kwargs: Reserved for future use
        '''
        self.baseplate = baseplate
        self.token = token
        self.last_ping = 0
        # 'event':'method'
        self.supported_events = {'message': self.on_message}
        self.slack_client = SlackClient(self.token)
        threading.Thread.__init__(self)

    def connect(self):
        '''
        Initialize connection to slack.
        :return: None
        '''

        self.slack_client.rtm_connect()

    def on_message(self, event):
        '''
        Runs when a message event is received
        :return: Legobot.Message
        '''
        metadata = self._parse_metadata(event)
        message = Message(text=event['text'],
                          metadata=metadata).__dict__
        return message

    def run(self):
        '''
        Extends the run() method of threading.Thread

        :return: None
        '''

        self.connect()
        while True:
            for event in self.slack_client.rtm_read():
                logger.debug(event)
                if event['type'] in self.supported_events:
                    event_type = event['type']
                    dispatcher = self.supported_events[event_type]
                    message = dispatcher(event)
                    logger.debug(message)
                    self.baseplate.tell(message)
            self.keepalive()
            time.sleep(0.1)
        return

    def _parse_metadata(self, message):
        '''
        Parse incoming messages to build metadata dict

        Lots of 'if' statements. It sucks, I know.

        :param message: Message dict sent from Slack

        :return: dict
        '''

        # Try to handle all the fields of events we care about.
        metadata = Metadata(source=self).__dict__
        if 'presence' in metadata:
            metadata['presence'] = message['presence']
        if 'text' in metadata:
            metadata['text'] = message['text']

        if 'user' in message:
            metadata['source_user'] = message['user']
        elif 'bot_id' in message:
            metadata['source_user'] = message['bot_id']

        if 'channel' in message:
            metadata['source_channel'] = message['channel']
            # Slack starts DM channel IDs with "D"
            if message['channel'].startswith('D'):
                metadata['is_private_message'] = True
            else:
                metadata['is_private_message'] = False

        return metadata

    def keepalive(self):
        '''
        Sends a keepalive to Slack
        '''
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now


class Slack(Lego):
    '''
    Lego that builds and connects Legobot.Connectors.Slack.RtmBot

    :param baseplate: baseplate/parent lego. Typically created in your bot
    script

    :param lock: thread lock created in your bot script. All legos should
    share the same lock

    :param args: args to pass into RtmBot (like token)

    :param kwargs: keyword args to pass to RtmBot
    '''

    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = RtmBot(baseplate, *args, **kwargs)

    def on_start(self):
        '''
        Extends pykka's on_start method to launch this as an actor
        '''

        self.botThread.start()

    def listening_for(self, message):
        '''
        Describe what this should listen for (hint: everything)
        Extends Legobot.Lego.listening_for()
        '''

        return str(self.botThread) != str(message['metadata']['source'])

    def handle(self, message):
        '''
        Describe how this lego should handle messages.
        Extends Legobot.Lego.handle()
        '''

        logger.info(message)
        self.botThread.slack_client.api_call(
            "chat.postMessage",
            channel=message['metadata']['opts']['target'],
            text=message['text']
        )

    def get_name(self):
        '''
        Called by built-in !help lego

        Returns name of Lego. Returns none because this is
        a non-interactive Lego

        :return: None
        '''

        return None
