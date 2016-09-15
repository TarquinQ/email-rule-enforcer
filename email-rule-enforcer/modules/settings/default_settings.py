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
    config['imap_headers_only'] = True
    config['imap_folders_to_exclude'] = set()

    # SMTP Defaults
    config['smtp_server_name'] = None
    config['smtp_username'] = 'Not_Set'
    config['smtp_password'] = None
    config['smtp_use_tls'] = False
    config['smtp_server_port'] = None
    config['smtp_auth_required'] = False
    config['smtp_forward_from'] = None
    config['smtp_smtplib_debug'] = False

    # Logging Defaults
    config['console_loglevel'] = 2
    config['console_ultra_debug'] = False
    config['console_insane_debug'] = False
    config['log_settings_logfile'] = None
    config['log_settings_logfile_debug'] = None

    # Exchange Defaults
    config['Exchange_shared_mailbox_alias'] = None

    # Behaviour Settings
    config['parse_config_and_stop'] = False
    config['assess_rules_againt_mainfolder'] = True
    config['assess_rules_againt_allfolders'] = True
    config['actually_perform_actions'] = True
    config['allow_body_match_for_all_folders'] = False
    config['allow_body_match_for_main_folder'] = True
    config['imap_headers_only_for_all_folders'] = True
    config['imap_headers_only_for_main_folder'] = True

    # Finalise
    config['defaults_are_set'] = True
