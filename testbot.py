import logging
import threading
import configparser
from Legobot.Lego import Lego
from Legobot.Connectors.Slack import Slack
from Legobot.Connectors.IRC import IRC
from Legobot.Legos.Help import Help
from local.factoids import Factoids

config = configparser.ConfigParser()
config.read('config.ini')
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

# Initialize lock and baseplate
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()
# Add children
baseplate_proxy.add_child(Slack, token=config['c2c-slack']['token'])
baseplate_proxy.add_child(IRC,
                          channels=[channel.strip() for channel in config.get(
                              "irc1", "channels").split(",")],
                          nickname=config['irc1']['username'],
                          server=config['irc1']['host'],
                          port=int(config['irc1']['port']),
                          use_ssl=config.getboolean('irc1','ssl'),
                          username=config['irc1']['username'],
                          password=config['irc1']['password'])
baseplate_proxy.add_child(Factoids)
baseplate_proxy.add_child(Help)
