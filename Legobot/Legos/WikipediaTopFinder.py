import requests

from Legobot.Lego import Lego


class WikipediaTopFinder(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!wtf'

    def handle(self, message):
        base_url = 'https://en.wikipedia.org/w/index.php?search='
        search_params = '%20'.join(message['text'].split()[1:])
        r = requests.get(base_url + search_params)
        if r.status_code == 200:
            self.reply(message, "I found this: " + r.url)
        else:
            self.reply(message, "I could not reach Wikipedia. Sorry.")

    def get_name(self):
        return 'wtf'

    def get_help(self):
        return 'Wikipedia Top Finder. Search Wikipedia. Usage: !wtf <search string>'
