from modules.models.RulesAndMatches import Rule, RuleAction, MatchField
from modules.email.make_new_emails import new_email
from modules.email.smtp_send import send_email_from_config
from modules.logging import LogMaster
from modules.email.supportingfunctions_email import get_relevant_email_headers_for_logging, convert_bytes_to_utf8


def check_match_list(email_to_validate, matches):
    num_required_matches = len(matches)
    num_actual_matches = 0

    if num_required_matches == 0:
        LogMaster.ultra_debug('Zero matches required for this rule - rule invalid, not attempting.')
        return False

    for match_check in matches:
        if match_check is type(list):  # Then we know this is an 'OR'clause, and match on any of these
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

        elif match_check is type(MatchField):
            LogMaster.ultra_debug('Email matching is now a field match, Match ID %s.', match_check.id)
            if match_check.test_match_email(email_to_validate):
                LogMaster.ultra_debug('Email matched this field; continuing matching.')
                num_actual_matches += 1
            else:
                LogMaster.ultra_debug('Email did not match this field.')
                break

    if num_actual_matches == num_required_matches:
        LogMaster.ultra_debug('Email matched. Num matches required: %s, num matches found: %s', num_required_matches, num_actual_matches)
        return True
    else:
        LogMaster.ultra_debug('Email unmatched. Num matches required: %s, num matches found: %s', num_required_matches, num_actual_matches)
        return False


def iterate_rules_over_mailfolder(imap_connection, config, rules):
    LogMaster.log(40, 'Now commencing iteration of Rules over all emails in folder')

    if (imap_connection.is_connected is False):
        LogMaster.log(40, 'Aborting: IMAP server is not connected')
        return None

    for email_to_validate in imap_connection.get_emails_in_currfolder():
        LogMaster.log(20, 'New Email found. Email Details:\n%s',
            get_relevant_email_headers_for_logging(email_to_validate))
        LogMaster.log(20, 'Now assessing an email against all rules.')
        #LogMaster.insane_debug('Full email object instance variables and RFC contents:')
        #LogMaster.insane_debug('Instance variables: %s', email_to_validate.__dict__)
        #LogMaster.insane_debug('Full Email Contents: %s\n\n', email_to_validate.as_string())

        for rule in rules:
            email_matched = False
            email_actioned = False

            LogMaster.insane_debug('Now checking Rule ID %s against Email UID %s', rule.id, email_to_validate.uid_str)

            if len(rule.get_matches()) == 0:
                LogMaster.ultra_debug('Zero matches required for this rule - rule invalid, not attempting.')
                continue

            # First we check each match, to see if they all match
            # If not matched, exit this rule and onto the next
            if not (check_match_list(email_to_validate, rule.get_matches())):
                LogMaster.insane_debug('Now checking Rule ID %s: not matched', rule.id)
                continue
            else:
                LogMaster.insane_debug('Now checking Rule ID %s: matched against all criteria', rule.id)

            # Now we see if the exceptions apply
            LogMaster.insane_debug('Now checking Rule ID %s against match exceptions', rule.id)
            # If so, exit this rule and onto the next
            if len(rule.get_match_exceptions()) != 0:
                if (check_match_list(email_to_validate, rule.match_exceptions)):
                    LogMaster.insane_debug('Valid exception(s) found. Rule ID %s was matched, but also excepted', rule.id)
                    continue
                else:
                    LogMaster.insane_debug('Exceptions not matched on Rule ID %s', rule.id)
            else:
                LogMaster.insane_debug('Skipping exception checking: No exceptions in Rule ID %s.', rule.id)

            # Now we know that it is matched and not excepted, so we perform actions
            # valid_actions = frozenset(['move_to_folder', 'forward', 'delete', 'mark_as_read', 'mark_as_unread'])
            LogMaster.info('Match found, Rule ID %s matched against Email UID %s', rule.id, email_to_validate.uid_str)
            if len(rule.get_actions()) == 0:
                LogMaster.info('Zero matches required for this rule - rule invalid, not attempting actions.')
                continue

            LogMaster.info('Now performing all actions for Rule ID %s', rule.id)
            for action_to_perform in rule.actions:
                action_type = action_to_perform.action_type
                LogMaster.ultra_debug('Rule Action for Rule ID %s is type %s', rule.id, action_type)

                if action_type == "forward":
                    LogMaster.insane_debug('Now constructing a new email for Rule ID %s, from %s', rule.id, config['smtp_forward_from'])
                    forwarded_email(
                        email_from=config['smtp_forward_from'],
                        email_to=action_to_perform.email_recipients,
                        subject='FWD: ' + email_to_validate['Subject'],
                        bodytext=email_to_validate.as_string()
                    )
                    LogMaster.info('Rule Action for Rule ID %s is a forward, so now forwarding to %s', rule.id, action_to_perform.email_recipients)
                    send_email_from_config(config, forwarded_email)

                if action_type == "mark_as_read":
                    LogMaster.info('Now Markng Email UID %s as Read', rule.id, email_to_validate.uid_str)
                    imap_connection.mark_email_as_read_byuid(email_to_validate.uid)

                if action_type == "mark_as_unread":
                    LogMaster.info('Now Markng Email UID %s as Unread', rule.id, email_to_validate.uid_str)
                    imap_connection.mark_email_as_unread_byuid(email_to_validate.uid)

            for action_to_perform in rule.actions:
                action_type = action_to_perform.action_type
                LogMaster.insane_debug('2nd Run through Actions: Rule Action for Rule ID %s is type %s', rule.id, action_type)

                if action_type == "move_to_folder":
                    imap_connection.move_email(
                        uid=email_to_validate.uid,
                        dest_folder=action_to_perform.dest_folder,
                        mark_as_read_on_move=action_to_perform.mark_as_unread_on_action
                    )
                    LogMaster.info('Now Moving Email UID %s to folder', action_to_perform.dest_folder)
                    break  # Email gone now, no more actions

                if action_type == "Delete":
                    perm_delete = action_to_perform.delete_permanently
                    imap_connection.del_email(email_to_validate.uid, perm_delete)
                    LogMaster.info('Now Moving Email UID %s to folder', action_to_perform.dest_folder)
                    break  # Email gone now, no more actions

        LogMaster.log(20, 'Completed assessment of all rules against this email.\n')


# class Rule():
#     rule_count = 0
#     def get_rule_count(cls):
#     def __init__(self, rule_name=None):
#         self.incr_rule_count()
#         self.rule_num = self.get_rule_count()
#         self.id = self.get_rule_count()
#         self.set_name(rule_name)
#         self.actions = []
#         self.matches = []
#         self.match_exceptions = []
#         self.continue_rule_checks_if_matched = True

#     # Set Basic variables
#     def add_action(self, action):
#     def add_match(self, match):
#     def add_match_exception(self, match):
#     def set_continue_rule_checks_if_matched(self, flag):
#     # Handle or-matches in the match setion
#     def start_match_or(self):
#     def add_match_or(self, match):
#     def end_match_or(self):
#     # Handle or-matches in the exception setion
#     def start_exception_or(self):
#     def add_exception_or(self, match):
#     def end_exception_or(self):



# class MatchField():
#     match_types = frozenset(['starts_with', 'contains', 'ends_with', 'is'])
#     match_fields = frozenset(['to', 'from', 'subject', 'cc', 'bcc', 'body'])

#     def __init__(self, field_to_match=None, match_type=None, str_to_match=None, case_sensitive=False, parent_rule_id=None):
#     def set_field_to_match(self, field_to_match):
#     def set_match_type(self, match_type):
#     def set_str_to_match(self, str_to_match):
#     def set_match_is_case_sensitive(self, flag):
# class RuleAction():
#     valid_actions = frozenset(['move_to_folder', 'forward', 'delete', 'mark_as_read', 'mark_as_unread'])
#     def __init__(self, action_type):
#     def set_dest_folder(self, dest_folder):
#     def set_mark_as_read(self, mark_as_read):
#     def set_mark_as_unread(self, mark_as_unread):
#     def set_delete_permanently(self, flag):
#     def add_email_recipient(self, email_addr):

