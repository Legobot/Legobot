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
        try:
            function = message['text'].split()[1]
        except IndexError:
            function = None

        baseplate_proxy = self.baseplate.proxy()
        legos = baseplate_proxy.children.get()

        help_str = 'No help is available. Sorry.'

        # create a diction of legos that have names, indexed by lowercase name
        legos = {
            lego.proxy().get_name().get().lower(): {
                'name': lego.proxy().get_name().get(),
                'lego': lego
            }
            for lego in legos
            if lego.proxy().get_name().get()
            and lego.proxy().get_name().get() != '?'
        }
        lego_names = [v.get('name') for k, v in legos.items()]

        if not function:
            help_str = 'Available functions: ' + ', '.join(lego_names)

        if function and function.lower() in legos.keys():
            lego = legos[function.lower()].get('lego')
            try:
                sub = message['text'].split()[2]
                try:
                    help_str = lego.proxy().get_help(sub=sub).get()
                except (TypeError, KeyError):
                    help_str = '{} has no information on {}'.format(
                        function, sub)
            except IndexError:
                help_str = lego.proxy().get_help().get()

        opts = self.build_reply_opts(message)

        self.reply(message, help_str, opts=opts)

    @staticmethod
    def get_name():
        return None
