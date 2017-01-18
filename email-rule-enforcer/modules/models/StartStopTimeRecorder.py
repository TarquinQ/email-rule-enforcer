import datetime
import time


class StartStopTimeRecorder():
    def __init__(self, start=True):
        self.time_recorder = StartStopTimeRecorderBasic()
        self._is_running = False
        self.hard_reset()
        if (start is True):
            self.start()

    def start(self):
        self.time_recorder.start()
        self.start_datetimes.append(self.time_recorder.start_datetime)
        if self.initial_datetime is None:
            self.initial_datetime = self.time_recorder.start_datetime
        self._is_running = True

    def stop(self):
        if self._is_running is False:
            return
        self.time_recorder.stop()
        self.stop_datetimes.append(self.time_recorder.stop_datetime)
        self.last_stop_datetime = self.time_recorder.stop_datetime
        self._cumulative_seconds += self.time_recorder.get_elapsed_seconds()
        self.time_recorder.reset()
        self._is_running = False

    def hard_reset(self):
        self.stop()
        self.initial_datetime = None
        self.start_datetimes = []
        self.last_stop_datetime = None
        self.stop_datetimes = []
        self._cumulative_seconds = 0
        self._is_running = False
        self.time_recorder.reset()

    def is_running(self):
        return self._is_running

    def get_start_datetime(self):
        return self.initial_datetime

    def get_stop_datetime(self):
        return self.last_stop_datetime

    def get_elapsed_seconds(self):
        return self._cumulative_seconds + self.time_recorder.get_elapsed_seconds()

    def __repr__(self):
        ret_str = 'TimeRecorder:\n'
        ret_str += 'Is Running? %s\n' % self.is_running()
        if self.initial_datetime is not None:
            ret_str += 'Initial Start Time: %s\n' % self.initial_datetime.isoformat(' ')
            ret_str += 'All Start Times: %s\n' % self.start_datetimes
        else:
            ret_str += 'Start Time: Not Yet Started\n'
        if self.last_stop_datetime is not None:
            ret_str += 'Last Stop Time: %s\n' % self.last_stop_datetime.isoformat(' ')
            ret_str += 'All Stop Times: %s\n' % self.stop_datetimes
        else:
            ret_str += 'Stop Time: Not Yet Started'
        ret_str += 'Elapsed Seconds: %s\n' % self.get_elapsed_seconds()
        ret_str += '(Cumulative Seconds: %s)\n' % self._cumulative_seconds
        return ret_str

    def __str__(self):
        return self.__repr__()


class StartStopTimeRecorderBasic():
    def __init__(self, start=True):
        self._is_running = False
        self.reset()
        if (start is True):
            self.start()

    def reset(self):
        self.stop()
        self.start_datetime = None
        self.start_perf = None
        self.stop_datetime = None
        self.stop_perf = None
        self.final_seconds = 0
        self.final_timedelta = datetime.timedelta(0)

    def start(self):
        self.start_datetime = datetime.datetime.now()
        self.start_perf = time.perf_counter()
        self._is_running = True

    def stop(self):
        if self._is_running is False:
            return
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
        return int(round(ret_val, 0))

    def get_elapsed_timedelta(self):
        if self._is_running is True:
            return datetime.datetime.now() - self.start_datetime()
        else:
            return self.final_timedelta

    def __repr__(self):
        ret_str = 'TimeRecorderBasic:\n'
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

