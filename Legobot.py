import threading

import IRCConnector
from Lego import Lego
from Legos.WeatherListener import WeatherListener
from Legos.BingImageSearch import BingImageSearch
from Legos.Tip import Tip
from Legos.PrintTips import PrintTips

lock = threading.Lock()
baseplate = Lego.start(None, lock)

weather_listener = WeatherListener.start(baseplate, lock)
irc_connector = IRCConnector.IRCLego.start('#testing', 'TheOperative', 'irc.sithmail.com', baseplate, lock, 6697, True)
tips = Tip.start(baseplate, lock)
tip_printer = PrintTips.start(baseplate, lock)
img_search = BingImageSearch.start(baseplate, lock)

baseplate_proxy = baseplate.proxy()
baseplate_proxy.children.get().append(weather_listener)
baseplate_proxy.children.get().append(irc_connector)
baseplate_proxy.children.get().append(tips)
baseplate_proxy.children.get().append(tip_printer)

baseplate_proxy.children.get().append(img_search)