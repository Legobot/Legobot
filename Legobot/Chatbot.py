import logging
from pathlib import Path
from pydoc import locate
import threading

from jsonschema import validate
import yaml

from Legobot.Lego import Lego


DIR = Path(__file__).resolve().parent
HELP_PATH = 'Legobot.Legos.Help.Help'


def build_logger(log_file=None):
    if log_file:
        logging.basicConfig(filename=log_file)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)

    return logger


def load_yaml_file(path, default=None, raise_ex=None, logger=None):
    if not logger:
        logger = build_logger()

    if not isinstance(path, Path):
        path = Path(path)

    try:
        with path.open() as f:
            out = yaml.safe_load(f)

        logger.debug(f'Loaded {path} successfully.')
    except Exception as e:
        out = default
        if raise_ex is True:
            raise(e)
        else:
            logger.error(f'Error loading {path}:\n {e}\nReturning default.')

    return out


class Chatbot(object):
    def __init__(self, config_path=None):
        self.schema = load_yaml_file(
            DIR.joinpath('chatbot_schema.yaml'), raise_ex=True)
        self.config = self.load_config(config_path)
        self.logger = build_logger(self.config.get('log_file'))
        self.baseplate = None
        self.baseplate_proxy = None
        self.connectors = []
        self.legos = []

    def load_config(self, config_path):
        config = load_yaml_file(config_path, raise_ex=True)
        validate(config, self.schema)
        return config

    def initialize_baseplate(self):
        lock = threading.Lock()
        self.baseplate = Lego.start(None, lock)
        self.baseplate_proxy = self.baseplate.proxy()

    def add_lego(self, name, config, lego_type):
        if config['enabled'] is True:
            try:
                self.baseplate_proxy.add_child(
                    locate(config['path']), **config.get('kwargs', {}))

                if lego_type == 'connectors':
                    self.connectors.append(name)
                elif lego_type == 'legos':
                    self.legos.append(name)

            except Exception as e:
                self.logger.error(f'Error adding {name} to {lego_type}: {e}')

    def run(self):
        if not self.baseplate:
            self.initialize_baseplate()

        if self.config['helpEnabled'] is True:
            self.add_lego(
                'Help', {'enabled': True, 'path': HELP_PATH}, 'legos')

        for connector, config in self.config['connectors'].items():
            self.add_lego(connector, config, 'connectors')

        for lego, config in self.config['legos'].items():
            self.add_lego(lego, config, 'legos')

    def stop(self):
        self.baseplate.stop()
        self.baseplate_proxy = None
        self.baseplate = None
