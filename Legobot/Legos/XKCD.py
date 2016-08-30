from Legobot.Lego import Lego
import requests
import re


class XKCD(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!xkcd'

    def handle(self, message):
        webpage = requests.get('http://dynamic.xkcd.com/random/comic')
        webpage = webpage.text
        print(webpage)
        comic = re.search(r'<div id="comic".*?\n?.*?(//im.+?)".+?\s?title="(.+?)"',webpage)
        if comic:
            altText = comic.group(2).replace("&#39;","'")
            return_val = "%s %s" %(altText,"http:" + comic.group(1))
        else:
            return_val = 'Error encountered.'
        self.reply(message, return_val)

    def get_name(self):
        return 'xkcd'

    def get_help(self):
        return 'Get a random xkcd comic from the web. Usage: !xkcd'
