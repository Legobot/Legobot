from __future__ import print_function

import Queue
import datetime
import logging
import random
import re
import select
import socket
import ssl
import string
import threading
import time

import six

import legoCron

__author__ = "Bren Briggs and Kevin McCabe"
__copyright__ = "Copyright 2016"
__license__ = "GPLv2"
__version__ = "0.1"
__status__ = "Beta"

logger = logging.getLogger(__name__)


def _log_me(message, sev_level="INFO", loop_prevent=False):
    """
    This function is used for all textual output from LegoBot, if a logger object has been provided, we will use that
    otherwise we will print to the screen using the format we like best :-D
    """
    message = message.strip()
    if not message:
        return

    try:
        log_fun = getattr(logger, sev_level.lower())
        log_fun(message)

    except AttributeError:
        if loop_prevent:
            # since we call ourselves, we want to make sure it never happens twice.
            print("Entered into a loop while tryping to print: {} at sev: {}".format(message, sev_level))
            raise
        _log_me("Original message could not be logged due to an invalid sev_level of: %s" % sev_level.lower(),
                sev_level="WARNING", loop_prevent=True)
        # TODO referenced before assignment
        log_fun(message)


class RandTimerFunc:
    def __init__(self, func, rand_min, rand_max):
        self.func = func
        self.randMin = rand_min
        self.randMax = rand_max


class LegoBot:
    """
    Legobot is a framework for creating and connecting IRC bots to IRC servers / channels
    """

    def __init__(self, host, port, nick, chans, logfunc="", hostpw="", default_func=None, default_func_char=""):
        """
        Legobot must be initialized with at least a:
        host - IP/FQDN of IRC Server
        port - Port to connect to (6667 if you don't know otherwise)
        nick - Nickname for your bot
        chans - list of tuples like: [("#channel_name","channel password")]

        Optional variables include:
        logfunc - function to be run everytime we read something in from IRC, used for a chat logger
        hostpw - password for the IRC server itself (not the rooms)
        defaultFunc - Function to be run when defaultFuncChar is is seen at the beginning of the line, but the
                      characters following don't match a value in our function dictionary
        defaultFuncChar - Typically IRC bots listen for commands like !help, where the command is predicated by a
                          special character, this signifies what that special character should be so we can listen for
                          all things said starting with that character
        """
        # sanitize user input
        assert isinstance(host, six.string_types)
        assert isinstance(port, six.integer_types)
        assert isinstance(nick, six.string_types)
        assert isinstance(chans, list)
        if logfunc:
            assert hasattr(logfunc, '__call__')
        if hostpw:
            assert isinstance(hostpw, six.string_types)
        if default_func:
            assert hasattr(default_func, '__call__')
        if default_func_char:
            assert isinstance(default_func_char, six.string_types)

        # if bot hasn't defined a handler, create one by default
        # basicConfig only works if a format hasn't already been set
        logging.basicConfig(format="%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s", level=logging.INFO)

        # class variable assignment
        self.host = host  # IP / FQDN of IRC server
        self.hostpw = hostpw  # Password for IRC server
        self.port = port  # Port to connect to
        self.nick = nick  # Nick to use
        self.chans = chans  # List of tuples like [("#channel_name","channel password")]
        self.logfunc = logfunc  # Function to use for all read in information from an irc room, allows chat logging
        self.func = {}  # Function dictionary (should never be added to manually)
        self.timerFuncList = []  # List of functions to be run on a timer
        self.randTimerFuncList = []  # List of functions to be run on a random timer
        self.threadQueue = None  # Queue to be used for communication within threads. Private.
        self.threadList = []  # List of all spun up threads. Private.
        self.funcHelp = {}  # Dictionary of help text for each function

        self.connection = None

        self.defaultFunc = default_func
        # Function to be run anytime defaultFuncChar is seen but no func exists for that command

        self.defaultFuncChar = default_func_char
        # Character that will be looked for at the beginning of a chat message to call defaultFunc

        # add in default help function
        default_char = self.defaultFuncChar or "!"
        self.add_func(name="%shelp" % (default_char,),
                      function=self.default_help,
                      help_text="Function used to display help, this default help value can be overridden with a " +
                                "custom function")

        _log_me("Legobot object successfully initialized", "DEBUG")

    def default_help(self, msg_obj):
        """
        Default function that is used to provide output when users run !help (or help predicated by whatever
        defaultFuncChar is
        This method may be overridden
        """

        # If we ask for help on a particular function, return that functions help
        # Else return list of functions
        if not msg_obj.arg1:
            return "Available functions: %s" % ", ".join(sorted(self.func.keys()))

        try:
            help_text = self.funcHelp[msg_obj.arg1]
            return help_text
        except:
            return "couldn't find help text"

    def add_timer_func(self, function, minute="*", hour="*", day="*", month="*", dow="*", sec="*"):
        self.timerFuncList.append(legoCron.Event(function, minute, hour, day, month, dow, sec))

    def add_default_func(self, func, char):
        # Add a func to run whenever trigger char is seen as the first character if we don't match any
        # Other function
        self.defaultFunc = func
        self.defaultFuncChar = char

    def add_func(self, name, function, help_text=""):
        # Name should be str, function should be a function object (as in a function without the parens)
        self.func[name] = function
        self.funcHelp[name] = help_text

    def add_rand_timer_func(self, func, rand_min, rand_max):
        self.randTimerFuncList.append(RandTimerFunc(func, rand_min, rand_max))

    def batch_add_func(self, d):
        # Merge a dictionary of functions into the existing function dictionary
        self.func.update(d)

    def _send_raw_to_socket(self, txt_to_send):
        _log_me("trying to send to socket: %s" % txt_to_send, "INFO")
        # TODO 'dt' is not used anywhere
        dt = txt_to_send.replace('\x00', '')
        response = self.connection.sendall(txt_to_send)
        _log_me("msg sent, response is: %s" % response)

    def connect(self, is_ssl=False):
        if is_ssl:
            sock = socket.socket()
            self.connection = ssl.wrap_socket(sock)
        else:
            self.connection = socket.socket()

        self.connection.connect((self.host, self.port))
        if self.hostpw:
            self._send_raw_to_socket("PASS %s\r\n" % self.hostpw)

        iterate_nick = True
        orig_nick = self.nick
        i = 0
        while iterate_nick:
            # TO DO: add functionality to create separate nick, realname, etc
            if i:
                self.nick = orig_nick + "_" + str(i)
                _log_me("set new nick to: %s" % self.nick, "WARNING")

            _log_me("Attempting to log in with nick: %s" % self.nick, "INFO")

            self._send_raw_to_socket("NICK %s\r\n" % self.nick)

            self._send_raw_to_socket("USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.nick))

            # Read in socket to check if we got somethign like:
            # :ircd2.abc.com 433 * test_nick :Nickname already in use

            t = datetime.datetime.now()
            iterate_nick = False
            read_line = False

            while not read_line and (datetime.datetime.now() - t).total_seconds() < 60:
                if select.select([self.connection], [], [], 1.0)[0]:
                    readbuffer = self.connection.recv(1024)
                    # Split into lines
                    temp = string.split(readbuffer, "\n")

                    # Iterate through any lines received
                    for line in temp:
                        if len(line.strip(' \t\n\r')) == 0:
                            continue
                        read_line = True

                        if "nick" in line.lower() and "already in use" in line.lower():
                            _log_me("Nick already registered, iterating nick", "WARNING")
                            iterate_nick = True
                            i += 1
                            break
                        _log_me(line, "DEBUG")
                        # Debug level prints all messages back and forth from IRC server including chats
                else:
                    time.sleep(.5)

        time.sleep(1)
        for room, pw in self.chans:
            if pw:
                # TODO this passes too many arguments
                self._send_raw_to_socket("JOIN %s %s\r\n" % room, pw)
            else:
                self._send_raw_to_socket("JOIN %s\r\n" % room)
        self.__listen()

    def __listen(self):
        # Initiate queue to read off of
        self.threadQueue = Queue.Queue()

        # Spin up threads for timerFuncs
        for timerFunc in self.timerFuncList:
            self.threadList.append(threading.Thread(target=timer_daemon,
                                                    args=(timerFunc, self.threadQueue, self.chans)))
            self.threadList[-1].daemon = True
            self.threadList[-1].start()

        # Spin up threads for random timer funcs
        for rand_timer_func in self.randTimerFuncList:
            self.threadList.append(threading.Thread(target=rand_timer_daemon,
                                                    args=(rand_timer_func.func, self.threadQueue,
                                                          rand_timer_func.randMin, rand_timer_func.randMax,
                                                          self.chans)))
            self.threadList[-1].daemon = True
            self.threadList[-1].start()

        while True:
            if select.select([self.connection], [], [], 1.0)[0]:
                read_buffer = self.connection.recv(1024)
                # Split into lines
                temp = string.split(read_buffer, "\n")
                # Iterate through any lines received
                for line in temp:
                    if len(line.strip(' \t\n\r')) == 0:
                        continue
                    _log_me(line, "INFO")
                    msg = Message(line)
                    self.threadList.append(threading.Thread(target=msg.read,
                                                            args=(self.host, self.func, self.nick, self.logfunc,
                                                                  self.threadQueue, self.defaultFunc,
                                                                  self.defaultFuncChar)))
                    self.threadList[-1].daemon = True
                    self.threadList[-1].start()

            while not self.threadQueue.empty():
                response = self.threadQueue.get(block=False)
                if isinstance(response, str) and response.startswith("thread_exception"):
                    _log_me("Thread saw exception: %s" % str(response), "WARNING")
                else:
                    try:
                        self._send_raw_to_socket(response)
                    except:
                        _log_me("Hit error with response: %s" % str(response), "CRITICAL")
                        raise
            time.sleep(0.5)


def sanitize_output(txt_to_send):
    # We'll store our output here
    output_list = []

    # Remove any wrapping blankspace/newlines
    txt_to_send = txt_to_send.strip()

    # Split our lines on \n or \r and strip the result
    lines = [itm.strip() for itm in re.split("\n|\r", txt_to_send) if itm.strip()]

    # If no newlines in output, simply return it
    output_list = lines

    return [output_list[0]]


def timer_daemon(func, q, rooms):
    _log_me("Starting timer daemon for %s" % func.__name__, sev_level="DEBUG")
    temp_val = ""
    while True:
        try:
            _log_me("Checking thread:%s for output" % func.__name__, sev_level="DEBUG")
            temp_val = func.check(datetime.datetime.now())

        except SystemExit:
            _log_me(
                "thread is trying to kill bot, we will allow this - disabling this is not yet allowed," +
                "please open a git issue if you wish to dissalow this for any reason",
                "critical")
            raise

        except Exception as e:
            _log_me("thread_exception: error seen in function: %s, error: %s" % (func.__name__, str(e)), "WARNING")

        if temp_val:
            for room in rooms:
                if isinstance(temp_val, list):
                    for itm in temp_val:
                        for msg in sanitize_output(itm):
                            q.put("PRIVMSG %s :%s\r\n" % (room[0], msg))
                else:
                    for msg in sanitize_output(temp_val):
                        q.put("PRIVMSG %s :%s\r\n" % (room[0], msg))
        time.sleep(0.5)


def rand_timer_daemon(func, q, rand_min, rand_max, rooms):
    # Set random timer
    last_ran = datetime.datetime.now()
    rand_timer = random.randrange(rand_min, rand_max)
    while True:
        # Get diff in now and last ran, run if it's greater than rand_timer
        if (datetime.datetime.now() - last_ran).total_seconds() > rand_timer:
            # Run the function
            try:
                return_val = func()
            except SystemExit:
                _log_me(
                    "thread is trying to kill bot, we will allow this - disabling this is not yet allowed," +
                    " please open a git issue if you wish to disallow this for any reason",
                    "critical")
                raise
            except Exception as e:
                q.put("thread_exception: error seen in function: %s, error: %s" % (func.__name__, str(e)))

            for room in rooms:
                for msg in sanitize_output(return_val):
                    q.put("PRIVMSG %s :%s\r\n" % (room[0], msg))

            # Set last_ran
            last_ran = datetime.datetime.now()

            # Regenerate random timer
            rand_timer = random.randrange(rand_min, rand_max)


class Message:
    def __init__(self, message):
        self.fullMessage = message
        self.splitMessage = message.strip("\r").split(" ", 7)
        self.length = len(self.splitMessage)
        self.userInfo = None
        self.nick = None
        self.actualUserName = None
        self.target = None
        self.cmd = None
        self.arg1 = None
        self.arg2 = None
        self.arg3 = None
        self.allArgs = None
        self.isPM = None
        _log_me(self.fullMessage, "debug")

    def read(self, host, func, nick, logfunc, thread_queue, default_func, default_func_char):
        """
        Parse message from IRC into usable variables
        """

        _log_me("reading message with following attributes: nick:%s, host:%s, defaultFuncChar:%s" % (
            nick, host, default_func_char), "debug")

        self.host = host
        if self.splitMessage[0][0:4] == "PING":
            temp_reply = self.reply(host, {}, nick, default_func, default_func_char)
            if temp_reply:
                thread_queue.put(temp_reply)
                return

        else:
            try:

                # check to see if this was a PM to us
                if "privmsg %s" % nick.lower() in self.fullMessage.lower():
                    self.isPM = True
                else:
                    self.isPM = False

                # Load message lines into self vars
                self.userInfo = self.splitMessage[0].lower()
                self.nick = self.userInfo.split("!")[0][1:]
                self.actualUserName = self.splitMessage[0][1:self.splitMessage[0].find("!")].lower()
                self.target = self.splitMessage[2].lower()
                self.cmd = self.splitMessage[3].lower()
                self.allArgs = self.splitMessage[4:]
                self.arg1 = self.splitMessage[4].lower()
                self.arg2 = self.splitMessage[5].lower()
                self.arg3 = self.splitMessage[6].lower()
            except:
                if len(self.splitMessage) >= 4:
                    if "!" in self.splitMessage[3]:
                        # raise
                        pass
                pass

            if logfunc:
                # Pass line to our logging function
                logfunc(self)

            reply_val = self.reply(host, func, nick, default_func, default_func_char)
            if reply_val:
                if isinstance(reply_val, list):
                    for itm in reply_val:
                        thread_queue.put(itm)
                else:

                    thread_queue.put(reply_val)

    def reply(self, host, func, nick, default_func, default_func_char):
        """
        Quick replies to PING messages, determines if we have a func to be run and calls getReturnVal to execute that
        func if needed
        """
        if self.splitMessage[0][0:4] == "PING":
            return "PONG :%s\r\n" % host

        if self.cmd:
            if self.cmd[1:] in func:
                val = self.get_return_val(func, nick)
                return val

            if len(self.cmd) >= 2:
                if self.cmd[1] == default_func_char:
                    # hack to make this work
                    d = {self.cmd[1:]: default_func}

                    val = self.get_return_val(d, nick)
                    return val

    def get_return_val(self, func, nick):
        """
        Executes the function (func) and creates a list of messages (if any) to return to IRC
        """
        # Get raw return from function
        temp_val = func[self.cmd[1:]](self)

        # Determine what info we got back, tuples would indicate user passed back a room and a message
        if isinstance(temp_val, tuple):
            return_val, return_room = temp_val
        else:
            # We weren't passed a tuple back, assume the user only passed back something to the room which it was sent
            # from
            return_room = ""
            return_val = temp_val

        # If we didn't get anything back, quit
        if not return_val:
            return

        return_list = []
        final_dest = ""

        # Get target to send message to
        if not return_room and self.target.lower() == nick.lower():
            # This was a PM and no room was specified, respond with a PM
            final_dest = self.actualUserName

        elif not return_room:
            # No room was specified and this wasn't a PM, send back to source
            final_dest = self.target

        else:
            # Room was specified use that
            final_dest = return_room

        if isinstance(return_val, six.string_types):
            return_val = [return_val]

        # Iterate through all intended messages back
        for return_msg in return_val:
            # Iterate through all lines of response
            for final_msg in sanitize_output(return_msg):
                return_list.append("PRIVMSG %s :%s\r\n" % (final_dest, final_msg))

        return return_list

    def __len__(self):
        return self.length
