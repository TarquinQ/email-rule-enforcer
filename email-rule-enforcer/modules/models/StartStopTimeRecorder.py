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

    def get_start_datetime(self):
        return self.start_datetime

    def get_stop_datetime(self):
        return self.stop_datetime

    def get_elapsed_seconds(self):
        if self._is_running is True:
            ret_val = time.perf_counter() - self.start_perf
        else:
            ret_val = self.final_seconds

        if isinstance(ret_val, float):
            if ret_val < 30.0:
                ret_val = round(ret_val, 2)
            else:
                ret_val = round(ret_val, 0)
        return ret_val

    def get_elapsed_timedelta(self):
        if self._is_running is True:
            return datetime.datetime.now() - self.start_datetime()
        else:
            return self.final_timedelta

    def __repr__(self):
        ret_str = 'TimeRecorder:\n'
        ret_str += 'Is Running? %s\n' % self.is_running()
        if self.start_datetime is not None:
            ret_str += 'Start Time: %s\n' % self.start_datetime.isoformat(' ')
        else:
            ret_str += 'Start Time: Not Started\n'
        if self.stop_datetime is not None:
            ret_str += 'Stop Time: %s\n' % self.stop_datetime.isoformat(' ')
        else:
            if self._is_running:
                ret_str += 'Stop Time: (not yet stopped)'
            else:
                ret_str += 'Stop Time: Not Started'
        ret_str += 'Elapsed Seconds: %s\n' % self.get_elapsed_seconds()
        return ret_str

    def __str__(self):
        return self.__repr__()

