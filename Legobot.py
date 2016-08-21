from time import sleep

from Lego import Lego
import WeatherListener
import IRCConnector
import threading

lock = threading.Lock()
baseplate = Lego.start(None, lock)

weather_listener = WeatherListener.WeatherListener.start(baseplate, lock)
irc_connector = IRCConnector.IRCLego.start('#testing', 'TheOperative', 'irc.sithmail.com', baseplate, lock, 6697, True)

baseplate_proxy = baseplate.proxy()
baseplate_proxy.children.get().append(weather_listener)
baseplate_proxy.children.get().append(irc_connector)