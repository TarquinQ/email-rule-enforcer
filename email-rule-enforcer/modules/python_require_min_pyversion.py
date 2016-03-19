import sys

MIN_PYTHON = (3, 4)
if sys.version_info[0:2] < MIN_PYTHON:
    sys.stderr.write("Python %s.%s or later is required\n" % MIN_PYTHON)
    sys.exit(1)
