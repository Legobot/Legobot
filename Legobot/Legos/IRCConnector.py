import ssl
import threading
import logging

import irc.bot
import irc.client
import irc.connection

from Legobot.Message import *
from Legobot.Lego import Lego

logger = logging.getLogger(__name__)


class IRCBot(threading.Thread, irc.bot.SingleServerIRCBot):
    def __init__(self,  baseplate, channel, nickname, server, port=6667, use_ssl=False, password=None, username=None, ircname=None):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        threading.Thread.__init__(self)
        self.channel = channel
        self.nickname = nickname
        self.server = server
        self.baseplate = baseplate
        self.port = port
        self.use_ssl = use_ssl
        self.password = password
        self.username = username
        self.ircname = ircname

    def connect(self, *args, **kwargs):
        """
        Connect to a server.

        This overrides the function in SimpleIRCClient to provide SSL functionality.

        :param args:
        :param kwargs:
        :return:
        """
        if self.use_ssl:
            factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        else:
            factory = irc.connection.Factory()
        self.connection.connect(server=self.server, port=self.port, nickname=self.nickname, connect_factory=factory, password=self.password, username=self.username, ircname=self.ircname)
        self.connection.join(self.channel)

    def on_pubmsg(self, c, e):
        """
        This function runs when the bot receives a public message.
        """
        text = e.arguments[0]
        metadata = Metadata(source=self).__dict__
        message = Message(text=text, metadata=metadata).__dict__
        self.baseplate.tell(message)

    def run(self):
        """
        Run the bot in a thread.

        Implementing the IRC listener as a thread allows it to listen without blocking IRCLego's ability to listen
        as a pykka actor.

        :return: None
        """
        self._connect()
        super(irc.bot.SingleServerIRCBot, self).start()


class IRCConnector(Lego):
    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = IRCBot(baseplate, *args, **kwargs)
        self.channel = kwargs['channel']

    def on_start(self):
        self.botThread.start()

    def listening_for(self, message):
        return str(self.botThread) != str(message['metadata']['source'])

    def handle(self, message):
        self.botThread.connection.privmsg(self.channel, message['text'])

    def get_name(self):
        return None
