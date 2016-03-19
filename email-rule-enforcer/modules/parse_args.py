import argparse
import sys
import os.path
import xml.etree.ElementTree as ET
from .supportingfunctions import die_with_errormsg


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

    def _check_args(self):
        if not self.config_filepath_list:
            die_with_errormsg("ERROR: No configuration file has been specified on the command line. At least one is required.\n", 2)

        for possible_file in self.config_filepath_list:
            if not (os.path.isfile(possible_file)):
                die_with_errormsg("ERROR: a specified configuration file does not exist: %s" % possible_file, 3)

            # We now read in all config files & ensure we can read them.
            # Whilst this seems a bit wasteful, since we don't keep the read files yet need to re-read them again soon,
            #  this is ok since we know all config files will be quite small and OS-cached for next reading.
            # This saves passing around extra objects at this stage
            try:
                with open(possible_file) as f:
                    contents = f.read()
            except IOError as e:
                print ("I/O error({0}): {1}".format(e.errno, e.strerror))
                die_with_errormsg("\nERROR: a specified configuration file could not be read from disk: %s" % possible_file, 3)
            except:
                die_with_errormsg(("ERROR: Unexpected error reading config file %s.\n" % possible_file) + str(sys.exc_info()[0]), 3)

