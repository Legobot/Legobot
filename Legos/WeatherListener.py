from Lego import Lego
from Message import *


class WeatherListener(Lego):
    class ZipCodeListener(Lego):
        def listening_for(self, message):
            return '90210' in message['text']

        def handle(self, message):
            metadata = Metadata(source=self, dest=message['metadata']['source']).__dict__
            response = Message(text='The weather is sunny!', metadata=metadata).__dict__
            self.baseplate.tell(response)
            self.actor_ref.stop()

        def on_stop(self):
            print('ZipCodeListener stopped')

        def on_failure(self, exception_type, exception_value, traceback):
            print('ZipCodeListener crashed')

    def listening_for(self, message):
        return '!weather' in message['text']

    def handle(self, message):
        metadata = Metadata(source=self, dest=message['metadata']['source']).__dict__
        response = Message(text='Please enter a zipcode.', metadata=metadata).__dict__
        self.baseplate.tell(response)
        self.lock.acquire()
        print('Acquired lock in handle for ' + str(self))
        self.children.append(self.ZipCodeListener.start(self.baseplate, self.lock))
        self.lock.release()
