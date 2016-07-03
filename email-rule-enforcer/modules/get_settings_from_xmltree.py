import re
import xml.etree.ElementTree as ET
import modules.supportingfunctions
from modules.supportingfunctions import convert_text_to_boolean, die_with_errormsg
from modules.settings_Class_EmailNotifications import EmailNotificationSettings
from modules.settings_Class_LogfileSettings import LogfileSettings
from modules.settings_DefaultSettings import set_defaults
from modules.rule_Classes import Rule, RuleAction, MatchField
from modules.supportingfunctions_xml import set_value_if_xmlnode_exists, get_value_if_xmlnode_exists, get_attributes_if_xmlnode_exists
from modules.supportingfunctions_xml import get_attribvalue_if_exists_in_xmlNode, set_boolean_if_xmlnode_exists, xpath_findall


def parse_config_tree(xml_config_tree, config, rules):
    """Parses the XML config tree, and all fields therein."""

    def parse_auth(Node, config):
        """This function takes the XML node for config_authinfo and parses all expected contents"""
        if Node is None:
            return

        set_value_if_xmlnode_exists(config, 'imap_username', Node, './/imap_auth/username')
        set_value_if_xmlnode_exists(config, 'imap_password', Node, './/imap_auth/password')
        set_value_if_xmlnode_exists(config, 'smtp_username', Node, './/smtp_email/username')
        set_value_if_xmlnode_exists(config, 'smtp_password', Node, './/smtp_email/password')

    def parse_general(Node, config):
        """This function takes the XML node for config_general and parses all expected contents"""
        if Node is None:
            return

        def parse_email_notification_settings(config, Node):
            """Parses the email notification xml section"""
            if Node:
                sendme = EmailNotificationSettings()
                for subnode in xpath_findall(Node, './recipient_email'):
                    sendme.add_recipient(subnode.text)
                for subnode in xpath_findall(Node, './subject'):
                    sendme.set_subject(subnode.text)
                for subnode in xpath_findall(Node, './body_prefix'):
                    sendme.set_body_prefix(subnode.text)
                for subnode in xpath_findall(Node, './attach_log'):
                    attach_yn = convert_text_to_boolean(subnode.text, False)
                    if attach_yn is not None:
                        sendme.set_attach_log(attach_yn)
                config['notification_email_on_completion'] = sendme
                config['send_notification_email_on_completion'] = True

        def parse_logfile_settings(config, logtitle, Node):
            """Parses the logfile xml section"""
            if Node:
                logset = LogfileSettings()
                for subnode in xpath_findall(Node, './logfile_level'):
                    logset.set_logfile_level(subnode.text)
                for subnode in xpath_findall(Node, './log_folder'):
                    logset.set_log_folder(subnode.text)
                for subnode in xpath_findall(Node, './log_filename'):
                    logset.set_log_filename(subnode.text)
                for subnode in xpath_findall(Node, './append_date_to_filename'):
                    logset.set_append_date(convert_text_to_boolean(subnode.text, True))
                for subnode in xpath_findall(Node, './filename_extension'):
                    logset.set_filename_extension(subnode.text)
                for subnode in xpath_findall(Node, './continue_on_log_fail'):
                    logset.set_continute_on_log_fail(convert_text_to_boolean(subnode.text, True))

        set_boolean_if_xmlnode_exists(config, 'empty_trash_on_exit', Node, './/empty_trash_on_exit')
        set_boolean_if_xmlnode_exists(config, 'mark_as_read_on_move', Node, './/mark_as_read_on_move')
        set_value_if_xmlnode_exists(config, 'console_loglevel', Node, './logging/console_level')

        parse_email_notification_settings(config, Node.find('./logging/notification_email_on_completion'))
        parse_logfile_settings(config, 'logfile', Node.find('./logging/logfile'))
        parse_logfile_settings(config, 'logfile_debug', Node.find('./logging/logfile_debug'))
        # End Parsing of General Section

    def parse_serverinfo(Node, config):
        if Node is None:
            return

        def parse_email_server_settings(config, conf_prefix, Node):
            set_value_if_xmlnode_exists(config, conf_prefix + 'server_name', Node, './server_name')
            set_value_if_xmlnode_exists(config, conf_prefix + 'server_port', Node, './server_port')
            set_value_if_xmlnode_exists(config, conf_prefix + 'username', Node, './username')
            set_value_if_xmlnode_exists(config, conf_prefix + 'password', Node, './password')
            set_boolean_if_xmlnode_exists(config, conf_prefix + 'use_tls', Node, './use_tls')
            set_boolean_if_xmlnode_exists(config, conf_prefix + 'auth_required', Node, './auth_required')  # SMTP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'initial_folder', Node, './initial_folder')  # IMAP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'deletions_folder', Node, './deletions_folder')  # IMAP only

        parse_email_server_settings(config, 'imap_', Node.find('./connection_imap'))
        parse_email_server_settings(config, 'smtp_', Node.find('./sending_email_smtp'))
        # End Parsing of ServerInfo Section

    def parse_rules(Node, config, rules):
        if Node is None:
            return

        def parse_generic_rule_match(Node):
            match_field = get_attribvalue_if_exists_in_xmlNode(Node, 'field')
            match_type = get_attribvalue_if_exists_in_xmlNode(Node, 'type')
            case_sensitive = convert_text_to_boolean(get_attribvalue_if_exists_in_xmlNode(Node, 'case_sensitive'), False)
            match_val = Node.text
            match_to_add = MatchField(
                field_to_match=match_field,
                match_type=match_type,
                str_to_match=match_val,
                case_sensitive=case_sensitive
            )
            return match_to_add

        def parse_rule_node(Node, config, rules):
            def parse_rule_actions(Node, config, rule):
                """Parses all actions inside a defined rule """
                if Node.find('./mark_as_read'):
                    action_to_add = RuleAction('mark_as_read')
                    action_to_add.set_mark_as_read()
                    rule.add_action(action_to_add)

                if Node.find('./mark_as_unread'):
                    action_to_add = RuleAction('mark_as_unread')
                    action_to_add.set_mark_as_unread()
                    rule.add_action(action_to_add)

                for node in xpath_findall(Node, './move_to_folder'):
                    action_to_add = RuleAction('move_to_folder')
                    dest_folder = Node.text
                    action_to_add.set_dest_folder(dest_folder)
                    mark_as_read_on_move = convert_text_to_boolean(
                        get_attribvalue_if_exists_in_xmlNode(Node, 'mark_as_read'),
                        config['mark_as_read_on_move']
                    )
                    action_to_add.set_mark_as_read(mark_as_read_on_move)
                    rule.add_action(action_to_add)

                for node in xpath_findall(Node, './delete'):
                    action_to_add = RuleAction('delete')
                    delete_permanently = convert_text_to_boolean(get_attribvalue_if_exists_in_xmlNode(Node, 'permanently'), False)
                    action_to_add.set_delete_permanently(delete_permanently)
                    rule.add_action(action_to_add)

                for node in xpath_findall(Node, './forward'):
                    action_to_add = RuleAction('forward')
                    for address_node in xpath_findall(Node, './dest_address'):
                        action_to_add.add_email_recipient(Node.text)
                    rule.add_action(action_to_add)

            def parse_rule_matches(Node, rule):
                for node in xpath_findall(Node, './match_field'):
                    rule.add_match(parse_generic_rule_match(node))

                for node in xpath_findall(Node, './match_or'):
                    rule.start_match_or()
                    for node in xpath_findall(Node, './match_field'):
                        rule.add_match_or(parse_generic_rule_match(node))
                    rule.stop_match_or()

            def parse_rule_match_exceptions(Node, rule):
                for node in xpath_findall(Node, './match_field'):
                    rule.add_match_exception(parse_generic_rule_match(node))

                for node in xpath_findall(Node, './match_or'):
                    rule.start_exception_or()
                    for node in xpath_findall(Node, './match_field'):
                        rule.add_exception_or(parse_generic_rule_match(node))
                    rule.stop_exception_or()

            new_name = get_value_if_xmlnode_exists(Node, './rule_name')
            new_rule = Rule(new_name)

            for subnode in xpath_findall(Node, './rule_actions'):
                parse_rule_actions(subnode, config, new_rule)

            for subnode in xpath_findall(Node, './rule_matches'):
                parse_rule_matches(subnode, new_rule)

            for subnode in xpath_findall(Node, './rule_match_exceptions'):
                parse_rule_match_exceptions(subnode, new_rule)

            rules.append(new_rule)

        for rule_node in xpath_findall(Node, './rule'):
                parse_rule_node(rule_node, config, rules)

        # End Parsing of Rules Section

    parse_auth(xml_config_tree.find('config_authinfo'), config)
    parse_general(xml_config_tree.find('config_general'), config)
    parse_serverinfo(xml_config_tree.find('config_serverinfo'), config)
    parse_rules(xml_config_tree.find('config_rules'), config, rules)


def set_dependent_config(config):
    if config['imap_server_port'] is None:
        if config['imap_use_tls']:
            config['imap_server_port'] = 993
        else:
            config['imap_server_port'] = 143

    if config['smtp_server_port'] is None:
        if config['smtp_use_tls']:
            config['smtp_server_port'] = 587
        else:
            config['smtp_server_port'] = 25


def get_settings_from_configtree(xml_config_tree):
    config = dict()
    rules = []
    set_defaults(config)
    parse_config_tree(xml_config_tree, config, rules)
    set_dependent_config(config)
    return (config, rules)
    #validate_config(config)

