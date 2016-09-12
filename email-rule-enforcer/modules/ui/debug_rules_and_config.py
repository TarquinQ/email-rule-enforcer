from modules.supportingfunctions import nested_data_to_str
from modules.logging import LogMaster


def debug_rules_and_config(config, rules_main, rules_all):
    LogMaster.debug("Unified Config:\n%s", '\n'.join(nested_data_to_str(config.clone_nopasswd())))
    LogMaster.debug("Rules for Main Folder (Inbox):\n%s", '\n'.join(nested_data_to_str(rules_main)))
    LogMaster.debug("Rules for All Folders:\n%s", '\n'.join(nested_data_to_str(rules_all)))


