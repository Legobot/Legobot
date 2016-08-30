class Message():
    """
    Messages in pykka must be passed as dictionaries. This class provides fields corresponding to the keys in that
    dictionary to facilitate the construction of such messages.
    """
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = metadata


class Metadata():
    """
    Message Metadata is passed as a dictionary. This class provides fields corresponding to the keys in that dictionary
    to facilitate the construction of such dictionaries.
    """
    def __init__(self, source, dest=None):
        self.source = source
        self.dest = dest
