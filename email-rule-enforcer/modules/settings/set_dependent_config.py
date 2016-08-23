def set_dependent_config(config, rules):
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

    if config['smtp_forward_from'] is None:
        config['smtp_forward_from'] = config['smtp_username']

    if config['smtp_forward_from'].lower() == 'same_as_imap_auth':
        config['smtp_forward_from'] = config['imap_username']

    if config['smtp_username'].lower() == 'same_as_imap_auth':
        config['smtp_username'] = config['imap_username']

    if config['smtp_password'].lower() == 'same_as_imap_auth':
        config['smtp_password'] = config['imap_password']

    if isinstance(config['imap_imaplib_debuglevel'], str):
        try:
            config['imap_imaplib_debuglevel'] = int(config['imap_imaplib_debuglevel'])
        except:
            config['imap_imaplib_debuglevel'] = 0

    if config['Exchange_shared_mailbox_alias'] is not None:
        config['imap_username'] = config['imap_username'] + '\\' + config['Exchange_shared_mailbox_alias']

