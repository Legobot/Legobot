from Lego import Lego
import Message


class WeatherListener(Lego):
    class ZipCodeListener(Lego):
        def listening_for(self, message):
            return '90210' in message['text']

        def handle(self, message):
            metadata = {"source": self}
            response = {"text": "The weather is sunny!", "metadata": metadata}
            message['metadata']['source'].tell(response)
            self.stop()

    def listening_for(self, message):
        return '!weather' in message['text']

    def handle(self, message):
        metadata = {"source": self}
        response = {"text": "Please enter a zipcode.", "metadata": metadata}
        message['metadata']['source'].tell(response)
        self.children.append(self.ZipCodeListener.start(self))
