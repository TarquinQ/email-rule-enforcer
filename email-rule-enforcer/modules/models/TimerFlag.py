import threading
import datetime
import re


class TimerFlag():
    def __init__(self, name=None):
        self.name = name
        self.flag = threading.Event()
        self.timer = threading.Timer(0, print)  # dummy values just to create a Timer
        self.timer.daemon = True
        self.next_deadline = datetime.datetime.now()
        self.set_default_time_incr(21600)  # 6 hours
        self.is_deadline_based = False
        self.deadline_base = '25:00'

    def set_default_time_incr(self, time_incr):
        self.default_time_incr = time_incr

    def set_deadline_base(self, deadline_base):
        if re.match('[0-9][0-9]:[0-9][0-9]', str(deadline_base)):
            self.deadline_base = deadline_base
            self.deadline_base_hours = int(deadline_base.split(':')[0])
            self.deadline_base_mins = int(deadline_base.split(':')[1])
            #self.deadline_base_seconds = (self.deadline_base_hours*3600)+(deadline_base_minutes*60)
            self.is_deadline_based = True

    def reset_next_deadline_from_base(self):
        """Derives time of next deadline according to the requested base"""
        now = datetime.datetime.now()
        compare_hours = now.hour
        compare_mins = now.minute
        target_hours, target_mins = self.deadline_base_hours, self.deadline_base_mins
        # convert to seconds, and make sure that we account for the 00:00 > 23:00 conundrum....
        if target_hours < compare_hours:
            target_hours += 24
        target_s = ((60 * target_hours) + target_mins) * 60
        compare_s = ((60 * compare_hours) + compare_mins) * 60
        # Now we just work out when the next run should be, in order to hit the timing_base
        while compare_s < target_s:
            target_s = target_s - self.default_time_incr
        target_s = target_s + self.default_time_incr
        next_deadline_hours = (target_s//60)//60
        next_deadline_mins = (target_s//60) % 60
        if next_deadline_hours > 23:
            next_deadline_days = next_deadline_hours // 24
            next_deadline_hours = next_deadline_hours - 24
        else:
            next_deadline_days = 0
        next_deadline = now + datetime.timedelta(days=next_deadline_days)
        next_deadline = next_deadline.replace(hour=next_deadline_hours, minute=next_deadline_mins)
        next_deadline = next_deadline.replace(second=0, microsecond=0)
        self.reset_timer_datetime(next_deadline)
        #import pdb; pdb.set_trace()

    def reset_timer(self, next):
        """Sets next timer. next is passed in as seconds"""
        self.stop()
        self.clear_flag()
        self.next_deadline = datetime.datetime.now() + datetime.timedelta(seconds=next)
        self.next_deadline = self.next_deadline.replace(microsecond=0)
        self.timer = threading.Timer(next, self.flag.set)
        self.timer.daemon = True
        self.timer.start()

    def reset_timer_default(self):
        if self.is_deadline_based is False:
            self.reset_timer(self.default_time_incr)
        else:
            self.reset_next_deadline_from_base()

    def reset_timer_datetime(self, next_deadline):
        """Sets next timer. next_deadline is passed in as datetime"""
        timediff = next_deadline - datetime.datetime.now()
        if timediff.days < 0:
            timediff_s = 0
        else:
            timediff_s = timediff.seconds + (timediff.days * 86400)
        self.reset_timer(timediff_s)

    def stop(self):
        if self.timer.is_alive():
            self.timer.cancel()

    def join(self, timeout=None):
        if self.timer.is_alive():
            self.timer.join(timeout)

    def is_alive(self):
        return self.timer.is_alive()

    def is_set(self):
        return self.flag.is_set()

    def is_required(self):
        return self.is_set()

    def set_flag(self):
        self.flag.set()

    def clear_flag(self):
        self.flag.clear()

    def reset_flag(self):
        self.clear_flag()

    def __repr__(self):
        ret_str = '%s:\n' % self.__class__.__name__
        ret_str += 'Name: %s\n' % self.name
        ret_str += 'Configured Info:\n'
        ret_str += '  Default Interval Increment: %s\n' % self.default_time_incr
        ret_str += '  Is Deadline-Based? %s\n' % self.is_deadline_based
        ret_str += '  Deadline-Base: %s\n' % self.deadline_base
        ret_str += 'Specific Info:\n'
        ret_str += '  Flag Set to: %s\n' % self.is_set()
        ret_str += '  Is Timer Running? %s\n' % self.is_alive()
        ret_str += '  Next Deadline: %s\n' % self.next_deadline
        return ret_str

    def __str__(self):
        return self.__repr__()

