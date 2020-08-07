# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

import json
import logging
import threading
import time

import jmespath
from pykka import ThreadingActor, ActorRegistry

from Legobot.LegoError import LegoError
from Legobot.Message import Message, Metadata

logger = logging.getLogger(__name__)


class Lego(ThreadingActor):
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

    def __init__(self, baseplate, lock: threading.Lock, log_file=None,
                 acl=None, rate_config=None):
        """
        :param baseplate: the baseplate Lego, which should be \
                          the same instance of Lego for all Legos
        :param lock: a threading lock, which should be the same \
                     instance of threading.Lock for all Legos
        :param log_file str: a file path for writing logs to file
        :param acl dict: a dict representing an access control list. \
                         ex: {'whitelist': [list of source_users]}
        :param rate_config dict: a dict representing the rate limite config. \
                                 ex: {'rate_key': jmespath expr to get rate \
                                        key value from message object, \
                                      'rate_interval': the rate limit \
                                        interval in seconds}
        """
        super().__init__()
        if not lock:
            raise LegoError("Lock expected but not provided!")
        self.baseplate = baseplate
        self.children = []
        self.lock = lock
        self.log_file = log_file
        self.acl = acl if acl else {}

        # set rate limit items
        self.set_rate_limit(rate_config)

    def set_rate_limit(self, rate_config):
        """
        Set rate limit config for this Lego.

        :param rate_config dict: dict representing the rate limit config
        """
        rate_config = rate_config if isinstance(rate_config, dict) else {}
        self.rate_key = rate_config.get('rate_key')
        self.rate_interval = rate_config.get('rate_interval')
        self.rate_log = {}

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
        if (self.acl_check(message)
                and self.rate_check(message)
                and self.listening_for(message)):
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

    def rate_check(self, message):
        """
        Return whether the message passes the rate limite check for this Lego.

        :param message: a Message object
        :return: Boolean
        """
        if not self.rate_key or not self.rate_interval:
            return True

        now = int(round(time.time()))
        key = jmespath.search(self.rate_key, message)
        last_invoke = self.rate_log.get(key, 0)

        if now - last_invoke >= self.rate_interval:
            self.rate_log[key] = now
            return True
        else:
            return False

    def acl_check(self, message):
        """
        Return whether the message passes the ACL check for this Lego.

        :param message: a Message object
        :return: Boolean
        """
        user = message.get('metadata', {}).get('source_user')
        acl_conditions = [
            user,
            isinstance(user, str),
            self.acl,
            isinstance(self.acl, dict)
        ]
        if all(acl_conditions):
            whitelist = self.acl.get('whitelist', [])
            if whitelist and user in whitelist:
                return True
            elif whitelist and user not in whitelist:
                return False

            blacklist = self.acl.get('blacklist', [])
            if blacklist and user in blacklist:
                return False
            if blacklist and user not in blacklist:
                return True

        return True

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
        metadata = Metadata(source=self.actor_urn,
                            dest=message['metadata']['source']).__dict__
        metadata['opts'] = opts
        message = Message(text=text, metadata=metadata,
                          should_log=message['should_log']).__dict__
        dest_actor = ActorRegistry.get_by_urn(message['metadata']['dest'])
        if dest_actor is not None:
            dest_actor.tell(message)
        else:
            raise("Tried to send message to nonexistent actor")

    def reply_attachment(self, message, text, attachment, opts=None):
        """
        Convenience method for formatting reply as attachment (if available)
        and passing it on to the reply method. Individual connectors can then
        deal with the attachment or simply pass it on as a regular message

        :param message: the message to reply to
        :param text: the text to reply with
        :param attachment: the attachment link
        :param opts: A dictionary of additional values to add to metadata
        :return: None
        """
        if not opts:
            opts = {}

        opts['attachment'] = attachment
        opts['fallback'] = text
        text += '\n {}'.format(attachment)
        self.reply(message, text, opts)

    def build_reply_opts(self, message):
        """
        Convenience method for constructing default options for a
        reply message.

        :param message: the message to reply to
        :return: opts
        """
        try:
            source = message['metadata']['source_channel']
            thread = message['metadata'].get('thread_ts')
            opts = {'target': source, 'thread': thread}
        except LookupError:
            source = None
            opts = None
            logger.error("Could not identify source from  message:{}\n"
                         .format(str(message)))
        return opts

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
        ref = ActorRegistry.get_by_urn(self.actor_urn)
        logger.exception('Lego crashed: ' + str(ref))
        logger.exception(exception_type)
        logger.exception(exception_value)
