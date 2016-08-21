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

    def __init__(self, baseplate, lock):
        super(pykka.ThreadingActor, self).__init__()
        self.baseplate = baseplate
        self.children = []
        self.lock = lock

    def on_receive(self, message):
        if self.listening_for(message):
            self_thread = self.HandlerThread(self.handle, message)
            self_thread.start()
        self.cleanup()
        for child in self.children:
            child.tell(message)


    def cleanup(self):
        """
        Clean up finished children.

        :return: None
        """
        self.lock.acquire()
        print('Acquired lock in cleanup for ' + str(self))
        self.children = [child for child in self.children if child.is_alive()]
        self.lock.release()

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

    def on_failure(self, exception_type, exception_value, traceback):
        print('Lego crashed')
        print(exception_type)
        print(exception_value)