import requests
from Legobot.Lego import Lego

class Audit(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!msync'

    def handle(self,message):
        if len(message['text'].split()) == 1:
            # No args supplied
            base_url = 'https://raw.githubusercontent.com/voxpupuli/'
            msync_blob = requests.get('modulesync_config/master/moduleroot/.msync.yml')
            msync_text = msync_blob.text
            self.reply(message, msync_text.strip('\n'))
        elif len(message['text'].split() > 1):
            arg = message['text'].split()[1]
        return

    def get_name(self):
        return 'msync'

    def get_help(self):
        return 'Discover information about the status of modulesync on managed repositories. Usage: !msync [olderthan a.b.c]'
