class Message():
    def __init__(self, text, metadata):
        self.text = text
        self.metadata = metadata

    def build(self):
        message = {}
        message['text'] = self.text
        message['metadata'] = self.metadata


class Metadata():
    def __init__(self, source=None):
        self.source = source

    def build(self):
        metadata = {}
        metadata['source'] = self.source