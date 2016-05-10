import socket
import select
import string
import ssl
import threading
import Queue
import datetime
import time
import legoCron
import random
import logging
import six
import re
import sys

__author__ = "Bren Briggs and Kevin McCabe"
__copyright__ = "Copyright 2016"
__license__ = "GPLv2"
__version__ = "0.1"
__status__ = "Beta"

logger = logging.getLogger(__name__)


def _log_me(message, sev_level = "INFO", loop_prevent = False):
  """
  This function is used for all textual output from LegoBot, if a logger object has been provided, we will use that
  otherwise we will print to the screen using the format we like best :-D
  """
  message = message.strip()
  if not message:
    return
    
  try:
    logFun = getattr(logger, sev_level.lower())
    logFun(message)
    
  except AttributeError:
    if loop_prevent:
      #since we call ourselves, we want to make sure it never happens twice.
      print "Entered into a loop while tryping to print: {} at sev: {}".format(message, sev_level)
      raise
    _log_me("Original message could not be logged due to an invalid sev_level of: %s" % sev_level.lower(), sev_level = "WARNING", loop_prevent = True)
    
    logFun(message)

"""
Depricated, now we use legoCron
class timerFunc():
  def __init__(self, func, interval = -1, timeOfDay=None, chans = []):
    self.func = func
    self.interval = interval
    self.lastRun = datetime.datetime.fromordinal(1)
    self.timeOfDay = timeOfDay
    self.chans = chans

  def runIfNeeded(self):
    if (datetime.datetime.now() - self.lastRun).total_seconds() > self.interval and self.interval != -1:
      #run
      self.func()
      self.lastRun = datetime.datetime.now()
"""

class randTimerFunc():
  def __init__(self, func, randMin, randMax):
    self.func = func
    self.randMin = randMin
    self.randMax = randMax

class legoBot():
  """
  Legobot is a framework for creating and connecting IRC bots to IRC servers / channels
  """
  def __init__(self,host,port,nick,chans, logfunc = "", hostpw = "", defaultFunc = None, defaultFuncChar = ""):
    """
    Legobot must be initialized with at least a:
    host - IP/FQDN of IRC Server
    port - Port to connect to (6667 if you don't know otherwise)
    nick - Nickname for your bot
    chans - list of tuples like: [("#channel_name","channel password")]
    
    Optional variables include:
    logfunc - function to be run everytime we read something in from IRC, used for a chat logger
    hostpw - password for the IRC server itself (not the rooms)
    defaultFunc - Function to be run when defaultFuncChar is is seen at the beginning of the line, but the characters following don't match a value in our function dictionary
    defaultFuncChar - Typically IRC bots listen for commands like !help, where the command is predicated by a special character, this signifies what that special character should be so we can listen for all things said starting with that character
    """
    #sanitize user input
    assert isinstance(host, six.string_types)
    assert isinstance(port, six.integer_types)
    assert isinstance(nick, six.string_types)
    assert isinstance(chans, list)
    if logfunc: assert hasattr(logfunc, '__call__')
    if hostpw: assert isinstance(hostpw, six.string_types)
    if defaultFunc: assert hasattr(defaultFunc, '__call__')
    if defaultFuncChar: assert isinstance(defaultFuncChar, six.string_types)
    
    #if bot hasn't defined a handler, create one by default
    #basicConfig only works if a format hasn't already been set
    logging.basicConfig(format="%(asctime)s - [%(name)s] - [%(levelname)s] - %(message)s", level = logging.INFO)
    
    #class variable assignment
    self.host = host                        #ip / fqdn of irc server
    self.hostpw = hostpw                    #password for irc server
    self.port = port                        #port to connect to
    self.nick = nick                        #nick to use
    self.chans = chans                      #list of tuples like [("#channel_name","channel password")]
    self.logfunc = logfunc                  #function to use for all read in information from an irc room, allows chat logging
    self.func = {}                          #function dictionary (should never be added to manually)
    self.timerFuncList = []                 #list of functions to be run on a timer
    self.randTimerFuncList = []             #list of functions to be run on a random timer
    self.threadQueue = None                 #queue to be used for communication within threads, internal only
    self.threadList = []                    #used internally only, list of all spun up threads
    self.funcHelp = {}                      #dictionary of help text for each function
    self.defaultFunc = defaultFunc          #function to be run anytime defaultFuncChar is seen but no func exists for that command
    self.defaultFuncChar = defaultFuncChar  #character that will be looked for at the beginning of a chat message to call defaultFunc
    
    #add in default help function
    default_char = self.defaultFuncChar or "!"
    self.addFunc(name = "%shelp" % (default_char,),
                 function = self.defaultHelp,
                 helpText = "Function used to display help, this default help value can be overridden with a custom function")
    
    _log_me("Legobot object successfully initialized","DEBUG")
    
  
  def defaultHelp(self, msgObj):
    """
    Default function that is used to provide output when users run !help (or help predicated by whatever defaultFunchChar is
    This method may be overridden
    """
    
    #if we ask for help on a particular function, return that functions help, otherwise return list of functions
    if not msgObj.arg1:
      return "Available functions: %s" % ", ".join(sorted(self.func.keys()))
    
    try:
      helpText = self.funcHelp[msgObj.arg1]
      return helpText
    except:
      return "couldn't find help text"
  
  def addTimerFunc(self, function, min = "*", hour = "*", day = "*", month="*", dow="*", sec = "*"):
    self.timerFuncList.append(legoCron.Event(function, min, hour, day, month, dow, sec))
  
  def addDefaultFunc(self, func, char):
    #adds a func to run whenever trigger char is seen as the first character if we don't match any
    #other function
    self.defaultFunc = func
    self.defaultFuncChar = char
  
  def addFunc(self, name, function, helpText = ""):
    #name should be str, function should be a function object (as in a function without the parens)
    self.func[name] = function
    self.funcHelp[name] = helpText
  
  def addRandTimerFunc(self, func, randMin, randMax):
    self.randTimerFuncList.append(randTimerFunc(func, randMin, randMax))
  
  def batchAddFunc(self, d):
    #merge a dictionary of functions into the existing function dictionary
    self.func.update(d)
  
  def _send_raw_to_socket(self, txt_to_send):
    _log_me("trying to send to socket: %s" % txt_to_send, "INFO")
    #dt = txt_to_send.decode("ascii", errors="ignore")
    #_log_me("ascii only text: {}".format(dt))
    #print [dt]
    #remove null char \x00 as it causes problems
    dt = txt_to_send.replace('\x00', '')
    response = self.connection.sendall(txt_to_send)
    
    _log_me("msg sent, response is: %s" % response)
  
  def connect(self, isSSL=False):
    if isSSL:
      sock=socket.socket()
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
      #TO DO: add functionality to create separate nick, realname, etc
      if i:
        self.nick = orig_nick + "_" + str(i)
        _log_me("set new nick to: %s" % self.nick, "WARNING")
      
      _log_me("Attempting to log in with nick: %s" % self.nick, "INFO")
      
      self._send_raw_to_socket("NICK %s\r\n" % self.nick)

      self._send_raw_to_socket("USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.nick))
    
      #read in socket to check if we got somethign like:
      # :ircd2.abc.com 433 * test_nick :Nickname already in use

      t = datetime.datetime.now()
      iterate_nick = False
      read_line = False
      
      while not read_line and (datetime.datetime.now() - t).total_seconds() < 60:
        if select.select([self.connection],[],[],1.0)[0]:
          readbuffer = self.connection.recv(1024)
          #split into lines
          temp = string.split(readbuffer, "\n")
          
          #iterate through any lines received
          for line in temp:
            if len(line.strip(' \t\n\r')) == 0:
              continue
            read_line = True
            
            if "nick" in line.lower() and "already in use" in line.lower():
              _log_me("Nick already registered, iterating nick", "WARNING")
              iterate_nick = True
              i += 1
              break
            _log_me(line, "DEBUG") #debug level prints all messages back and forth from IRC server including chats
        else:
          time.sleep(.5)
    
    
    time.sleep(1)
    for room, pw in self.chans:
      if pw:
        self._send_raw_to_socket("JOIN %s %s\r\n" % room, pw)
      else:
        self._send_raw_to_socket("JOIN %s\r\n" % room)
    self.__listen()
  
  def __listen(self):
    #initiate queue to read off of
    self.threadQueue = Queue.Queue()
    
    #spin up threads for timerFuncs
    for timerFunc in self.timerFuncList:
      self.threadList.append(threading.Thread(target=timerDaemon, args=(timerFunc, self.threadQueue, self.chans)))
      self.threadList[-1].daemon = True
      self.threadList[-1].start()
    
    #spin up threads for random timer funcs
    for randTimerFunc in self.randTimerFuncList:
      self.threadList.append(threading.Thread(target=randTimerDaemon, args=(randTimerFunc.func, self.threadQueue, randTimerFunc.randMin, randTimerFunc.randMax, self.chans)))
      self.threadList[-1].daemon = True
      self.threadList[-1].start()
    
    while True:
      if select.select([self.connection],[],[],1.0)[0]:
        readbuffer = self.connection.recv(1024)
        #split into lines
        temp = string.split(readbuffer, "\n")
    
        #iterate through any lines received
        for line in temp:
          if len(line.strip(' \t\n\r')) == 0:
            continue
          _log_me(line, "INFO")
          msg = Message(line)
          self.threadList.append(threading.Thread(target= msg.read, args = (self.host, self.func, self.nick, self.logfunc, self.threadQueue, self.defaultFunc, self.defaultFuncChar)))
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
  #we'll store our output here
  output_list = []
  
  #remove any wrapping blankspace/newlines
  txt_to_send = txt_to_send.strip()
  
  #split our lines on \n or \r and strip the result
  lines = [itm.strip() for itm in re.split("\n|\r", txt_to_send) if itm.strip()]
  
  #if no newlines in output, simply return it
  output_list = lines
  
  return [output_list[0]]

def timerDaemon(func, q, rooms):
  _log_me("Starting timer daemon for %s" % func.__name__, sev_level="DEBUG")
  tempVal = ""
  while True:
    try:
      _log_me("Checking thread:%s for output" % func.__name__, sev_level="DEBUG")
      tempVal = func.check(datetime.datetime.now())
      
    except SystemExit:
        _log_me("thread is trying to kill bot, we will allow this - disabling this is not yet allowed, please open a git issue if you wish to dissalow this for any reason", "critical")
        raise
    
    except Exception as e:
      _log_me("thread_exception: error seen in function: %s, error: %s" % (func.__name__, str(e)), "WARNING")
      
    if tempVal:
      for room in rooms:
        if isinstance(tempVal, list):
          for itm in tempVal:
            for msg in sanitize_output(itm):
              q.put("PRIVMSG %s :%s\r\n" % (room[0], msg))
        else:
          for msg in sanitize_output(tempVal):
            q.put("PRIVMSG %s :%s\r\n" % (room[0], msg))
    time.sleep(0.5)

def randTimerDaemon(func, q, randMin, randMax, rooms):
  #set random timer
  lastRan = datetime.datetime.now()
  randTimer = random.randrange(randMin, randMax)
  while True:
    #get diff in now and last ran, run if it's greater than randTimer
    if (datetime.datetime.now() - lastRan).total_seconds() > randTimer:
      #run the function
      try:
        returnVal = func()
      except SystemExit:
        _log_me("thread is trying to kill bot, we will allow this - disabling this is not yet allowed, please open a git issue if you wish to dissalow this for any reason", "critical")
        raise
      except Exception as e:
        q.put("thread_exception: error seen in function: %s, error: %s" % (func.__name__, str(e)))
        
      for room in rooms:
        for msg in sanitize_output(returnVal):
          q.put("PRIVMSG %s :%s\r\n" % (room[0], msg))
      
      #set lastRan
      lastRan = datetime.datetime.now()
      
      #regenerate random timer
      randTimer = random.randrange(randMin, randMax)

class Message():
  def __init__(self, message):
    self.fullMessage = message
    self.splitMessage = message.strip("\r").split(" ",7)
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
      
  def read(self,host, func, nick, logfunc, threadQueue, defaultFunc, defaultFuncChar):
    """
    Parse message from IRC into usable variables
    """
    
    _log_me("reading message with following attributes: nick:%s, host:%s, defaultFuncChar:%s" % (nick, host, defaultFuncChar), "debug")
    
    self.host = host
    if self.splitMessage[0][0:4] == "PING":
      tempReply = self.reply(host, {}, nick, defaultFunc, defaultFuncChar)
      if tempReply:
        threadQueue.put(tempReply)
        return
        
    else:
      try:
        
        #check to see if this was a PM to us
        if "privmsg %s" % nick.lower() in self.fullMessage.lower():
          self.isPM = True
        else:
          self.isPM = False
        
        #load message lines into self vars
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
            #raise
            pass
        pass
      
      if logfunc:
        #pass line to our logging function
        logfunc(self)
      
      replyVal = self.reply(host, func, nick, defaultFunc, defaultFuncChar)
      if replyVal:
        if isinstance(replyVal, list):
          for itm in replyVal:
            threadQueue.put(itm)
        else:
          
          threadQueue.put(replyVal)
  
  def reply(self, host, func, nick, defaultFunc, defaultFuncChar):
    """
    Quick replies to PING messages, determines if we have a func to be run and calls getReturnVal to execute that func if needed
    """
    if self.splitMessage[0][0:4] == "PING":
      return "PONG :%s\r\n" % host
    
    if self.cmd:
      if self.cmd[1:] in func:
        val = self.getReturnVal(func, nick)
        return val
        
      if len(self.cmd) >= 2:
        if self.cmd[1] == defaultFuncChar:          
          #hack to make this work
          d = {self.cmd[1:]:defaultFunc}
          
          val = self.getReturnVal(d, nick)
          return val

  def getReturnVal(self,func,nick):
    """
    Executes the function (func) and creates a list of messages (if any) to return to IRC
    """
    #get raw return from function
    tempVal = func[self.cmd[1:]](self)
    
    #determine what info we got back, tuples would indicate user passed back a room and a message
    if isinstance(tempVal, tuple):
      returnVal, returnRoom = tempVal
    else:
      #we weren't passed a tuple back, assume the user only passed back something to the room which it was sent from
      returnRoom = ""
      returnVal = tempVal
    
    #if we didn't get anything back, quit
    if not returnVal:
      return
    
    returnList = []
    final_dest = ""
    
    
    #get target to send message to
    if not returnRoom and self.target.lower() == nick.lower():
      #this was a PM and no room was specified, respond with a PM
      final_dest = self.actualUserName
      
    elif not returnRoom:
      #no room was specified and this wasn't a PM, send back to source
      final_dest = self.target
      
    else:
      #room was specified use that
      final_dest = returnRoom
    
    if isinstance(returnVal, six.string_types):
      returnVal = [returnVal]
    
    #iterate through all intended messages back
    for return_msg in returnVal:
      #iterate through all lines of response
      for final_msg in sanitize_output(return_msg):
        returnList.append("PRIVMSG %s :%s\r\n" % (final_dest, final_msg))
    
    return returnList
    
    """
    #get destination:
    if returnVal and returnRoom:
      #respond to room/person that function told us to
      if isinstance(returnVal, list):
        for itm in returnVal:
          for i in sanitize_output(itm):
            returnList.append("PRIVMSG %s :%s\r\n" % (returnRoom, i))
        return returnList
      return "PRIVMSG %s :%s\r\n" % (returnRoom, returnVal)
      
    elif returnVal and self.target.lower() == nick.lower():
      #if no room/person and it's a PM, reply to a PM with a PM
      if isinstance(returnVal, list):
        for itm in returnVal:
          for i in sanitize_output(itm):
            returnList.append("PRIVMSG %s :%s\r\n" % (self.actualUserName, i))
        return returnList
      
      
      return "PRIVMSG %s :%s\r\n" % (self.actualUserName, returnVal)
      
    elif returnVal and not returnRoom:
      #if no room/person returned just respond back to same room
      if isinstance(returnVal, list):
        for itm in returnVal:
          returnList.append("PRIVMSG %s :%s\r\n" % (self.target, itm))
        return returnList
      
      return "PRIVMSG %s :%s\r\n" % (self.target, returnVal)
      """
      
  def __len__(self):
    return self.length