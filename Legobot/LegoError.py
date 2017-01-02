# LegoError.py
# Copyright (C) 2017 Brenton Briggs, Kevin McCabe, and Drew Bronson


class Error(Exception):
    """Base class for exception in the Legobot module"""

    pass


class LegoError(Error):
    """Exceptions raised inside legos"""

    def __init__(self, message):
        self.message = message
        Exception.__init__(self, message)
