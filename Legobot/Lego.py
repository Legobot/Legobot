# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

import threading
import json
import logging

import pykka

from Legobot.LegoError import LegoError
from Legobot.Message import Message, Metadata


logger = logging.getLogger(__name__)


class Lego(pykka.ThreadingActor):
    class HandlerThread(threading.Thread):
        """
        This class provides a simple thread for running message handlers.
        It is used to ensure that message handlers do not block other Legos
        from running by simply taking too long to execute.
        """

        def __init__(self, handler, message):
            threading.Thread.__init__(self)
            self.handler = handler
            self.message = message

        def run(self):
            self.handler(self.message)

    def __init__(self, baseplate, lock: threading.Lock, log_file=None):
        """
        :param baseplate: the baseplate Lego, which should be \
                          the same instance of Lego for all Legos
        :param lock: a threading lock, which should be the same \
                     instance of threading.Lock for all Legos
        """
        super().__init__()
        if not lock:
            raise LegoError("Lock expected but not provided!")
        self.baseplate = baseplate
        self.children = []
        self.lock = lock
        self.log_file = log_file

    def on_receive(self, message):
        """
        Handle being informed of a message.

        This function is called whenever a Lego receives a message, as
        specified in the pykka documentation.

        Legos should not override this function.

        :param message:
        :return:
        """
        if self.log_file is not None and message['should_log']:
            message_copy = Message(message['text'],
                                   Metadata(None).__dict__,
                                   message['should_log']).__dict__
            with open(self.log_file, mode='w') as f:
                f.write(json.dumps(message_copy))
            logger.info(message['metadata']['source'])
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
        logger.debug('Acquired lock in cleanup for ' + str(self))
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

    def add_child(self, child_type, *args, **kwargs):
        """
        Initialize and keep track of a child.

        :param child_type: a class inheriting from Lego to initialize \
                           an instance of
        :param args: arguments for initializing the child
        :param kwargs: keyword arguments for initializing the child
        :return:
        """
        try:
            baseplate = kwargs['baseplate']
        except:
            if self.baseplate is None:
                baseplate = self.actor_ref
            else:
                baseplate = self.baseplate
        try:
            lock = kwargs['lock']
        except:
            lock = self.lock
        child = child_type.start(baseplate, lock, *args, **kwargs)
        self.children.append(child)

    def reply(self, message, text, opts=None):
        """
        Reply to the sender of the provided message with a message \
        containing the provided text.

        :param message: the message to reply to
        :param text: the text to reply with
        :param opts: A dictionary of additional values to add to metadata
        :return: None
        """
        metadata = Metadata(source=self,
                            dest=message['metadata']['source']).__dict__
        metadata['opts'] = opts
        message = Message(text=text, metadata=metadata,
                          should_log=message['should_log']).__dict__
        self.baseplate.tell(message)

    def get_name(self):
        """
        Return the name the Lego recognizes from the help function.

        :return: a string
        """
        return '?'

    def get_help(self):
        """
        Return a helpstring for the function.

        :return: a string
        """
        return ''

    def on_failure(self, exception_type, exception_value, traceback):
        logger.exception('Lego crashed: ' + str(self))
        logger.exception(exception_type)
        logger.exception(exception_value)
