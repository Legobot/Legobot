import time
import threading
import pykka


class Lego(pykka.ThreadingActor):
    class HandlerThread(threading.Thread):
        def __init__(self, handler, message):
            threading.Thread.__init__(self)
            self.handler = handler
            self.message = message

        def run(self):
            self.handler(self.message)

    def __init__(self, baseplate):
        super(pykka.ThreadingActor, self).__init__()
        self.baseplate = baseplate
        self.children = []
        self.finished = False

    def on_receive(self, message):
        if self.listening_for(message):
            self_thread = self.HandlerThread(self.handle, message)
            self_thread.start()
        for child in self.children:
            child.tell(message)


    def listening_for(self, message):
        """
        Return whether this Lego is listening for the provided Message.

        All Legos should override this function.

        :param message: a Message object
        :return: a boolean
        """
        return False

    def handle(self, message):
        """
        Handle the provided Message.

        All Legos should override this function.

        :param message: a Message object
        :return: None
        """
        return