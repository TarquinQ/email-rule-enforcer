def set_defaults(config):
    """This function sets defaults for all settings which can be set by default"""

    # General behaviour
    config['empty_trash_on_exit'] = False
    config['mark_as_read_on_move'] = True
    config['send_notification_email_on_completion'] = False
    config['notification_email_on_completion'] = None

    # IMAP Defaults
    config['imap_server_name'] = None
    config['imap_username'] = 'Not_Set'
    config['imap_password'] = None
    config['imap_use_tls'] = False
    config['imap_server_port'] = None
    config['imap_initial_folder'] = 'INBOX'
    config['imap_deletions_folder'] = 'Trash'
    config['imap_imaplib_debuglevel'] = 0
    config['imap_folders_to_exclude'] = set()
    config['imap_headers_only_for_all_folders'] = True
    config['imap_headers_only_for_main_folder'] = False
    config['imap_max_authfail_10min'] = 3
    config['imap_max_authfail_24hrs'] = 5
    config['imap_max_connectionfail_10min'] = 3
    config['imap_max_connectionfail_24hrs'] = 24
    config['imap_keepalive_mins'] = 29

    # Exchange Defaults
    config['Exchange_shared_mailbox_alias'] = None

    # SMTP Defaults
    config['smtp_server_name'] = None
    config['smtp_username'] = 'Not_Set'
    config['smtp_password'] = None
    config['smtp_use_tls'] = False
    config['smtp_server_port'] = None
    config['smtp_auth_required'] = False
    config['smtp_forward_from'] = None
    config['smtp_smtplib_debug'] = False

    # Database Defaults
    config['database_filename'] = ':memory:'

    # Daemon-Mode Defaults
    config['daemon_mode'] = False
    config['daemon_monitor_inbox'] = True
    config['daemon_monitor_inbox_delay'] = 5
    config['daemon_keepalive'] = 20
    config['full_scan_at_startup'] = True
    config['full_scan_delay'] = 6
    config['full_scan_align_to_timing'] = False
    config['full_scan_align_to_timing_base'] = '25:00'

    # Logging Defaults
    config['console_loglevel'] = 2
    config['console_ultra_debug'] = False
    config['console_insane_debug'] = False
    config['log_settings_logfile'] = None
    config['log_settings_logfile_debug'] = None

    # Behaviour Settings
    config['parse_config_and_stop'] = False
    config['assess_rules_againt_mainfolder'] = True
    config['assess_rules_againt_allfolders'] = True
    config['actually_perform_actions'] = True
    config['allow_body_match_for_all_folders'] = False
    config['allow_body_match_for_main_folder'] = True

    # Daemon-Mode Settings
    config['daemon_mode_enable'] = True
    config['daemon_allow_multiple_imapconns'] = True
    config['daemon_check_inbox_mins'] = 5
    config['daemon_repeat_mainrules_hours'] = 24
    config['daemon_repeat_mainrules_at'] = '00:00'
    config['daemon_check_mainrules_at_startup'] = True

    # Finalise
    config['defaults_are_set'] = True
