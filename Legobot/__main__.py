#!/usr/bin/env python3

from pathlib import Path
from Legobot.Chatbot import Chatbot

def main():
    bot = Chatbot(Path(__file__).resolve().parent.joinpath('config.yaml'))
    bot.run()

if __name__ == "__main__":
    main()
