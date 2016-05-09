import re
import xml.etree.ElementTree as ET
import .supportingfunctions
from .supportingfunctions import die_with_errormsg, generate_logfile_fullpath, convert_text_to_boolean
from .logging import log_messages as log


class EmailNotificationSettings():
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


class LogfileSettings():
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


def set_defaults(config):
    """This function sets defaults for all settings which can be set by default"""

    # General behaviour
    config['empty_trash_on_exit'] = False
    config['mark_as_read_on_move'] = True
    config['send_notification_email_on_completion'] = False
    config['notification_email_on_completion'] = None
    config['console_loglevel'] = 2

    # IMAP Defaults
    config['imap_server_name'] = None
    config['imap_username'] = None
    config['imap_password'] = None
    config['imap_use_tls'] = False
    config['imap_server_port'] = None
    config['imap_initial_folder'] = 'INBOX'
    config['imap_deletions_folder'] = 'Trash'

    # SMTP Defaults
    config['smtp_server_name'] = None
    config['smtp_username'] = None
    config['smtp_password'] = None
    config['smtp_use_tls'] = False
    config['smtp_server_port'] = None
    config['smtp_auth_required'] = False

    config['defaults_are_set'] = True


class Rule():
    rule_count = 0

    @classmethod
    def get_rule_count(cls):
        return cls.rule_count

    def incr_rule_count(cls):
        cls.rule_count += 1

    def __init__(self, rule_name=None):
        self.incr_rule_count()
        self.rule_num = self.get_rule_count()
        self.id = self.get_rule_count()
        self.set_name(rule_name)
        self.actions = []
        self.matches = []
        self.match_exceptions = []
        self.continue_rule_checks_if_matched = True

    # Set Basic variables
    def set_name(self, name):
        if rule_name is not None:
            self.name = str(rule_name)
        else:
            self.name = 'Rule' + str(self.get_rule_count())

    def add_action(self, action):
        self.actions.append(action)

    def add_match(self, match):
        self.matches.append(match)

    def add_match_exception(self, match):
        self.match_exceptions.append(match)

    def set_continue_rule_checks_if_matched(self, flag):
        self.continue_rule_checks_if_matched = flag

    # Handle or-matches in the match setion
    def start_match_or(self):
        self._temp_match_or = []

    def add_match_or(self, match):
        self._temp_match_or.append(match)

    def end_match_or(self):
        sel.matches.append(self._temp_match_or)
        del self._temp_match_or

    # Handle or-matches in the exception setion
    def start_exception_or(self):
        self._temp_exception_or = []

    def add_exception_or(self, match):
        self._temp_exception_or.append(match)

    def end_exception_or(self):
        sel.matches.append(self._temp_exception_or)
        del self._temp_exception_or

    # Basic property access
    def get_actions(self, action):
        return self.actions

    def get_matches(self, match):
        return self.matches

    def get_match_exceptions(self, match):
        return self.match_exceptions

    def get_continue_rule_checks_if_matched(self):
        return self.continue_rule_checks_if_matched

    # Validation
    def validate(self):
        if len(self.matches) = 0:
            return (False, 'Rule invalid: No matches for this rule. Rule id:' + str(self.id) + ', Name:' + self.name)
        if len(self.actions) = 0:
            return (False, 'Rule invalid: No actions for this rule. Rule id:' + str(self.id) + ', Name:' + self.name)
        for rule in self.actions:
            if not insinstance(rule, RuleAction)
        return (True, 'Rule seems valid')


class RuleAction():
    valid_actions = frozenset(['move', 'forward', 'delete'])

    def __init__(self, action_type):
        self.action_type = action_type
        self.delete_permanently = False

    def set_dest_folder(self, dest_folder):
        self.dest_folder = dest_folder

    def set_delete_permanently(self, flag):
        self.delete_permanently = flag

    def set_email_recipient(self, email_addr):
        self.email_recipient = email_addr

    def validate(self):
        if self.action_type not in self.valid_actions:
            return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but only valid actions are: ' + str(valid_actions))

        if self.action_type = 'move':
            check_for = 'dest_folder'
            try:
                self.dest_folder
            except NameError:
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but no value is set for suboption ' + check_for)

        if self.action_type = 'delete':
            if not insinstance('delete_permanently', bool):
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but delete_permanently flag not boolean: set to ' + str(self.delete_permanently))

        if self.action_type = 'forward':
            check_for = 'email_recipient'
            try:
                self.email_recipient
            except NameError:
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but no value is set for suboption ' + check_for)


class MatchField():
    match_types = frozenset(['starts_with', 'contains', 'ends_with', 'is'])
    match_fields = frozenset(['to', 'from', 'subject', 'cc', 'bcc', 'body'])

    def __init__(self, field_to_match=None, match_type=None, str_to_match=None, case_sensitive=False, parent_rule_id=None):
        self.field_to_match = None
        self.match_type = match_type
        self.str_to_match = str_to_match
        self.case_sensitive = case_sensitive
        self.parent_rule_id = parent_rule_id
        self.generate_re()

    def set_field_to_match(self, field_to_match):
        self.field_to_match = field_to_match
        self.generate_re()

    def set_match_type(self, match_type):
        self.match_type = match_type
        self.generate_re()

    def set_str_to_match(self, str_to_match):
        self.str_to_match = str_to_match
        self.generate_re()

    def set_case_sensitive(self, flag):
        self.case_sensitive = flag
        self.generate_re()

    def generate_re():
        if ((self.match_type in self.match_types) and (self.str_to_match is not None)):
            match_str = str(self.str_to_match)[:]
            if self.match_type = 'starts_with':
                match_str = match_str + '.*'
            if self.match_type = 'contains':
                match_str = '.*' + match_str + '.*'
            if self.match_type = 'ends_with':
                match_str = '.*' + match_str
            match_str = '^' + match_str + '$'  # Do I need this? I don't think so.
            self.matching_string = match_str
            flags = 0
            if not self.case_sensitive:
                flags = re.IGNORECASE
            self.re = re.compile(match_str, flags)

    def get_field_to_match(self):
        return self.field_to_match

    def get_match_type(self):
        return self.match_type

    def get_str_to_match(self):
        return self.str_to_match

    def get_case_sensitive(self):
        return self.case_sensitive

    def validate(self):
        if self.field_to_match not in self.match_fields:
            return (False, 'Field to match is invalid. Field type "' + self.field_to_match +
                '" selected, but only valid fields are: ' + str(match_fields))

        if self.match_type not in self.match_types:
            return (False, 'Match type is invalid. Field type "' + self.match_type +
                '" selected, but only valid fields are: ' + str(match_types))

        if self.str_to_match is None:
            return (False, 'Match invalid. Missing field value string. Trying to match field ' +
                self.field_to_match + '" selected, but no actual value is set for matching')

        if not insinstance(self.case_sensitive, bool):
            return (False, 'Match invalid. Case sensitivity should be boolean, but isnt. Trying to match: ' +
                self.action_type + '" selected, but delete_permanently flag not boolean: set to ' +
                str(self.delete_permanently))


def MatchBody(match_type='contains', str_to_match=None, case_sensitive=False, parent_rule_id=None):
    return MatchField(field_to_match='body', match_type, str_to_match, case_sensitive, parent_rule_id)


def parse_config_tree(xml_config_tree, config):
    def set_value_if_xmlnode_exists(configdict, key, Node, xpath):
        """Set a config value only if the value is in the xml"""
        node_found = Node.find(xpath)
        if node_found:
            configdict[key] = node_found.text

    def get_value_if_xmlnode_exists(Node, xpath):
        """Return a config value only if the value is in the xml"""
        node_found = Node.find(xpath)
        if node_found:
            return node_found.text
        else:
            return None

    def get_attributes_if_xmlnode_exists(Node, xpath):
        """Return a set of atributes only if the value is in the xml"""
        node_found = Node.find(xpath)
        if node_found:
            return node_found.text
        else:
            return None

    def set_boolean_if_xmlnode_exists(configdict, key, Node, xpath):
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
                sendme = EmailNotificationSettings()
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
                config['send_notification_email_on_completion'] = True

        def parse_logfile_settings(config, Node):
            """Parses the logfile xml section"""
            if Node:
                logset = LogfileSettings()
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

        set_boolean_if_xmlnode_exists(config, 'empty_trash_on_exit', Node, './/empty_trash_on_exit')
        set_boolean_if_xmlnode_exists(config, 'mark_as_read_on_move', Node, './/mark_as_read_on_move')
        set_value_if_xmlnode_exists(config, 'console_loglevel', Node, './logging/console_level')

        parse_email_notification_settings(config, Node.find('./logging/notification_email_on_completion'))
        parse_logfile_settings(config, 'logfile', Node.find('./logging/logfile'))
        parse_logfile_debug_settings(config, 'logfile_debug', Node.find('./logging/logfile_debug'))
        # End Parsing of General Section

    def parse_serverinfo(Node, config):
        def parse_email_server_settings(config, conf_prefix, Node):
            set_value_if_xmlnode_exists(config, conf_prefix + 'server_name', Node.find('./server_name'))
            set_value_if_xmlnode_exists(config, conf_prefix + 'server_port', Node.find('./server_port'))
            set_value_if_xmlnode_exists(config, conf_prefix + 'username', Node.find('./username')
            set_value_if_xmlnode_exists(config, conf_prefix + 'password', Node.find('./password')
            set_boolean_if_xmlnode_exists(config, conf_prefix + 'use_tls', Node.find('./use_tls')
            set_boolean_if_xmlnode_exists(config, conf_prefix + 'auth_required', Node.find('./auth_required') # SMTP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'initial_folder', Node, './initial_folder') # IMAP only
            set_value_if_xmlnode_exists(config, conf_prefix + 'deletions_folder', Node, './deletions_folder') # IMAP only

        parse_imap_settings(config, 'imap_', Node.find('./connection_imap'))
        parse_smtp_settings(config, 'smtp_', Node.find('./sending_email_smtp'))
        # End Parsing of ServerInfo Section

    def parse_rules(Node, config):
        def parse_rule_node(Node, config):
            def parse_rule_actions(Node, config):
                for action in Node.findall('./action'):
                    action_type = action.attrib['type']
                    if action_type = 'move':
                        dest_folder = get_value_if_xmlnode_exists('./dest_folder')
                        if action.attrib['type']:
                    if action_type = 'delete':
                        delete_permanently = False
                        if 'permanently' in action.attrib:
                            delete_permanently = convert_text_to_boolean(action.attrib['permanently'])
                    if action_type = 'forward':
                        dest_addresses = []
                        for address_node in Node.findall('./dest_address'):
                            dest_address = Node.value
                            dest_addresses


                <rule_actions>
                    <action type="move">
                        <dest_folder>Archived Items</dest_folder>  <!-- IMAP requries a '\\' at the start of the first folder name: do not add this slash to this config -->
                    </action>
                    <action type="mark_as_read">no</action> <!-- All move operations mark an email as read, this will do it without moving it -->
                </rule_actions>
                pass

            def parse_rule_matches(Node, config):
                <rule_matches> <!-- all matches are required to match at the same time, unless added as an "match_or" -->
                    <match_field field="to" type="contains">recipient@domain2</match_field>
                    <match_or>
                        <match_field field="from" type="contains">sender@domain1</match_field>
                        <match_field field="from" type="ends_with">Undeliverable: </match_field>
                    </match_or>
                </rule_matches>
                pass

            def parse_rule_match_exceptions(Node, config):
                <rule_match_exceptions> <!-- Same matching format as rule_matches -->
                    <match_or>
                        <match_field field="subject" type="starts_with" case_sensitive="no">Undeliverable: </match_field>
                        <match_field field="body" type="starts_with" case_sensitive="no">Undeliverable: </match_field>
                        <match_field field="from" type="equals">mailerdaemon@spammydomain.com</match_field>
                    </match_or>
                    <match_field field="to" type="contains">recipient@domain2</match_field>
                </rule_match_exceptions>
                pass

            new_name = get_value_if_xmlnode_exists(Node, './rule_name')
            new_rule = Rule(new_name)

            for subnode in Node.find('./rule_actions'):
                parse_rule_actions(subnode, config)

            for subnode in Node.find('./rule_matches'):
                parse_rule_matches(subnode, config)

            for subnode in Node.find('./rule_match_exceptions'):
                parse_rule_match_exceptions(subnode, config)




        for rule_node in Node.findall('./rule')):
                parse_rule_node(rule_node, config)

        # End Parsing of Rules Section



    parse_auth(xml_config_tree.find('config_authinfo'), config)
    parse_general(xml_config_tree.find('config_general'), config)
    parse_serverinfo(xml_config_tree.find('config_serverinfo'), config)
    parse_rules(xml_config_tree.find('config_rules'), config)

        <rule>
            <rule_name>Move Undeliverable Emails to Trash folder</rule_name>
            <rule_actions>
                <action type="move" move_to_trash="yes" mark_as_read="no" />  <!-- move_to-trash moves the email into the Deleted Items/Trash folder as specified in config-serverinfo -->
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


def validate_config(config):
    """
    Validates the config files and full config-XML tree

    This ensures that the following conditions are met:
    * Mandatory values are set
    * Value-dependencies are set (eg smtp_auth = true => smtp_U&P must be also set)
    * Other conditions are required
    """

    configfail = 13378411
    def die_with_errormsg_conf(msg, configfail):
        die_with_errormsg(msg, configfail)

    def assert_value_type(setting, value, expected_type):
    if not insinstance(value, expected_type):
        die_with_errormsg_conf('Incorrect value set for config setting "' + setting + '"; Expected type: ' + expected_type + ', got value: ' + str(value))

    def assert_value_type_optional(setting, value, expected_type):
        if val is not None:
            assert_value_type(setting, value, expected_type)

    # Basic: Check Mandatory values

    # Basic General behaviour
    setting = 'empty_trash_on_exit'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    setting = 'mark_as_read_on_move'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    setting = 'send_notification_email_on_completion'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    val = 'console_loglevel'
    expected_type = int
    assert_value_type(setting, config[setting], expected_type)

    setting = 'empty_trash_on_exit'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    setting = 'send_notification_email_on_completion'
    expected_type = bool
    assert_value_type(setting, config[setting], expected_type)

    def validate_imap_server_settings(config):
        conf_prefix = 'imap'
        setting = conf_prefix + 'server_name'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'server_port'
        expected_type = int
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'use_tls'
        expected_type = bool
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'username'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'password'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'initial_folder'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'deletions_folder'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

    def validate_smtp_server_settings(config):
        conf_prefix = 'smtp'
        setting = conf_prefix + 'server_name'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'server_port'
        expected_type = int
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'use_tls'
        expected_type = str
        assert_value_type(setting, config[setting], expected_type)

        setting = conf_prefix + 'auth_required'
        expected_type = bool
        assert_value_type(setting, config[setting], expected_type)

        if (config[conf_prefix + 'auth_required']):
            setting = conf_prefix + 'username'
            expected_type = str
            assert_value_type(setting, config[setting], expected_type)

            setting = conf_prefix + 'password'
            expected_type = str
            assert_value_type(setting, config[setting], expected_type)

    validate_imap_server_settings(config)
    validate_smtp_server_settings(config)


config = dict()
set_defaults(config)
parse_config_tree(xml_config_tree, config)
set_dependent_config(config)
validate_config(config)

