class Message:
    def __init__(self):
        self.text = None
        
class Lego:
    def __init__(self):
        self.finished = False
        self.children = []
        
    def listening_for(self, message):
        """Return whether this Lego is listening for a Message."""
        return (self.self_listening_for(message) or
                self.child_listening_for(message))
        
    def self_listening_for(self, message):
        """Return whether this Lego itself is listening for a Message."""
        return False
    
    def child_listening_for(self, message):
        """Return whether a child Lego is listening for a Message."""
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
        """Clean up finished children."""
        self.children = [child for child in self.children
                         if not child.finished]
        

class Weather(Lego):
    class ZipCode(Lego):
        def self_listening_for(self, message):
            return message.text == '90210'
            
        def self_handle(self, message):
            print 'The weather is sunny. It\'s California, after all.'
            self.finished = True
    
    def self_listening_for(self, message):
        return '!weather' in message.text

    def self_handle(self, message):
        if self.self_listening_for(message):
            zipcodeLego = self.ZipCode()
            self.children.append(zipcodeLego)


baseplate = Lego()
baseplate.children.append(Weather())


message = Message()
message.text = "!weather"

message2 = Message()
message2.text = '90210'

messages = [message, message2]

for message in messages:
    if baseplate.listening_for(message):
        baseplate.handle(message)


# weather = Weather()
# weather.handle(message)
# print weather.children
# print weather.listening_for(message2)
# weather.handle(message2)
# weather.cleanup()
# print weather.children
# print weather.listening_for(message2)