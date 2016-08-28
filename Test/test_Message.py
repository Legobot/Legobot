import unittest
from Source.Message import *
from Source.Lego import Lego
import threading

class TestMetadata(unittest.TestCase):
    def test_default_init_values(self):
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        assert(metadata.dest is None)

    def test_initialization(self):
        source = Lego(None, threading.Lock())
        dest = Lego(None, threading.Lock())
        metadata = Metadata(source, dest)
        assert(metadata.source == source)
        assert(metadata.dest == dest)

class TestMessage(unittest.TestCase):
    def test_initialization(self):
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('a message', metadata)
        assert(message.text == 'a message')
        assert(message.metadata == metadata)
