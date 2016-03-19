from modules.parse_args import parse_args
import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support

prog_version = '0.01-inital-build'


sysvargs = parse_args(prog_version=prog_version)

print (sysvargs.config_files)
print (sysvargs.debug_level)

# for each contents:
# 	parseXML(contents)


