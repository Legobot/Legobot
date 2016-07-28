import re
from datetime import datetime


# Some utility classes / functions first
class AllMatch(set):
    """Universal set - match everything"""

    def __contains__(self, item): return True

    def __bool__(self):
        return True

    __nonzero__ = __bool__


allMatch = AllMatch()


def conv_to_set(obj, divisible_val):  # Allow single integer to be provided
    # obj should come in as a string
    try:

        # * means match on everything
        if obj == "*":
            return allMatch

        # just an int
        if is_integer(obj):
            if int(obj) > divisible_val - 1:
                return False
            return list([int(obj)])

        # slash option
        if "/" in obj:
            # allow slash notation
            divisor = obj[obj.find("/") + 1:]

            if is_integer(divisor):
                return [x for x in range(divisible_val) if x % int(divisor) == 0]

            else:
                return False

        # already a set
        if isinstance(obj, set):
            return set(obj)

        # iterate and change all ranges to a list eg: 1-3 becomes 1,2,3
        if obj.find(",") != -1 or obj.find("-") != -1:
            temp_list = obj.split(",")
            final_list = []
            for itm in temp_list:
                if re.search(r"(\d+)-(\d+)", itm):
                    match_obj = re.search(r"(\d+)-(\d+)", itm)
                    begin_num = match_obj.group(1)
                    end_num = match_obj.group(2)
                    lst = range(int(begin_num), int(end_num) + 1)
                    final_list.extend(lst)
                elif is_integer(itm):
                    final_list.append(int(itm))
                else:
                    return False

            # check if values are too big/small
            bad_list = [x for x in final_list if x > divisible_val - 1]
            if len(bad_list) != 0:
                return False

            return final_list

    except:
        print "HIT ERROR!"
        return False


# The actual Event class
class Event(object):
    def __init__(self, func, minute=allMatch, hour=allMatch,
                 day=allMatch, month=allMatch, dow=allMatch, sec=allMatch):

        self.mins = conv_to_set(minute, 60)
        self.hours = conv_to_set(hour, 24)
        self.days = conv_to_set(day, 31)
        self.months = conv_to_set(month, 31)
        self.dow = conv_to_set(dow, 7)
        self.sec = conv_to_set(sec, 60)
        self.func = func

        self.__name__ = func.__name__

        if not (self.mins and self.hours and self.days and self.months and self.dow and self.sec):
            self.goodCron = False
        else:
            self.goodCron = True

        self.lastRun = datetime.fromordinal(1)

    def __matchtime__(self, t):
        """Return True if this event should trigger at the specified datetime"""
        if not self.goodCron:
            # never run if we don't have good cron variables
            return False

        if not self.__runAlready__(t):
            return ((t.minute in self.mins) and
                    (t.hour in self.hours) and
                    (t.day in self.days) and
                    (t.month in self.months) and
                    (t.weekday() in self.dow) and
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


def is_integer(val):
    """
    Determine whether a value is an integer.

    :param val: a string, int, or float type
    :return: whether val could be successfully cast as an int without loss of precision
    """

    try:
        float_cast = float(val)
        int_cast = int(float_cast)
        if float_cast != int_cast:
            return False
        return True
    except TypeError:
        return False


def print_test():
    print "%s Test" % str(datetime.now())


if __name__ == '__main__':
    testCron = Event(print_test, minute="*", hour="*", day="*", month="*", dow="*", sec="1,5,10,30")
    print testCron.goodCron
    while True:
        testCron.check(datetime.now())
