import logging
import sys
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


class log_controller():
    debug_this_class = False
    """Wraps around the standard Logger class, and builds logs the way we want to."""
    def __init__(self, name, log_level=20, filepath=None):
        # Sets up a new logger, and sets it to Null by default
        self.name = name
        self.logger = logging.getLogger(name)
        self.formatter_default = self.get_formatter_plainmsg()
        self.handler_null = logging.NullHandler()
        self.logger.addHandler(self.handler_null)
        self.set_loglevel(log_level)
        # if filepath:
        #     self.filepath = filepath
        # else:
        #     self.set_logger_console()
        if self.debug_this_class:
            print("New log controller intiated; name: ", self.name, " level: ", log_level)

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
        """Enables output from this log_controller to the console, via stdout"""
        self.handler_console = self.get_handler_console()
        self.formatter = self.get_formatter_plainmsg()
        self.handler_console.setFormatter(self.formatter)
        self.logger.addHandler(self.handler_console)
        if self.debug_this_class:
            print("Log controller set to console; Controller name: ", self.name)

    def set_loglevel(self, log_level=None):
        if log_level: self.log_level = log_level
        self.logger.setLevel(self.log_level)
        if self.debug_this_class:
            print("Log controller level changed; Controller name: ", self.name, " New level is ", self.log_level)

    def add_logfile(self, filepath, append=False, formatter=None, die_if_file_fails=False):
        """Enables output from this log_controller to a filename"""
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
        if self.debug_this_class:
            print("Log controller filename added; Controller name: ", self.name, " new level is ", self.log_level)

    def _get_new_filehandler(self, filepath, append=False, die_if_file_fails=False):
        if append:
            mode = 'a'
        else:
            mode = 'w'

        if self.debug_this_class:
            print("Log controller filehandle addition attempt; Controller name: ", self.name, ", mode: ", mode, ", path: ", filepath)

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


class log_messages(metaclass=Singleton):
    """Provides unified console and file logging for whole app"""
    debug_this_class = False
    name_console = 'console'
    name_logfile = 'logfile'
    name_debugfile = 'debugfile'
    controller_console = log_controller(name_console)
    controller_console.set_logger_console()
    controller_logfile = log_controller(name_logfile)
    controller_debugfile = log_controller(name_debugfile)
    log_controllers = {name_console: controller_console, name_logfile: controller_logfile, name_debugfile: controller_debugfile}
    if debug_this_class:
        print('New log controllers established: ', log_controllers)

    # General Methods to operate on all log_controllers
    @classmethod
    def log(cls, lvl, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            if cls.debug_this_class:
                print('Now logging a message for controller. Name: ', log_controller.name, ", msg: ", msg, str(*args), str(**kwargs))
            log_controller.logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def debug(cls, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            log_controller.logger.debug(msg, *args, **kwargs)

    @classmethod
    def info(cls, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            log_controller.logger.info(msg, *args, **kwargs)

    @classmethod
    def warning(cls, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            log_controller.logger.warning(msg, *args, **kwargs)

    @classmethod
    def error(cls, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            log_controller.logger.error(msg, *args, **kwargs)

    @classmethod
    def critical(cls, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            log_controller.logger.critical(msg, *args, **kwargs)

    @classmethod
    def exception(cls, msg, *args, **kwargs):
        for log_controller in cls.log_controllers.values():
            log_controller.logger.exception(msg, *args, **kwargs)

    # Methods to operate on specific log_controllers
    @classmethod
    def log_to_logfile(cls, lvl, msg, *args, **kwargs):
        cls.controller_logfile.logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def log_to_console(cls, lvl, msg, *args, **kwargs):
        cls.controller_console.logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def log_to_debug(cls, lvl, msg, *args, **kwargs):
        cls.controller_debugfile.logger.log(lvl, msg, *args, **kwargs)

    # Methods to operate on named controllers
    @classmethod
    def _set_loglevel_namedcontr(cls, contr_name, log_level):
        cls.log_controllers[contr_name].logger.set_loglevel(log_level)

    @classmethod
    def _log_to_namedcontr(cls, contr_name, lvl, msg, *args, **kwargs):
        cls.log_controllers[contr_name].logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def _add_logfile_to_namedcontr(cls, contr_name, filepath, append=False, formatter=None, die_if_file_fails=False):
        cls.log_controllers[contr_name].add_logfile(filepath, append, formatter, die_if_file_fails)

    # Methods to set up specific log_controllers
    @classmethod
    def set_loglevel_console(cls, log_level):
        cls._set_loglevel_namedcontr(cls.name_console, lvl)

    @classmethod
    def set_loglevel_logfile(cls, log_level):
        cls._set_loglevel_namedcontr(cls.name_logfile, lvl)

    @classmethod
    def set_loglevel_debugfile(cls, log_level):
        cls._set_loglevel_namedcontr(cls.name_debugfile, lvl)

    @classmethod
    def add_filepath_to_logfile(cls, filepath, append=False, formatter=None, die_if_file_fails=False):
        cls._add_logfile_to_namedcontr(cls, cls.name_logfile, filepath, append=False, formatter=None, die_if_file_fails=False)

    @classmethod
    def add_filepath_to_debugfile(cls, filepath, append=False, formatter=None, die_if_file_fails=False):
        cls._add_logfile_to_namedcontr(cls, cls.name_debugfile, filepath, append=False, formatter=None, die_if_file_fails=False)


# log_levels = OrderedDict([
#     (50, 'CRITICAL'),
#     (40, 'ERROR'),
#     (30, 'WARNING'),
#     (20, 'INFO'),
#     (10, 'DEBUG'),
#     (0, 'NOTSET')
# ])

