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
        self.token = token
        self.last_ping = 0
        self.slack_client = SlackClient(self.token)
        threading.Thread.__init__(self)

    def connect(self):
        self.slack_client.rtm_connect()

    def run(self):
        self.connect()
        while True:
            for reply in self.slack_client.rtm_read():
                logger.debug(reply)
            self.autoping()
            time.sleep(0.1)
        return

    def autoping(self):
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

    def get_name(self):
        return None
