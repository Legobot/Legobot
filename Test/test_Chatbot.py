from mock import patch
import os
from pathlib import Path
import sys

import pytest


sys.path.append(str(Path(__file__).parent.joinpath('..').resolve()))


from Legobot import Chatbot   # noqa E402


def test_build_logger():
    logger = Chatbot.build_logger()
    assert logger
    handlers = [h for h in logger.handlers if h.level == 10]
    assert len(handlers) == 1

    logger = Chatbot.build_logger('/tmp/test.log')
    assert logger
    handlers = [h for h in logger.handlers if h.level == 10]
    assert len(handlers) == 2


def test_load_yaml(caplog):
    path = Path(__file__).parent.joinpath('test_chatbot.yaml').resolve()
    resp = Chatbot.load_yaml_file(path)
    assert resp == {'test': 'test'}

    path = str(path)
    resp = Chatbot.load_yaml_file(path)
    assert resp == {'test': 'test'}

    resp = Chatbot.load_yaml_file('bad_file.yaml')
    assert resp is None
    assert 'Error loading bad_file.yaml' in caplog.text

    resp = Chatbot.load_yaml_file('bad_file.yaml', default={})
    assert resp == {}

    with pytest.raises(Exception) as e:
        resp = Chatbot.load_yaml_file('bad_file.yaml', raise_ex=True)
    assert 'No such file or directory' in str(e)


def test_replace_vars():
    assert Chatbot.replace_vars(None) is None
    assert Chatbot.replace_vars(True) is True
    assert Chatbot.replace_vars(1) == 1

    data = ['abc', '123']
    assert Chatbot.replace_vars(data) == data

    data = {'abc': '123'}
    assert Chatbot.replace_vars(data) == data

    data = '${{ENV::TEST}}'
    os.environ['TEST'] = 'TEST DATA'
    assert Chatbot.replace_vars(data) == 'TEST DATA'

    data = '${{LIST::ITEM1, ITEM2}}'
    assert Chatbot.replace_vars(data) == ['ITEM1', 'ITEM2']


@patch('pykka.ThreadingActor.start')
def test_chatbot(mock_start):
    config_path = Path(__file__).parent.joinpath(
        '..', 'examples', 'chatbot_config.yaml')
    chatbot = Chatbot.Chatbot(config_path)

    schema_draft = 'http://json-schema.org/draft-07/schema#'
    assert chatbot.schema['$schema'] == schema_draft
    assert 'IRC' in chatbot.config['connectors']

    chatbot.initialize_baseplate()
    assert chatbot.baseplate
    assert chatbot.baseplate_proxy
    chatbot.stop()
    assert not chatbot.baseplate_proxy
    assert not chatbot.baseplate

    chatbot.initialize_baseplate()
    lego_config = {
        'enabled': False,
        'path': 'Legobot.Test.test_Chatbot.TestLego',
        'kwargs': {}
    }
    chatbot.add_lego('TestLego', lego_config, 'legos')
    assert chatbot.legos == []
    lego_config['enabled'] = True
    chatbot.add_lego('TestLego', lego_config, 'legos')
    assert chatbot.legos == ['TestLego']
    chatbot.stop()
