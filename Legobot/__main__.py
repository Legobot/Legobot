#!/usr/bin/env python3

import click
from pathlib import Path
from Legobot.Chatbot import Chatbot

@click.command()
@click.option('-c', '--config', default="config.yaml", help="Path to your config, defaults to './config.yaml'")
def main(config):
    bot = Chatbot(Path(__file__).resolve().parent.joinpath(config))
    bot.run()

if __name__ == "__main__":
    main()
