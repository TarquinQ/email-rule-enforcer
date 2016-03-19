from modules.parse_args import parse_args
import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support

prog_version = '0.01-inital-build'


sysvargs = parse_args(prog_version=prog_version)
config_files = sysvargs.config_files

config_files.debug_print_config_file_details()

# for each contents:
# 	parseXML(contents)


