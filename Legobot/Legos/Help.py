# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

import logging

from Legobot.Lego import Lego
from Legobot.Utilities import Utilities

logger = logging.getLogger(__name__)


class Help(Lego):
    @staticmethod
    def listening_for(message):
        if Utilities.isNotEmpty(message['text']):
            try:
                return message['text'].split()[0] == '!help'
            except Exception as e:
                logger.error(
                    'Help lego failed to check message text: {0!s}'.format(e))
                return False

    def handle(self, message):
        logger.info(message)
        try:
            target = message['metadata']['source_channel']
        except IndexError:
            logger.error('Could not identify message source in message: {0!s}'
                         .format(str(message)))
        try:
            function = message['text'].split()[1]
        except IndexError:
            function = None

        baseplate_proxy = self.baseplate.proxy()
        legos = baseplate_proxy.children.get()

        help_str = 'No help is available. Sorry.'

        if not function:
            lego_names = []
            for lego in legos:
                lego_proxy = lego.proxy()
                if lego_proxy.get_name().get() is not None:
                    lego_names.append(lego_proxy.get_name().get())
            help_str = 'Available functions: ' + ', '.join(lego_names)

        if function:
            for lego in legos:
                lego_proxy = lego.proxy()
                if lego_proxy.get_name().get() == function:
                    help_str = lego_proxy.get_help().get()

        opts = {'target': target}

        self.reply(message, help_str, opts=opts)

    @staticmethod
    def get_name():
        return None
