import unittest
from Legobot.Message import *
from Legobot.Lego import Lego
import threading


class TestMetadata(unittest.TestCase):
    def test_default_init_values(self):
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        assert(metadata.dest is None) # nosec

    def test_initialization(self):
        source = Lego(None, threading.Lock())
        dest = Lego(None, threading.Lock())
        metadata = Metadata(source, dest)
        assert(metadata.source == source) # nosec
        assert(metadata.dest == dest) # nosec


class TestMessage(unittest.TestCase):
    def test_initialization(self):
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('a message', metadata)
        assert(message.text == 'a message') # nosec
        assert(message.metadata == metadata) # nosec
        message = Message('a message', metadata, True)
        assert(message.text == 'a message') # nosec
        assert(message.metadata == metadata) # nosec
        assert(message.should_log) # nosec

    def test_default_init_values(self):
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('a message', metadata)
        assert(not message.should_log) # nosec
