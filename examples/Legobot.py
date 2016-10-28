import logging
import threading
from Legobot.Lego import Lego

from Legobot.Legos.BingImageSearch import BingImageSearch
from Legobot.Legos.IRCConnector import IRCConnector
from Legobot.Legos.PrintTips import PrintTips
from Legobot.Legos.Tip import Tip
from Legobot.Legos.WeatherListener import WeatherListener
from Legobot.Legos.WikipediaTopFinder import WikipediaTopFinder
from Legobot.Legos.Roll import Roll
from Legobot.Legos.XKCD import XKCD
from Legobot.Legos.Help import Help
from Legobot.Legos.Commendations import Commendations
from Legobot.Legos.Commendations import PrintCommendations

# Initialize lock and master lego
# All others are considered children of the master/base lego
lock = threading.Lock()
master = Lego.start(None, lock)
# This comes from using Pykka for actors
# It will be simpler soon
master_proxy = master.proxy()

# Add children
master_proxy.add_child(WeatherListener)
master_proxy.add_child(Tip)
master_proxy.add_child(PrintTips)
master_proxy.add_child(BingImageSearch)
master_proxy.add_child(IRCConnector,
                          channel='#general',
                          nickname='chatbot',
                          server='foo.slack.com',
                          port=6697,
                          use_ssl=True,
                          username='chatbot',
                          password='example.yourIRCgatewaypass')
master_proxy.add_child(WikipediaTopFinder)
master_proxy.add_child(Roll)
master_proxy.add_child(XKCD)
master_proxy.add_child(Help)
master_proxy.add_child(Commendations)
master_proxy.add_child(PrintCommendations)
