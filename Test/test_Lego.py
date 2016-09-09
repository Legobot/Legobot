import unittest
from Legobot.Lego import Lego
import threading
from Legobot.Message import *
import pykka
import json
import os
import time

class TestLego(unittest.TestCase):
    def test_initialization(self):
        lock = threading.Lock()
        baseplate = Lego(None, lock)
        lego = Lego(baseplate, baseplate.lock, 'lego.log')
        assert(baseplate.lock == lock)
        assert(lego.lock == lock)
        assert(baseplate.baseplate is None)
        assert(lego.baseplate is baseplate)
        assert(lego.children == [])
        assert(lego.log_file == 'lego.log')

    def test_default_init_values(self):
        lock = threading.Lock()
        baseplate = Lego(None, lock)
        lego = Lego(baseplate, baseplate.lock)
        assert lego.log_file is None

    def test_lock_required(self):
        with self.assertRaises(AssertionError):
            lego = Lego(None, None)

    def test_listening_for(self):
        lego = Lego(None, threading.Lock())
        message = self.make_message()
        assert not lego.listening_for(message)

    def test_handle(self):
        lego = Lego(None, threading.Lock())
        assert(lego.handle(self.make_message()) is None)

    def make_message(self):
        metadata = Metadata(self, None)
        return Message('a message', metadata)

    def test_add_child(self):
        baseplate = Lego(None, threading.Lock())
        baseplate.add_child(Lego)
        child = baseplate.children[0]
        assert(isinstance(child, pykka.ActorRef))
        child_proxy = child.proxy()
        child_proxy.add_child(Lego)
        child_children = child_proxy.children.get()
        assert(isinstance(child_children[0], pykka.ActorRef))
        child_children[0].stop()
        child.stop()

    def test_cleanup(self):
        baseplate = Lego(None, threading.Lock())
        baseplate.add_child(Lego)
        child = baseplate.children[0]
        child.stop()
        baseplate.cleanup()
        assert(len(baseplate.children) == 0)

    def test_get_name(self):
        lego = Lego(None, threading.Lock())
        assert lego.get_name() == '?'

    def test_get_help(self):
        lego = Lego(None, threading.Lock())
        assert lego.get_help() == ''

    def test_receive_logs(self):
        log_file_name = 'test_logging.log'
        lego = Lego(None, threading.Lock(), log_file_name)
        message = Message('Test Message 1', Metadata(None).__dict__, True).__dict__
        lego.on_receive(message)
        with open(log_file_name, mode='r') as f:
            log = json.loads(f.read())
        assert log == message
        os.remove(log_file_name)

    def test_on_receive_informs_children(self):
        log_file_name = 'test_child_informed.log'
        baseplate = Lego(None, threading.Lock())
        child = Lego.start(baseplate, threading.Lock(), log_file_name)
        baseplate.children.append(child)
        message = Message('Test Message 1', Metadata(None).__dict__, True).__dict__
        baseplate.on_receive(message)
        child.stop()
        with open(log_file_name, mode='r') as f:
            log = json.loads(f.read())
        os.remove(log_file_name)
        assert log == message


    def test_reply(self):
        log_file_name = 'test_reply.log'
        baseplate = Lego.start(None, threading.Lock())
        baseplate_proxy = baseplate.proxy()
        baseplate_proxy.add_child(ReplyTestingPingLego, log_file_name)
        baseplate_proxy.add_child(ReplyTestingPongLego)
        baseplate.tell(Message('0', Metadata(None).__dict__, True).__dict__)
        time.sleep(1)
        children = baseplate_proxy.children.get()
        for child in children:
            child.stop()
        baseplate.stop()
        with open(log_file_name, mode='r') as f:
            log = json.loads(f.read())
        os.remove(log_file_name)
        assert log['text'] == '4'

    def test_on_failure(self):
        lego = Lego(None, threading.Lock())
        lego.on_failure("Exception Type", "Exception Value", "Traceback")
        assert True


class ReplyTestingPingLego(Lego):
    def listening_for(self, message):
        return message['metadata']['dest'] is self or message['text'] == '0'

    def handle(self, message):
        if message['text'] == '0':
            self.baseplate.tell(Message('1', Metadata(self).__dict__, True).__dict__)
        elif message['text'] == '2':
            self.reply(message, '3')
        else:
            print(message['text'])
            # self.stop()


class ReplyTestingPongLego(Lego):
    def listening_for(self, message):
        return message['metadata']['dest'] is self or message['text'] == '1'

    def handle(self, message):
        if message['text'] == '1':
            self.reply(message, '2')
        elif message['text'] == '3':
            self.reply(message, '4')
            self.stop()


class TestHandlerThread(unittest.TestCase):
    def test_initialization(self):
        lego = Lego(None, threading.Lock())
        message = Message('Test Message', Metadata(lego))
        thread = Lego.HandlerThread(lego.handle, message)
        assert thread.handler == lego.handle
        assert thread.message == message