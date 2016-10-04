import argparse
import sys
import os.path
import glob
import xml.etree.ElementTree as ET
from modules.supportingfunctions import die_with_errormsg


class parse_args():
    def __init__(self):
        parser = argparse.ArgumentParser(description=('Enforces rules against a remote email mailbox'))
        parser.add_argument('-c', "--conf", metavar="config_file_path", dest="conf_filedir", help="Path to a config file, or a directory of config files", action='append')

        self.args = parser.parse_args()

        self.file_testlist = self.args.conf_filedir
        self.config_filepath_list = []

        if not self.file_testlist:
            die_with_errormsg("ERROR: No configuration file or directory has been specified on the command line.\n" +
                "At least one is required.\n", 2)

        for possible_file_or_dir in self.file_testlist:
            # We now read in all config files & ensure we can read them.
            # Whilst this seems a bit wasteful, since we don't keep the read files,
            #  this is ok since we know all config files will be quite small and OS-cached for next reading.
            # This saves passing around extra objects at this stage
            if (os.path.isfile(possible_file_or_dir)):
                self.open_and_read_file_or_die(possible_file_or_dir)
                self.config_filepath_list.append(
                    os.path.abspath(possible_file_or_dir)
                )
            elif (os.path.isdir(possible_file_or_dir)):
                dir_path = os.path.normpath(possible_file_or_dir)

                filelist = glob.glob(dir_path + '/*.xml')
                for filename in filelist:
                    self.open_and_read_file_or_die(filename)
                    self.config_filepath_list.append(filename)

            else:
                die_with_errormsg("ERROR: a specified configuration file does not exist: %s" % possible_file_or_dir, 3)

    @staticmethod
    def open_and_read_file_or_die(possible_file):
        try:
            with open(possible_file) as f:
                contents = f.read()
        except IOError as e:
            print ("I/O error({0}): {1}".format(e.errno, e.strerror))
            die_with_errormsg("\nERROR: a specified configuration file could not be read from disk: %s" % possible_file, 3)
        except:
            die_with_errormsg(("ERROR: Unexpected error reading config file %s.\n" % possible_file) + str(sys.exc_info()[0]), 3)


