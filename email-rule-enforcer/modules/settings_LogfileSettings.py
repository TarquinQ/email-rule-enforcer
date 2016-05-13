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
        if ((self.log_folder) and (self.log_filename) and (self.filename_extension)):
            self.logfilepath = generate_logfile_fullpath(
                log_directory=self.log_folder, filename_pre=self.log_filename,
                filename_extension=self.filename_extension,
                insert_datetime=self.append_date_to_filename)

    def validate(self):
        if not self.logfilepath:
            return False
        return True

