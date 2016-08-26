import threading

from IRCConnector import IRCLego
from Lego import Lego
from Legos.WeatherListener import WeatherListener
from Legos.BingImageSearch import BingImageSearch
from Legos.Tip import Tip
from Legos.PrintTips import PrintTips

# Initialize lock and baseplate
lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()

# Add children
baseplate_proxy.add_child(WeatherListener)
baseplate_proxy.add_child(Tip)
baseplate_proxy.add_child(PrintTips)
baseplate_proxy.add_child(BingImageSearch)
baseplate_proxy.add_child(IRCLego, '#testing', 'TheOperative', 'irc.sithmail.com', 6697, True)