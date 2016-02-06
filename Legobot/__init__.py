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

__author__ = "Bren Briggs and Kevin McCabe"
__copyright__ = "Copyright 2016"
__license__ = "GPLv2"
#__version__ = "0.1"
__status__ = "Beta"

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
    
class randTimerFunc():
  def __init__(self, func, randMin, randMax):
    self.func = func
    self.randMin = randMin
    self.randMax = randMax

class legoBot():
  def __init__(self,host,port,nick,chans, logfunc = "", hostpw = "", defaultFunc = None, defaultFuncChar = ""):
    self.host = host
    self.hostpw = hostpw
    self.port = port
    self.nick = nick
    self.chans = chans
    self.logfunc = logfunc
    self.func = {}
    self.timerFuncList = []
    self.randTimerFuncList = []
    self.threadQueue = None
    self.threadList = []
    self.funcHelp = {}
    self.defaultFunc = defaultFunc
    self.defaultFuncChar = defaultFuncChar
    
    #add in default help function
    self.addFunc("!help", self.defaultHelp, "Function used to display help, this default help value can be overridden with a custom function")
    
  def defaultHelp(self, msgObj):
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
  
  def _send_raw_to_socket(txt_to_send):
    print "trying to send to socket: %s" % txt_to_send
    self.connection.sendall(txt_to_send)
  
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
        print "set new nick to: %s" % self.nick
      
      print "Attempting to log in with nick: %s" % self.nick
      
      self._send_raw_to_socket("NICK %s\r\n" % self.nick)

      self._send_raw_to_socket("USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.nick))
    
      #read in socket to check if we got somethign like:
      # :ircd2.abc.com 433 * test_nick :Nickname already in use

      t = datetime.datetime.now()
      iterate_nick = False
      read_line = False
      
      while not read_line and (datetime.datetime.now() - t).total_seconds() < 60:
        print "in while"
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
              print "Nick already registered, iterating nick"
              iterate_nick = True
              i += 1
              break
            print line
        else:
          time.sleep(.5)
    
    
    time.sleep(1)
    for room, pw in self.chans:
      if pw:
        self._send_raw_to_socket("JOIN %s %s\r\n" % room, pw)
      else:
        self._send_raw_to_socket("JOIN %s\r\n" % room)
    self.__listen()

  
  def sendMsg(self, msgToSend):
    #msgtoSend must be str
    self._send_raw_to_socket(msgToSend)
  
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
          print line
          msg = Message(line)
          self.threadList.append(threading.Thread(target= msg.read, args = (self.host, self.func, self.nick, self.logfunc, self.threadQueue, self.defaultFunc, self.defaultFuncChar)))
          self.threadList[-1].daemon = True
          self.threadList[-1].start()
      
      while not self.threadQueue.empty():
        response = self.threadQueue.get(block=False)
        if response:
          try:
            self._send_raw_to_socket(response)
          except:
            print "Hit error with response: %s" % str(response)
            raise
      time.sleep(0.5)

def timerDaemon(func, q, rooms):
  while True:
    tempVal = func.check(datetime.datetime.now())
    if tempVal:
      for room in rooms:
        if isinstance(tempVal, list):
          for itm in tempVal:
            q.put("PRIVMSG %s :%s\r\n" % (room[0], itm))
        else:
          q.put("PRIVMSG %s :%s\r\n" % (room[0], tempVal))
    time.sleep(0.5)

def randTimerDaemon(func, q, randMin, randMax, rooms):
  #set random timer
  lastRan = datetime.datetime.now()
  randTimer = random.randrange(randMin, randMax)
  while True:
    #get diff in now and last ran, run if it's greater than randTimer
    if (datetime.datetime.now() - lastRan).total_seconds() > randTimer:
      #run the function
      returnVal = func()
      for room in rooms:
        q.put("PRIVMSG %s :%s\r\n" % (room[0], returnVal))
      
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
      
  def read(self,host, func, nick, logfunc, threadQueue, defaultFunc, defaultFuncChar):
    self.host = host
    if self.splitMessage[0][0:4] == "PING":
      tempReply = self.reply(host, {}, nick, defaultFunc, defaultFuncChar)
      if tempReply:
        threadQueue.put(tempReply)
        return
        
    else:
      try:
        
        #check to see if this was a PM to us
        if "privmsg %s" % nick in self.fullMessage:
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
    tempVal = func[self.cmd[1:]](self)
    if isinstance(tempVal, tuple):
      returnVal, returnRoom = tempVal
    else:
      #we weren't passed a tuple back, assume the user only passed back something to the room which it was sent from
      returnRoom = ""
      returnVal = tempVal
      
    if returnVal and returnRoom:
      #respond to room/person that function told us to
      if isinstance(returnVal, list):
        returnList = []
        for itm in returnVal:
          returnList.append("PRIVMSG %s :%s\r\n" % (returnRoom, itm))
        return returnList
      return "PRIVMSG %s :%s\r\n" % (returnRoom, returnVal)
      
    elif returnVal and self.target.lower() == nick.lower():
      #if no room/person and it's a PM, reply to a PM with a PM
      if isinstance(returnVal, list):
        returnList = []
        for itm in returnVal:
          returnList.append("PRIVMSG %s :%s\r\n" % (self.actualUserName, itm))
        return returnList
      return "PRIVMSG %s :%s\r\n" % (self.actualUserName, returnVal)
      
    elif returnVal and not returnRoom:
      #if no room/person returned just respond back to same room
      if isinstance(returnVal, list):
        returnList = []
        for itm in returnVal:
          returnList.append("PRIVMSG %s :%s\r\n" % (self.target, itm))
        return returnList
      
      return "PRIVMSG %s :%s\r\n" % (self.target, returnVal)

  def __len__(self):
    return self.length