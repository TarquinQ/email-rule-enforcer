import logging
import sys
from collections import OrderedDict
from .supportingfunctions import die_with_errormsg
from .supportingfunctions import get_ISOTimestamp_ForLogFilename
from .supportingfunctions import generate_logfile_fullpath
from .supportingfunctions import generate_logfilename


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_logger_instance():
    return logging.getLogger()


class log_messages(metaclass=Singleton):
    log_levels = OrderedDict([
        (50, 'CRITICAL'),
        (40, 'ERROR'),
        (30, 'WARNING'),
        (20, 'INFO'),
        (10, 'DEBUG'),
        (0, 'NOTSET')
    ])

    # Console Log
    handler_console = logging.StreamHandler(sys.stdout)
    formatter_console = logging.Formatter('%(message)s')
    handler_console.setFormatter(formatter_console)
    logger_console = logging.getLogger('console')
    logger_console.addHandler(handler_console)
    loglevel_console = 20
    logger_logfile.setLevel(loglevel_console)

    # Logfile Log
    handler_logfile_null = logging.NullHandler()
    formatter_logfile = logging.Formatter('%(message)s')
    handler_logfile_null.setFormatter(formatter_logfile)
    logger_logfile = logging.getLogger('logfile')
    logger_logfile.addHandler(handler_logfile_null)
    loglevel_logfile = 20
    logger_logfile.setLevel(loglevel_logfile)

    logfile_directory = None
    logfile_filename = None
    logfile_filepath = None

    # Debug Log
    handler_debug_null = logging.NullHandler()
    formatter_debug = logging.Formatter('%(asctime)s - %(message)s')
    handler_debug_null.setFormatter(formatter_debug)
    logger_debug = logging.getLogger('debug')
    cls.logger__logfiledebug.addHandler(handler_debug_null)
    logger_debug.setLevel(cls.logger__logfile)

    debug_directory = None
    debug_filename = None
    debug_filepath = None

    @classmethod
    def log(cls, lvl, msg):
        cls.log_to_console(lvl, msg)
        cls.log_to_logfile(lvl, msg)
        cls.log_to_debug(lvl, msg)

    @classmethod
    def log_to_logfile(cls, lvl, msg):
        cls.logger_logfile.log(lvl, msg)

    @classmethod
    def log_to_console(cls, lvl, msg):
        cls.logger_console.log(lvl, msg)

    @classmethod
    def log_to_debug(cls, lvl, msg):
        cls.logger_debug.log(lvl, msg)

    @classmethod
    def log_exception(cls, msg):
        cls.logger_console.exception(msg)
        cls.logger_logfile.(msg)
        cls.logger_debug.exception(msg)

    @classmethod
    def setlevel_console(cls, level):
        cls.logger_console.setLevel(level)

    @classmethod
    def setlevel_logfile(cls, level):
        cls.setlevel_logfile
        cls.logger_logfile.setLevel(level)

    @classmethod
    def setlevel_debug(cls, level):
        cls.logger_debug.setLevel(level)


# This class wraps around the std Logger class, and builds logs
# the way we want to.
class log_controller():
    def __init__(self, name, log_level=20, filepath=None):
        # Sets up a new logger, and sets it to Null by default
        self.name = name
        self.logger = logging.getLogger(name)
        self.formatter_default = self.get_formatter_plainmsg()
        self.handler_null = logging.NullHandler()
        self.handler_null.setFormater(self.formatter_default)
        self.logger.addHandler(handler_logfile_null)
        self.set_loglevel(log_level)
        if filepath:
            self.filepath = filepath
        else:
            self.set_logger_console()

    def get_formatter_default(self):
        return self.get_formatter_plainmsg()

    @staticmethod
    def get_formatter_plainmsg():
        return logging.Formatter('%(message)s')

    @staticmethod
    def get_formatter_msgwithtime():
        return logging.Formatter('%(asctime)s - %(message)s')

    @staticmethod
    def get_handler_console():
        return logging.StreamHandler(sys.stdout)

    def set_logger_console(self):
        self.handler_console = self.get_handler_console()
        self.formatter = self.get_formatter_plainmsg()
        self.handler_console.setFormatter(self.formatter)
        self.logger.addHandler(self.handler_console)

    def set_loglevel(self, log_level=None):
        if log_level: self.log_level = log_level
        self.logger.setLevel(self.log_level)

    def add_logfile(self, filepath, append=False, formatter=None, die_if_file_fails=False):
        self.filepath = filepath
        if formatter:
            self.formatter_file = formatter
        else:
            self.formatter_file = get_formatter_default()

        try:
            new_handler = self._get_new_filehandler(self.logfile_filepath, append, die_if_file_fails)
            if new_handler:
                self.handler_file = new_handler
                self.handler_file.setFormatter(self.formatter_file)
                self.logger.addHandler(self.handler_file)
        except:
            if die_if_file_fails:
                self.log_exception('FATAL: Died when opening log file: ', filepath)
                die_with_errormsg('FATAL: Died when opening log file: ', filepath)
            else:
                self.log('ERROR: Failed to open log file: ', filepath, '\nContinuing with program anyway.')

    def _get_new_filehandler(self, filepath, append=False, die_if_file_fails=False):
        if append:
            mode = 'a'
        else:
            mode = 'w'

        try:
            new_handler = logging.FileHandler(filepath, mode, encoding='utf8')
        except:
            if die_if_file_fails:
                self.log_exception('FATAL: Died when opening log file: ', filepath)
                die_with_errormsg('FATAL: Died when opening log file: ', filepath)
            else:
                self.log('ERROR: Failed to open log file: ', filepath, '\nContinuing with program anyway.')
                new_handler = None

        return new_handler

    def log(self, lvl, msg):
        self.logger.log(lvl, msg)

    def log_exception(self, msg):
        self.logger.exception(msg)

