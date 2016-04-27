import xml.etree.ElementTree as ET
import .supportingfunctions
from .supportingfunctions import die_with_errormsg
from .supportingfunctions import generate_logfile_fullpath
from .supportingfunctions import convert_text_to_boolean
from .logging import log_messages as log
import re


class email_notification_settings():
    email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')

    def __init__(self, recipient=None, recipients=None, subject=None, body_prefix=None, attach_log=True):
        self.recipients = []
        if recipient:
            self.add_recipient(recipient)
        if recipients:
            for recipient in recipients:
                self.add_recipient(recipient)
        self.subject = subject
        self.body_prefix = body_prefix
        self.attach_log = attach_log

    def add_recipient(self, recipient_email):
        self.recipients.append(recipient_email)

    def set_subject(self, subject):
        self.subject = subject

    def set_body_prefix(self, prefix):
        self.body_prefix = prefix

    def set_attach_log(self, attach_yn):
        self.attach_log = attach_yn

    def validate(self):
        validate = true
        if ((len(recipients) == 0) or (not self.subject)):
            validate = false
        for recipient in self.recipients:
            if not email_regex.match(recipient):
                validate = false


class logfile_settings():
    def __init__(self, logfile_level=2, log_folder=None, log_filename=None, append_date_to_filename=True, filename_extension='.log', continue_on_log_fail=False):
        self.logfile_level = logfile_level
        self.log_folder = log_folder
        self.log_filename = log_filename
        self.append_date_to_filename = append_date_to_filename
        self.filename_extension = filename_extension
        self.continue_on_log_fail = continue_on_log_fail
        self.logfilepath = None
        self.set_full_filepath()

    def set_logfile_level(self, level):
        self.logfile_level = level

    def set_log_folder(self, log_folder):
        self.log_folder = log_folder
        self.set_full_filepath()

    def set_log_filename(self, log_filename):
        self.log_filename = log_filename
        self.set_full_filepath()

    def set_append_date(self, yn):
        self.append_date_to_filename = yn
        self.set_full_filepath()

    def set_filename_extension(self, ext):
        self.filename_extension = ext
        self.set_full_filepath()

    def set_continute_on_log_fail(self, yn):
        self.continue_on_log_fail = yn

    def set_full_filepath(self):
        if ((self.log_folder) and (self.log_filename) and (self.filename_extension)):
            self.logfilepath = generate_logfile_fullpath(
                log_directory=self.log_folder, filename_pre=self.log_filename,
                filename_extension=self.filename_extension,
                insert_datetime=self.append_date_to_filename)

    def validate(self):
        if not self.logfilepath:
            return False
        return True


def validate_config(config):
    pass


def set_defaults(config):
    """This function sets defaults for all settings which can be set by default"""
    config['defaults_are_set'] = True
    config['imap_username'] = None
    config['imap_password'] = None
    config['smtp_username'] = None
    config['smtp_username'] = None
    config['empty_trash_on_exit'] = False
    config['mark_as_read_on_move'] = True
    config['notification_email_on_completion'] = None
    config['console_loglevel'] = 2
    config['imap_initial_folder'] = 'INBOX'
    config['imap_deletions_folder'] = 'Trash'
    config['imap_use_tls'] = False
    config['imap_server_port'] = None


def parse_config_tree(xml_config_tree, config):
    def set_value_if_xmlnode_exists(configdict, key, Node, xpath):
        """Set a config value only if the value is in the xml"""
        node_found = Node.find(xpath)
        if node_found:
            configdict[key] = node_found.text

    def set_boolean_if_xml_exists(configdict, key, Node, xpath):
        """Set a config value only if the value is in the xml"""
        node_found = Node.find(xpath)
        if node_found:
            node_val = convert_text_to_boolean(node_found.text)
            if node_val is not None:
                configdict[key] = node_val

    def parse_auth(Node, config):
        """This function takes the XML node for config_authinfo and parses all expected contents"""
        set_value_if_xmlnode_exists(config, 'imap_username', Node, './/imap_auth/username')
        set_value_if_xmlnode_exists(config, 'imap_password', Node, './/imap_auth/password')
        set_value_if_xmlnode_exists(config, 'smtp_username', Node, './/smtp_email/username')
        set_value_if_xmlnode_exists(config, 'smtp_password', Node, './/smtp_email/password')
        # End Parsing of Auth Section

    def parse_general(Node, config):
        def parse_email_notification_settings(config, Node):
            """Parses the email notification xml section"""
            if Node:
                sendme = email_notification_settings()
                for subnode in Node.findall('./recipient_email'):
                    sendme.add_recipient(subnode.text)
                for subnode in Node.findall('./subject'):
                    sendme.set_subject(subnode.text)
                for subnode in Node.findall('./body_prefix'):
                    sendme.set_body_prefix(subnode.text)
                for subnode in Node.findall('./attach_log'):
                    attach_yn = convert_text_to_boolean(subnode.text)
                    if attach_yn is not None:
                        sendme.set_attach_log(attach_yn)
                config['notification_email_on_completion'] = sendme

        def parse_logfile_settings(config, Node):
            """Parses the logfile xml section"""
            if Node:
                logset = logfile_settings()
                for subnode in Node.findall('./logfile_level'):
                    logset.set_logfile_level(subnode.text)
                for subnode in Node.findall('./log_folder'):
                    logset.set_log_folder(subnode.text)
                for subnode in Node.findall('./log_filename'):
                    logset.log_filename(subnode.text)
                for subnode in Node.findall('./append_date_to_filename'):
                    logset.append_date_to_filename(convert_text_to_boolean(subnode.text))
                for subnode in Node.findall('./filename_extension'):
                    logset.set_filename_extension(subnode.text)
                for subnode in Node.findall('./continue_on_log_fail'):
                    logset.set_continute_on_log_fail(convert_text_to_boolean(subnode.text))

        set_boolean_if_xml_exists(config, 'empty_trash_on_exit', Node, './/empty_trash_on_exit')
        set_boolean_if_xml_exists(config, 'mark_as_read_on_move', Node, './/mark_as_read_on_move')
        set_value_if_xmlnode_exists(config, 'console_loglevel', Node, './logging/console_level')

        parse_email_notification_settings(config, Node.find('./logging/notification_email_on_completion'))
        parse_logfile_settings(config, 'logfile', Node.find('./logging/logfile'))
        parse_logfile_debug_settings(config, 'logfile_debug', Node.find('./logging/logfile_debug'))
        # End Parsing of General Section

    def parse_serverinfo(Node, config):
        def parse_email_server_settings(config, conf_prefix, Node):
            set_value_if_xmlnode_exists(config, conf_prefix + 'server_name', Node.find('./server_name'))
            set_value_if_xmlnode_exists(config, conf_prefix + 'server_port', Node.find('./server_port'))
            set_value_if_xmlnode_exists(config, conf_prefix + 'use_tls', Node.find('./use_tls')
            set_value_if_xmlnode_exists(config, conf_prefix + 'username', Node.find('./username')
            set_value_if_xmlnode_exists(config, conf_prefix + 'password', Node.find('./password')
            set_value_if_xmlnode_exists(config, conf_prefix + 'initial_folder', Node, './initial_folder') # IMAP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'deletions_folder', Node, './deletions_folder') # IMAP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'auth_required', Node.find('./auth_required') # SMTP only

        parse_imap_settings(config, 'imap_', Node.find('./connection_imap'))
        parse_smtp_settings(config, 'smtp_', Node.find('./sending_email_smtp'))
        # End Parsing of ServerInfo Section

    parse_auth(xml_config_tree.find('config_authinfo'), config)
    parse_general(xml_config_tree.find('config_general'), config)
    parse_serverinfo(xml_config_tree.find('config_serverinfo'), config)


    <config_rules>
        <rule>
            <rule_name>Name of this rule</rule_name>
            <rule_actions>
                <action type="move">
                    <dest_folder>Archived Items</dest_folder>  <!-- IMAP requries a '\\' at the start of the first folder name: do not add this slash to this config -->
                </action>
                <action type="mark_as_read" mark_as_read="no" /> <!-- All move operations mark an email as read, this will do it without moving it -->
            </rule_actions>
            <rule_matches> <!-- all matches are required to match at the same time, unless added as an "match_or" -->
                <match_field field="to" type="contains">recipient@domain2</match_field>
                <match_or>
                    <match_field field="from" type="contains">sender@domain1</match_field>
                    <match_field field="from" type="ends_with">Undeliverable: </match_field>
                </match_or>
            </rule_matches>
            <rule_match_exceptions> <!-- Same matching format as rule_matches -->
                <match_or>
                    <match_field field="subject" type="starts_with" case_sensitive="no">Undeliverable: </match_field>
                    <match_field field="body" type="starts_with" case_sensitive="no">Undeliverable: </match_field>
                    <match_field field="from" type="equals">mailerdaemon@spammydomain.com</match_field>
                </match_or>
            </rule_match_exceptions>
        </rule>
        <rule>
            <rule_name>Move Undeliverable Emails to Trash folder</rule_name>
            <rule_actions>
                <action type="move" move_to_trash="yes" mark_as_read="no" />  <!-- move_to-trash moves the email into the Deleted Items/Trash folder as specificed in config-serverinfo -->
            </rule_actions>
            <rule_matches> <!-- all matches are required to match at the same time, unless added as an "match_or" -->
                <match_field field="subject" type="starts_with" case_sensitive="no">Undeliverable: </match_field>
            </rule_matches>
        </rule>
        <rule>
            <rule_name>Delete older emails (permanently)</rule_name>
            <rule_actions>
                <action type="delete"></action>
            </rule_actions>
            <rule_matches>
                <match_field field="date" type="older_than">Now + 3 months</match_field>  <!-- Explicit date or relative date -->
            </rule_matches>
        </rule>
        <rule>
            <rule_name>Default</rule_name>  <!-- Default rule - no matches, no exceptions -->
            <rule_actions>
                <action type="move">
                    <dest_folder>Archived Items</dest_folder>  <!-- IMAP requries a '\\' at the start of the first folder name: do not add this slash to this config -->
                </action>
            </rule_actions>
        </rule>
    </config_rules>


config = dict()
set_defaults(config)
parse_config_tree(xml_config_tree, config)
validate_config(config)

