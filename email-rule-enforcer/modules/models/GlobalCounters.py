from modules.models.Counter import Counter


class GlobalCounters(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def new_counter(self, counter_name, start_val=0):
        self[counter_name] = Counter(start_val=start_val, allow_decr=True)
        return self[counter_name]

    def incr(self, counter_name, incr=1):
        try:
            self[counter_name].incr(incr=incr)
        except (KeyError, AttributeError):
            self.add_counter(counter_name=counter_name, start_val=incr)
        return self[counter_name]

    def decr(self, counter_name, decr=1):
        try:
            self[counter_name].decr(decr=decr)
        except (KeyError, AttributeError):
            self.add_counter(counter_name=counter_name, start_val=(-1 * incr))
        return self[counter_name]

    def get(self, counter_name):
        try:
            return self[counter_name].get()
        except (KeyError, AttributeError):
            return 0
