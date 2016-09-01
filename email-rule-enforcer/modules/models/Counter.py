class Counter():
    def __init__(self, start_val=0, allow_decr=False):
        if isinstance(start_val, int):
            self.count = start_val
        else:
            self.count = 0

        if isinstance(allow_decr, bool):
            self.allow_decr = allow_decr
        else:
            self.allow_decr = False

    def get(self):
        return self.count

    def incr(self, incr=1):
        self.count += incr
        return self.count

    def decr(self, decr=1):
        if self.allow_decr:
            self.count -= decr
        else:
            raise UserWarning('Counter Decrementing not permitted, action ignored')
        return self.count

    def __repr__(self):
        return str(self.count)

    def __str__(self):
        return self.__repr__()
