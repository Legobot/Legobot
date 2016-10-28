import logging
import threading
from Legobot.Lego import Lego

from Legobot.Connectors.IRC import IRC
from Legobot.Legos.Help import Help

# Initialize lock and master lego
# All others are considered children of the master/base lego
lock = threading.Lock()
master = Lego.start(None, lock)
# This comes from using Pykka for actors
# It will be simpler soon
master_proxy = master.proxy()

# Add children
master_proxy.add_child(IRC,
                          channel='#social',
                          nickname='legobot',
                          server='irc.sithmail.com',
                          port=6697,
                          use_ssl=True,
                          username=None,
                          password=None)
master_proxy.add_child(Help)
