import .supportingfunctions
from .supportingfunctions import die_with_errormsg


class settings():
    def __init__(self,xml_config_tree):
        self.xml_config_tree = xml_config_tree


class settings_authinfo():
    def __init__(self):
    <config_authinfo>
        <connection_auth>
            <username>username</username>
            <password>password</password>
        </connection_auth>
        <sending_email_auth>
            <username>username</username>
            <password>password</password>
        </sending_email_auth>
    </config_authinfo>

class settings_():
    def __init__(self):
    <config_general>
        <behaviour>
            <empty_trash_on_exit>no</empty_trash_on_exit> <!-- default: no -->
            <mark_as_read_on_move>yes</mark_as_read_on_move> <!-- default: yes -->
        </behaviour>
        <notification_email_on_completion>
            <recipient_email>admin@domain.com</recipient_email>
            <subject>Successfully completed mailbox rule enforcement</subject>
            <body_prefix>Report below</body_prefix>
            <attach_log>yes</attach_log>  <!-- default: yes -->
        </notification_email_on_completion>
        <logging>
            <log_level>7</log_level>  <!-- 0-7 low-high; default: 3 -->
            <logfile>
                <log_folder>logs</log_folder>  <!-- trailing slash can be omitted -->
                <log_filename_prepend>log-test</log_filename_prepend>  <!-- First bit of log filename -->
                <append_date>yes</append_date>  <!-- ISO format, including current time; default: yes -->
                <filename_extension>.log</filename_extension>  <!-- default: .log -->
                <tee_to_screen>yes</tee_to_screen>  <!-- Display on screen as well as log file; default: yes -->
                <continue_on_log_fail>no</continue_on_log_fail>  <!-- Continue even if log file is not writeable; default: no -->
            </logfile>
        </logging>
    </config_general>

class settings_():
    def __init__(self):
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

class settings_():
    def __init__(self):
    <config_serverinfo>
        <connection>
            <protocol>IMAP4</protocol> <!--IMAP4 by default (only IMAP at present!) -->
            <server_name>full.domain.name</server_name> <!-- Or IP -->
            <server_port></server_port> <!-- Leave blank for protocol default -->
            <use_tls>yes</use_tls> <!-- default: no -->
        </connection>
        <folderinfo>
            <initial_folder>INBOX</initial_folder> <!-- default: INBOX -->
            <delete_folder>Trash</delete_folder> <!-- default: Trash -->
        </folderinfo>
        <sending_email>
            <protocol>SMTP</protocol> <!--SMTP by default (only SMTP at present!) -->
            <server_name>full.domain.name</server_name> <!-- Or IP -->
            <server_port></server_port> <!-- Leave blank for protocol default -->
            <use_tls>yes</use_tls> <!-- default: no -->
            <auth_required>yes</auth_required> <!-- default: no -->
        </sending_email>
    </config_serverinfo>
