from collections import OrderedDict
import datetime


class LogfileSettings():
    def __init__(self, logfile_level=2, log_folder=None, log_filename=None, append_date_to_filename=True, filename_extension='.log', continue_on_log_fail=False):
        self.logfile_level = logfile_level
        self.log_folder = log_folder
        self.log_filename = log_filename
        self.append_date_to_filename = append_date_to_filename
        self.filename_extension = filename_extension
        self.continue_on_log_fail = continue_on_log_fail
        self.logfilepath = None
        self.set_full_filepath()

    def set_logfile_level(self, level):
        self.logfile_level = level

    def set_log_folder(self, log_folder):
        self.log_folder = log_folder
        self.set_full_filepath()

    def set_log_filename(self, log_filename):
        self.log_filename = log_filename
        self.set_full_filepath()

    def set_append_date(self, yn):
        self.append_date_to_filename = yn
        self.set_full_filepath()

    def set_filename_extension(self, ext):
        self.filename_extension = ext
        self.set_full_filepath()

    def set_continute_on_log_fail(self, yn):
        self.continue_on_log_fail = yn

    def set_full_filepath(self):
        if (
            (self.log_folder) and
            (self.log_filename) and
            (self.append_date_to_filename) and
            (self.filename_extension)
        ):
            self.logfilepath = generate_logfile_fullpath(
                log_directory=self.log_folder, filename_pre=self.log_filename,
                filename_extension=self.filename_extension,
                insert_datetime=self.append_date_to_filename
            )

    def validate(self):
        if not self.logfilepath:
            return False
        return True

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        retval = OrderedDict()
        retval['Log Level'] = self.logfile_level
        retval['Log Path'] = self.logfilepath
        retval['Continue on log fail'] = self.continue_on_log_fail
        return '%s:' % self.__class__.__name__ + str(retval)


def generate_logfile_fullpath(log_directory, filename_pre='', filename_post='', filename_extension='.log', insert_datetime=True, specific_logname=None):
    if not log_directory.endswith('/'):
        log_directory = log_directory + '/'

    if specific_logname:
        filename = specific_logname
    else:
        filename = generate_logfilename(filename_pre, filename_post, filename_extension, insert_datetime)

    filepath = log_directory + filename

    return filepath


def generate_logfilename(filename_pre='', filename_post='', filename_extension='log', insert_datetime=True):
    ret_val = ''

    if filename_pre.endswith('.'):
        filename_pre = filename_pre[:-1]

    timeval = ''
    if insert_datetime:
        timestamp = get_ISOTimestamp_ForLogFilename()
#        print ('timestamp: ', timestamp)
        timeval = '-' + timestamp + '-'
#        print ('timeval:   ', timeval)
        if filename_pre.endswith('-'):
            filename_pre = filename_pre[:-1]
        if (filename_post == ''):
            timeval = timeval[:-1]
        elif filename_post.startswith('-'):
            timeval = timeval[:-1]

    if filename_post.endswith('.'):
        filename_post = filename_post[:-1]

    if filename_extension.startswith('.'):
        filename_extension = filename_extension[1:]

    ret_val = filename_pre + timeval + filename_post + '.' + filename_extension

    if (
        (ret_val == '.') or
        (ret_val == ('.' + filename_extension))
    ):
        raise ValueError('Log filename was not specific enough to log against. Final value:', ret_val)

    return ret_val


def get_ISOTimestamp_ForLogFilename():
    timestamp = datetime.datetime.now().isoformat()  # '2016-03-20T21:30:44.560397'
    timestamp = ''.join(timestamp.split(':')[0:2])  # Remove the seconds & milliseconds => '2016-03-20T2130'
    timestamp = timestamp.replace('T', '')  # Remove the 'T' => '2016-03-202130'
    timestamp = timestamp.replace('-', '')  # Remove the 'T' => '201603202130'
    return timestamp
