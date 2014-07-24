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
__version__ = "0.1"
__status__ = "Development"

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
  def __init__(self,host,port,nick,chans, logfunc = ""):
    self.host = host
    self.port = port
    self.nick = nick
    self.chans = chans
    self.logfunc = logfunc
    self.func = {}
    self.timerFunc = []
  
  def addTimerFunc(self, function, interval):
    self.timerFunc.append(timerFunc(function, interval))
  
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
    self.connection.sendall("NICK %s\r\n" % self.nick)
    #TO DO: add functionality to create separate nick, realname, etc
    self.connection.sendall("USER %s %s %s :%s\r\n" % (self.nick, self.nick, self.nick, self.nick))
    for room in self.chans:
      self.connection.sendall("JOIN %s\r\n" % room)
    self.__listen()
  
  def sendMsg(self, msgToSend):
    #msgtoSend must be str
    self.connection.sendall(msgToSend)
  
  def __listen(self):
    while 1:
      for func in self.timerFunc:
        timerReply = func.runIfNeeded()
        if timerReply:
          self.connection.sendall(timerReply)
        
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
          reply = msg.read(self.host, self.func, self.nick, self.logfunc)
          if reply:
            self.connection.sendall(reply)
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
      
  def read(self,host, func, nick, logfunc):
    self.host = host
    if self.splitMessage[0][0:4] == "PING":
      return self.reply(host, {}, nick)
      
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
        
      return self.reply(host, func, nick)

  def getReturnVal(self,q,func,nick):
    returnVal, returnRoom = func[self.cmd[1:]](self)
    if returnVal and returnRoom:
      #respond to room/person that function told us to
       q.put("PRIVMSG %s :%s\r\n" % (returnRoom, returnVal))
      
    elif returnVal and self.target.lower() == nick.lower():
      #if no room/person and it's a PM, reply to a PM with a PM
      q.put("PRIVMSG %s :%s\r\n" % (self.actualUserName, returnVal))
      
    elif returnVal and not returnRoom:
      #if no room/person returned just respond back to same room
      q.put("PRIVMSG %s :%s\r\n" % (self.target, returnVal))
  
  def reply(self, host, func, nick):
    if self.splitMessage[0][0:4] == "PING":
      return "PONG :%s\r\n" % host
    
    if self.cmd:
      if self.cmd[1:] in func:
        q = Queue.Queue()
        t = threading.Thread(target=self.getReturnVal, args=(q,func,nick))
        t.start()
        s = q.get()
        return s

  def __len__(self):
    return self.length
