import sys
import imaplib
import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
import modules.core_logic as core_logic
from modules.settings.get_config import get_config
from modules.settings.default_counters_and_timers import create_default_stopwatches, create_default_rule_counters
from modules.settings.get_config import get_config
from modules.email.IMAPServerConnection import IMAPServerConnection
from modules.email.smtp_send_completion_email import smtp_send_completion_email
from modules.logging import LogMaster, add_log_files_from_config
from modules.supportingfunctions import die_with_errormsg
from modules.ui.display_headers import get_header_preconfig, get_header_postconfig
from modules.ui.display_footers import get_completion_footer
from modules.ui.debug_rules_and_config import debug_rules_and_config
from modules.models.SignalHandlers import register_sighandlers, Signal_GlobalShutdown
from modules.models.GracefulShutdown import graceful_shutdown_imap, graceful_shutdown_db
from modules.db.DatabaseHandler import DatabaseHandler
from modules.models.GlobalTimerFlags import GlobalTimerFlags


def main():
    # We set up a whole bunch of things first (configs, counters, database & IMAP)
    # Then we proceed to loop over the ruleset as requested in the configs.

    print(get_header_preconfig())

    # Create the Counters and Timers
    global_stopwatches = create_default_stopwatches()
    rule_counters_mainfolder = create_default_rule_counters()
    rule_counters_allfolders = create_default_rule_counters()

    # Get the configs
    (config, rules_mainfolder, rules_allfolders) = get_config()
    print(get_header_postconfig(config))

    # Set up the rule counters
    rule_counters_mainfolder.new_counter(counter_name='rules_in_set', start_val=len(rules_mainfolder))
    rule_counters_allfolders.new_counter(counter_name='rules_in_set', start_val=len(rules_allfolders))

    # Die if in config-parse-only mode
    if config['parse_config_and_stop']:
        global_stopwatches.stop('overall')
        print(get_completion_footer(config, global_stopwatches, rule_counters_mainfolder, rule_counters_allfolders))
        die_with_errormsg('Config Testing only, dont connect. Now exiting', 0)

    # Set up Logging
    add_log_files_from_config(config)
    debug_rules_and_config(config, rules_mainfolder, rules_allfolders)

    # Set up database
    db = DatabaseHandler(db_filename=config['database_filename'], auto_open=True)
    if db.connected is False:
        global_stopwatches.stop('overall')
        die_with_errormsg('Database Connection failed before we did anything, so we are now exiting.')

    # Now we try to perform IMAP actions
    try:
        # Connect to IMAP
        imap_connection = IMAPServerConnection()
        imap_connection.set_parameters_from_config(config)
        imap_connection.connect_to_server()
        if imap_connection.is_connected():
            imap_connection.connect_to_folder(config['imap_initial_folder'])
        else:
            global_stopwatches.stop('overall')
            die_with_errormsg('IMAP Server Connection failed before we did anything, so we are now exiting.')

        # Set up signal handling to handle shutdown of our long-lived process.
        # These signal handlers will throw Exceptions any time a kill signal is received, which will drop out of this section
        # and ensure a clean shutdown occurs
        register_sighandlers()

        core_logic.sync_full_folderlist_to_db(db, imap_connection)

        if config['daemon_mode'] is False:
            # Full sync of Mailbox here
            pass
        else:
            # Determine Startup actions
            if config['full_scan_at_startup'] is True:
                # Full sync of Mailbox here
                pass
            else:
                # Full Sync Folders here
                pass

            # Set up Timers to track things which occur at different times
            global_timer_flags = GlobalTimerFlags()
            global_timer_flags.set_from_config(config)

            while True:
                if global_timer_flags.sync_full.is_required():
                    LogMaster.info('Full Mailbox Sync Required, now commencing.')
                    pass  # FIXME: Full sync of Mailbox here
                    # Parse IMAP Emails
                    global_stopwatches.start('mainfolder')
                    core_logic.iterate_rules_over_mainfolder(imap_connection, config, rules_mainfolder, rule_counters_mainfolder)
                    global_stopwatches.stop('mainfolder')

                    global_stopwatches.start('allfolders')
                    core_logic.iterate_rules_over_allfolders(imap_connection, config, rules_allfolders, rule_counters_allfolders)
                    global_stopwatches.stop('allfolders')

                    global_timer_flags.sync_full.reset_timer_default()
                    global_timer_flags.keepalive.reset_timer_default()

                if global_timer_flags.sync_new.is_required():
                    LogMaster.info('Sync of New Inbox Items Required, now commencing.')
                    pass  # FIXME:  Sync New Inbox here
                    global_timer_flags.sync_new.reset_timer_default()
                    global_timer_flags.keepalive.reset_timer_default()

                if global_timer_flags.keepalive.is_required():
                    LogMaster.info('KeepAlive requested, now commencing.')
                    core_logic.keepalive(imap_connection)
                    global_timer_flags.keepalive.reset_timer_default()

                nextEvent = global_timer_flags.get_Timer_with_next_deadline()
                LogMaster.info('All required events processed, now sleeping until next event.')
                LogMaster.info('The next event will be a %s, which will occur at: %s\n', nextEvent.name, nextEvent.next_deadline.isoformat())
                del nextEvent

                global_timer_flags.wait_for_next_deadline()

    except KeyboardInterrupt as KI:
        # Someone pressed Ctrl-C, so close & cleanup
        LogMaster.info('\n\nRules processing has been cancelled by user action. \
            Now disconnecting from IMAP and exiting')

    except Signal_GlobalShutdown:
        # Someone killed us!
        LogMaster.info('\n\nRules processing has been cancelled by user or system request. \
            Now disconnecting from IMAP and exiting')

    except (imaplib.IMAP4.abort, IMAPServerConnection.PermanentFailure) as socket_err:
        # Something went wrong with the IMAP socket. Safely Disconnect just in case.
        LogMaster.critical('There has been an error with the IMAP Server connection.')
        LogMaster.critical('We will now disconnect from IMAP and exit.')
        LogMaster.exception('Error was:')

    except (Exception) as e:
        # Something went wrong with the IMAP socket. Safely Disconnect just in case.
        LogMaster.critical('There has been an error with the email processing, and an unhandled error occurred.')
        LogMaster.critical('We will now safely disconnect from IMAP and exit.')
        LogMaster.exception('Error was: ')

    # Disconnect from all data sources
    graceful_shutdown_imap(imap_connection=imap_connection)

    global_stopwatches.stop('overall')
    # Print the Footers
    final_output = get_completion_footer(config, global_stopwatches, rule_counters_mainfolder, rule_counters_allfolders)
    #LogMaster.critical(final_output)

    # Send Completion Email
    smtp_send_completion_email(config, final_output)

    # Disconnect from database
    graceful_shutdown_db(db=db)

if __name__ == "__main__":
    main()
