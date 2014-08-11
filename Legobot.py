import sys
import socket
import select
import string
import ssl
import threading
import Queue
import datetime
import time
import legoCron

__author__ = "Bren Briggs and Kevin McCabe"
__copyright__ = "Copyright 2014"
__license__ = "GPL"
#__version__ = "0.1"
__status__ = "Beta"

class timerFunc():
  def __init__(self, func, interval = -1, timeOfDay=None):
    self.func = func
    self.interval = interval
    self.lastRun = datetime.datetime.fromordinal(1)
    self.timeOfDay = timeOfDay

  def runIfNeeded(self):
    if (datetime.datetime.now() - self.lastRun).total_seconds() > self.interval and self.interval != -1:
      #run
      self.func()
      self.lastRun = datetime.datetime.now()
    
    
class legoBot():
  def __init__(self,host,port,nick,chans, logfunc = "", hostpw = ""):
    self.host = host
    self.hostpw = hostpw
    self.port = port
    self.nick = nick
    self.chans = chans
    self.logfunc = logfunc
    self.func = {}
    self.timerFuncList = []
    self.threadQueue = None
    self.threadList = []
  
  def addTimerFunc(self, function, min = "*", hour = "*", day = "*", month="*", dow="*", sec = "*"):
    self.timerFuncList.append(legoCron.Event(function, min, hour, day, month, dow, sec))
  
  def addFunc(self, name, function):
    #name should be str, function should be a function object (as in a function without the parens)
    self.func[name] = function
  
  def batchAddFunc(self, d):
    #merge a dictionary of functions into the existing function dictionary
    self.func.update(d)
  
  def connect(self, isSSL=False):
    if isSSL:
      sock=socket.socket()
      self.connecton = ssl.wrap_socket(sock)
    else:
      self.connection = socket.socket()
      
    self.connection.connect((self.host, self.port))
    if self.hostpw:
      self.connection.sendall("PASS %s\r\n" % self.hostpw)
    self.connection.sendall("NICK %s\r\n" % self.nick)
    #TO DO: add functionality to create separate nick, realname, etc
    self.connection.sendall("USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.nick))
    for room, pw in self.chans:
      if pw:
        self.connection.sendall("JOIN %s %s\r\n" % room, pw)
      else:
        self.connection.sendall("JOIN %s\r\n" % room)
    self.__listen()
  
  def sendMsg(self, msgToSend):
    #msgtoSend must be str
    self.connection.sendall(msgToSend)
  
  def __listen(self):
    #initiate queue to read off of
    self.threadQueue = Queue.Queue()
    
    #spin up threads for timerFuncs
    for timerFunc in self.timerFuncList:
      self.threadList.append(threading.Thread(target=timerDaemon, args=(timerFunc, self.threadQueue)))
      self.threadList[-1].daemon = True
      self.threadList[-1].start()
      
    while True:
      print "ran while"
      if select.select([self.connection],[],[],1.0)[0]:
        readbuffer = self.connection.recv(1024)
        print readbuffer
        #split into lines
        temp = string.split(readbuffer, "\n")
    
        #iterate through any lines received
        for line in temp:
          if len(line.strip(' \t\n\r')) == 0:
            continue
          msg = Message(line)
          self.threadList.append(threading.Thread(target= msg.read, args = (self.host, self.func, self.nick, self.logfunc, self.threadQueue)))
          self.threadList[-1].daemon = True
          self.threadList[-1].start()
  
      if not self.threadQueue.empty():
        response = self.threadQueue.get(block=False)
        if response:
          self.connection.sendall(response)
      time.sleep(0.5)

def timerDaemon(func, q):
  while True:
    tempVal = func.check(datetime.datetime.now())
    if tempVal:
      q.put("PRIVMSG %s :%s\r\n" % ("#dcn-dev", tempVal))
    time.sleep(0.5)


class Message():
  def __init__(self, message):
    self.splitMessage = message.strip("\r").split(" ",7)
    self.length = len(self.splitMessage)
    self.userInfo = None
    self.actualUserName = None
    self.target = None
    self.cmd = None
    self.arg1 = None
    self.arg2 = None
    self.arg3 = None
    self.allArgs = None
      
  def read(self,host, func, nick, logfunc, threadQueue):
    self.host = host
    if self.splitMessage[0][0:4] == "PING":
      tempReply = self.reply(host, {}, nick)
      if tempReply:
        threadQueue.put(tempReply)
        
    else:
      try:
        self.userInfo = self.splitMessage[0].lower()
        self.actualUserName = self.splitMessage[0][1:self.splitMessage[0].find("!")].lower()
        self.target = self.splitMessage[2].lower()
        self.cmd = self.splitMessage[3].lower()
        self.allArgs = self.splitMessage[4:]
        self.arg1 = self.splitMessage[4].lower()
        self.arg2 = self.splitMessage[5].lower()
        self.arg3 = self.splitMessage[6].lower()
      except:
        pass
      
      if logfunc:
        #pass line to our logging function
        logfunc(self)
      
      replyVal = self.reply(host, func, nick)
      threadQueue.put(replyVal)

  def getReturnVal(self,func,nick):
    returnVal, returnRoom = func[self.cmd[1:]](self)
    if returnVal and returnRoom:
      #respond to room/person that function told us to
      return "PRIVMSG %s :%s\r\n" % (returnRoom, returnVal)
      
    elif returnVal and self.target.lower() == nick.lower():
      #if no room/person and it's a PM, reply to a PM with a PM
      return "PRIVMSG %s :%s\r\n" % (self.actualUserName, returnVal)
      
    elif returnVal and not returnRoom:
      #if no room/person returned just respond back to same room
      return "PRIVMSG %s :%s\r\n" % (self.target, returnVal)
  
  def reply(self, host, func, nick):
    if self.splitMessage[0][0:4] == "PING":
      return "PONG :%s\r\n" % host
    
    if self.cmd:
      if self.cmd[1:] in func:
        val = self.getReturnVal(func, nick)
        return val

  def __len__(self):
    return self.length