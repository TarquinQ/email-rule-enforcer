class RawEmailResponse():
    def __init__(self, raw_email_bytes=None, flags=None, size=None, server_date=None):
        self.raw_email_bytes = raw_email_bytes
        self.size = size
        self.flags = flags
        self.server_date = server_date

    def __str__(self):
        ret_str = str(self.__class__.__name__)
        ret_str += ': Size {0}, Flags: {1}, ServerDate: {2}, raw_email:\n{3}'.format(
            self.size,
            self.flags,
            self.server_date,
            self.raw_email_bytes
        )
        return ret_str

    def __repr__(self):
        return self.__str__()


