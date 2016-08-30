from Legobot import Lego


class CommandLinePrinter(Lego):
    def listening_for(self, message):
        return str(self) != str(message['metadata']['source'])

    def handle(self, message):
        print(message['text'])
