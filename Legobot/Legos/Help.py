from Legobot.Lego import Lego


class Help(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!help'

    def handle(self, message):
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

        self.reply(message, help_str)

    def get_name(self):
        return None
