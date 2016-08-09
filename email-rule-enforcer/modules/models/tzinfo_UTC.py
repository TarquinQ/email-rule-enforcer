from datetime import timedelta, tzinfo

# Concrete implementation of UTC tzinfo object, from python standard docs
# https://docs.python.org/3.4/library/datetime.html#tzinfo-objects


ZERO = timedelta(0)


class UTC(tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO


utc = UTC()
