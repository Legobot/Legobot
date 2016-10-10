import dice
from Legobot.Lego import Lego


class Roll(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!roll'

    def handle(self, message):
        dice_string = message['text'].split()[1]
        results = dice.roll(dice_string)
        results_str = ', '.join([str(result) for result in results])
        txt = "You Rolled: %s" % results_str
        self.reply(message, txt)

    def get_name(self):
        return 'roll'

    def get_help(self):
        help_text = "Roll some dice. Usage: " \
                    "!roll 2d6t, !roll 6d6^3, !roll d20"
        return help_text
