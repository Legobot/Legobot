import ssl

import irc.client
import irc.connection
import irc.bot
import threading
from Lego import Lego

class IRCBot(threading.Thread, irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, baseplate, port=6667, use_ssl=False):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        threading.Thread.__init__(self)
        self.channel = channel
        self.nickname = nickname
        self.server = server
        self.baseplate = baseplate
        self.port = port
        self.use_ssl = use_ssl

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
        self.connection.connect(self.server, self.port, self.nickname, connect_factory=factory)
        self.connection.join(self.channel)

    def on_pubmsg(self, c, e):
        """
        This function runs when the bot receives a public message.
        """
        text = e.arguments[0]
        metadata = {"source": self}
        message = {"text": text, "metadata": metadata}
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


class IRCLego(Lego):
    def __init__(self, channel, nickname, server, baseplate, lock, port=6667, use_ssl=False):
        super().__init__(baseplate, lock)
        self.botThread = IRCBot(channel, nickname, server, baseplate, port, use_ssl)
        self.channel = channel

    def on_start(self):
        self.botThread.start()

    def listening_for(self, message):
        return (str(self.botThread) != str(message['metadata']['source']))

    def handle(self, message):
        self.botThread.connection.privmsg(self.channel, message['text'])