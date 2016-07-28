import logging
import sys
from modules.supportingfunctions import die_with_errormsg
from modules.settings.models.LogfileSettings import LogfileSettings


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LogController():
    debug_this_class = False
    """Wraps around the standard Logger class, and builds logs the way we want to."""
    def __init__(self, name, log_level=10, filepath=None):
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
        """Enables output from this LogController to the console, via stdout"""
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
        """Enables output from this LogController to a filename"""
        self.filepath = filepath
        if formatter is None:
            self.formatter_file = self.get_formatter_default()
        else:
            self.formatter_file = formatter

        try:
            new_handler = self._get_new_filehandler(self.filepath, append, die_if_file_fails)
            if new_handler is not None:
                self.handler_file = new_handler
                self.handler_file.setFormatter(self.formatter_file)
                self.logger.addHandler(self.handler_file)
                print('Added new file as a log handler. Lofile name:', filepath)
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


class LogMaster(metaclass=Singleton):
    """Provides unified console and file logging for whole app"""
    debug_this_class = True
    name_console = 'console'
    name_logfile = 'logfile'
    name_debugfile = 'debugfile'
    controller_console = LogController(name_console)
    controller_console.set_logger_console()
    controller_logfile = LogController(name_logfile)
    controller_debugfile = LogController(name_debugfile)
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
        cls.log_controllers[contr_name].logger.setLevel(log_level)

    @classmethod
    def _log_to_namedcontr(cls, contr_name, lvl, msg, *args, **kwargs):
        cls.log_controllers[contr_name].logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def _add_logfile_to_namedcontr(cls, contr_name, filepath, append=False, formatter=None, die_if_file_fails=False):
        if cls.debug_this_class:
            print ('Now adding new log file handler to log file output.')
            print ('  Log controller: ', contr_name, '. Logfile path:', filepath)
        cls.log_controllers[contr_name].add_logfile(filepath, append, formatter, die_if_file_fails)

    # Methods to set up specific log_controllers
    @classmethod
    def set_loglevel_console(cls, log_level):
        cls._set_loglevel_namedcontr(cls.name_console, log_level)

    @classmethod
    def set_loglevel_logfile(cls, log_level):
        cls._set_loglevel_namedcontr(cls.name_logfile, log_level)

    @classmethod
    def set_loglevel_debugfile(cls, log_level):
        cls._set_loglevel_namedcontr(cls.name_debugfile, log_level)

    @classmethod
    def add_filepath_to_logfile(cls, *args, **kwargs):
        cls._add_logfile_to_namedcontr(cls.name_logfile, *args, **kwargs)

    @classmethod
    def add_filepath_to_debugfile(cls, *args, **kwargs):
        cls._add_logfile_to_namedcontr(cls.name_debugfile, *args, **kwargs)


def add_log_files_from_config(config):
    """Add all of the logging config from config files and enacts them on the LogMaster object"""

    LogMaster.set_loglevel_console(config['console_loglevel'] * 10)

    settings_logfile = config['log_settings_logfile']
    settings_debugfile = config['log_settings_logfile_debug']

    if ((settings_logfile is not None) and (isinstance(settings_logfile, LogfileSettings))):
        print ('New logfile settings to be added:')
        print ('  LogFile or DebugFile: LogFile')
        print ('  Path: ', settings_logfile.log_fullpath)
        print ('  Continue on failure: ', settings_logfile.continue_on_log_fail)
        LogMaster.add_filepath_to_logfile(
            filepath=settings_logfile.log_fullpath,
            die_if_file_fails=settings_logfile.continue_on_log_fail
        )
        LogMaster.set_loglevel_logfile(settings_logfile.logfile_level * 10)

    if ((settings_debugfile is not None) and (isinstance(settings_debugfile, LogfileSettings))):
        LogMaster.add_filepath_to_debugfile(
            filepath=settings_debugfile.log_fullpath,
            formatter=LogController.get_formatter_msgwithtime(),
            die_if_file_fails=settings_debugfile.continue_on_log_fail
        )
        LogMaster.set_loglevel_debugfile(settings_debugfile.logfile_level * 10)

# log_levels = OrderedDict([
#     (50, 'CRITICAL'),
#     (40, 'ERROR'),
#     (30, 'WARNING'),
#     (20, 'INFO'),
#     (10, 'DEBUG'),
#     (0, 'NOTSET')
# ])

