import threading

import IRCConnector
from Lego import Lego
from Legos import WeatherListener
from Legos import BingImageSearch

lock = threading.Lock()
baseplate = Lego.start(None, lock)

weather_listener = WeatherListener.WeatherListener.start(baseplate, lock)
irc_connector = IRCConnector.IRCLego.start('#testing', 'TheOperative', 'irc.sithmail.com', baseplate, lock, 6697, True)
img_search = BingImageSearch.BingImageSearch.start(baseplate, lock)

baseplate_proxy = baseplate.proxy()
baseplate_proxy.children.get().append(weather_listener)
baseplate_proxy.children.get().append(irc_connector)
baseplate_proxy.children.get().append(img_search)