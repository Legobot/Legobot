import json

from Legobot.Lego import Lego
from Legobot.Message import *
import os

class Commendations(Lego):
    def __init__(self, baseplate, lock, tips_file='commendations.json'):
        super().__init__(baseplate, lock)
        self.tips_file = tips_file

    def listening_for(self, message):
        return message['text'].split()[0] == '!commend'

    def handle(self, message):
        user = message['text'].split()[1]
        commendation_amount = 1
        if user == '-d':
            user = message['text'].split()[2]
            commendation_amount = -1
        json_str = None
        if not os.path.isfile(self.tips_file):
            with open(self.tips_file, 'w') as f:
                json_str = '{}'
                f.write(json_str)
        with open(self.tips_file, 'r') as f:
            json_str = f.read()
            print(json_str)
            try:
                commendations = json.loads(json_str)
            except:
                print('Failed to read commendations in ' + str(self) + '; initializing empty file ' + str(self.tips_file))
                commendations = {}
            try:
                commendations[user] += commendation_amount
            except:
                print('Could not find the user ' + str(user) + '; initializing their commendations at zero')
                commendations[user] = commendation_amount
            json_str = json.dumps(commendations)
        if json_str is not None:
            with open(self.tips_file, 'w') as f:
                f.write(json_str)
            metadata = Metadata(source=self, dest=message['metadata']['source']).__dict__
            message = Message(text=(str(user) + ' given ' + str(commendation_amount) +
                                    ' commendation points, giving them a total of ' + str(commendations[user])),
                              metadata=metadata).__dict__
            self.baseplate.tell(message)

    def get_name(self):
        return 'commend'

    def get_help(self):
        return 'Commend a user. Usage: !commend <username> to commend; !commend -d <username> to give demerit'


class PrintCommendations(Lego):
    def __init__(self, baseplate, lock, tips_file='commendations.json'):
        super().__init__(baseplate, lock)
        self.tips_file = tips_file

    def listening_for(self, message):
        return message['text'].split()[0] == '!commendations'

    def handle(self, message):
        with open(self.tips_file, mode='r') as f:
            json_str = f.read()
            print(json_str)
            try:
                commendations = json.loads(json_str)
            except:
                print('Failed to read in commendations')
                commendations = {}
            for commendation in commendations:
                metadata = Metadata(source=self, dest=message['metadata']['source']).__dict__
                message = Message(text=(str(commendation) + ': ' + str(commendations[commendation])), metadata=metadata).__dict__
                self.baseplate.tell(message)

    def get_name(self):
        return 'commendations'

    def get_help(self):
        return 'Print the commendations for all users in the commendations file. Usage: !commendations'
