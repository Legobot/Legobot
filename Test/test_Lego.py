import unittest
from Source.Lego import Lego
import threading
from Source.Message import *
import pykka

class TestLego(unittest.TestCase):
    def test_initialization(self):
        lock = threading.Lock()
        baseplate = Lego(None, lock)
        lego = Lego(baseplate, baseplate.lock)
        assert(baseplate.lock == lock)
        assert(lego.lock == lock)
        assert(baseplate.baseplate is None)
        assert(lego.baseplate is baseplate)
        assert(lego.children == [])

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
