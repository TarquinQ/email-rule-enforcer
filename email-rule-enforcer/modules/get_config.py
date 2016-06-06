import modules.parse_args as parse_args
import modules.get_xml_configs as get_xml_configs
from modules.logging import log_messages as log
from modules.get_settings_from_xmltree import get_settings_from_configtree, rules, config


def print_rules_and_config(rules, config):
    print(config)
    print(rules)
    for rule in rules:
        print(str(rule))


def get_config():
    parsed_args = parse_args.parse_args()
    config_files = get_xml_configs.config_files_xml(parsed_args.config_filepath_list[:])
    xml_config_tree = config_files.full_config_tree
    get_settings_from_configtree(xml_config_tree)
    config_files.log_config_file_details(40)

    print_rules_and_config(rules, config)
