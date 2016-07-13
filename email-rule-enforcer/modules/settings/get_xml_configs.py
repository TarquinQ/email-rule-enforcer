import sys
import xml.etree.ElementTree as ET
from modules.supportingfunctions import die_with_errormsg
from modules.logging import LogMaster


class ConfigFilesXML():
    def __init__(self, config_filepath_list):
        self.config_filepath_list = config_filepath_list[:]
        self._num_config_files = len(self.config_filepath_list)
        self.config_file_contents = dict()
        self.config_xmltrees = dict()
        self.short_configpath_list = [None] * self._num_config_files
        self._indexed_short_pathlist = [None] * self._num_config_files
        self.full_config_tree = ET.fromstring('<emailenforcer></emailenforcer>')

        self._generate_filepath_shortlists()
        self._read_config_files_contents()
        self._parse_config_files_xml()

    def _generate_filepath_shortlists(self):
        for index, config_filename in enumerate(self.config_filepath_list):
            LogMaster.info('Now parsing config_filename: %s', config_filename)
            if '/' in config_filename:
                shortname = config_filename.split('/')[-1]
            elif "\\" in config_filename:
                shortname = config_filename.split("\\")[-1]
            else:
                shortname = config_filename
            #LogMaster.debug('config shortname is:  %s', shortname)
            self.short_configpath_list[index] = shortname
            self._indexed_short_pathlist[index] = str(index) + '_' + shortname  # To ensure name uniqueness

    def _read_config_files_contents(self):
        for index, config_file in enumerate(self.config_filepath_list):
            # NB: we have read all of these files earlier in this program, so no error handling applied here
            with open(config_file) as f:
                self.config_file_contents[self._indexed_short_pathlist[index]] = f.read()

    def _parse_config_files_xml(self):
        LogMaster.debug("Now parsing all config file contents")
        for index in range(self._num_config_files):
            filename_to_parse = self.config_filepath_list[index]
            shortfilename_to_parse = self._indexed_short_pathlist[index]
            filecontents_to_parse = self.config_file_contents[self._indexed_short_pathlist[index]]
            try:
                self.config_xmltrees[shortfilename_to_parse] = ET.fromstring(filecontents_to_parse)
            except ET.ParseError as xmlError:
                LogMaster.critical("\n****\nERROR: XML Config File cannot be read due to malformed XML file.\n")
                LogMaster.critical("Error in file:  %s", filename_to_parse)
                LogMaster.critical("Error returned is xmlerror code " + str(xmlError.code) + ": " + str(xmlError) + "\n\n*****\n")
                die_with_errormsg("", 3)
            # No error handling, as previous ET.fromstring operation succeeded or died
            self.full_config_tree.extend(ET.fromstring(filecontents_to_parse))

    def debug_print_config_file_details(self):
        print ("Now dumping all config file details and contents.\n")
        print ("Number of config files: " + str(self._num_config_files))
        print ("List of config files: ", self.config_filepath_list)
        print ('\n')

        for index in range(self._num_config_files):
            filename_to_parse = self.config_filepath_list[index]
            shortfilename_to_parse = self._indexed_short_pathlist[index]
            filecontents_to_parse = self.config_file_contents[self._indexed_short_pathlist[index]]
            config_xmltree = self.config_xmltrees[shortfilename_to_parse]

            print ("Config file {0}: {1}".format(index, filename_to_parse))
            print ("Config file shortname: {0}".format(shortfilename_to_parse))
            print ("Config file contents:")
            print (filecontents_to_parse)
            print ("Config file XML tree:")
            print (config_xmltree)
            print (ET.dump(config_xmltree))
            print ('\n')

        print ("Global XML tree:")
        print (self.full_config_tree)
        print (ET.dump(self.full_config_tree))
        print (ET.tostring(self.full_config_tree))

    def log_config_file_details(self, log_level=10):
        LogMaster.log(log_level, "Number of config files:  %s", self._num_config_files)
        LogMaster.log(log_level, "List of config files:  %s", self.config_filepath_list)

        for index in range(self._num_config_files):
            filename_to_parse = self.config_filepath_list[index]
            shortfilename_to_parse = self._indexed_short_pathlist[index]
            filecontents_to_parse = self.config_file_contents[self._indexed_short_pathlist[index]]
            config_xmltree = self.config_xmltrees[shortfilename_to_parse]

            #LogMaster.log(log_level, "Config file  %s:  %s", index, filename_to_parse)
