from datetime import datetime, timedelta
import time
import re

# Some utility classes / functions first
class AllMatch(set):
  """Universal set - match everything"""
  def __contains__(self, item): return True
  
  def __bool__(self):
    return True
  
  __nonzero__=__bool__

allMatch = AllMatch()

def conv_to_set(obj, divisibleVal):  # Allow single integer to be provided
  # Obj should come in as a string
  try:
    
    # * means match on everything ########################################
    if obj == "*":
      return allMatch
  
    # Just an int ########################################################
    if fIsNum(obj):
      if int(obj) > divisibleVal -1:
        return False
      return list([int(obj)])
    
    # Slash option #######################################################
    if "/" in obj:
      # Allow slash notation
      divisor = obj[obj.find("/")+1:]
  
      if fIsNum(divisor):
        return [x for x in range(divisibleVal) if x % int(divisor) == 0]
    
      else:
        return False

    # Already a set #####################################################
    if isinstance(obj, set):
      return set(obj)

    # Iterate and change all ranges to a list eg: 1-3 becomes 1,2,3 #####
    if obj.find(",") != -1 or obj.find("-") != -1:
      tempList = obj.split(",")
      finalList = []
      for itm in tempList:
        if re.search(r"(\d+)-(\d+)", itm):
          matchObj = re.search(r"(\d+)-(\d+)", itm)
          beginNum = matchObj.group(1)
          endNum = matchObj.group(2)
          lst = range(int(beginNum), int(endNum) + 1)
          finalList.extend(lst)
        elif fIsNum(itm):
          finalList.append(int(itm))
        else:
          return False
    
      # Check if values are too big/small
      badList = [x for x in finalList if x > divisibleVal -1]
      if len(badList) != 0:
        return False
    
      return finalList
     
  except:
    print "HIT ERROR!"
    return False
  
# The actual Event class
class Event(object):
  def __init__(self, func, min=allMatch, hour=allMatch, 
               day=allMatch, month=allMatch, dow=allMatch, sec=allMatch):
             
    self.mins = conv_to_set(min, 60)
    self.hours= conv_to_set(hour, 24)
    self.days = conv_to_set(day, 31)
    self.months = conv_to_set(month, 31)
    self.dow = conv_to_set(dow, 7)
    self.sec = conv_to_set(sec, 60)
    self.func = func
    
    if not(self.mins and self.hours and self.days and self.months and self.dow and self.sec):
      self.goodCron = False
    else:
      self.goodCron = True
      
    self.lastRun = datetime.fromordinal(1)

  def __matchtime__(self, t):
    """Return True if this event should trigger at the specified datetime"""
    if not self.goodCron:
      # Never run if we don't have good cron variables
      return False
    
    if not self.__runAlready__(t):
      return ((t.minute   in self.mins) and
             (t.hour     in self.hours) and
             (t.day    in self.days) and
             (t.month    in self.months) and
             (t.weekday()  in self.dow) and
             (t.second in self.sec))
    else:
      return False
           
  def __runAlready__(self, t):
    """check to see if it has been triggered this second"""
    lr = self.lastRun
      
    if (lr.minute == t.minute and
        lr.hour == t.hour and
        lr.day == t.day and
        lr.month == t.month and
        lr.weekday() == t.weekday() and
        lr.second == t.second):
      return True
    else:
      return False

  def check(self, t):
    if self.__matchtime__(t):
      self.lastRun = t
      return self.func()

def fIsNum(val):
  """
  Inputs:
    takes val which should either be string, int or float type, but can be anything
  
  Outputs:
    returns whether or not val was able to be successfully cast as an int
  
  Purpose:
    Used to determine if a value is an integer or not, especially when taking input from IRC
  """

  try:
    if float(val) != int(val):
      return False
    
    test = int(val)
    test = int(float(val))
    
    return True
  except:
    return False
    
def printTest():
  print "%s Test" % str(datetime.now())

if __name__ == '__main__':
  testCron = Event(printTest, min = "*", hour = "*", day = "*", month="*", dow="*", sec = "1,5,10,30")
  print testCron.goodCron
  while True:
    testCron.check(datetime.now())
