import datetime
import time


class TimeRecorder():
    def __init__(self):
        self.init_datetime = datetime.datetime.now()
        self.init_perf = time.perf_counter()

    def get_elapsed_seconds(self):
        return time.perf_counter() - self.init_perf()

    def get_elapsed_timedelta(self):
        return datetime.datetime.now() - self.init_datetime()

    def __repr__(self):
        ret_str = 'TimeRecorder:'
        ret_str += 'Init Time: ' + str(init_time.iso_format())
        ret_str += 'Elapsed Seconds: ' + str(self.get_elapsed_seconds())
        return ret_str

    def __str__(self):
        return self.__repr__()
