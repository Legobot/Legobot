from websocket import create_connection
import json
import logging
import requests
import sys
import threading
import time

from Legobot.Lego import Lego
from Legobot.Message import Message, Metadata
from Legobot.Utilities import Utilities

__author__ = "Bren Briggs (fraq)"
__copyright__ = "Copyright 2017, Legobot"

logger = logging.getLogger(__name__)


class Heartbeat(threading.Thread, object):
    """
    Manage heartbeat connection to Discord

    Attributes:
        ws: Websocket connection to Discord
        interval (float): time between heartbeat pings to the server

    """

    def __init__(self, ws, interval):
        self.ws = ws
        self.interval = float(interval) / 1000.0
        self.sequence = 0
        logger.debug("Heartbeat handler initialized \
                     with interval of {}".format(self.interval))
        threading.Thread.__init__(self)

    def send(self, ws, seq):
        """
        Sends heartbeat message to Discord

        Attributes:
            ws: Websocket connection to discord
            seq: Sequence number of heartbeat
        """

        payload = {'op': 1, 'd': seq}
        payload = json.dumps(payload)
        logger.debug("Sending heartbeat with payload {}".format(payload))
        ws.send(payload)
        return

    def update_sequence(self, seq):
        """

        Attributes:
            seq (int): Sequence number of heartbeat
        """

        self.sequence = seq
        logger.debug("Heartbeat sequence updated to {}".format(self.sequence))
        return

    def run(self):
        while True:
            self.send(self.ws, self.sequence)
            time.sleep(self.interval)


class DiscoBot(threading.Thread, object):
    """
    Relays messages between Discord and the Legobot baseplate.
    Uses the REST API and Websockets. No plans to use async.

    Attibutes:
        actor_urn: URN (unique ID) of actor that initialized the bot
        baseplate: Parent lego/actor
        headers: HTTP headers use for calls to Discord REST endpoints
        rest_baseurl: Base URL to the REST API
        token: Discord bot token
        ws: Websocket connected to Discord
    """

    def __init__(self, baseplate, token, actor_urn, *args, **kwargs):
        """
        Initialize DiscoBot

        Args:
            baseplate (Legobot.Lego): The parent Pykka actor.
                Typically passed in from Legobot.Connectors.Discord.Discord
            token (string): Discord bot token
            actor_urn (string): URN of Pykka actor launching DiscoBot
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """

        self.baseplate = baseplate
        self.rest_baseurl = 'https://discordapp.com/api/v6'
        self.token = token
        self.headers = {"Authorization": "Bot {}".format(token),
                        "User-Agent": "Legobot",
                        "Content-Type": "application/json"}
        self.actor_urn = actor_urn
        self.ws = None
        threading.Thread.__init__(self)

    def connect(self):
        return create_connection(self.get_ws_url())

    def create_message(self, channel_id, text):
        """
        Sends a message to a Discord channel or user via REST API

        Args:
            channel_id (string): ID of destingation Discord channel
            text (string): Content of message
        """

        baseurl = self.rest_baseurl + \
            '/channels/{}/messages'.format(channel_id)
        requests.post(baseurl,
                      headers=self.headers,
                      data=json.dumps({'content': text}))

    def identify(self, token):
        """
        Identifies to the websocket endpoint

        Args:
            token (string): Discord bot token
        """

        payload = {
            'op': 2,
            'd': {
                'token': self.token,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'legobot',
                    '$device': 'legobot'
                },
                'compress': False,
                'large_threshold': 250
            }
        }
        payload['d']['synced_guilds'] = []
        logger.info("Identifying with the following message: \
                    {}".format(payload))
        self.ws.send(json.dumps(payload))
        return

    def on_hello(self, message):
        """
        Runs on a hello event from websocket connection

        Args:
            message (dict): Full message from Discord websocket connection"
        """

        logger.info("Got a hello")
        self.identify(self.token)
        self.heartbeat_thread = Heartbeat(self.ws,
                                          message['d']['heartbeat_interval'])
        self.heartbeat_thread.start()
        return

    def on_heartbeat(self, message):
        """
        Runs on a heartbeat event from websocket connection

        Args:
            message (dict): Full message from Discord websocket connection"
        """

        logger.info("Got a heartbeat")
        logger.info("Heartbeat message: {}".format(message))
        self.heartbeat_thread.update_sequence(message['d'])
        return

    def on_message(self, message):
        """
        Runs on a create_message event from websocket connection

        Args:
            message (dict): Full message from Discord websocket connection"
        """

        if 'content' in message['d']:
            metadata = self._parse_metadata(message)
            message = Message(text=message['d']['content'],
                              metadata=metadata).__dict__
            logger.debug(message)
            self.baseplate.tell(message)

    def _parse_metadata(self, message):
        """
        Sets metadata in Legobot message

        Args:
            message (dict): Full message from Discord websocket connection"

        Returns:
            Legobot.Metadata
        """

        metadata = Metadata(source=self.actor_urn).__dict__
        if 'author' in message['d']:
            metadata['source_user'] = message['d']['author']['username']
        else:
            metadata['source_user'] = None
        if 'channel_id' in message['d']:
            metadata['source_channel'] = message['d']['channel_id']
        else:
            metadata['source_channel'] = None
        metadata['user_id'] = metadata['source_user']
        metadata['display_name'] = metadata['source_user']

        metadata['source_connector'] = 'discord'

        return metadata

    @staticmethod
    def get_ws_url():
        url = requests.get(
            'https://discordapp.com/api/v6/gateway').json()['url']
        return url + '?v=6&encoding=json'

    def handle(self, message):
        """
        Dispatches messages to appropriate handler based on opcode

        Args:
            message (dict): Full message from Discord websocket connection
        """

        opcode = message['op']
        if opcode == 10:
            self.on_hello(message)
        elif opcode == 11:
            self.on_heartbeat(message)
        elif opcode == 0:
            self.on_message(message)
        else:
            logger.debug("Not a message we handle: OPCODE {}".format(opcode))
        return

    def run(self):
        """
        Overrides run method of threading.Thread.
        Called by DiscoBot.start(), inherited from threading.Thread
        """

        self.ws = self.connect()
        while True:
            try:
                data = json.loads(self.ws.recv())
                self.handle(data)
            except json.decoder.JSONDecodeError as e:
                logger.fatal("No data on socket...")


class Discord(Lego):
    '''
    Lego that builds and connects Legobot.Connectors.Discord.DiscoBot

    Args:
        baseplate (Legobot.Lego): baseplate/parent lego (Pykka Actor)
        lock (threading.Lock: thread lock created in your bot script.
            All legos should share the same lock.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    '''

    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = DiscoBot(baseplate, actor_urn=self.actor_urn,
                                  *args, **kwargs)

    def on_start(self):
        '''
        Extends pykka's on_start method to launch this as an actor
        '''

        self.botThread.start()

    def listening_for(self, message):
        '''
        Describe what this should listen for
        (hint: everything not from ourself)
        Extends Legobot.Lego.listening_for()

        Args:
            message (Legobot.Message): Message to handle

        Returns:
            bool: True if lego is interested in the message.
        '''

        return str(self.actor_urn) != str(message['metadata']['source'])

    def handle(self, message):
        '''
        Attempts to send a message to the specified destination in Discord.
        Extends Legobot.Lego.handle()

        Args:
            message (Legobot.Message): message w/ metadata to send.
        '''

        logger.debug(message)
        if Utilities.isNotEmpty(message['metadata']['opts']):
            target = message['metadata']['opts']['target']
            self.botThread.create_message(target, message['text'])

    @staticmethod
    def get_name():
        '''
        Called by built-in !help lego

        Returns name of Lego. Returns None because this is
        a non-interactive Lego
        '''

        return None
