# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

from Legobot.Lego import Lego


class TestingConnector(Lego):
    def __init__(self, baseplate, lock, temp_file='testing_file.tmp'):
        super().__init__(baseplate, lock)
        self.temp_file = temp_file

    def listening_for(self, message):
        return True

    def handle(self, message):
        with open(self.temp_file, mode='w') as f:
            f.write(str(message))
