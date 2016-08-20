import ssl

import irc.client
import irc.connection
import irc.bot
import threading
from Lego import Lego


class IRCLego(Lego, threading.Thread, irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, baseplate, port=6667):
        super(Lego, self).__init__(baseplate)
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        threading.Thread.__init__(self)
        self.channel = channel
        self.baseplate = baseplate

    def connect(self, *args, **kwargs):
        factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        self.connection.connect('irc.sithmail.com', 6697, 'TheOperative', connect_factory=factory)
        self.connection.join("#social")

    def on_pubmsg(self, c, e):
        text = e.arguments[0]
        metadata = {"source": self}
        message = {"text": text, "metadata": metadata}
        self.baseplate.tell(message)

    def on_start(self):
        super(threading.Thread, self).start()

    def run(self):
        self._connect()
        super(irc.bot.SingleServerIRCBot, self).start()

    def listening_for(self, message):
        print('asking irc listener if it wants that')
        return (str(self) != str(message['metadata']['source']))

    def handle(self, message):
        print(message['text'])