# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

'''
.. module:: Legobot.Connectors.Slack
  :synopsis: A backend for connecting Legobot to Slack

.. moduleauthor:: Bren Briggs

Module lovingly built with inspiration from slackhq's RtmBot
'''

import logging
import os
import re
import sys
import threading
import time

import jmespath
from slackclient import SlackClient
import yaml

from Legobot.Lego import Lego
from Legobot.Message import Message
from Legobot.Message import Metadata
from Legobot.Utilities import JMESPATH_OPTIONS
from Legobot.Utilities import Utilities

logger = logging.getLogger(__name__)

# I forgot why this is here, but it's very necessary.
sys.dont_write_bytecode = True


CONFIG_DIR = os.path.join(
    os.path.abspath(os.path.dirname(__file__)),
    '..',
    'Config'
)


class RtmBot(threading.Thread, object):
    """
    Creates a Slack bot using the Slackclient RTM API

    Attributes:
        baseplate: The parent pykka actor
        token: The Slack API token
        last_ping: Timestamp of last keepalive ping
        actor_urn: URN of the Pykka actor the RtmBot runs in
        supported_events: dict of Slack RTM API events we care about
        slack_client: initialized RTM client
    """

    def __init__(self, baseplate, token, actor_urn, reconnect=True,
                 *args, **kwargs):
        """Initializes RtmBot

        Args:
            baseplate (Legobot.Lego): The parent Pykka actor.
                Typically passed in fromLegobot.Connectors.Slack.Slack
            token (string): Slack API token
            actor_urn (string): URN of Pykka actor launching RtmBot
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Returns an instance of RtmBot which connects to Slack.
        """
        self.baseplate = baseplate
        self.token = token
        self.last_ping = 0
        self.actor_urn = actor_urn
        self.reconnect = reconnect
        self.auto_reconnect = True
        # 'event':'method'
        self.user_map = {}
        self.slack_client = SlackClient(self.token)
        self.get_channels()
        self.get_users()
        self.parse_configs()
        threading.Thread.__init__(self)

    def parse_configs(self):
        with open(os.path.join(CONFIG_DIR, 'type_configs.yaml')) as f:
            configs = yaml.safe_load(f)

        self.supported_events = configs.keys()
        self.meta_xforms = {}
        self.meta_methods = {}
        self.msg_kwargs = {}

        for event_type, config in configs.items():
            meta = config.get('metadata', {})
            self.meta_xforms[event_type] = self.compile_transforms(
                meta.get('transform'))
            self.meta_methods[event_type] = meta.get('methods', {})
            msg = config.get('message', {})
            self.msg_kwargs[event_type] = msg.get('kwargs', {})

    def compile_transforms(self, transform):
        if not transform:
            trans_str = '@'
        else:
            elements = [f'{k}: {v}' for k, v in transform.items()]
            trans_str = '{' + ', '.join(elements) + '}'

        return jmespath.compile(trans_str)

    def connect(self):
        self.slack_client.rtm_connect(reconnect=self.reconnect,
                                      auto_reconnect=self.auto_reconnect)

    def parse_config_item(self, item, event, meta):
        data_map = {
            '$event': event,
            '$metadata': meta
        }
        items = item.split('.')
        if len(items) == 1:
            return data_map.get(item, item)
        else:
            transform = jmespath.compile('.'.join(items[1:]))
            data = data_map.get(items[0], {})
            return transform.search(data, JMESPATH_OPTIONS)

    def parse_method_args(self, args, event, meta):
        out = []
        for arg in args:
            if isinstance(arg, str):
                out.append(self.parse_config_item(arg, event, meta))
            else:
                out.append(arg)

        return out

    def on_event(self, event_type, event):
        '''Runs when a message event is received

        Args:
            event: RTM API event.

        Returns:
            Legobot.messge
        '''

        metadata = Metadata(source=self.actor_urn).__dict__
        transform = self.meta_xforms.get(event_type)
        if transform:
            metadata.update(transform.search(event, JMESPATH_OPTIONS))

        for key, config in self.meta_methods.get(event_type, {}).items():
            args = self.parse_method_args(config.get(
                'args', []), event, metadata)
            metadata[key] = getattr(self, config['method'])(*args)

        msg_kwargs = {}
        for k, v in self.msg_kwargs.get(event_type, {}).items():
            msg_kwargs[k] = self.parse_config_item(v, event, metadata)

        message = Message(**msg_kwargs).__dict__

        text = message.get('text')
        if text:
            text = self.find_and_replace_userids(text)
            message['text'] = self.find_and_replace_channel_refs(text)

        return message

    def run(self):
        '''Extends the run() method of threading.Thread
        '''

        self.connect()
        while True:
            for event in self.slack_client.rtm_read():
                logger.debug(event)
                event_type = event.get('type', '')
                if event_type in self.supported_events:
                    message = self.on_event(event_type, event)
                    logger.debug(message)
                    self.baseplate.tell(message)
            self.keepalive()
            time.sleep(0.1)
        return

    def find_and_replace_userids(self, text):
        '''Finds occurrences of Slack userids and attempts to replace them with
           display names.

        Args:
            text (string): The message text
        Returns:
            string: The message text with userids replaced.
        '''

        match = True
        pattern = re.compile('<@([A-Z0-9]{9})>')
        while match:
            match = pattern.search(text)
            if match:
                name = self.get_user_name_by_id(
                    match.group(1), return_display_name=True, default='')
                text = re.sub(re.compile(match.group(0)), '@' + name, text)

        return text

    def find_and_replace_channel_refs(self, text):
        '''Find occurrences of Slack channel referenfces and attempts to
           replace them with just channel names.

        Args:
            text (string): The message text
        Returns:
            string: The message text with channel references replaced.
        '''

        match = True
        pattern = re.compile('<#([A-Z0-9]{9})\|([A-Za-z0-9-]+)>')
        while match:
            match = pattern.search(text)
            if match:
                text = text.replace(match.group(0), '#' + match.group(2))

        return text

    def get_channel_name_by_id(self, id, default=None):
        '''Given a slack channel id return the channel's name.

        Args:
            id (string): The channel id
            default: The default value to return if no match is found

        Returns:
            string | default: The channel name or default provided
        '''

        ch = self.channels_by_id.get(id, {})
        if not ch:
            self.get_channels()
            ch = self.channels_by_id.get(id, {})

        return ch.get('name', default)

    def get_channel_id_by_name(self, name, default=None):
        '''Given a slack channel name return the channel's id.

        Args:
            name (string): The channel name
            default: The default value to return if no match is found

        Returns:
            string | default: The channel id or default provided
        '''

        ch = self.channels_by_name.get(name, {})
        if not ch:
            self.get_channels()
            ch = self.channels_by_name.get(name, {})

        return ch.get('id', default)

    def get_channels(self):
        '''Grabs all channels in the slack team. Stores them by name and by id
           as class properties.
        '''

        channels = []
        cursor = None
        params = {
            'exclude_archived': False,
            'limit': 50
        }
        while True:
            if cursor:
                params['cursor'] = cursor
            channel_list = self.slack_client.api_call(
                'conversations.list', **params)
            channels += channel_list.get('channels', [])
            cursor = channel_list.get(
                'response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        self.channels_by_id = {ch.get('id'): ch for ch in channels}
        self.channels_by_name = {ch.get('name'): ch for ch in channels}

    def get_user_id_by_name(self, name, default=None):
        '''Given a slack user name return the user's id.

        Args:
            name (string): The user name
            default: The default value to return if no match is found

        Returns:
            string | default: The user id or default provided
        '''

        if name.startswith('@'):
            name = name[1:]

        u = self.users_by_name.get(name, self.users_by_display_name.get(name))
        if not u:
            self.get_users()
            u = self.users_by_name.get(name, self.users_by_display_name.get(
                name, {}))

        return u.get('id', default)

    def get_user_name_by_id(self, id, return_display_name=None, default=None):
        '''Given a Slack userid, return user name or display_name.

        Args:
            id (string): the user id of the user being queried
            return_display_name (bool): return profile display name instead of
                user name
            default: default value to return if no match is found
        Returns:
            dict: a dictionary of the api response
        '''

        u = self.users_by_id.get(id)
        if not u:
            self.get_users()
            u = self.users_by_id.get(id, {})

        if return_display_name:
            return u.get('profile', {}).get('display_name', default)
        else:
            return u.get('name', default)

    def get_users(self):
        '''Grabs all users in the slack team and stores them in the connector.

        This should should only be used for getting list of all users. Do not
        use it for searching users. Use get_user_info instead.
        '''

        users = []
        cursor = None
        params = {
            'include_locale': True,
            'limit': 50
        }
        while True:
            if cursor:
                params['cursor'] = cursor
            user_list = self.slack_client.api_call('users.list', **params)
            users += user_list.get('members', [])
            cursor = user_list.get('response_metadata', {}).get('next_cursor')
            if not cursor:
                break

        self.users_by_id = {u.get('id'): u for u in users}
        self.users_by_name = {u.get('name'): u for u in users}
        self.users_by_display_name = {
            u.get('profile', {}).get('display_name'): u for u in users}

    def get_dm_channel(self, userid):
        '''Perform a lookup of users to resolve a userid to a DM channel

        Args:
            userid (string): Slack userid to lookup.

        Returns:
            string: DM channel ID of user
        '''

        dm_open = self.slack_client.api_call('im.open', user=userid)
        return dm_open['channel']['id']

    def post_attachment(self, attachment):
        self.slack_client.api_call('chat.postMessage', **attachment)

    def get_userid_from_botid(self, botid):
        '''Perform a lookup of bots.info to resolve a botid to a userid

        Args:
            botid (string): Slack botid to lookup.
        Returns:
            string: userid value
        '''

        if not botid:
            return None

        botinfo = self.slack_client.api_call('bots.info', bot=botid)
        if botinfo['ok'] is True:
            return botinfo['bot'].get('user_id')
        else:
            return botid

    def keepalive(self):
        '''Sends a keepalive to Slack
        '''
        # hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now


class Slack(Lego):
    '''Lego that builds and connects Legobot.Connectors.Slack.RtmBot

    Args:
        baseplate (Legobot.Lego): baseplate/parent lego (Pykka Actor)
        lock (threading.Lock: thread lock created in your bot script.
            All legos should share the same lock.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.
    '''

    def __init__(self, baseplate, lock, *args, **kwargs):
        super().__init__(baseplate, lock)
        self.botThread = RtmBot(baseplate, actor_urn=self.actor_urn,
                                *args, **kwargs)

    def on_start(self):
        '''Extends pykka's on_start method to launch this as an actor
        '''

        self.botThread.start()

    def listening_for(self, message):
        '''Describe what this should listen for (hint: everything)
        Extends Legobot.Lego.listening_for()

        Args:
            message (Legobot.Message): Message to handle

        Returns:
            bool: True if lego is interested in the message.
        '''

        return str(self.botThread) != str(message['metadata']['source'])

    def build_attachment(self, text, target, attachment, thread):
        '''Builds a slack attachment.

        Args:
            message (Legobot.Message): message w/ metadata to send.

        Returns:
            attachment (dict): attachment data.
        '''

        attachment = {
            'as_user': True,
            'text': text,
            'channel': target,
            'attachments': [
                {
                    'fallback': text,
                    'image_url': attachment
                }
            ]
        }
        if thread:
            attachment['thread_ts'] = thread
        return attachment

    def handle(self, message):
        '''Attempts to send a message to the specified destination in Slack.
        Extends Legobot.Lego.handle()

        Args:
            message (Legobot.Message): message w/ metadata to send.
        '''

        logger.debug(message)
        if Utilities.isNotEmpty(message['metadata']['opts']):
            target = message['metadata']['opts']['target']
            thread = message['metadata']['opts'].get('thread')
            # pattern = re.compile('@([a-zA-Z0-9._-]+)')
            pattern = re.compile('^@([a-zA-Z0-9._-]+)|\s@([a-zA-Z0-9._-]+)')
            matches = re.findall(pattern, message['text'])
            matches = set(matches)
            logger.debug('MATCHES!!!!   {}'.format(matches))
            for match in matches:
                if isinstance(match, tuple):
                    if match[0] != '':
                        match = match[0]
                    else:
                        match = match[1]
                if not match.startswith('@'):
                    match = '@' + match
                message['text'] = message['text'].replace(
                    match,
                    '<{}>'.format(match)
                )

            pattern = re.compile('#([A-Za-z0-9-]+)')
            matches = re.findall(pattern, message['text'])
            matches = set(matches)
            for match in matches:
                channel_id = self.botThread.get_channel_id_by_name(match)
                if channel_id:
                    message['text'] = message['text'].replace(
                        '#' + match,
                        '<#{}|{}>'.format(
                            channel_id,
                            match
                        )
                    )

            if (message['text'].find('<<@') != -1
                    or message['text'].find('<<#') != -1):
                message['text'] = message['text'].replace('<<', '<')
                message['text'] = message['text'].replace('>>', '>')

            if target.startswith('U'):
                target = self.botThread.get_dm_channel(target)
            attachment = message['metadata']['opts'].get('attachment')
            if attachment:
                text = message['metadata']['opts'].get('fallback')
                attachment = self.build_attachment(
                    text, target, attachment, thread)
                self.botThread.post_attachment(attachment)
            else:
                self.botThread.slack_client.rtm_send_message(
                    target, message['text'], thread=thread)

    @staticmethod
    def get_name():
        '''Called by built-in !help lego
        Returns name of Lego. Returns none because this is
        a non-interactive Lego
        '''

        return None
