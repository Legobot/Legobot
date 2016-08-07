class Message:
    def __init__(self):
        self.text = None
        self.metadata = None


class Lego:
    def __init__(self):
        self.children = []
        self.finished = False
        
    def listening_for(self, message):
        """Return whether this Lego or a child is listening for a Message."""
        return (self.self_listening_for(message) or
                self.child_listening_for(message))
        
    def self_listening_for(self, message):
        """Return whether this Lego itself is listening for a Message."""
        return False
    
    def child_listening_for(self, message):
        """Return whether a child of this Lego is listening for a Message."""
        for child in self.children:
            if child.listening_for(message):
                return True
        return False
        
    def handle(self, message):
        """Handle a Message."""
        if self.self_listening_for(message):
            self.self_handle(message)
        for child in self.children:
            if child.listening_for(message):
                child.handle(message)
        return
    
    def self_handle(self, message):
        """Tell this lego to handle a Message itself."""
        return
        
    def cleanup(self):
        """Clean up this Lego and its children."""
        for child in self.children:
            child.cleanup()
        self.children = [child for child in self.children
                         if not child.finished]
        self.self_cleanup()

    def self_cleanup(self):
        """Clean up this Lego."""
        return


class Weather(Lego):
    class ZipCode(Lego):
        def self_listening_for(self, message):
            return message.text == '90210'
            
        def self_handle(self, message):
            print('The weather is sunny. It\'s California, after all.')
            self.finished = True

    def self_listening_for(self, message):
        return '!weather' in message.text

    def self_handle(self, message):
        zipcodeLego = self.ZipCode()
        self.children.append(zipcodeLego)

    # def self_cleanup(self):
    #     if len(self.children) == 0:
    #         self.finished = True


def handle_incoming_message(message, baseplate):
    """Handle an incoming Message."""
    if baseplate.listening_for(message):
        baseplate.handle(message)
        baseplate.cleanup()


class Legobot:
    def __init__(self):
        self.legos = []
        self.connections = []

    def poll(self):
        for connection in self.connections:
            for message in connection.messages:
                self.messages.append


message = Message()
message.text = "!weather"
message2 = Message()
message2.text = '90210'
messages = [message, message2]

baseplate = Lego()
baseplate.children.append(Weather())

for message in messages:
    handle_incoming_message(message, baseplate)

print(baseplate)