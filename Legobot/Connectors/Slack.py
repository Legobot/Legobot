# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

'''
.. module:: Legobot.Connectors.Slack
  :synopsis: A backend for connecting Legobot to Slack

.. moduleauthor:: Bren Briggs

Module lovingly built with inspiration from slackhq's RtmBot
'''

import logging
import sys
import threading
import time

from slackclient import SlackClient

from Legobot.Lego import Lego
from Legobot.Message import Message, Metadata
from Legobot.Utilities import Utilities

logger = logging.getLogger(__name__)

# I forgot why this is here, but it's very necessary.
sys.dont_write_bytecode = True


class RtmBot(threading.Thread, object):
    """
    Creates a Slack bot using the Slackclient RTM API

    Attributes:
        baseplate: The parent pykka actor
        token: The Slack API token
        last_ping: Timestamp of last keepalive ping
        actor_urn: URN of the Pykka actor the RtmBot runs in
        supported_events: dict of Slack RTM API events we care about
        slack_client: initialized RTM client
    """

    def __init__(self, baseplate, token, actor_urn, reconnect=True,
                 *args, **kwargs):
        """Initializes RtmBot

        Args:
            baseplate (Legobot.Lego): The parent Pykka actor.
                Typically passed in fromLegobot.Connectors.Slack.Slack
            token (string): Slack API token
            actor_urn (string): URN of Pykka actor launching RtmBot
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Returns an instance of RtmBot which connects to Slack.
        """
        self.baseplate = baseplate
        self.token = token
        self.last_ping = 0
        self.actor_urn = actor_urn
        self.reconnect = reconnect
        self.auto_reconnect = True
        # 'event':'method'
        self.supported_events = {'message': self.on_message}
        self.slack_client = SlackClient(self.token)
        threading.Thread.__init__(self)

    def connect(self):
        self.slack_client.rtm_connect(reconnect=self.reconnect,
                                      auto_reconnect=self.auto_reconnect)

    def on_message(self, event):
        '''Runs when a message event is received

        Args:
            event: RTM API event.

        Returns:
            Legobot.messge
        '''
        metadata = self._parse_metadata(event)
        message = Message(text=metadata['text'],
                          metadata=metadata).__dict__
        return message

    def run(self):
        '''Extends the run() method of threading.Thread
        '''

        self.connect()
        while True:
            for event in self.slack_client.rtm_read():
                logger.debug(event)
                if 'type' in event and event['type'] in self.supported_events:
                    event_type = event['type']
                    dispatcher = self.supported_events[event_type]
                    message = dispatcher(event)
                    logger.debug(message)
                    self.baseplate.tell(message)
            self.keepalive()
            time.sleep(0.1)
        return

    def get_users(self):
        '''Grabs all users in the slack team

        Returns:
            dict: Dict of users in Slack team.
                See also: https://api.slack.com/methods/users.list
        '''
        return self.slack_client.api_call('users.list')

    def get_dm_channel(self, userid):
        '''Perform a lookup of users to resolve a userid to a DM channel

        Args:
            userid (string): Slack userid to lookup.

        Returns:
            string: DM channel ID of user
        '''

        dm_open = self.slack_client.api_call('im.open', user=userid)
        return dm_open['channel']['id']

    def get_username(self, userid):
        '''Perform a lookup of users to resolve a userid to a username

        Args:
            userid (string): Slack userid to lookup.

        Returns:
            string: Human-friendly name of the user
        '''

        for member in self.get_users()['members']:
            if member['id'] == userid:
                return member['name']

    def get_userid_from_botid(self, botid):
        '''Perform a lookup of bots.info to resolve a botid to a userid

        Args:
            botid (string): Slack botid to lookup.
        Returns:
            string: userid value
        '''
        botinfo = self.slack_client.api_call('bots.info', bot=botid)
        if botinfo['ok'] is True:
            return botinfo['bot']['user_id']
        else:
            return botid

    def _parse_metadata(self, message):
        '''Parse incoming messages to build metadata dict
        Lots of 'if' statements. It sucks, I know.

        Args:
            message (dict): JSON dump of message sent from Slack

        Returns:
            Legobot.Metadata
        '''

        # Try to handle all the fields of events we care about.
        metadata = Metadata(source=self.actor_urn).__dict__
        if 'presence' in message:
            metadata['presence'] = message['presence']

        if 'text' in message:
            metadata['text'] = message['text']
        elif 'previous_message' in message:
            # Try to handle slack links
            if 'text' in message['previous_message']:
                metadata['text'] = message['previous_message']['text']
            else:
                metadata['text'] = None
        else:
            metadata['text'] = None

        if 'user' in message:
            metadata['source_user'] = message['user']
        elif 'bot_id' in message:
            metadata['source_user'] = self.get_userid_from_botid(
                                      message['bot_id'])
        elif 'message' in message and 'user' in message['message']:
            metadata['source_user'] = message['message']['user']
        else:
            metadata['source_user'] = None

        metadata['user_id'] = metadata['source_user']
        metadata['display_name'] = self.get_username(metadata['source_user'])

        if 'channel' in message:
            metadata['source_channel'] = message['channel']
            # Slack starts DM channel IDs with "D"
            if message['channel'].startswith('D'):
                metadata['is_private_message'] = True
            else:
                metadata['is_private_message'] = False

        metadata['source_connector'] = 'slack'

        return metadata

    def keepalive(self):
        '''Sends a keepalive to Slack
        '''
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now


class Slack(Lego):
    '''Lego that builds and connects Legobot.Connectors.Slack.RtmBot

    Args:
        baseplate (Legobot.Lego): baseplate/parent lego (Pykka Actor)
        lock (threading.Lock: thread lock created in your bot script.
            All legos should share the same lock.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    '''

    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = RtmBot(baseplate, actor_urn=self.actor_urn,
                                *args, **kwargs)

    def on_start(self):
        '''Extends pykka's on_start method to launch this as an actor
        '''

        self.botThread.start()

    def listening_for(self, message):
        '''Describe what this should listen for (hint: everything)
        Extends Legobot.Lego.listening_for()

        Args:
            message (Legobot.Message): Message to handle

        Returns:
            bool: True if lego is interested in the message.
        '''

        return str(self.botThread) != str(message['metadata']['source'])

    def handle(self, message):
        '''Attempts to send a message to the specified destination in Slack.
        Extends Legobot.Lego.handle()

        Args:
            message (Legobot.Message): message w/ metadata to send.
        '''

        logger.debug(message)
        if Utilities.isNotEmpty(message['metadata']['opts']):
            target = message['metadata']['opts']['target']
            if target.startswith('U'):
                target = self.botThread.get_dm_channel(target)
            self.botThread.slack_client.rtm_send_message(target,
                                                         message['text'])

    @staticmethod
    def get_name():
        '''Called by built-in !help lego
        Returns name of Lego. Returns none because this is
        a non-interactive Lego
        '''

        return None
