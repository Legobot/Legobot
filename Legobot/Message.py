import six

__all__ = ["Message",
           "Metadata"]

class Message():
    """
    Messages in pykka must be passed as dictionaries. This class provides
    fields corresponding to the keys in that dictionary to facilitate the
    construction of such messages.
    """

    def __init__(self, text, metadata, should_log=False):
        assert isinstance(text, six.string_types)
        assert isinstance(metadata, dict)
        assert isinstance(should_log, bool)
        
        self.text = text
        self.metadata = metadata
        self.should_log = should_log


class Metadata():
    """
    Message Metadata is passed as a dictionary. This class provides
    fields corresponding to the keys in that dictionary to facilitate
    the construction of such dictionaries.
    """

    def __init__(self, source, dest=None, opts=None):
        assert opts is None or isinstance(opts, opts)
        
        self.source = source
        self.dest = dest
        self.opts = opts
