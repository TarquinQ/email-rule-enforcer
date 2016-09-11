from modules.logging import LogMaster
from modules.models.RulesAndMatches import Rule, RuleAction, MatchField, MatchDate
from modules.email.smtp_send import send_email_from_config
from modules.email.supportingfunctions_email import get_relevant_email_headers_for_logging, convert_bytes_to_utf8
from modules.email.make_new_emails import new_email_forward


def check_match_list(matches, email_to_validate):
    num_required_matches = len(matches)
    num_actual_matches = 0

    if num_required_matches == 0:
        LogMaster.ultra_debug('Zero matches required for this rule - rule invalid, not attempting.')
        return False

    for match_check in matches:
        if isinstance(match_check, list):  # Then we know this is an 'OR'clause, and match on any of these
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

        elif (isinstance(match_check, MatchField) or isinstance(match_check, MatchDate)):
            LogMaster.ultra_debug('Email matching is now a match Match ID %s, of type %s.', match_check.id, type(match_check))
            if match_check.test_match_email(email_to_validate):
                LogMaster.ultra_debug('Email matched this field; continuing matching.')
                num_actual_matches += 1
            else:
                LogMaster.ultra_debug('Email did not match this field.')
                break
        else:
            LogMaster.ultra_debug('Match ID %s is neither of type MatchField, MatchDate or List. Is actually type: %s.', match_check.id, type(match_check))

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
            LogMaster.info('Match found, Rule ID %s (Name: \"%s\"") matched against Email UID %s (From: \"%s\", Date: \"%s\")',
                rule.id, rule.name,
                email_to_validate.uid_str, email_to_validate["from"], email_to_validate["date"]
                )

    return email_matched


def perform_actions(imap_connection, config, rule, email_to_validate):
    for action_to_perform in rule.actions:
        action_type = action_to_perform.action_type
        LogMaster.ultra_debug('Rule Action for Rule ID %s is type %s. Relevant value is \"%s\"',
            rule.id, action_type, action_to_perform.get_relevant_value())

        if action_type == "forward":
            LogMaster.info('Rule Action for Rule ID %s is a forward, so now forwarding to %s', rule.id, action_to_perform.email_recipients)
            LogMaster.insane_debug('Now constructing a new email for Rule ID %s, to be sent From: %s', rule.id, config['smtp_forward_from'])

            if (email_to_validate.headers_only):
                raw_email = imap_connection.get_raw_email_byuid(email_to_validate.uid)
            else:
                raw_email = email_to_validate.original_raw_email
            email_to_attach = imap_connection.parse_raw_email(raw_email)

            email_to_forward = new_email_forward(
                email_from=config['smtp_forward_from'],
                email_to=action_to_perform.email_recipients,
                subject='FWD: ' + email_to_validate['subject'],
                bodytext="Forwarded Email Attached",
                email_to_attach=email_to_attach)

            LogMaster.insane_debug('Constructed email for Rule ID %s:\n%s', rule.id, email_to_forward)

            if config['actually_perform_actions']:
                send_email_from_config(config, email_to_forward)

        if action_type == "mark_as_read":
            LogMaster.info('Now Marking Email UID %s as Read', rule.id, email_to_validate.uid_str)
            if config['actually_perform_actions']:
                imap_connection.mark_email_as_read_byuid(email_to_validate.uid)

        if action_type == "mark_as_unread":
            LogMaster.info('Now Marking Email UID %s as Unread', rule.id, email_to_validate.uid_str)
            if config['actually_perform_actions']:
                imap_connection.mark_email_as_unread_byuid(email_to_validate.uid)

    for action_to_perform in rule.actions:
        action_type = action_to_perform.action_type
        LogMaster.insane_debug('2nd Run through Actions: Rule Action for Rule ID %s is type %s', rule.id, action_type)

        if action_type == "move_to_folder":
            LogMaster.info('Now Moving Email UID %s to folder', email_to_validate.uid_str, action_to_perform.dest_folder)
            if config['actually_perform_actions']:
                imap_connection.move_email(
                    uid=email_to_validate.uid,
                    dest_folder=action_to_perform.dest_folder,
                    mark_as_read_on_move=action_to_perform.mark_as_unread_on_action
                )
            break  # Email gone now, no more actions

        if action_type == "Delete":
            perm_delete = action_to_perform.delete_permanently
            LogMaster.info('Now Deleting Email UID %s, permanently=%s', email_to_validate.uid_str, perm_delete)
            if config['actually_perform_actions']:
                imap_connection.del_email(email_to_validate.uid, perm_delete)
            break  # Email gone now, no more actions


def check_email_against_rules_and_perform_actions(imap_connection, config, rules, email_to_validate):
    for rule in rules:
        email_matched = False
        email_actioned = False

        LogMaster.ultra_debug('Now checking Email UID %s against Rule ID %s (Rule Name: \"%s\"")', email_to_validate.uid_str, rule.id, rule.name)

        if len(rule.get_matches()) == 0:
            LogMaster.ultra_debug('Zero matches required for Rule %s - rule invalid, not attempting.', rule.id)
            continue
        if len(rule.get_actions()) == 0:
            LogMaster.info('Zero matches actions for this rule - rule invalid, not attempting actions.')
            continue

        email_matched = check_email_against_rule(rule, email_to_validate)

        if (email_matched):
            LogMaster.info('Now performing all actions for Rule ID %s', rule.id)
            perform_actions(imap_connection, config, rule, email_to_validate)
        else:
            LogMaster.debug('Rule ID %s not matched, ignoring.', rule.id)


def iterate_rules_over_mailfolder(imap_connection, config, rules):
    LogMaster.log(40, 'Now commencing iteration of Rules over all emails in folder')

    if (imap_connection.is_connected() is False):
        LogMaster.log(40, 'Aborting: IMAP server is not connected')
        return None

    if (imap_connection.get_currfolder() == ''):
        LogMaster.log(40, 'Aborting: IMAP server is connected, but not attached to a Folder')
        return None

    for email_to_validate in imap_connection.get_emails_in_currfolder(headers_only=config['imap_headers_only']):
        if email_to_validate is None:
            continue
        LogMaster.log(20, '\n\Email in found in folder. UID %s. Email Details:\n%s',
            email_to_validate.uid_str,
            get_relevant_email_headers_for_logging(email_to_validate))
        LogMaster.log(20, 'Now assessing this email against all rules.')

        check_email_against_rules_and_perform_actions(imap_connection, config, rules, email_to_validate)

        LogMaster.log(20, 'Completed assessment of all rules against this email.\n')


def iterate_over_allfolders(imap_connection, config, rules):

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

        LogMaster.info('Now connecting to folder "%s".', folder_name)
        imap_connection.connect_to_folder(folder_name)

        iterate_allfolderrules_over_mailfolder(imap_connection, config, rules)

    LogMaster.info('Now resetting IMAP connection back to default folder.')
    imap_connection.connect_to_default_folder()


def iterate_allfolderrules_over_mailfolder(imap_connection, config, rules):
    for email_to_validate in imap_connection.get_emails_in_currfolder(headers_only=True):
        if email_to_validate is None:
            continue
        LogMaster.debug('\n\Email found in folder, UID %s.', email_to_validate.uid_str)
        LogMaster.insane_debug('\n\nNew Email being processed, UID %s. Email Details:\n%s',
            email_to_validate.uid_str,
            get_relevant_email_headers_for_logging(email_to_validate))
        LogMaster.insane_debug('Now assessing this email against all_folder rules.')

        check_email_against_rules_and_perform_actions(imap_connection,
            config,
            rules,
            email_to_validate)

        LogMaster.insane_debug('Completed assessment of the all_folder rules against this email.\n')


