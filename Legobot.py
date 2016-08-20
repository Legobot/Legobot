from time import sleep

from Lego import Lego
import WeatherListener
import CommandLinePrinter
import IRCConnector
import Message
import threading

baseplate = Lego.start(None)

weather_listener = WeatherListener.WeatherListener.start(baseplate)
# cli_printer = CommandLinePrinter.CommandLinePrinter.start(baseplate)
irc_connector = IRCConnector.IRCLego.start('#social', 'TheOperative', 'irc.sithmail.com', baseplate, 6697)


baseplate_proxy = baseplate.proxy()
baseplate_proxy.children.get().append(weather_listener)
# baseplate_proxy.children.get().append(cli_printer)
baseplate_proxy.children.get().append(irc_connector)


# metadata_1 = {"source": cli_printer}
# message_1 = {"text": "!weather", "metadata": metadata_1}
# message_2 = {"text": "90210", "metadata": metadata_1}


# baseplate.tell(message_1)
# sleep(2)
# baseplate.tell(message_2)
