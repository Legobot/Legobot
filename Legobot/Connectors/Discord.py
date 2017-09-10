from websocket import create_connection
import json
import logging
import requests
import sys
import threading
import time

from Legobot.Lego import Lego
from Legobot.Message import Message, Metadata

__author__ = "Bren Briggs (fraq)"
__copyright__ = "Copyright 2017, Legobot"

logger = logging.getLogger(__name__)


class Heartbeat(threading.Thread, object):
    def __init__(self, ws, interval):
        self.ws = ws
        self.interval = float(interval) / 1000.0
        self.sequence = 0
        logger.debug("Heartbeat handler initialized \
                     with interval of {}".format(self.interval))
        threading.Thread.__init__(self)

    def send(self, ws, seq):
        payload = {'op': 1, 'd': seq}
        payload = json.dumps(payload)
        logger.debug("Sending heartbeat with payload {}".format(payload))
        ws.send(payload)
        return

    def update_sequence(self, seq):
        self.sequence = seq
        logger.debug("Heartbeat sequence updated to {}".format(self.sequence))
        return

    def run(self):
        while True:
            self.send(self.ws, self.sequence)
            time.sleep(self.interval)


class DiscoBot(threading.Thread, object):

    def __init__(self, baseplate, token, actor_urn, *args, **kwargs):
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
        baseurl = self.rest_baseurl + \
            '/channels/{}/messages'.format(channel_id)
        requests.post(baseurl,
                      headers=self.headers,
                      data=json.dumps({'content': text}))

    def identify(self, token):
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
        logger.info("Got a hello")
        self.identify(self.token)
        self.heartbeat_thread = Heartbeat(self.ws,
                                          message['d']['heartbeat_interval'])
        self.heartbeat_thread.start()
        return

    def on_heartbeat(self, message):
        logger.info("Got a heartbeat")
        logger.info("Heartbeat message: {}".format(message))
        self.heartbeat_thread.update_sequence(message['d'])
        return

    def on_message(self, message):
        if 'content' in message['d']:
            metadata = self._parse_metadata(message)
            message = Message(text=message['d']['content'],
                              metadata=metadata).__dict__
            logger.debug(message)
            self.baseplate.tell(message)

    def _parse_metadata(self, message):
        metadata = Metadata(source=self.actor_urn).__dict__
        if 'author' in message['d']:
            metadata['source_user'] = message['d']['author']['username']
        else:
            metadata['source_user'] = None
        if 'channel_id' in message['d']:
            metadata['source_channel'] = message['d']['channel_id']
        else:
            metadata['source_channel'] = None
        return metadata

    @staticmethod
    def get_ws_url():
        url = requests.get(
            'https://discordapp.com/api/v6/gateway').json()['url']
        return url + '?v=6&encoding=json'

    def handle(self, message):
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
        self.ws = self.connect()
        while True:
            try:
                data = json.loads(self.ws.recv())
                self.handle(data)
            except json.decoder.JSONDecodeError as e:
                logger.fatal("No data on socket...")


class Discord(Lego):
    '''Lego that builds and connects Legobot.Connectors.Discord.DiscoBot

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

        return str(self.actor_urn) != str(message['metadata']['source'])

    def handle(self, message):
        '''Attempts to send a message to the specified destination in Discord.
        Extends Legobot.Lego.handle()

        Args:
            message (Legobot.Message): message w/ metadata to send.
        '''
        logger.info(message)
        target = message['metadata']['opts']['target']
        self.botThread.create_message(target, message['text'])

    @staticmethod
    def get_name():
        '''Called by built-in !help lego

        Returns name of Lego. Returns none because this is
        a non-interactive Lego
        '''

        return None
