import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
import modules.parse_args as parse_args
import modules.get_xml_configs as get_xml_configs
from modules.logging import log_messages as log_msg


prog_version = '0.01-inital-build'

parsed_args = parse_args.parse_args(prog_version=prog_version)
config_files = get_xml_configs.config_files_xml(parsed_args.config_filepath_list[:])

xml_config_tree = config_files.full_config_tree

log_msg.log(30, "Test Warning from logger")
