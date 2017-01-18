from modules.logging import LogMaster
from modules.models.RuleMatches import Match
from modules.email.supportingfunctions_email import convert_bytes_to_utf8
from modules.email.supportingfunctions_email import get_extended_email_headers_for_logging, get_basic_email_headers_for_logging
from modules.supportingfunctions import strip_quotes


def check_match_list(matches, email_to_validate):
    num_required_matches = len(matches)
    num_actual_matches = 0

    if num_required_matches == 0:
        LogMaster.ultra_debug('Zero matches required for this rule - rule invalid, not attempting.')
        return False

    for match_check in matches:
        if isinstance(match_check, list):  # Then we know this is an 'OR' clause, and match on any of these
            LogMaster.ultra_debug('Email matching is now in \'or\' clause.')
            matched_or = False
            for match_or in match_check:
                if match_or.test_match_email(email_to_validate):
                    matched_or = True
                    num_actual_matches += 1
                    LogMaster.ultra_debug('Email \'or\' is now matched, continuing.')
                    break  # Stop counting
            else:
                LogMaster.ultra_debug('Email \'or\' is unmatched; matching over.')

        elif (isinstance(match_check, Match)):
            LogMaster.ultra_debug('Email matching is now a match Match ID %s, of type %s.',
                match_check.id, match_check.__class__.__name__)
            if match_check.test_match_email(email_to_validate):
                LogMaster.ultra_debug('Email matched this field; continuing matching.')
                num_actual_matches += 1
            else:
                LogMaster.ultra_debug('Email did not match this field.')
                break
        else:
            LogMaster.ultra_debug('Match ID %s is neither of type Match nor List. Is actually type: %s.', match_check.id, type(match_check))

    if num_actual_matches == num_required_matches:
        LogMaster.ultra_debug('Email matched. Num matches required: %s, num matches found: %s', num_required_matches, num_actual_matches)
        return True
    else:
        LogMaster.ultra_debug('Email unmatched. Num matches required: %s, num matches found: %s', num_required_matches, num_actual_matches)
        return False


def check_email_against_rule(rule, email_to_validate):
    email_matched = False
    email_excepted = False
    # First we check each match, to see if they all match
    # If not matched, exit this rule and onto the next
    if not (check_match_list(rule.get_matches(), email_to_validate)):
        LogMaster.insane_debug('Now checking Rule ID %s: not matched', rule.id)
    else:
        LogMaster.insane_debug('Now checking Rule ID %s: matched against all criteria', rule.id)
        email_matched = True

    if (email_matched):
        # Now we see if the exceptions apply
        LogMaster.insane_debug('Now checking Rule ID %s against match exceptions', rule.id)
        # If so, exit this rule and onto the next
        if len(rule.get_match_exceptions()) != 0:
            if (check_match_list(rule.match_exceptions, email_to_validate)):
                LogMaster.insane_debug('Valid exception(s) found. Rule ID %s was matched, but also excepted', rule.id)
                email_excepted = True
            else:
                LogMaster.insane_debug('Exceptions not matched on Rule ID %s', rule.id)
        else:
            LogMaster.insane_debug('Skipping exception checking: No exceptions in Rule ID %s.', rule.id)

        if (email_excepted):
            email_matched = False
        else:
            # Now we know that it is matched and not excepted, so we will perform actions
            LogMaster.info('Match found, Rule ID %s (Name: \"%s\"") matched against Email UID %s',
                rule.id, rule.name,
                email_to_validate.uid_str
                )

    return email_matched


def perform_actions(imap_connection, config, rule, email_to_validate, counters):
    for action_to_perform in rule.actions:
        if action_to_perform.is_destructive():
            LogMaster.ultra_debug('Rule ID %s Action %s is \"destructive\", so will skip for now',
                rule.id, action_to_perform.id)
            continue

        LogMaster.info('Rule Action for Rule ID %s is ID %s, of type \'%s\'. Relevant information is \"%s\"',
            rule.id, action_to_perform.id, action_to_perform.action_type, action_to_perform.get_relevant_value())

        counters.incr('actions_taken')
        action_to_perform.perform_action(email_to_action=email_to_validate, config=config,
            imap_connection=imap_connection, LogMaster=LogMaster)

    for action_to_perform in rule.actions:
        action_type = action_to_perform.action_type
        LogMaster.insane_debug('2nd Run through Actions: Rule Action for Rule ID %s is type %s', rule.id, action_type)

        if not action_to_perform.is_destructive():
            LogMaster.ultra_debug('Rule ID %s Action %s is not \"destructive\", so has been done already; skipping.',
                rule.id, action_to_perform.id)
            continue

        LogMaster.info('Rule Action for Rule ID %s is ID %s, of type \'%s\'. Relevant information is \"%s\"',
            rule.id, action_to_perform.id, action_to_perform.action_type, action_to_perform.get_relevant_value())

        counters.incr('actions_taken')
        action_to_perform.perform_action(email_to_action=email_to_validate, config=config,
            imap_connection=imap_connection, LogMaster=LogMaster)
        break  # Email gone now, no more actions


def check_email_against_rules_and_perform_actions(imap_connection, config, rules, email_to_validate, counters):
    for rule in rules:
        email_matched = False
        email_actioned = False

        LogMaster.ultra_debug('Now checking Email UID %s against Rule ID %s (Rule Name: \"%s\"")', email_to_validate.uid_str, rule.id, rule.name)

        if len(rule.get_matches()) == 0:
            LogMaster.ultra_debug('Zero matches required for Rule %s - rule invalid, not attempting.', rule.id)
            continue

        if len(rule.get_actions()) == 0:
            LogMaster.ultra_debug('Zero matches actions for Rule %s - rule invalid, not attempting.', rule.id)
            continue

        email_matched = check_email_against_rule(rule, email_to_validate)
        counters.incr('rules_checked')

        if (email_matched):
            LogMaster.info('Now performing all actions for Rule ID %s', rule.id)
            perform_actions(imap_connection, config, rule, email_to_validate, counters)
            counters.incr('emails_matched')
        else:
            LogMaster.debug('Rule ID %s not matched, ignoring.', rule.id)


def iterate_rules_over_mailfolder(imap_connection, config, rules, counters, headers_only=False):
    LogMaster.log(40, 'Now commencing iteration of Rules over all emails in folder {0}'.format(
        imap_connection.currfolder_name
    ))

    for email_to_validate in imap_connection.get_emails_in_currfolder(headers_only):
        if email_to_validate is None:
            continue
        LogMaster.info('Email UID %s found in IMAP folder (\"%s\"). Email Date: %s; From: %s',
            email_to_validate.uid_str,
            imap_connection.get_currfolder(),
            email_to_validate.date_datetime,
            email_to_validate.addr_from
        )

        LogMaster.debug('Now assessing this email against all rules.')
        LogMaster.ultra_debug('Extended Email Details for UID %s:\n%s',
            email_to_validate.uid_str,
            get_extended_email_headers_for_logging(email_to_validate))

        counters.incr('emails_seen')
        check_email_against_rules_and_perform_actions(imap_connection, config, rules, email_to_validate, counters)

        LogMaster.debug('Completed assessment of all rules against this email.\n')


def iterate_rules_over_mainfolder(imap_connection, config, rules, counters):
    LogMaster.log(40, 'Now commencing iteration of Rules over all emails in Main folder')

    if (not config['assess_rules_againt_mainfolder']):
        LogMaster.info('Main Folder Rules Not Processed: this processing has been disabled in the program config files.')
        return None

    if (imap_connection.is_connected() is False):
        LogMaster.log(40, 'Aborting: IMAP server is not connected')
        return None

    if (imap_connection.get_currfolder() == ''):
        LogMaster.log(40, 'Aborting: IMAP server is connected, but not attached to a Folder')
        return None

    counters.incr('folders_processed')
    return iterate_rules_over_mailfolder(imap_connection, config, rules, counters, headers_only=config['imap_headers_only_for_main_folder'])


def iterate_rules_over_allfolders(imap_connection, config, rules, counters):

    if (not config['assess_rules_againt_allfolders']):
        LogMaster.info('All Folders Rules Not Processed: this processing has been disabled in the program config files.')
        return None

    if (imap_connection.is_connected is False):
        LogMaster.log(40, 'Aborting: IMAP server is not connected')
        return None

    if (rules is None):
        LogMaster.debug('Ignoring: no global all_folders rule is set, no need to connect to all folders')
        return None

    LogMaster.log(40, 'Now commencing iteration of a rule over all emails in all folders in the mailbox')
    LogMaster.info('\nNow looping over all folders in the mailbox.')
    LogMaster.ultra_debug("All folders: %s", imap_connection.get_all_folders())
    for folder_record in imap_connection.get_all_folders():
        folder_record_utf8 = convert_bytes_to_utf8(folder_record)
        (folder_flags, folder_parent_and_name) = folder_record_utf8.split(')', 1)
        (empty_str, folder_parent, folder_name) = folder_parent_and_name.split('"', 2)
        folder_name = folder_name.strip()
        folder_name_noquotes = strip_quotes(folder_name)

        LogMaster.ultra_debug('Now checking folder "%s" for folder exclusions.', folder_name)
        if folder_is_excluded(folder_name_noquotes, config['imap_folders_to_exclude']):
            LogMaster.info('Skipping folder "%s" due to folder exclusions.', folder_name)
        else:
            LogMaster.info('Now connecting to folder \"%s\".', folder_name_noquotes)
            imap_connection.connect_to_folder(folder_name)
            counters.incr('folders_processed')
            iterate_rules_over_mailfolder(imap_connection, config, rules, counters, headers_only=config['imap_headers_only_for_all_folders'])

    LogMaster.info('Now resetting IMAP connection back to default folder.')
    imap_connection.connect_to_default_folder()


def folder_is_excluded(folder_name, exclusion_set):
    exclude = False
    if folder_name in exclusion_set:
        exclude = True
    elif folder_name.find('/') > 0:
        # There are parent folders of this folders to check
        folder_path = folder_name.split('/')
        path_to_check = folder_path[0]
        if path_to_check in exclusion_set:
            exclude = True
        else:
            for i in range(1, len(folder_path)):
                path_to_check += '/' + folder_path[i]
                if path_to_check in exclusion_set:
                    exclude = True
                    break

    return exclude


def keepalive(imap_connection):
    LogMaster.log(40, 'Now commencing keepalive of IMAP connection')

    if (imap_connection.is_connected() is False):
        LogMaster.log(40, 'Aborting: IMAP server is not connected')
        return None

    return imap_connection.noop()
