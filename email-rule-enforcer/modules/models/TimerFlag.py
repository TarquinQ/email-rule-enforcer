import threading
import datetime


class TimerFlag():
    def __init__(self, name=None, default_time_incr=None):
        self.name = name
        self.flag = threading.Event()
        self.timer = threading.Timer(0, print)  # dummy values just to create a Timer
        self.timer.daemon = True
        self.set_default_time_incr(default_time_incr)

    def set_default_time_incr(self, time_incr):
        self.default_time_incr = time_incr

    def reset_timer(self, next):
        """Sets next timer. next is passed in as seconds"""
        self.clear_flag()
        self.next_deadline = datetime.datetime.now() + datetime.timedelta(seconds=next)
        self.timer = threading.Timer(next, self.flag.set)
        self.timer.daemon = True
        self.timer.start()

    def reset_timer_default(self):
        if self.default_time_incr is not None:
            self.reset_timer(self.default_time_incr)
        else:
            raise ValueError('No default time_incr has been set on TimerFlag object, \
                but default methods have been called requiring this value')

    def reset_timer_datetime(self, next_deadline):
        """Sets next timer. next_deadline is passed in as datetime"""
        timediff = next_deadline - datetime.datetime.now()
        if timediff.days < 0:
            timediff_s = 0
        else:
            timediff_s = timediff.seconds
        self.start_new_timer(timediff_s)

    def stop_timer(self):
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

