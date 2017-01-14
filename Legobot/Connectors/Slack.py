import sys
import os
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
    '''
    def __init__(self, baseplate, token):
        self.baseplate = baseplate
        self.token = token
        self.last_ping = 0
        self.slack_client = SlackClient(self.token)
        threading.Thread.__init__(self)

    def connect(self):
        self.slack_client.rtm_connect()

    def run(self):
        self.connect()
        while True:
            for event in self.slack_client.rtm_read():
                logger.debug(event)
                if event['type'] == 'message':
                    metadata = self._parse_metadata(event)
                    message = Message(text=event['text'],
                                      metadata=metadata).__dict__
                    self.baseplate.tell(message)
            self.keepalive()
            time.sleep(0.1)
        return

    def _parse_metadata(self, message):
        metadata = Metadata(source=self).__dict__
        if 'text' in metadata:
            metadata['text'] = message['text']
        if 'user' in message:
            metadata['source_user'] = message['user']
        elif 'bot_id' in message:
            metadata['source_user'] = message['bot_id']
        metadata['source_channel'] = message['channel']
        # Slack starts DM channel IDs with "D"
        if message['channel'].startswith('D'):
            metadata['is_private_message'] = True
        else:
            metadata['is_private_message'] = False
        return metadata

    def keepalive(self):
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

class Slack(Lego):
    '''
    '''


    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = RtmBot(baseplate, *args, **kwargs)

    def on_start(self):
        self.botThread.start()

    def listening_for(self, message):
        return str(self.botThread) != str(message['metadata']['source'])

    def handle(self, message):
        logger.info(message)
        self.botThread.slack_client.api_call(
            "chat.postMessage",
            channel=message['metadata']['opts']['target'],
            text=message['text']
        )

    def get_name(self):
        return None
