import unittest
import threading
import pykka
import json
import os
import time
from Legobot.LegoError import LegoError
from Legobot.Message import Message, Metadata
from Legobot.Lego import Lego


class TestLego(unittest.TestCase):
    @staticmethod
    def test_initialization():
        lock = threading.Lock()
        baseplate = Lego(None, lock)
        lego = Lego(baseplate, baseplate.lock)
        lego = Lego(baseplate, baseplate.lock, 'lego.log')
        assert(baseplate.lock == lock)  # nosec
        assert(lego.lock == lock)  # nosec
        assert(baseplate.baseplate is None)  # nosec
        assert(lego.baseplate is baseplate)  # nosec
        assert(lego.children == [])  # nosec
        assert(lego.log_file == 'lego.log')  # nosec

    @staticmethod
    def test_default_init_values():
        lock = threading.Lock()
        baseplate = Lego(None, lock)
        lego = Lego(baseplate, baseplate.lock)
        assert lego.log_file is None  # nosec

    def test_lock_required(self):
        with self.assertRaises(LegoError):
            lego = Lego(None, None)  # noqa: F841

    def test_listening_for(self):
        lego = Lego(None, threading.Lock())
        message = self.make_message()
        assert not lego.listening_for(message)  # nosec

    def test_handle(self):
        lego = Lego(None, threading.Lock())
        assert(lego.handle(self.make_message()) is None)  # nosec

    def make_message(self):
        metadata = Metadata(self, None)
        return Message('a message', metadata)

    @staticmethod
    def test_add_child():
        baseplate = Lego(None, threading.Lock())
        baseplate.add_child(Lego)
        child = baseplate.children[0]
        assert(isinstance(child, pykka.ActorRef))  # nosec
        child_proxy = child.proxy()
        child_proxy.add_child(Lego)
        child_children = child_proxy.children.get()
        assert(isinstance(child_children[0], pykka.ActorRef))  # nosec
        child_children[0].stop()
        child.stop()

    @staticmethod
    def test_cleanup():
        baseplate = Lego(None, threading.Lock())
        baseplate.add_child(Lego)
        child = baseplate.children[0]
        child.stop()
        baseplate.cleanup()
        assert(len(baseplate.children) == 0)  # nosec

    @staticmethod
    def test_get_name():
        lego = Lego(None, threading.Lock())
        assert lego.get_name() == '?'  # nosec

    @staticmethod
    def test_get_help():
        lego = Lego(None, threading.Lock())
        assert lego.get_help() == ''  # nosec

    @staticmethod
    def test_receive_logs():
        log_file_name = 'test_logging.log'
        lego = Lego(None, threading.Lock(),
                    log_file_name)
        message = Message('Test Message 1',
                          Metadata(None).__dict__, True).__dict__
        lego.on_receive(message)
        with open(log_file_name, mode='r') as f:
            log = json.loads(f.read())
        assert log == message  # nosec
        os.remove(log_file_name)

    @staticmethod
    def test_on_receive_informs_children():
        log_file_name = 'test_child_informed.log'
        baseplate = Lego(None, threading.Lock())
        child = Lego.start(baseplate, threading.Lock(), log_file_name)
        baseplate.children.append(child)
        message = Message('Test Message 1',
                          Metadata(None).__dict__, True).__dict__
        baseplate.on_receive(message)
        child.stop()
        with open(log_file_name, mode='r') as f:
            log = json.loads(f.read())
        os.remove(log_file_name)
        assert log == message  # nosec

    @staticmethod
    def test_reply():
        # Setup
        baseplate = Lego.start(None, threading.Lock())
        baseplate_proxy = baseplate.proxy()
        urn = baseplate.actor_urn
        meta = Metadata(source=urn).__dict__
        message = Message(text='0', metadata=meta, should_log=True).__dict__
        log_file_name = 'test_reply.log'

        children = baseplate_proxy.children.get()
        for child in children:
            print(child.actor_urn)
        # Test
        baseplate_proxy.add_child(ReplyTestingPingLego, log_file_name)
        baseplate.tell(message)
        time.sleep(1)

        # Cleanup
        children = baseplate_proxy.children.get()
        for child in children:
            child.stop()
        baseplate.stop()

        with open(log_file_name, mode='r') as f:
            log = json.loads(f.read())
        os.remove(log_file_name)
        assert log['text'] == '1'  # nosec

    @staticmethod
    def test_on_failure():
        lego = Lego(None, threading.Lock())
        lego.on_failure("Exception Type", "Exception Value", "Traceback")
        assert True  # nosec


class ReplyTestingPingLego(Lego):
    def listening_for(self, message):
        print('\n\n{}\n\n'.format(message))
        return message['text'] == '0' or message['text'] == '1'

    def handle(self, message):
        if message['text'] == '0':
            self.reply(message, '1')
        else:
            print(message['text'])


class TestHandlerThread(unittest.TestCase):
    @staticmethod
    def test_initialization():
        lego = Lego(None, threading.Lock())
        message = Message('Test Message', Metadata(lego))
        thread = Lego.HandlerThread(lego.handle, message)
        assert thread.handler == lego.handle  # nosec
        assert thread.message == message  # nosec
