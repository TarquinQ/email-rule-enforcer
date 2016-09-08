import datetime
import time


class StartStopTimeRecorder():
    def __init__(self, start=True):
        self.reset()
        if (start is True):
            self.start()

    def reset(self):
        self.start_datetime = None
        self.start_perf = None
        self.stop_datetime = None
        self.stop_perf = None
        self.final_seconds = None
        self.final_timedelta = None
        self._is_running = False

    def start(self):
        self.start_datetime = datetime.datetime.now()
        self.start_perf = time.perf_counter()
        self._is_running = True

    def stop(self):
        self.stop_datetime = datetime.datetime.now()
        self.stop_perf = time.perf_counter()
        self.final_seconds = self.stop_perf - self.start_perf
        self.final_timedelta = self.stop_datetime - self.start_datetime
        self._is_running = False

    def is_running(self):
        return self._is_running

    def get_elapsed_seconds(self):
        if self._is_running is True:
            return time.perf_counter() - self.start_perf()
        else:
            return self.final_seconds

    def get_elapsed_timedelta(self):
        if self._is_running is True:
            return datetime.datetime.now() - self.start_datetime()
        else:
            return self.final_timedelta

    def __repr__(self):
        ret_str = 'TimeRecorder:\n'
        ret_str += 'Start Time: %s\n' % self.start_datetime.isoformat(' ')
        ret_str += 'Is Running? %s\n' % self.is_running()
        ret_str += 'Stop Time: %s\n' % self.stop_datetime.isoformat(' ')
        ret_str += 'Elapsed Seconds: %s\n' % self.get_elapsed_seconds()
        return ret_str

    def __str__(self):
        return self.__repr__()

