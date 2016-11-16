import threading
import six

from bottle import post, request, run
from pykka.actor import ActorRef
from _thread import LockType

from Legobot.Lego import Lego
from Legobot.Message import *


class HTTPConnecter(Lego):
    def __init__(self, baseplate, lock, host = "localhost", url_path="/lego", http_port=8080):
        assert isinstance(baseplate, ActorRef)
        assert isinstance(lock, LockType)
        assert isinstance(url_path, six.string_types)
        assert len(url_path)>0
        assert len(url_path.split()) == 1
        assert isinstance(http_port, six.integer_types)
        assert isinstance(host, six.string_types)
        
        self.host = host
        self.http_port = http_port
        self.url_path = url_path
        super().__init__(baseplate, lock)
        
    def on_start(self):
        @post(self.url_path)
        def execute_on_post():
            j = request.json
            message = {"text":"some text",
                       "metadata": j}
                       
            message["metadata"]["source"] = self
            message["metadata"]["opts"] = {}
            self.baseplate.tell(message)
        threading.Thread(target=run, kwargs=dict(host=self.host, port=self.http_port, debug=True)).start()
        #run(host=self.host, port=self.http_port, debug=True)
        
    def listening_for(self, message):
        return False

    def handle(self, message):
        logger.info(message)
        pass

    def get_name(self):
        return None
