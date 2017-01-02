# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

import ssl
import threading
import logging

import irc.bot
import irc.client
import irc.connection

from Legobot.Message import Message, Metadata
from Legobot.Lego import Lego
from jaraco.stream import buffer

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
    def __init__(self, baseplate, channels, nickname, server,
                 port=6667, use_ssl=False, password=None,
                 username=None, ircname=None, nickserv=False,
                 nickserv_pass=None):
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

    def on_pubmsg(self, c, e):
        """
        This function runs when the bot receives a public message.
        """
        text = e.arguments[0]
        metadata = Metadata(source=self).__dict__
        metadata['source_channel'] = e.target
        metadata['source_user'] = e.source
        metadata['source_username'] = e.source.split('!')[0]
        metadata['is_private_message'] = False
        message = Message(text=text, metadata=metadata).__dict__
        self.baseplate.tell(message)

    def on_privmsg(self, c, e):
        """
        This function runs when the bot receives a private message (query).
        """
        text = e.arguments[0]
        metadata = Metadata(source=self).__dict__
        logger.debug('{0!s}'.format(e.source))
        metadata['source_channel'] = e.source.split('!')[0]
        metadata['source_username'] = e.source.split('!')[0]
        metadata['source_user'] = e.source
        metadata['is_private_message'] = True
        message = Message(text=text, metadata=metadata).__dict__
        self.baseplate.tell(message)

    def on_welcome(self, c, e):
        """
        This function runs when the bot successfully connects to the IRC server
        """
        for channel in self.my_channels:
            logger.debug('Attempting to join {0!s}'.format(channel))
            c.join(channel)

        if self.nickserv is True and self.nickserv_pass is not None:
            self.identify(c, e, self.nickserv_pass)
        else:
            logger.error('If nickserv is enabled, you must supply a password')

        if self.nickserv is False and self.nickserv_pass is not None:
            logger.warn('It appears you provided a nickserv password but '
                        'did not enable nickserv authentication')

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
        self.botThread = IRCBot(baseplate, *args, **kwargs)

    def on_start(self):
        self.botThread.start()

    def listening_for(self, message):
        return str(self.botThread) != str(message['metadata']['source'])

    def handle(self, message):
        logger.info(message)
        self.botThread.connection.privmsg(message['metadata']['opts'][
            'target'], message['text'])

    def get_name(self):
        return None
