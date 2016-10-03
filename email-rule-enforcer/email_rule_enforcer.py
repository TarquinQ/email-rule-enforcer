import sys
import imaplib
import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
import modules.match_emails as match_emails
from modules.settings.get_config import get_config
from modules.settings.default_counters_and_timers import create_default_timers, create_default_rule_counters
from modules.settings.get_config import get_config
from modules.email.IMAPServerConnection import IMAPServerConnection
from modules.email.smtp_send_completion_email import smtp_send_completion_email
from modules.logging import LogMaster, add_log_files_from_config
from modules.supportingfunctions import die_with_errormsg
from modules.ui.display_headers import get_header_preconfig, get_header_postconfig
from modules.ui.display_footers import get_completion_footer
from modules.ui.debug_rules_and_config import debug_rules_and_config


def main():
    print(get_header_preconfig())

    # Create the Counters and Timers
    global_timers = create_default_timers()
    rule_counters_mainfolder = create_default_rule_counters()
    rule_counters_allfolders = create_default_rule_counters()

    # Get the configs
    (config, rules_mainfolder, rules_allfolders) = get_config()

    print(get_header_postconfig(config))
    rule_counters_mainfolder.new_counter(counter_name='rules_in_set', start_val=len(rules_mainfolder))
    rule_counters_allfolders.new_counter(counter_name='rules_in_set', start_val=len(rules_allfolders))

    # Die if in config-parse-only mode
    if config['parse_config_and_stop']:
        global_timers.stop('overall')
        print(get_completion_footer(config, global_timers, rule_counters_mainfolder, rule_counters_allfolders))
        die_with_errormsg('Config Testing only, dont connect. Now exiting', 0)

    # Set up Logging
    add_log_files_from_config(config)
    debug_rules_and_config(config, rules_mainfolder, rules_allfolders)

    # Connect to IMAP
    imap_connection = IMAPServerConnection()
    imap_connection.set_parameters_from_config(config)
    imap_connection.connect_to_server()
    if imap_connection.is_connected():
        imap_connection.connect_to_folder(config['imap_initial_folder'])
    else:
        global_timers.stop('overall')
        die_with_errormsg('IMAP Server Connection failed before we did anything, so we are now exiting.')

    # Now we try to perform IMAP actions
    try:
        # Parse IMAP Emails
        global_timers.start('mainfolder')
        match_emails.iterate_rules_over_mainfolder(imap_connection, config, rules_mainfolder, rule_counters_mainfolder)
        global_timers.stop('mainfolder')

        global_timers.start('allfolders')
        match_emails.iterate_rules_over_allfolders(imap_connection, config, rules_allfolders, rule_counters_allfolders)
        global_timers.stop('allfolders')

        imap_connection.disconnect()
    except KeyboardInterrupt as KI:
        # Someone ressed Ctrl-C, so close & cleanup
        LogMaster.info('\n\nRules processing has been cancelled by user action. \
            Now disconnecting from IMAP and exiting')
        imap_connection.disconnect()
    except imaplib.IMAP4.abort as socket_err:
        # Something went wrong with the IMAP socket. Safely Disconnect just in case.
        LogMaster.critical('There has been an error with the IMAP Server connection.')
        LogMaster.critical('We will now disconnect from IMAP and exit.')
        LogMaster.critical('Error was: %s', repr(socket_err))
        imap_connection.disconnect()

    except (TypeError, AttributeError, KeyError, IndexError, NameError) as e:
        # Something went wrong with the IMAP socket. Safely Disconnect just in case.
        LogMaster.critical('There has been an error with the email processing, and an unhandled error occurred.')
        LogMaster.critical('We will now safely disconnect from IMAP and exit.')
        LogMaster.exception('Error was: ')
        imap_connection.disconnect()

    global_timers.stop('overall')
    # Print the Footers
    final_output = get_completion_footer(config, global_timers, rule_counters_mainfolder, rule_counters_allfolders)
    LogMaster.critical(final_output)

    # Send Completion Email
    smtp_send_completion_email(config, final_output)


if __name__ == "__main__":
    main()
