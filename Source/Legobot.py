import threading

from Legos.BingImageSearch import BingImageSearch
from Legos.IRCConnector import IRCConnector
from Legos.PrintTips import PrintTips
from Legos.Tip import Tip
from Legos.WeatherListener import WeatherListener
from Legos.WikipediaTopFinder import WikipediaTopFinder
from Legos.Roll import Roll
from Legos.XKCD import XKCD
from Source.Lego import Lego

# Initialize lock and baseplate
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add children
baseplate_proxy.add_child(WeatherListener)
baseplate_proxy.add_child(Tip)
baseplate_proxy.add_child(PrintTips)
baseplate_proxy.add_child(BingImageSearch)
baseplate_proxy.add_child(IRCConnector, '#testing', 'TheOperative', 'irc.sithmail.com', 6697, True)
baseplate_proxy.add_child(WikipediaTopFinder)
baseplate_proxy.add_child(Roll)
baseplate_proxy.add_child(XKCD)