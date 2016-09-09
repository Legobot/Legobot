import unittest
from Legobot.Legos.TestingConnector import TestingConnector
from Legobot.Lego import Lego
import threading
from Legobot.Message import *


class TestTestingConnector(unittest.TestCase):
    def test_init(self):
        testing_connector = self._make_testing_connector('blah.tmp')
        assert testing_connector.temp_file == 'blah.tmp'

    def test_default_parameters(self):
        testing_connector = self._make_testing_connector()
        assert testing_connector.temp_file == 'testing_file.tmp'

    def test_listening_for(self):
        testing_connector = self._make_testing_connector()
        assert testing_connector.listening_for(self._make_message())

    def test_handle(self):
        testing_connector = self._make_testing_connector()
        message = self._make_message()
        testing_connector.handle(message)
        with open(testing_connector.temp_file, mode='r') as f:
            text = f.read()
        assert text == str(message)

    @staticmethod
    def _make_testing_connector(temp_file=None):
        lock = threading.Lock()
        baseplate = Lego(None, lock)
        if temp_file is None:
            testing_connector = TestingConnector(baseplate, lock)
        else:
            testing_connector = TestingConnector(baseplate, lock, temp_file)
        return testing_connector

    @staticmethod
    def _make_message():
        source = Lego(None, threading.Lock())
        metadata = Metadata(source)
        message = Message('blah', metadata)
        return message