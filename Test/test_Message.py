import unittest
<<<<<<< HEAD
from Legobot.Message import *
from Legobot.Lego import Lego
=======
from Source.Message import *
from Source.Lego import Lego
>>>>>>> 8e61541... Adding unit tests for Lego and Message
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
<<<<<<< HEAD
        message = Message('a message', metadata, True)
        assert(message.text == 'a message')
        assert(message.metadata == metadata)
        assert(message.should_log)

    def test_default_init_values(self):
        source =Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('a message', metadata)
        assert(not message.should_log)
=======
        message = Message('a message', metadata)
        assert(message.text == 'a message')
        assert(message.metadata == metadata)
>>>>>>> 8e61541... Adding unit tests for Lego and Message
