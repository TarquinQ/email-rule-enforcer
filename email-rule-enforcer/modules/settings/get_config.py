import modules.settings.parse_args as parse_args
from modules.settings.get_xml_configs import ConfigFilesXML
from modules.logging import LogMaster
from modules.settings.get_settings_from_xmltree import get_settings_from_configtree
from modules.supportingfunctions import print_nested_data, nested_data_to_str


def print_rules_and_config(config, rules):

#    print_nested_data(config)
#    print_nested_data(rules)
    print("Config:")
    print(*nested_data_to_str(config), sep='\n')
    print("Rules:")
    print(*nested_data_to_str(rules), sep='\n')


def get_config():
    """Gets all program configuration, including command line and xml configs"""
    # Get CLI arguments
    parsed_args = parse_args.parse_args()
    list_of_configfiles = parsed_args.config_filepath_list[:]
    # Get xml files,parse into XML tree
    config_files = ConfigFilesXML(list_of_configfiles)
    config_files.log_config_file_details(40)
    xml_config_tree = config_files.full_config_tree
    # Parse XML Tree into actual config
    (config, rules) = get_settings_from_configtree(xml_config_tree)

    # Dump out a list to command
    print_rules_and_config(config, rules)

    return (config, rules)
