def set_defaults(config):
    """This function sets defaults for all settings which can be set by default"""

    # General behaviour
    config['empty_trash_on_exit'] = False
    config['mark_as_read_on_move'] = True
    config['send_notification_email_on_completion'] = False
    config['notification_email_on_completion'] = None
    config['console_loglevel'] = 2
    config['console_ultra_debug'] = False
    config['console_insane_debug'] = False
    config['test_config_parse_only'] = False

    # IMAP Defaults
    config['imap_server_name'] = None
    config['imap_username'] = None
    config['imap_password'] = None
    config['imap_use_tls'] = False
    config['imap_server_port'] = None
    config['imap_initial_folder'] = 'INBOX'
    config['imap_deletions_folder'] = 'Trash'
    config['imap_imaplib_debuglevel'] = 0

    # SMTP Defaults
    config['smtp_server_name'] = None
    config['smtp_username'] = None
    config['smtp_password'] = None
    config['smtp_use_tls'] = False
    config['smtp_server_port'] = None
    config['smtp_auth_required'] = False
    config['smtp_forward_from'] = None

    # Logging Defaults
    config['log_settings_logfile'] = None
    config['log_settings_logfile_debug'] = None

    config['defaults_are_set'] = True
