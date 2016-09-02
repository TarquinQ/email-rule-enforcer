import sys
import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
import modules.match_emails as match_emails
from modules.settings.get_config import get_config
from modules.email.IMAPServerConnection import IMAPServerConnection
from modules.logging import LogMaster, add_log_files_from_config
from modules.supportingfunctions import die_with_errormsg
from modules.ui.display_headers import get_header_preconfig, get_header_postconfig


def main():
    print(get_header_preconfig())

    # Get the configs
    (config, rules) = get_config()
    print(get_header_postconfig(config))

    # Set up Logging
    add_log_files_from_config(config, rules)

    if config['parse_config_and_stop']:
        die_with_errormsg('Config Testing only, dont connect. Now exiting', 0)

    # Connect to IMAP
    imap_connection = IMAPServerConnection()
    imap_connection.set_parameters_from_config(config)
    imap_connection.connect_to_server()
    if imap_connection.is_connected:
        imap_connection.connect_to_folder(config['imap_initial_folder'])
    else:
        die_with_errormsg('IMAP Server failed, so we are now exiting.')

    try:
        # Parse IMAP Emails
        if config['assess_mainfolder_rules']:
            match_emails.iterate_rules_over_mailfolder(imap_connection, config, rules)

        if config['assess_allfolders_rules']:
            match_emails.iterate_over_allfolders(imap_connection, config, rules)

        imap_connection.disconnect()
    except KeyboardInterrupt as KI:
        imap_connection.disconnect()

    # Send Completion Email
    # send_smtp_completion_email()


if __name__ == "__main__":
    main()
