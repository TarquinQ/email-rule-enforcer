import argparse
import sys
import os.path
import xml.etree.ElementTree as xmltree


class parse_args():
    def __init__(self, prog_version=0):
        parser = argparse.ArgumentParser(description=('Enforces rules against a remote email mailbox, version ' + str(prog_version)))
        parser.add_argument('-d', "--debug-level", metavar="debug_level", dest="debug_level", help="Debug verbosity level, 0-7 low-high", type=int, default=3)
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
            # Whilst this seems a bit wasteful, since we don't keep the read files yet need to re-read them again soon,
            #  this is ok since we know all config files will be small and OS-cached for next reading.
            # This saves passing around extra objects at this stage
            try:
                with open(possible_file) as f:
                    contents = f.read()
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
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
        self.config_filepath_list = parent_args.config_filepath_list[:]
        self._num_config_files = len(self.config_filepath_list)
        self.config_file_contents = dict()
        self.config_xmltrees = dict()

        self._generate_filepath_shortlists()
        self._read_config_files_contents()
        self._parse_config_files_xml()

    def _generate_filepath_shortlists(self):
        self.short_configpath_list = [None] * self._num_config_files
        self._indexed_short_pathlist = [None] * self._num_config_files
        for index, config_filename in enumerate(self.config_filepath_list):
            if '/' in config_filename:
                self.short_configpath_list[index] = str(config_filename.split('/')[-1:])
            elif "\\" in config_filename:
                self.short_configpath_list[index] = str(config_filename.split("\\")[-1:])
            else:
                self.short_configpath_list[index] = str(config_filename)
            self._indexed_short_pathlist[index] = str(index) + '_' + str(self.short_configpath_list[index])  # To ensure uniqueness

    def _read_config_files_contents(self):
        for index, config_file in enumerate(self.config_filepath_list):
            # NB: we have read all of these files earlier in this program, so no error handling applied here
            with open(config_file) as f:
                self.config_file_contents[self._indexed_short_pathlist[index]] = f.read()

    def _parse_config_files_xml(self):
        for index in range(self._num_config_files):
            self.config_xmltrees[self._indexed_short_pathlist[index]] = xmltree.fromstring(self.config_filepath_list[index])
            try:
                self.config_xmltrees[self._indexed_short_pathlist[index]] = xmltree.fromstring(self.config_filepath_list[index])
            except xmltree.ParseError as xmlError:
                print ("\n****\nERROR: XML Config File cannot be read due to malformed XML file.\n")
                print ("Error in file: " + self.config_filepath_list[index])
                print ("Error returned is xmlerror code " + str(xmlError.code) + ": " + str(xmlError) + "\n\n*****")
                self._parent_args._exit_with_error("", 3)



# for each config file:
