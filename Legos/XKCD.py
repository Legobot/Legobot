from Source.Lego import Lego
import urllib3
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
            returnVal = "%s %s" %(altText,"http:" + comic.group(1))
        self.reply(message, returnVal)