import datetime
from modules.models.TimeRecorder import TimeRecorder


class GlobalTimeCounters(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_counter(self, counter_name):
        try:
            self[counter_name]
        except KeyError:
            self[counter_name] = TimeRecorder()
        return self[counter_name]

    def get_elapsed_seconds(self, counter_name):
        try:
            return self[counter_name].get_elapsed_seconds()
        except KeyError, AttributeError:
            return 0

    def get_elapsed_timedelta(self, counter_name):
        try:
            return self[counter_name].get_elapsed_timedelta()
        except KeyError, AttributeError:
            return datetime.timedelta(0)
