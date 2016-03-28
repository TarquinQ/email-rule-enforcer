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

    @classmethod
    def add_logfile(cls, filepath=None, log_level=20, append=False, die_if_file_fails=False):
        cls.logfile_filepath = filepath
        if append:
            logfile_mode = 'a'
        else:
            logfile_mode = 'w'
        cls.loglevel_logfile = log_level

        try:
            cls.handler_logfile = cls._get_new_filehandler(cls.logger_logfile, cls.formatter_logfile, cls.logfile_filepath, logfile_mode, die_if_file_fails)
            if cls.handler_logfile:
                cls.logger_logfile.addHandler(cls.handler_logfile)

        except:
            if die_if_file_fails:
                cls.log_exception('FATAL: Died when opening log file: ', filepath)
                die_with_errormsg('FATAL: Died when opening log file: ', filepath)
            else:
                cls.log('ERROR: Failed to open log file: ', filepath, '\nContinuing with program anyway.')

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
                die_with_errormsg('FATAL: Died when opening log file: ', filepath)
            else:
                cls.log('ERROR: Failed to open log file: ', filepath, '\nContinuing with program anyway.')
                new_handler = None

        if new_handler:
            new_handler.setFormatter(formatter)

        return new_handler

    @classmethod
    def generate_logfile_fullpath(cls, log_directory, filename_pre, filename_post='', filename_extension='.log', insert_datetime=True, specific_logname=None):
        if not log_directory.endswith('\\'):
            log_directory = log_directory + '\\'

        if specific_logname:
            filename = specific_logname
        else:
            filename = cls.generate_logfilename(filename_pre, filename_post, filename_extension, insert_datetime, None)

        filepath = log_directory + filename

        return filepath

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

