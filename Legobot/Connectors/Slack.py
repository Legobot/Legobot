# Legobot
# Copyright (C) 2016 Brenton Briggs, Kevin McCabe, and Drew Bronson

'''
.. module:: Legobot.Connectors.Slack
  :synopsis: A backend for connecting Legobot to Slack

.. moduleauthor:: Bren Briggs

Module lovingly built with inspiration from slackhq's RtmBot
'''

import logging
import re
import sys
import threading
import time

from slackclient import SlackClient

from Legobot.Lego import Lego
from Legobot.Message import Message, Metadata
from Legobot.Utilities import Utilities

logger = logging.getLogger(__name__)

# I forgot why this is here, but it's very necessary.
sys.dont_write_bytecode = True


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
        self.supported_events = {'message': self.on_message}
        self.user_map = {}
        self.slack_client = SlackClient(self.token)
        threading.Thread.__init__(self)

    def connect(self):
        self.slack_client.rtm_connect(reconnect=self.reconnect,
                                      auto_reconnect=self.auto_reconnect)

    def on_message(self, event):
        '''Runs when a message event is received

        Args:
            event: RTM API event.

        Returns:
            Legobot.messge
        '''

        metadata = self._parse_metadata(event)
        message = Message(text=metadata['text'],
                          metadata=metadata).__dict__
        if message.get('text'):
            message['text'] = self.find_and_replace_userids(message['text'])
            message['text'] = self.find_and_replace_channel_refs(
                message['text']
            )
        return message

    def run(self):
        '''Extends the run() method of threading.Thread
        '''

        self.connect()
        while True:
            for event in self.slack_client.rtm_read():
                logger.debug(event)
                if 'type' in event and event['type'] in self.supported_events:
                    event_type = event['type']
                    dispatcher = self.supported_events[event_type]
                    message = dispatcher(event)
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
                name = self.get_user_display_name(match.group(1))
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

    def get_channel_id_by_name(self, name):
        channels = self.get_channels(condensed=True)
        if not channels:
            return name

        if name.startswith('#'):
            name = name[1:]

        channels_transform = {channel.get('name'): channel.get('id')
                              for channel in channels}
        return channels_transform.get(name)

    def get_user_id_by_name(self, name):
        users = self.get_users(condensed=True)
        if not users:
            return name

        if name.startswith('@'):
            name = name[1:]

        users_transform = {}
        for user in users:
            users_transform[user.get('name')] = user.get('id')
            users_transform[user.get('display_name')] = user.get('id')

        if name in users_transform.keys():
            return users_transform[name]
        else:
            return name

    def get_channels(self, condensed=False):
        '''Grabs all channels in the slack team

        Args:
            condensed (bool): if true triggers list condensing functionality

        Returns:
            dic: Dict of channels in Slack team.
                See also: https://api.slack.com/methods/channels.list
        '''

        channel_list = self.slack_client.api_call('channels.list')
        if not channel_list.get('ok'):
            return None

        if condensed:
            channels = [{'id': item.get('id'), 'name': item.get('name')}
                        for item in channel_list.get('channels')]
            return channels
        else:
            return channel_list

    def get_users(self, condensed=False):
        '''Grabs all users in the slack team

        This should should only be used for getting list of all users. Do not
        use it for searching users. Use get_user_info instead.

        Args:
            condensed (bool): if true triggers list condensing functionality

        Returns:
            dict: Dict of users in Slack team.
                See also: https://api.slack.com/methods/users.list
        '''

        user_list = self.slack_client.api_call('users.list')
        if not user_list.get('ok'):
            return None
        if condensed:
            users = [{'id': item.get('id'), 'name': item.get('name'),
                     'display_name': item.get('profile').get('display_name')}
                     for item in user_list.get('members')]
            return users
        else:
            return user_list

    def get_user_display_name(self, userid):
        '''Given a Slack userid, grabs user display_name from api.

        Args:
            userid (string): the user id of the user being queried
        Returns:
            dict: a dictionary of the api response
        '''

        out = userid
        user_info = self.slack_client.api_call('users.info', user=userid)
        if user_info.get('ok'):
            user = user_info.get('user')
            out = user.get('profile', {}).get('display_name')
            if not out:
                out = user.get('name', userid)
        else:
            return userid
        return out

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

    def get_username(self, userid):
        '''Perform a lookup of users to resolve a userid to a username

        Args:
            userid (string): Slack userid to lookup.

        Returns:
            string: Human-friendly name of the user
        '''

        username = self.user_map.get(userid)
        if not username:
            users = self.get_users()
            if users:
                members = {
                    m['id']: m['name']
                    for m in users.get('members', [{}])
                    if m.get('id')
                    and m.get('name')
                }
                if members:
                    self.user_map.update(members)

                username = self.user_map.get(userid, userid)

        return username

    def get_userid_from_botid(self, botid):
        '''Perform a lookup of bots.info to resolve a botid to a userid

        Args:
            botid (string): Slack botid to lookup.
        Returns:
            string: userid value
        '''
        botinfo = self.slack_client.api_call('bots.info', bot=botid)
        if botinfo['ok'] is True:
            return botinfo['bot'].get('user_id')
        else:
            return botid

    def _parse_metadata(self, message):
        '''Parse incoming messages to build metadata dict
        Lots of 'if' statements. It sucks, I know.

        Args:
            message (dict): JSON dump of message sent from Slack

        Returns:
            Legobot.Metadata
        '''

        # Try to handle all the fields of events we care about.
        metadata = Metadata(source=self.actor_urn).__dict__
        metadata['thread_ts'] = message.get('thread_ts')
        metadata['ts'] = message.get('ts')
        if 'presence' in message:
            metadata['presence'] = message['presence']

        if 'text' in message:
            metadata['text'] = message['text']
        elif 'previous_message' in message:
            # Try to handle slack links
            if 'text' in message['previous_message']:
                metadata['text'] = message['previous_message']['text']
            else:
                metadata['text'] = None
        else:
            metadata['text'] = None

        if 'user' in message:
            metadata['source_user'] = message['user']
        elif 'bot_id' in message:
            metadata['source_user'] = self.get_userid_from_botid(
                                      message['bot_id'])
        elif 'message' in message and 'user' in message['message']:
            metadata['source_user'] = message['message']['user']
        else:
            metadata['source_user'] = None

        metadata['user_id'] = metadata['source_user']
        metadata['display_name'] = self.get_username(metadata['source_user'])

        if 'channel' in message:
            metadata['source_channel'] = message['channel']
            # Slack starts DM channel IDs with "D"
            if message['channel'].startswith('D'):
                metadata['is_private_message'] = True
            else:
                metadata['is_private_message'] = False

        metadata['subtype'] = message.get('subtype')
        metadata['source_connector'] = 'slack'

        return metadata

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
