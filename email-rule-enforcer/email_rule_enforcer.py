from modules.parse_args import parse_args


prog_version = '0.01inital-build'


sysvargs = parse_args(prog_version=prog_version)

print (sysvargs.config_files)
print (sysvargs.debug_level)

# for each contents:
# 	parseXML(contents)


