from Lego import Lego
import Message


class WeatherListener(Lego):
    class ZipCodeListener(Lego):
        def listening_for(self, message):
            return '90210' in message['text']

        def handle(self, message):
            metadata = {"source": self, "dest": message['metadata']['source']}
            response = {"text": "The weather is sunny!", "metadata": metadata}
            self.baseplate.tell(response)
            self.stop()

    def listening_for(self, message):
        return '!weather' in message['text']

    def handle(self, message):
        metadata = {"source": self}
        response = {"text": "Please enter a zipcode.", "metadata": metadata}
        self.baseplate.tell(response)
        self.children.append(self.ZipCodeListener.start(self.baseplate))
        print(self.children)

    def on_failure(self, exception_type, exception_value, traceback):
        print('WeatherListener crashed.')
        print(exception_type)
        print(exception_value)
