import logging
from Legobot.Lego import Lego

logger = logging.getLogger(__name__)

class Help(Lego):
    def handle(self, message):
        logger.critical("help called with message: {}".format(message))
        try:
            target = message['metadata']['source_channel']
        except IndexError:
            logger.error('Could not identify message source in message: %s' % str(message))
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
                    name = lego_proxy.get_name().get()
                    if name: lego_names.append(name)
                    
            help_str = 'Available functions: {functions}'.format(functions = ', '.join(sorted(lego_names)))
        if function:
            for lego in legos:
                lego_proxy = lego.proxy()
                if lego_proxy.get_name().get() == function:
                    help_str = lego_proxy.get_help().get()
        
        opts = {'target':target}
        self.reply(message, help_str, opts=opts)