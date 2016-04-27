import modules.parse_args as parse_args
import modules.get_xml_configs as get_xml_configs
from modules.logging import log_messages as log

parsed_args = parse_args.parse_args()

config_files = get_xml_configs.config_files_xml(parsed_args.config_filepath_list[:])

xml_config_tree = config_files.full_config_tree

config_files.log_config_file_details(40)
