class MetaData:
    def __init__(self, source=None):
        self.source = source

class Message:
    def __init__(self, text=None, metadata=MetaData()):
        self.text = text
        self.metadata = metadata


