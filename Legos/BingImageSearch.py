import requests
import random
import re
from Lego import Lego
from Message import *

class BingImageSearch(Lego):
    def __init__(self, baseplate, lock):
        super().__init__(baseplate, lock)
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'


    def listening_for(self, message):
        return '!img'

    def handle(self, message):
        command_end_index = message['text'].find('!img') + 4
        query = ' '.join(message['text'][command_end_index:])
        query = query.replace(' ', '%20')
        req_url = self._make_url(query)
        response = requests.get(req_url)
        urls = []
        for url in re.finditer('"https?://[^"]*\.(jpg|jpeg|png|gif|gifv)"', response.text):
            urls += [url.group(0).strip('"')]
        if len(urls) == 0:
            url = 'Nothing found :('
        else:
            url = random.choice(urls)

        metadata = Metadata(source=self).__dict__()
        message = Message(text=str(url), metadata=metadata).__dict__()
        self.baseplate.tell(message)

    def _make_url(self, query):
        req_url = 'http://www.bing.com/images/search'
        req_url += '?q=' + query
        req_url += '&safesearch=on'
        return req_url
