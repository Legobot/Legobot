import logging
import threading
from Legobot.Lego import Lego

from Legobot.Connectors.IRC import IRC 
from Legobot.Legos.Help import Help

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

# Initialize lock and master lego
# All others are considered children of the master/base lego
lock = threading.Lock()
master = Lego.start(None, lock)
# This comes from using Pykka for actors
# It will be simpler soon
master_proxy = master.proxy()

# Add children
master_proxy.add_child(IRC,
                          channels=['#social'],
                          nickname='legobot',
                          server='irc.sithmail.com',
                          port=6697,
                          use_ssl=True,
                          username=None,
                          password=None)
master_proxy.add_child(Help)
