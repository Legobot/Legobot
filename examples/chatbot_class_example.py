from pathlib import Path

from Legobot.Chatbot import Chatbot


bot = Chatbot(Path(__file__).resolve().parent.joinpath('config.yaml'))
bot.run()
