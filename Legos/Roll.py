import random
from Source.Lego import Lego

class Roll(Lego):
    def listening_for(self, message):
        return message['text'].split()[0] == '!roll'

    def handle(self, message):
        dice_string = message['text'].split()[1]
        if 'd' in dice_string:
            num_dice = int(dice_string.split('d')[0])
            num_sides = int(dice_string.split('d')[1])
        else:
            num_dice = 1
            num_sides = int(dice_string)
        results = [random.randint(1, num_sides) for i in range(num_dice)]
        self.reply(message, 'You Rolled: ' + ' '.join([str(result) for result in results]))
        self.reply(message, 'Your Total: ' + str(sum(results)))

    def get_name(self):
        return 'roll'

    def get_help(self):
        return 'Roll some dice. Usage: !roll 20, !roll 2d8'