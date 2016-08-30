import json
import os

from Legobot.Message import *
from Legobot.Lego import Lego


class Tip(Lego):
    def __init__(self, baseplate, lock, tips_file='tips.json'):
        super().__init__(baseplate, lock)
        self.tips_file = tips_file

    def listening_for(self, message):
        return message['text'].split()[0] == '!tip'

    def handle(self, message):
        user = message['text'].split()[1]
        tip_amount = int(message['text'].split()[2])
        json_str = None
        if not os.path.isfile(self.tips_file):
            with open(self.tips_file, 'w') as f:
                json_str = '{}'
                f.write(json_str)
        with open(self.tips_file, 'r') as f:
            json_str = f.read()
            print(json_str)
            try:
                tips = json.loads(json_str)
            except:
                print('Failed to read tips in ' + str(self) + '; initializing empty tips file ' + str(self.tips_file))
                tips = {}
            try:
                tips[user] += tip_amount
            except:
                print('Could not find the user ' + str(user) + '; initializing their tips at zero')
                tips[user] = tip_amount
            json_str = json.dumps(tips)
        if json_str is not None:
            with open(self.tips_file, 'w') as f:
                f.write(json_str)
            metadata = Metadata(source=self, dest=message['metadata']['source']).__dict__
            message = Message(text=(str(user) + ' tipped ' + str(tip_amount) +
                                    ' internet points, giving them a total of ' + str(tips[user])),
                              metadata=metadata).__dict__
            self.baseplate.tell(message)

    def get_name(self):
        return 'tip'

    def get_help(self):
        return 'Tip a user. Usage: !tip <username> <integer>'
