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
baseplate_proxy.add_child(Help)
baseplate_proxy.add_child(Commendations)
baseplate_proxy.add_child(PrintCommendations)
