from modules.models.RuleMatches import Match


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

    if config['parse_config_and_stop']:
        config['send_notification_email_on_completion'] = False


def set_headersonly_mode(config, rules, conf_check, conf_setting):
    def check_for_body_rule(match_list):
        for match in match_list:
            if isinstance(match, Match):
                if match.field_to_match.lower() == 'body':
                    turn_bodymatch_on = True
                    return turn_bodymatch_on
            elif isinstance(match, list):  # Then we know this is an 'OR' clause
                for match_or in match:
                    if isinstance(match_or, Match):
                        if match_or.field_to_match.lower() == 'body':
                            turn_bodymatch_on = True
                            return turn_bodymatch_on
        return False

    if config[conf_check]:  # This checks to see if this is even allowed in the first place
        turn_bodymatch_on = False
        for rule in rules:
            turn_bodymatch_on = (check_for_body_rule(rule.matches) |
                 check_for_body_rule(rule.match_exceptions))
            if turn_bodymatch_on:
                break
        if turn_bodymatch_on:
            config[conf_setting] = False
