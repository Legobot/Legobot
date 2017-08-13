import logging, time
from Legobot.Lego import Lego
import requests

logger = logging.getLogger(__name__)

class Factoids(Lego):
    """Class to hold all factoids
    Args: Lego
    """
    def listening_for(self, message):
        """Checks if the message contains a command that we need to execute
        Args:
            self:
            message: The complete line/message that comes from an IRC channel

        Returns:
            Bool: Returns true if the first word in the message is a command for this class
        """
        self.cmds = ['!newlines', '!oneline']
        return message['text'].split()[0] in self.cmds 
    def handle(self, message):
        """Execute the needed command
        Args:
            self:
            message: The complete line/message that comes from an IRC channel

        Returns:
            string: Returns the suitable factoid"""
        opts = None
        logger.info(message)
        try:
            target = message['metadata']['source_channel']
            opts = {'target':target}
        except IndexError:
            logger.error('Could not identify message source in message: %s' % str(message))
        command = message['text'].split()[0]
        if command == '!newlines':
            self.reply(message, 'This\nmessage\nhas\nnewlines', opts)
        if command == '!oneline':
            self.reply(message, 'This is a short message on a single line', opts)

    def get_name(self):
        """Returns the name of this class
        Args:
            self:

        Returns:
            string: The name of this class
        """
        return 'factoids'

    def get_help(self):
        """Prints a useful help message into the channel

        Args:
            self:

        Returns:
            String: A help message that explains this class
        """
        help_text = "Collection of responses providing links to resources. "
        return help_text
