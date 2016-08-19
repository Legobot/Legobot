from time import sleep

from Lego import Lego
import WeatherListener
import CommandLinePrinter
import Message

baseplate = Lego.start(None)
weather_listener = WeatherListener.WeatherListener.start(baseplate)
cli_printer = CommandLinePrinter.CommandLinePrinter.start(baseplate)
baseplate_proxy = baseplate.proxy()
baseplate_proxy.children.get().append(weather_listener)
baseplate_proxy.children.get().append(cli_printer)

metadata_1 = {"source": cli_printer}
message_1 = {"text": "!weather", "metadata": metadata_1}
message_2 = {"text": "90210", "metadata": metadata_1}


baseplate.tell(message_1)
sleep(2)
baseplate.tell(message_2)
