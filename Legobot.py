import threading

from IRCConnector import IRCLego
from Lego import Lego
from Legos.WeatherListener import WeatherListener
from Legos.BingImageSearch import BingImageSearch
from Legos.Tip import Tip
from Legos.PrintTips import PrintTips

lock = threading.Lock()
baseplate = Lego.start(None, lock)
baseplate_proxy = baseplate.proxy()
baseplate_proxy.add_child(WeatherListener, baseplate, lock)
baseplate_proxy.add_child(Tip, baseplate, lock)
baseplate_proxy.add_child(PrintTips, baseplate, lock)
baseplate_proxy.add_child(BingImageSearch, baseplate, lock)
baseplate_proxy.add_child(IRCLego, '#testing', 'TheOperative', 'irc.sithmail.com', baseplate, lock, 6697, True)