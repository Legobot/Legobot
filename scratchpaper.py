import queue
import time
import threading

class Lego:
    class HandlerThread(threading.Thread):
        def __init__(self, handler, message):
            threading.Thread.__init__(self)
            self.handler = handler
            self.message = message

        def run(self):
            self.handler(self.message)

    def __init__(self):
        self.children = []
        self.finished = False

    def listening_for(self, message):
        """
        Return whether this Lego or a child is listening for a Message.

        This function is called to determine if this Lego wants to handle a
        particular message, either because it itself is listening for that
        message, because one or more of its children is listening for that
        message, or because both are true.

        Legos should not override this function.
        """
        return (self.self_listening_for(message) or
                self.child_listening_for(message))

    def self_listening_for(self, message):
        """
        Return whether this lego itself is listening for a Message.

        Used to identify whether any processing should happen at this level of
        the hierarchy, or whether this Lego is only listening for a message
        because a child has asked it to.

        All legos should override this function.
        """
        return False

    def child_listening_for(self, message):
        """
        Return whether a child of this Lego is listening for a Message.

        Legos should not override this function.
        """
        for child in self.children:
            if child.listening_for(message):
                return True
        return False

    def handle(self, message):
        """
        Handle a Message.

        If this Lego itself is listening for a message, a thread will be
        started and this Lego's handler will be started. If any children are
        listening for the message, the message will be passed to them.

        Legos should not override this function.
        """
        if self.self_listening_for(message):
            start_time = time.clock()
            self_thread = self.HandlerThread(self.self_handle, message)
            self_thread.start()
        for child in self.children:
            if child.listening_for(message):
                child.handle(message)
        return

    def self_handle(self, message):
        """
        Tell this lego to handle a Message itself.

        This is the function that executes when the Lego itself is listening
        for a message and receives it, allowing for arbitrary code to be
        executed by overriding it.

        This function will always run inside a thread, so one Lego cannot
        interfere with another's ability to listen for and respond to messages.
        Legos are responsible for implementing their own timeouts within this
        function, to ensure their threads do not run forever.

        This function is responsible for setting self.finished to True if the
        Lego needs to be garbage collected, unless self.self_cleanup() has been
        overridden.

        All Legos should override this function.
        """
        return

    def cleanup(self):
        """
        Clean up this Lego and its children.

        Legos should not override this function.
        """
        for child in self.children:
            child.cleanup()
        self.children = [child for child in self.children
                         if not child.finished]
        self.self_cleanup()

    def self_cleanup(self):
        """
        Check if this Lego should be cleaned up and mark it accordingly.

        This function is responsible for setting self.finished to True if it
        determines that this Lego needs to be garbage collected. Imperative
        Legos will often perform this action at the end of self.self_handle()
        instead.

        Legos may optionally override this function.
        """
        return

class Message:
    def __init__(self):
        self.text = None
        self.metadata = None

class Weather(Lego):
    class ZipCode(Lego):
        def self_listening_for(self, message):
            return message.text == '90210'
            
        def self_handle(self, message):
            print('The weather is sunny. It\'s California, after all.')
            self.finished = True

    def self_listening_for(self, message):
        return '!weather' in message.text

    def self_handle(self, message):
        zipcode_lego = self.ZipCode()
        self.children.append(zipcode_lego)

    # def self_cleanup(self):
    #     if len(self.children) == 0:
    #         self.finished = True


def handle_incoming_message(message, baseplate):
    """Handle an incoming Message."""
    if baseplate.listening_for(message):
        baseplate.handle(message)
        baseplate.cleanup()


class Legobot:
    def __init__(self):
        self.connections = []
        self.message_queue = queue.Queue()
        self.baseplate = Lego()

    def process_message(self, message):
        self.baseplate.handle(message)
        self.baseplate.cleanup()

    def add_lego(self, lego):
        self.baseplate.children.append(lego)



#
#
# message = Message()
# message.text = "!weather"
# message2 = Message()
# message2.text = '90210'
# messages = [message, message2]
#
# baseplate = Lego()
# baseplate.children.append(Weather())
#
# for message in messages:
#     handle_incoming_message(message, baseplate)
#
# print(baseplate)