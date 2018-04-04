# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

import logging
import ssl
import threading
import time

import irc.bot
import irc.client
import irc.connection

from jaraco.stream import buffer

from Legobot.Lego import Lego
from Legobot.Message import Message, Metadata
from Legobot.Utilities import Utilities

logger = logging.getLogger(__name__)


class IgnoreErrorsBuffer(buffer.DecodingLineBuffer):
    """  Handle char decode errors better
    """
    def handle_exception(self):
        pass


irc.client.ServerConnection.buffer_class = IgnoreErrorsBuffer
irc.client.SimpleIRCClient.buffer_class = IgnoreErrorsBuffer


class IRCBot(threading.Thread, irc.bot.SingleServerIRCBot):
    """
    Create bot instance
    """
    def __init__(self,
                 baseplate,
                 channels,
                 nickname,
                 server,
                 actor_urn,
                 port=6667,
                 use_ssl=False,
                 password=None,
                 username=None,
                 ircname=None,
                 nickserv=False,
                 nickserv_pass=None,
                 rejoin_on_kick=True,
                 auto_reconnect=True):
        irc.bot.SingleServerIRCBot.__init__(self,
                                            [(server, port)],
                                            nickname,
                                            nickname)
        threading.Thread.__init__(self)

        # the obvious self.channels is already used by irc.bot
        self.my_channels = channels
        self.nickname = nickname
        self.server = server
        self.baseplate = baseplate
        self.port = port
        self.use_ssl = use_ssl
        self.password = password
        self.username = username
        self.ircname = ircname
        self.nickserv = nickserv
        self.nickserv_pass = nickserv_pass
        self.actor_urn = actor_urn
        self.rejoin_on_kick = rejoin_on_kick
        self.auto_reconnect = auto_reconnect

        self.backoff = 1

    def connect(self, *args, **kwargs):
        """
        Connect to a server.

        This overrides the function in SimpleIRCClient
        to provide SSL functionality.

        :param args:
        :param kwargs:
        :return:
        """
        if self.use_ssl:
            factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        else:
            factory = irc.connection.Factory()
        self.connection.connect(server=self.server,
                                port=self.port,
                                nickname=self.nickname,
                                connect_factory=factory,
                                password=self.password,
                                username=self.username,
                                ircname=self.ircname)

    def set_metadata(self, e):
        """
        This function sets the metadata that is common between pub and priv
        """
        metadata = Metadata(source=self.actor_urn).__dict__
        metadata['source_connector'] = 'irc'
        metadata['source_channel'] = e.target
        metadata['source_user'] = e.source
        metadata['source_username'] = e.source.split('!')[0]
        metadata['user_id'] = metadata['source_user']
        metadata['display_name'] = metadata['source_username']
        return metadata

    def on_pubmsg(self, c, e):
        """
        This function runs when the bot receives a public message.
        """
        text = e.arguments[0]
        metadata = self.set_metadata(e)
        metadata['is_private_message'] = False
        message = Message(text=text, metadata=metadata).__dict__
        self.baseplate.tell(message)

    def on_privmsg(self, c, e):
        """
        This function runs when the bot receives a private message (query).
        """
        text = e.arguments[0]
        logger.debug('{0!s}'.format(e.source))
        metadata = self.set_metadata(e)
        metadata['is_private_message'] = True
        message = Message(text=text, metadata=metadata).__dict__
        self.baseplate.tell(message)

    def on_welcome(self, c, e):
        """
        This function runs when the bot successfully connects to the IRC server
        """
        self.backoff = 1  # Assume we had a good connection. Reset backoff.
        if self.nickserv:
            if Utilities.isNotEmpty(self.nickserv_pass):
                self.identify(c, e, self.nickserv_pass)
                time.sleep(3)  # Make sure Nickserv really sees us
            else:
                logger.error('If nickserv is enabled, you must supply'
                             ' a password')

        if self.nickserv is False and self.nickserv_pass is not None:
            logger.warn('It appears you provided a nickserv password but '
                        'did not enable nickserv authentication')

        for channel in self.my_channels:
            logger.debug('Attempting to join {0!s}'.format(channel))
            c.join(channel)

    def on_kick(self, c, e):
        if self.rejoin_on_kick is True:
            time.sleep(2)
            c.join(e.target)
        return

    def on_disconnect(self, c, e):
        if self.auto_reconnect is True:
            time.sleep(2 ** self.backoff)
            try:
                self._connect()
            except:
                self.backoff += 1

    def identify(self, c, e, password):
        c.privmsg('NickServ',
                  'IDENTIFY {0!s} {1!s}'.format(self.nickname, password))
        return

    def run(self):
        """
        Run the bot in a thread.

        Implementing the IRC listener as a thread allows it to
        listen without blocking IRCLego's ability to listen
        as a pykka actor.

        :return: None
        """
        self._connect()
        super(irc.bot.SingleServerIRCBot, self).start()


class IRC(Lego):

    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = IRCBot(baseplate=baseplate, actor_urn=self.actor_urn,
                                *args, **kwargs)

    def on_start(self):
        self.botThread.start()

    def listening_for(self, message):
        return str(self.actor_urn) != str(message['metadata']['source'])

    def handle(self, message):
        '''
        Attempts to send a message to the specified destination in IRC
        Extends Legobot.Lego.handle()

        Args:
            message (Legobot.Message): message w/ metadata to send.
        '''

        logger.debug(message)
        if Utilities.isNotEmpty(message['metadata']['opts']):
            target = message['metadata']['opts']['target']

            for split_line in Utilities.tokenize(message['text']):
                for truncated_line in Utilities.truncate(split_line):
                    self.botThread.connection.privmsg(target, truncated_line)
                    # Delay to prevent floods
                    time.sleep(0.25)

    @staticmethod
    def get_name():
        return None
