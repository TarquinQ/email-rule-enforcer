import datetime
from modules.models.StartStopTimeRecorder import StartStopTimeRecorder


class GlobalTimeRecorders(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_counter(self, counter_name, start=True):
        try:
            self[counter_name]
        except KeyError:
            self[counter_name] = StartStopTimeRecorder(start=start)
        return self[counter_name]

    def get_start_datetime(self, counter_name):
        try:
            return self[counter_name].get_start_datetime()
        except (KeyError, AttributeError):
            return 0

    def get_stop_datetime(self, counter_name):
        try:
            return self[counter_name].get_stop_datetime()
        except (KeyError, AttributeError):
            return 0

    def get_elapsed_seconds(self, counter_name):
        try:
            return self[counter_name].get_elapsed_seconds()
        except (KeyError, AttributeError):
            return 0

    def get_elapsed_timedelta(self, counter_name):
        try:
            return self[counter_name].get_elapsed_timedelta()
        except (KeyError, AttributeError):
            return datetime.timedelta(0)

    def stop(self, counter_name):
        try:
            return self[counter_name].stop()
        except (KeyError, AttributeError):
            return None

    def start(self, counter_name):
        try:
            return self[counter_name].start()
        except (KeyError, AttributeError):
            return None

    def is_running(self, counter_name):
        try:
            return self[counter_name].is_running()
        except (KeyError, AttributeError):
            return None

