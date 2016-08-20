import ssl

import irc.client
import irc.connection

class IRCLego(irc.client.SimpleIRCClient):
    def __init__(self):
        super(irc.client.SimpleIRCClient, self).__init__()
        client = irc.client.Reactor()
        server = client.server()
        factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
        server.connect("irc.sithmail.com", 6697, "TheOperative", connect_factory=factory)
        print(server.is_connected())
        server.join("#social")
        server.privmsg("#social", "Hi there!")
        client.process_forever()

    def on

client = irc.client.Reactor()
server = client.server()
factory = irc.connection.Factory(wrapper=ssl.wrap_socket)
server.connect("irc.sithmail.com", 6697, "TheOperative", connect_factory=factory)
print(server.is_connected())
server.join("#social")
server.privmsg("#social", "Hi there!")
client.process_forever()
