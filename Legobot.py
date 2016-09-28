import logging
import threading
from Legobot.Lego import Lego

from Legobot.Legos.IRCConnector import IRCConnector
from Legobot.Legos.Help import Help
from Legobot.Legos.Msync import Audit

# Initialize logging
# create logger with 'spam_application'
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
loghandler = logging.StreamHandler()
loghandler.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
loghandler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(loghandler)

# Initialize lock and baseplate
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add children
baseplate_proxy.add_child(Audit)
baseplate_proxy.add_child(Help)
baseplate_proxy.add_child(IRCConnector, channel='#social', nickname='TheVoxFox', server='irc.sithmail.com', port=6697, use_ssl=True, username=None, password=None)
