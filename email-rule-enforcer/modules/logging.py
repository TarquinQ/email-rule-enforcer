import logging
import sys
import datetime
from modules.settings.models.LogfileSettings import LogfileSettings
from modules.supportingfunctions import die_with_errormsg, get_username, get_hostname, get_os_str
from modules.supportingfunctions import nested_data_to_str
from modules.models.Singleton import Singleton
try:
    import colorlog
    console_colours = True
except ImportError:
    console_colours = False


class LogController():
    debug_this_class = False
    """Wraps around the standard Logger class, and builds logs the way we want to."""
    def __init__(self, name, log_level=10, filepath=None, console=False):
        # Sets up a new logger, and sets it to Null by default
        self.name = name
        self.formatter_default = self.get_formatter_plainmsg()
        self.handler_null = logging.NullHandler()
        if console and console_colours:
            self.logger = colorlog.getLogger(name)
        else:
            self.logger = logging.getLogger(name)
            self.logger.addHandler(self.handler_null)
        self.set_loglevel(log_level)
        #     self.filepath = filepath
        # else:
        #     self.set_logger_console()
        if self.debug_this_class:
            print("New log controller intiated; name: ", self.name, " level: ", log_level)

    def get_formatter_default(self):
        return self.get_formatter_plainmsg()

    @staticmethod
    def get_formatter_plainmsg(coloured=False):
        if coloured:
            log_colours = {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red'
            }
            return colorlog.ColoredFormatter('%(log_color)s%(message)s', log_colors=log_colours)
        else:
            return logging.Formatter('%(message)s')

    @staticmethod
    def get_formatter_msgwithtime():
        return logging.Formatter('%(asctime)s - %(message)s')

    @staticmethod
    def get_handler_console():
        return logging.StreamHandler(sys.stdout)

    def get_formatter_console(self):
        return self.get_formatter_plainmsg(console_colours)

    def set_logger_console(self):
        """Enables output from this LogController to the console, via stdout"""
        self.handler_console = self.get_handler_console()
        self.formatter = self.get_formatter_console()
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
                #print('Added new file as a log handler. Lofile name:', filepath)
        except:
            if die_if_file_fails:
                print('FATAL: Died when opening log file: %s' % filepath)
                die_with_errormsg('FATAL: Died when opening log file: ', filepath)
            else:
                print('ERROR: Failed to open log file: %s\nContinuing with program anyway.' % filepath)
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
                print('FATAL: Died when opening log file: %s' % filepath)
                die_with_errormsg('FATAL: Died when opening log file: ', filepath)
            else:
                print('ERROR: Failed to open log file: %s\nContinuing with program anyway.' % filepath)
                new_handler = None

        return new_handler


class LogMaster(metaclass=Singleton):
    """Provides unified console and file logging for whole app"""
    debug_this_class = False
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

    @classmethod
    def ultra_debug(cls, msg, *args, **kwargs):
        cls.log(8, '*UltraDebug :: ' + msg, *args, **kwargs)

    @classmethod
    def insane_debug(cls, msg, *args, **kwargs):
        cls.log(5, '*InsaneDebug:: ' + msg, *args, **kwargs)

    # Methods to operate on specific log_controllers
    @classmethod
    def log_to_logfile(cls, lvl, msg, *args, **kwargs):
        cls.controller_logfile.logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def log_to_console(cls, lvl, msg, *args, **kwargs):
        cls.controller_console.logger.log(lvl, msg, *args, **kwargs)

    @classmethod
    def log_to_debugfile(cls, lvl, msg, *args, **kwargs):
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
    # Override if Ultra or Insane Debug config options set
    if config['console_ultra_debug']:
        LogMaster.set_loglevel_console(8)
        LogMaster.info('** Ultra Debug set. This will print a lot of extra debug info to the console.')
        config['imap_imaplib_debuglevel'] = 3
        config['smtp_smtplib_debuglevel'] = True
    if config['console_insane_debug']:
        LogMaster.set_loglevel_console(4)
        LogMaster.info('** Insane Debug set. This will print an insane amount of extra debug info to the console.')
        config['imap_imaplib_debuglevel'] = 4
        config['smtp_smtplib_debuglevel'] = True

    settings_logfile = config['log_settings_logfile']
    settings_debugfile = config['log_settings_logfile_debug']

    # Init debug log file first, so that when(/if) main log initialised there is no spurious message about debug log added
    if ((settings_debugfile is not None) and (isinstance(settings_debugfile, LogfileSettings))):
        LogMaster.add_filepath_to_debugfile(
            filepath=settings_debugfile.log_fullpath,
            formatter=LogController.get_formatter_msgwithtime(),
            die_if_file_fails=settings_debugfile.continue_on_log_fail
        )
        LogMaster.set_loglevel_debugfile(settings_debugfile.logfile_level * 10)

        LogMaster.log_to_debugfile(50, log_file_headers(config, 'Debug Log'))
        LogMaster.info('New DebugFile added, path: %s', settings_logfile.log_fullpath)

    if ((settings_logfile is not None) and (isinstance(settings_logfile, LogfileSettings))):
        LogMaster.add_filepath_to_logfile(
            filepath=settings_logfile.log_fullpath,
            die_if_file_fails=settings_logfile.continue_on_log_fail
        )
        LogMaster.set_loglevel_logfile(settings_logfile.logfile_level * 10)

        # Now we initialise the file and print info
        LogMaster.log_to_logfile(50, log_file_headers(config, 'Output Log File'))
        LogMaster.info('New LogFile added, path: %s', settings_logfile.log_fullpath)


def ultradebug_rules_and_config(config, rules_main, rules_all):
    LogMaster.ultra_debug("Unified Config:\n%s", '\n'.join(nested_data_to_str(config)))
    LogMaster.ultra_debug("Rules for Main Folder (Inbox):\n%s", '\n'.join(nested_data_to_str(rules_main)))
    LogMaster.ultra_debug("Rules for All Folders:\n%s", '\n'.join(nested_data_to_str(rules_all)))


def log_file_headers(config, logname):
    ret_val = [
        '*************************************',
        '** Log File for Email Rule Enforcer',
        '** Log name is: %s' % logname,
        '** ',
        '** Current time is %s' % datetime.datetime.now(),
        '** ',
        '** Running on host: %s' % get_hostname(),
        '** Running as user: %s' % get_username(),
        '** ',
        '*************************************',
        '** ',
        '** Important Config info for this session:',
        '** IMAP Server: %s' % config['imap_server_name'],
        '** IMAP Username: %s' % config['imap_username'],
        '** IMAP Port Number: %s, Use SSL: %s' % (str(config['imap_server_port']), config['imap_use_tls']),
        '** IMAP Initial Folder: %s' % config['imap_initial_folder'],
        '** IMAP Deletions Folder: %s' % config['imap_deletions_folder'],
        '** IMAP Empty Deleted Items on Exit: %s' % config['empty_trash_on_exit'],
        '** SMTP Server: %s' % config['smtp_server_name'],
        '** SMTP Port Number: %s, Use SSL: %s,' % (str(config['smtp_server_port']), config['smtp_use_tls']),
        '** SMTP Auth Required: %s' % config['smtp_auth_required'],
        '** SMTP Username: %s' % config['smtp_username'],
        '** Send Email on Completion: %s' % config['notification_email_on_completion'],
        '** ',
        '*************************************',
        '** ',
    ]
    return '\n'.join(ret_val)


# log_levels = OrderedDict([
#     (50, 'CRITICAL'),
#     (40, 'ERROR'),
#     (30, 'WARNING'),
#     (20, 'INFO'),
#     (10, 'DEBUG'),
#     (0, 'NOTSET')
# ])

