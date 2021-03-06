import datetime
import xml.etree.ElementTree as ET
import modules.supportingfunctions
from collections import OrderedDict
from modules.supportingfunctions import text_to_bool, text_to_int, die_with_errormsg, strip_quotes
from modules.models.EmailNotificationSettings import EmailNotificationSettings
from modules.models.LogfileSettings import LogfileSettings
from modules.models.Config import Config
from modules.models.Rules import Rules, Rule
from modules.models.RuleMatches import Match, MatchHeader, MatchDate, MatchSize, MatchFolder, MatchFlag, MatchIsUnread, MatchIsRead
from modules.models.RuleMatches import MatchBody, MatchFrom, MatchTo, MatchSubject
from modules.models.RuleActions import Action, ActionForwardEmail, ActionMarkAsRead, ActionMarkAsUnread, ActionDelete, ActionMoveToNewFolder
from modules.settings.default_settings import set_defaults
from modules.settings.set_dependent_config import set_dependent_config, set_headersonly_mode
from modules.settings.supportingfunctions_xml import set_value_if_xmlnode_exists, get_value_if_xmlnode_exists, get_attributes_if_xmlnode_exists
from modules.settings.supportingfunctions_xml import get_attribvalue_if_exists_in_xmlNode, strip_xml_whitespace, xpath_findall
from modules.settings.supportingfunctions_xml import set_boolean_if_xmlnode_exists, set_invertedboolean_if_xmlnode_exists


def parse_config_tree(xml_config_tree, config, rules_main, rules_allfolders):
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
                    attach_yn = text_to_bool(subnode.text, False)
                    if attach_yn is not None:
                        sendme.set_attach_log(attach_yn)
                config['notification_email_on_completion'] = sendme
                config['send_notification_email_on_completion'] = True

        def parse_logfile_settings(config, logtitle, Node):
            """Parses the logfile xml section"""
            if Node:
                logset = LogfileSettings()
                for subnode in xpath_findall(Node, './logfile_level'):
                    logset.set_logfile_level(text_to_int(subnode.text, 2))
                for subnode in xpath_findall(Node, './log_folder'):
                    logset.set_log_folder(subnode.text)
                for subnode in xpath_findall(Node, './log_filename'):
                    logset.set_log_filename(subnode.text)
                for subnode in xpath_findall(Node, './append_date_to_filename'):
                    logset.set_append_date(text_to_bool(subnode.text, True))
                for subnode in xpath_findall(Node, './filename_extension'):
                    logset.set_filename_extension(subnode.text)
                for subnode in xpath_findall(Node, './continue_on_log_fail'):
                    logset.set_continute_on_log_fail(text_to_bool(subnode.text, True))
                config['log_settings_%s' % logtitle] = logset

        set_value_if_xmlnode_exists(config, 'console_loglevel', Node, './logging/console_level')
        config['console_loglevel'] = text_to_int(config['console_loglevel'], 2)

        set_boolean_if_xmlnode_exists(config, 'empty_trash_on_exit', Node, './/empty_trash_on_exit')
        set_boolean_if_xmlnode_exists(config, 'mark_as_read_on_move', Node, './/mark_as_read_on_move')
        set_boolean_if_xmlnode_exists(config, 'console_ultra_debug', Node, './/console_ultra_debug')
        set_boolean_if_xmlnode_exists(config, 'console_insane_debug', Node, './/console_insane_debug')

        # Testing / Behaviour Settings
        set_boolean_if_xmlnode_exists(config, 'parse_config_and_stop', Node, './/parse_config_and_stop')
        set_boolean_if_xmlnode_exists(config, 'assess_rules_againt_mainfolder', Node, './/assess_rules_againt_mainfolder')
        set_boolean_if_xmlnode_exists(config, 'assess_rules_againt_allfolders', Node, './/assess_rules_againt_allfolders')
        set_boolean_if_xmlnode_exists(config, 'actually_perform_actions', Node, './/actually_perform_actions')
        set_boolean_if_xmlnode_exists(config, 'allow_body_match_for_all_folders', Node, './/allow_body_match_for_all_folders')
        set_boolean_if_xmlnode_exists(config, 'allow_body_match_for_main_folder', Node, './/allow_body_match_for_main_folder')

        parse_email_notification_settings(config, Node.find('./notification_email_on_completion'))
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
            set_value_if_xmlnode_exists(config, conf_prefix + 'forward_from', Node, './forward_from')  # SMTP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'initial_folder', Node, './initial_folder')  # IMAP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'deletions_folder', Node, './deletions_folder')  # IMAP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'imaplib_debuglevel', Node, './imaplib_debuglevel')  # IMAP only
            set_boolean_if_xmlnode_exists(config, conf_prefix + 'smtplib_debug', Node, './smtplib_debug')  # SMTP only

        def parse_email_Exchange_settings(config, Node):
            set_value_if_xmlnode_exists(config, 'Exchange_shared_mailbox_alias', Node, './shared_mailbox_alias')

        parse_email_server_settings(config, 'imap_', Node.find('./connection_imap'))
        parse_email_server_settings(config, 'smtp_', Node.find('./sending_email_smtp'))
        parse_email_Exchange_settings(config, Node.find('./exchange_shared_mailbox'))

        config['imap_imaplib_debuglevel'] = text_to_int(config['imap_imaplib_debuglevel'])
        # End Parsing of ServerInfo Section

    def parse_rules(Node, config, rules):
        if Node is None:
            return None

        def parse_match_generictextfield(Node, match_field):
            match_type = get_attribvalue_if_exists_in_xmlNode(Node, 'type')
            name = get_attribvalue_if_exists_in_xmlNode(Node, 'name')
            case_sensitive = text_to_bool(get_attribvalue_if_exists_in_xmlNode(Node, 'case_sensitive'), False)
            match_val = strip_xml_whitespace(Node.text)
            return (match_type, match_val, case_sensitive, name)

        def parse_match_header(Node):
            match_field = get_attribvalue_if_exists_in_xmlNode(Node, 'header')
            (match_type, match_val, case_sensitive, name) = \
                parse_match_generictextfield(Node, match_field=match_field)
            match_to_add = MatchHeader(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                case_sensitive=case_sensitive,
                name=name
            )
            return match_to_add

        def parse_match_body(Node):
            match_field = 'body'
            (match_type, match_val, case_sensitive, name) = \
                parse_match_generictextfield(Node, match_field=match_field)
            match_to_add = MatchBody(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                case_sensitive=case_sensitive,
                name=name
            )
            return match_to_add

        def parse_match_subject(Node):
            match_field = 'subject'
            (match_type, match_val, case_sensitive, name) = \
                parse_match_generictextfield(Node, match_field=match_field)
            match_to_add = MatchFrom(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                case_sensitive=case_sensitive,
                name=name
            )
            return match_to_add

        def parse_match_from(Node):
            match_field = 'from'
            (match_type, match_val, case_sensitive, name) = \
                parse_match_generictextfield(Node, match_field=match_field)
            match_to_add = MatchFrom(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                case_sensitive=case_sensitive,
                name=name
            )
            return match_to_add

        def parse_match_to(Node):
            match_field = 'to'
            (match_type, match_val, case_sensitive, name) = \
                parse_match_generictextfield(Node, match_field=match_field)
            this_recipient_only = text_to_bool(
                get_attribvalue_if_exists_in_xmlNode(Node, 'this_recipient_only'),
                False)
            match_to_add = MatchTo(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                case_sensitive=case_sensitive,
                name=name,
                this_recipient_only=this_recipient_only
            )
            return match_to_add

        def parse_match_size(Node):
            match_field = 'size'
            match_type = get_attribvalue_if_exists_in_xmlNode(Node, 'type')
            match_name = get_attribvalue_if_exists_in_xmlNode(Node, 'name')
            match_val = text_to_int(strip_xml_whitespace(Node.text))
            match_to_add = MatchSize(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                name=match_name
            )
            return match_to_add

        def parse_match_date(Node):
            match_val = None
            match_field = get_attribvalue_if_exists_in_xmlNode(Node, 'field')
            match_type = get_attribvalue_if_exists_in_xmlNode(Node, 'type')
            match_name = get_attribvalue_if_exists_in_xmlNode(Node, 'name')
            fixed_date = get_value_if_xmlnode_exists(Node, './fixed_date')
            if fixed_date is not None:
                # Then it's an absolute date
                try:
                    match_val = datetime.datetime.strptime(
                        strip_xml_whitespace(fixed_date),
                        '%Y-%m-%d')
                except Exception:
                    pass
            else:
                # else it's a relative date, and we need to find the seconds->years of values
                time_names = OrderedDict(
                    [("seconds", 0), ("minutes", 0), ("hours", 0),
                     ("days", 0), ("weeks", 0), ("months", 0),
                     ("years", 0)
                    ])
                # Get all possible values from xml
                for time_name in time_names:
                    time_val = get_value_if_xmlnode_exists(Node, './%s' % time_name)
                    time_val = text_to_int(strip_xml_whitespace(time_val), 0)
                    time_names[time_name] = time_val
                # Now we mess with them a bit, to match python's timedelta function call argumants:
                time_names["days"] += round(365 / 12 * time_names["months"])
                time_names["weeks"] += 52 * time_names["years"]
                del time_names["months"]
                del time_names["years"]
                # Now we put it all together
                match_val = datetime.timedelta(**time_names)
                if match_val == datetime.timedelta():
                    # Then this is effectively zero for all values
                    match_val = datetime.datetime.max
                    match_type = 'newer_than'

            if match_field is None:
                match_field = 'date'

            match_to_add = MatchDate(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                name=match_name
            )
            return match_to_add

        def parse_match_folder(Node):
            match_field = 'IMAP_Folder'
            match_type = get_attribvalue_if_exists_in_xmlNode(Node, 'type')
            match_name = get_attribvalue_if_exists_in_xmlNode(Node, 'name')
            case_sensitive = text_to_bool(get_attribvalue_if_exists_in_xmlNode(Node, 'case_sensitive'), False)
            include_hierarchy = text_to_bool(get_attribvalue_if_exists_in_xmlNode(Node, 'include_hierarchy'), True)
            match_val = strip_xml_whitespace(Node.text)
            match_to_add = MatchFolder(
                field_to_match=match_field,
                match_type=match_type,
                value_to_match=match_val,
                case_sensitive=case_sensitive,
                include_hierarchy=include_hierarchy,
                name=match_name
            )
            return match_to_add

        def parse_match_isunread(Node):
            match_name = get_attribvalue_if_exists_in_xmlNode(Node, 'name')
            match_to_add = MatchIsUnread(
                name=match_name
            )
            return match_to_add

        def parse_match_isread(Node):
            match_name = get_attribvalue_if_exists_in_xmlNode(Node, 'name')
            match_to_add = MatchIsUnread(
                name=match_name
            )
            return match_to_add

        def parse_rule_node(Node, config):
            def parse_rule_actions(Node, config, rule):
                """Parses all actions inside a defined rule """
                if Node.find('./mark_as_read'):
                    action_to_add = ActionMarkAsRead()
                    rule.add_action(action_to_add)

                if Node.find('./mark_as_unread'):
                    action_to_add = ActionMarkAsUnread()
                    rule.add_action(action_to_add)

                for Subnode in xpath_findall(Node, './move_to_folder'):
                    action_to_add = ActionMoveToNewFolder()
                    dest_folder = '\"' + strip_xml_whitespace(Subnode.text) + '\"'
                    action_to_add.set_dest_folder(dest_folder)
                    mark_as_read_on_move = text_to_bool(
                        get_attribvalue_if_exists_in_xmlNode(Subnode, 'mark_as_read'),
                        config['mark_as_read_on_move']
                    )
                    action_to_add.set_mark_as_read_on_move(mark_as_read_on_move)
                    rule.add_action(action_to_add)

                for Subnode in xpath_findall(Node, './delete'):
                    action_to_add = ActionDelete()
                    delete_permanently = text_to_bool(
                        get_attribvalue_if_exists_in_xmlNode(Subnode, 'permanently'),
                        False
                    )
                    action_to_add.set_delete_permanently(delete_permanently)
                    rule.add_action(action_to_add)

                for Subnode in xpath_findall(Node, './forward'):
                    action_to_add = ActionForwardEmail()
                    for address_node in xpath_findall(Subnode, './forward_to'):
                        action_to_add.add_email_recipient(
                            strip_xml_whitespace(address_node.text)
                        )
                    rule.add_action(action_to_add)

            def parse_rule_matches(Node, rule, maxdepth=2):
                if maxdepth == 0:
                    return

                for node in xpath_findall(Node, './match_header'):
                    rule.add_match(parse_match_header(node))
                for node in xpath_findall(Node, './match_body'):
                    rule.add_match(parse_match_body(node))
                for node in xpath_findall(Node, './match_subject'):
                    rule.add_match(parse_match_subject(node))
                for node in xpath_findall(Node, './match_from'):
                    rule.add_match(parse_match_from(node))
                for node in xpath_findall(Node, './match_to'):
                    rule.add_match(parse_match_to(node))
                for node in xpath_findall(Node, './match_date'):
                    rule.add_match(parse_match_date(node))
                for node in xpath_findall(Node, './match_size'):
                    rule.add_match(parse_match_size(node))
                for node in xpath_findall(Node, './match_folder'):
                    rule.add_match(parse_match_folder(node))
                for node in xpath_findall(Node, './match_is_unread'):
                    rule.add_match(parse_match_isunread(node))
                for node in xpath_findall(Node, './match_is_read'):
                    rule.add_match(parse_match_isread(node))

                for subnode in xpath_findall(Node, './match_or'):
                    rule.start_match_or()
                    parse_rule_matches(subnode, rule, maxdepth=(maxdepth - 1))
                    rule.stop_match_or()

            def parse_rule_match_exceptions(Node, rule):
                for node in xpath_findall(Node, './match_header'):
                    rule.add_match_exception(parse_match_header(node))
                for node in xpath_findall(Node, './match_date'):
                    rule.add_match_exception(parse_match_date(node))
                for node in xpath_findall(Node, './match_size'):
                    rule.add_match_exception(parse_match_size(node))
                for node in xpath_findall(Node, './match_folder'):
                    rule.add_match_exception(parse_match_folder(node))
                for node in xpath_findall(Node, './match_is_unread'):
                    rule.add_match_exception(parse_match_isunread(node))
                for node in xpath_findall(Node, './match_is_read'):
                    rule.add_match_exception(parse_match_isread(node))

                for subnode in xpath_findall(Node, './match_or'):
                    rule.start_exception_or()
                    parse_rule_match_exceptions(subnode, rule)
                    rule.stop_exception_or()

            new_name = get_value_if_xmlnode_exists(Node, './rule_name')
            new_rule = Rule(new_name)

            for subnode in xpath_findall(Node, './rule_actions'):
                parse_rule_actions(subnode, config, new_rule)

            for subnode in xpath_findall(Node, './rule_matches'):
                parse_rule_matches(subnode, new_rule)

            for subnode in xpath_findall(Node, './rule_match_exceptions'):
                parse_rule_match_exceptions(subnode, new_rule)

            return new_rule

        def parse_folder_exceptions(Node, config):
            for folder_name in xpath_findall(Node, './folder_to_exclude'):
                config['imap_folders_to_exclude'].add(
                    strip_quotes(
                        strip_xml_whitespace(folder_name.text)
                    )
                )

        def rule_is_enabled(Node):
            rule_enabled = True
            if text_to_bool(get_attribvalue_if_exists_in_xmlNode(Node, 'enabled'), True) is False:
                rule_enabled = False
            if text_to_bool(get_attribvalue_if_exists_in_xmlNode(Node, 'disabled'), False) is True:
                rule_enabled = False
            if text_to_bool(get_attribvalue_if_exists_in_xmlNode(Node, 'ignore'), True) is False:
                rule_enabled = False
            return rule_enabled

        for rule_node in xpath_findall(Node, './rule'):
                if rule_is_enabled(rule_node):
                    rules.append(
                        parse_rule_node(rule_node, config)
                    )
        for folder_exception_node in xpath_findall(Node, './folder_exclusions'):
                parse_folder_exceptions(folder_exception_node, config)
        # End Parsing of Rules Section

    # Now we actually perform the parsin of each section
    parse_auth(xml_config_tree.find('config_authinfo'), config)
    parse_general(xml_config_tree.find('config_general'), config)
    parse_serverinfo(xml_config_tree.find('config_serverinfo'), config)
    # We allow multiple Rules sections, to allow smaller/reusable config files
    for rule_node in xml_config_tree.findall('config_rules_mainfolder'):
        parse_rules(rule_node, config, rules_main)
    for rule_node in xml_config_tree.findall('config_rules_allfolders'):
        parse_rules(rule_node, config, rules_allfolders)


def get_settings_from_configtree(xml_config_tree):
    config = Config()
    rules_main = Rules()
    rules_allfolders = Rules()
    set_defaults(config)
    parse_config_tree(xml_config_tree, config, rules_main, rules_allfolders)
    set_dependent_config(config)
    set_headersonly_mode(config, rules_main,
        'allow_body_match_for_main_folder', 'imap_headers_only_for_main_folder')
    set_headersonly_mode(config, rules_allfolders,
        'allow_body_match_for_all_folders', 'imap_headers_only_for_all_folders')
    return (config, rules_main, rules_allfolders)

