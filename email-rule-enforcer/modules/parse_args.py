import argparse
import sys
import os.path
import xml.etree.ElementTree as xmltree


class parse_args():
    def __init__(self, prog_version=0):
        parser = argparse.ArgumentParser(description='Enforces rules against a remote email mailbox', version=str(prog_version))
        parser.add_argument('-d', "--debug-level", metavar="debug_level", dest="debug_level", help="Debug verbosity level, 0-7 low-high", type=int)
        parser.add_argument('-c', "--conf-file", metavar="config_file_path", dest="conf_file", help="Path to the config file", action='append')

        self._parser = parser
        self.args = parser.parse_args()

        self.config_filepath_list = self.args.conf_file
        self.debug_level = self.args.debug_level

        self._check_args()
        self.config_files = config_files_xml(self)

    def _check_args(self):
        should_we_exit = False
        if not self.config_filepath_list:
            self._exit_with_error("ERROR: No configuration file has been specified on the command line. At least one is required.\n", 2)

        for possible_file in self.config_filepath_list:
            if not (os.path.isfile(possible_file)):
                self._exit_with_error("ERROR: a specified configuration file does not exist: %s" % possible_file, 3)

            # We now read in all config files & ensure we can read them.
            # Whilst this seems a bit wasteful, since we need to re-read them again soon,
            #  this is ok since we know all config files will be short and OS-cached for next reading.
            try:
                with open(possible_file) as f:
                    contents = f.read()
            except IOError as e:
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
                self._exit_with_error("\nERROR: a specified configuration file could not be read from disk: %s" % possible_file, 3)
            except:
                self._exit_with_error(("ERROR: Unexpected error reading config file %s.\n" % possible_file) + str(sys.exc_info()[0]), 3)

    def _exit_with_error(self, msg, errnum=1):
        print(str(msg) + "\n")
        self._parser.print_help()
        sys.exit(errnum)


class config_files_xml():
    def __init__(self, parent_args):
        self._parent_args = parent_args
        self.config_filepath_list = parent_args.config_filepath_list.copy()
        self.__empty_config_list = [None] * len(self.config_filepath_list)
        self.config_file_contents = self.__empty_config_list.copy()

        self._generate_filepath_shortlist()
        self._read_config_files_contents()
        self._parse_config_files_xml()

    def _generate_filepath_shortlist(self):
        self.short_config_list = self.__empty_config_list.copy()
        for index, config_filename in enumerate(self.config_filepath_list):
            if '/' in config_filename:
                self.short_config_list[index] = config_filename.split('/')[1]
            elif "\\" in config_filename:
                self.short_config_list[index] = config_filename.split("\\")[1]
            else:
                self.short_config_list[index] = config_filename

    def _read_config_files_contents(self):
        for index, config_file in enumerate(self.config_filepath_list):
            # NB: we have read all of these files earlier in this program, so no error handling applied here
            with open(config_file) as f:
                self.config_file_contents[index] = f.read()

    def _parse_config_files_xml(self):
        self.config_xmltrees = self.__empty_config_list.copy()
        for index, filecontents in enumerate(self.config_file_contents):
            try:
                self.config_xmltrees[index] = xmltree.fromstring(filecontents)
            except ParserError as e:
                print "XML Parse Error({0}): {1}".format(e.errno, e.strerror)
                self._parent_args._exit_with_error("\nERROR: a specified XML configuration file could not be read as valid XML.", 3)



# for each config file:
