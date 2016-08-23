class Config(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.counters = Counters()


class Counters(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def add_counter(self, counter_name):
        try:
            if not self[counter_name]:
                self[counter_name] = 0
        except KeyError:
            self[counter_name] = 0
        return self[counter_name]

    def incr_counter(self, counter_name):
        try:
            self[counter_name] += 1
        except KeyError:
            self[counter_name] = 1
        return self[counter_name]

    def get_counter(self, counter_name):
        try:
            return self[counter_name]
        except KeyError:
            return 0

