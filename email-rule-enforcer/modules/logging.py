import logging
import sys
from collections import OrderedDict
from .supportingfunctions import die_with_errormsg
from .supportingfunctions import get_ISOTimestamp_ForLogFilename
import .supportingfunctions_file_operations as fileops


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
    log_to_console = True
    loglevel_console = 20  # Python Default is 30; we want more info as well

    handler_console = logging.StreamHandler(sys.stdout)
    formatter_console = logging.Formatter('%(message)s')
    handler_console.setFormatter(formatter_console)
    logger_console = logging.getLogger('console')
    logger_console.addHandler(handler_console)
    logger_logfile.setLevel(10)

    handler_logfile = logging.NullHandler()
    formatter_logfile = logging.Formatter('%(message)s')
    handler_logfile.setFormatter(formatter_logfile)
    logger_logfile = logging.getLogger('logfile')
    logger_logfile.addHandler(handler_logfile)
    logger_logfile.setLevel(20)

    handler_debug = logging.NullHandler()
    formatter_debug = logging.Formatter('%(asctime)s - %(message)s')
    handler_debug.setFormatter(formatter_debug)
    logger_debug = logging.getLogger('debug')
    logger_debug.addHandler(handler_debug)
    logger_debug.setLevel(10)

    logfile_directory = None
    logfile_filename = None
    logfile_filepath = None

    debug_directory = None
    debug_filename = None
    debug_filepath = None

    @classmethod
    def _get_new_filehandler(cls, logger_instance, formatter, filepath, append=False, die_if_file_fails=False):
        if append:
            mode = 'a'
        else:
            mode = 'w'

        try:
            new_handler = logging.FileHandler(filepath, mode, encoding='utf8')
        except:
            if die_if_file_fails:
                cls.log_exception('FATAL: Died when opening log file: ', filepath)
            else:
                cls.log('ERROR: Failed to open log file: ', filepath, '\nContinuing with program anyway.')
                new_handler = None

        if new_handler:
            new_handler.setFormatter(formatter)

        return new_handler

    @classmethod
    def log(cls, lvl, msg):
        cls.logger_console.log(lvl, msg)
        cls.logger_logfile.log(lvl, msg)
        cls.logger_debug.log(lvl, msg)

    @classmethod
    def log_exception(cls, msg):
        cls.logger_console.exception(msg)
        cls.logger_logfile.(msg)
        cls.logger_debug.exception(msg)

    @classmethod
    def setlevel_console(cls, level):
        cls.logger_console.setLevel(level)

    @staticmethod
    def generate_logfilename(filename_pre, filename_post='', filename_extension='.log', insert_datetime=True, specific_logname=None):
        if specific_logname:
            return specific_logname

        ret_val = ''

        if filename_pre.endswith('.'):
            filename_pre = filename_pre[:-1]

        if append_datetime:
            timestamp = get_ISOTimestamp_ForLogFilename()
            timeval = '-' + timestamp + '-'
            if filename_pre.endswith('-'):
                filename_pre = filename_pre[:-1]
            if filename_post.startswith('-'):
                filename_pre = filename_pre[1:]
        else:
            timeval = ''

        if filename_post.endswith('.'):
            filename_pre = filename_pre[:-1]

        if not filename_extension.startswith('.'):
            filename_extension = '.' + filename_extension

        ret_val = filename_pre + timestamp + filename_extension

        return ret_val

    @classmethod
    def setup_logfile(cls, log_directory, filename_pre, filename_post='', filename_extension='.log', insert_datetime=True, specific_logname=None,
    append=False, log_level=20, die_if_file_fails=False):
        if log_directory.endswith('\\'):
            log_directory = log_directory[:-1]
        cls.logfile_directory = log_directory
        cls.logfile_filename = cls.generate_logfilename(filename_pre, filename_post, filename_extension, insert_datetime, specific_logname)
        cls.logfile_filepath = cls.logfile_directory + '\\' + cls.logfile_filename
        if append:
            cls.logfile_mode = 'a'
        else:
            cls.logfile_mode = 'w'
        cls.loglevel_logfile = log_level

        try:
            pass
