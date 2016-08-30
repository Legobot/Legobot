from Legobot.Lego import Lego

<<<<<<< HEAD:Source/Legobot.py
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
=======
from Source.Lego import Lego

from Legos.BingImageSearch import BingImageSearch
from Legos.IRCConnector import IRCConnector
from Legos.PrintTips import PrintTips
from Legos.Tip import Tip
from Legos.WeatherListener import WeatherListener
from Legos.WikipediaTopFinder import WikipediaTopFinder
from Legos.Roll import Roll
from Legos.XKCD import XKCD
from Legos.Help import Help
from Legos.Commendations import Commendations
from Legos.Commendations import PrintCommendations
>>>>>>> cc87117... Fix to run from command line:Legobot.py

# Initialize lock and baseplate
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add children
baseplate_proxy.add_child(WeatherListener)
baseplate_proxy.add_child(Tip)
baseplate_proxy.add_child(PrintTips)
baseplate_proxy.add_child(BingImageSearch)
baseplate_proxy.add_child(IRCConnector, '#testing', 'TheOperative', '127.0.0.1', 6697, True)
baseplate_proxy.add_child(WikipediaTopFinder)
baseplate_proxy.add_child(Roll)
baseplate_proxy.add_child(XKCD)
baseplate_proxy.add_child(Help)
baseplate_proxy.add_child(Commendations)
baseplate_proxy.add_child(PrintCommendations)
