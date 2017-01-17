import re
from modules.models.RuleMatches import MatchBody
import modules.models.RuleActions as RuleActions


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

    if config['Exchange_shared_mailbox_alias'] is not None:
        config['imap_username'] = config['imap_username'] + '\\' + config['Exchange_shared_mailbox_alias']

    if config['parse_config_and_stop']:
        config['send_notification_email_on_completion'] = False

    if (config['daemon_monitor_inbox_delay'] < 1):
        config['daemon_monitor_inbox_delay'] = 5

    if (config['daemon_keepalive'] < 1):
        config['daemon_keepalive'] = 20

    if (config['full_scan_delay'] < 1):
        config['full_scan_delay'] = 6

    # Convert daemon stuff to seconds
    config['daemon_monitor_inbox_delay'] = config['daemon_monitor_inbox_delay'] * 60
    config['daemon_keepalive'] = config['daemon_keepalive'] * 60
    config['full_scan_delay'] = config['full_scan_delay'] * 60 * 60

    if config['full_scan_align_to_timing_base'] != '25:00':
        if re.match('[0-9][0-9]:[0-9][0-9]', config['full_scan_align_to_timing_base']):
            base = config['full_scan_align_to_timing_base'].split(':')
            if (int(base[0]) < 24) and (int(base[1]) < 60):
                config['full_scan_align_to_timing'] = True

    RuleActions.Action.set_actually_perform_actions(config['actually_perform_actions'])


def set_headersonly_mode(config, rules, conf_check, conf_setting):
    def check_for_body_rule_in_matches(match_list):
        for match in match_list:
            if isinstance(match, MatchBody):
                turn_bodymatch_on = True
                return turn_bodymatch_on
            elif isinstance(match, list):  # Then we know this is an 'OR' clause
                for match_or in match:
                    if isinstance(match_or, MatchBody):
                        turn_bodymatch_on = True
                        return turn_bodymatch_on
        return False

    if config[conf_check]:  # This checks to see if this is even allowed in the first place
        turn_bodymatch_on = False
        for rule in rules:
            turn_bodymatch_on = (check_for_body_rule_in_matches(rule.matches) |
                 check_for_body_rule_in_matches(rule.match_exceptions))
            if turn_bodymatch_on:
                break
        if turn_bodymatch_on:
            config[conf_setting] = False
