import unittest
import threading

from Legobot.Lego import Lego
from Legobot.Message import Message, Metadata


class TestMetadata(unittest.TestCase):
    @staticmethod
    def test_default_init_values():
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        assert(metadata.dest is None)  # nosec

    @staticmethod
    def test_initialization():
        source = Lego(None, threading.Lock())
        dest = Lego(None, threading.Lock())
        metadata = Metadata(source, dest)
        assert(metadata.source == source)  # nosec
        assert(metadata.dest == dest)  # nosec


class TestMessage(unittest.TestCase):
    @staticmethod
    def test_initialization():
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('a message', metadata)
        assert(message.text == 'a message')  # nosec
        assert(message.metadata == metadata)  # nosec
        message = Message('a message', metadata, True)
        assert(message.text == 'a message')  # nosec
        assert(message.metadata == metadata)  # nosec
        assert(message.should_log)  # nosec

    @staticmethod
    def test_default_init_values():
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('a message', metadata)
        assert(not message.should_log)  # nosec
