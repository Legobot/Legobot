from  websocket import create_connection
import requests
import threading
import datetime
import json
import sys
import platform


class DiscoBot(threading.Thread):
    def __init__(self):
        self.heartbeat_interval = 0
        self.heartbeat_seq = 0
        self.last_heartbeat = None
        self.ws = None
        self.token = ''
        return

    def connect(self):
        return create_connection(self.get_ws_url())

    def identify(self, token):
        payload = {
            'op': 2,
            'd': {
                'token': self.token,
                'properties': {
                    '$os': sys.platform,
                    '$browser': 'legobot',
                    '$device': 'legobot'
                },
                'compress': False,
                'large_threshold': 250
            }
        }
        payload['d']['synced_guilds'] = []
        print("Identifying with the following message: {}".format(payload))
        self.ws.send(json.dumps(payload))
        return

    def on_hello(self, message):
        print("Got a hello")
        self.heartbeat_interval = message['d']['heartbeat_interval']
        self.identify(self.token)
        return

    def on_heartbeat(self, message):
        print("Got a heartbeat")
        self.hearbeat_seq = message['d']
        return

    @staticmethod
    def get_ws_url():
        url = requests.get('https://discordapp.com/api/v6/gateway').json()['url']
        return url + '?v=6&encoding=json'
    
    def handle(self, message):
        opcode = message['op']
        print(message)
        if opcode == 10:
            self.on_hello(message)
        elif opcode == 1:
            self.on_heartbeat(message)
        else:
            print("Not a hello")
        return

    def heartbeat_check(self):
        if self.last_heartbeat is not None:
            diff = datetime.datetime.now() - self.last_heartbeat
            if diff * 1000 > self.heartbeat_interval:
                self.send_heartbeat(self.heartbeat_seq)

    def run(self):
        self.ws = self.connect()
        while True:
            self.heartbeat_check()
            try:
                data = json.loads(self.ws.recv())
                print(type(data))
                self.handle(data)
            except json.decoder.JSONDecodeError as e:
                print("No data on socket...")

    def send_heartbeat(self, seq='null'):
        payload = {'op':1, 'd':seq}
        print("Sending heartbeat with payload {}".format(json.dumps(payload)))
        self.ws.send(json.dumps(payload))
        self.last_hearbeat = datetime.datetime.now()
        return

if __name__ == "__main__":
    bot = DiscoBot()
    bot.run()
