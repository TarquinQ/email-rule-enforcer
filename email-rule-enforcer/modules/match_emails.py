from modules.models.RulesAndMatches import Rule, RuleAction, MatchField
from modules.email.make_new_emails import new_email
from modules.email.smtp_send import send_email_from_config
from modules.logging import LogMaster
from modules.email.supportingfunctions_email import get_relevant_email_headers_for_logging


def check_match_list(email_to_validate, matches):
    num_required_matches = 0
    num_actual_matches = 0
    for match_check in matches:
        num_required_matches += 1
        if match_check is type(list):  # Then we know this is an 'OR'clause, and match on any of these
            matched_or = False
            for match_or in match_check:
                if match_or.test_match_email(email_to_validate):
                    matched_or = True
                    break  # No point trying more!
            if matched_or:
                num_actual_matches += 1

        elif match_check is type(MatchField):
            if match_check.test_match_email(email_to_validate):
                num_actual_matches += 1
            else:
                break

    if num_actual_matches == num_required_matches:
        return True
    else:
        return False


def iterate_rules_over_mailfolder(imap_connection, config, rules):
    LogMaster.log(40, 'Now commencing iteration of Rules over all emails in folder')

    if (imap_connection.is_connected is False):
        LogMaster.log(40, 'Aborting: IMAP server is not connected')
        return None

    for email_to_validate in imap_connection.get_emails_in_currfolder():
        LogMaster.log(20, 'New Email found. Email Details:')
        LogMaster.log(20, get_relevant_email_headers_for_logging(email_to_validate))
        LogMaster.log(20, 'Now assessing an email against all rules.')

        for rule in rules:
            email_matched = False
            email_actioned = False

            # First we check each match, to see if they all match
            # If not matched, exit this rule and onto the next
            if not (check_match_list(email_to_validate, rule.matches)):
                continue

            # Now we see if the exceptions apply
            # If so, exit this rule and onto the next
            if (check_match_list(email_to_validate, rule.match_exceptions)):
                continue

            # Now we know that it is matched and not excepted, so we perform actions
            # valid_actions = frozenset(['move_to_folder', 'forward', 'delete', 'mark_as_read', 'mark_as_unread'])

            for action_to_perform in rule.actions:
                action_type = action_to_perform.action_type
                if action_type == "forward":
                    forwarded_email(
                        email_from=config['smtp_forward_from'],
                        email_to=action_to_perform.email_recipients,
                        subject='FWD: ' + email_to_validate['Subject'],
                        bodytext=email_to_validate.as_string()
                    )
                    send_email_from_config(config, forwarded_email)

                if action_type == "mark_as_read":
                    imap_connection.mark_email_as_read_byuid(email_to_validate.uid)

                if action_type == "mark_as_unread":
                    imap_connection.mark_email_as_unread_byuid(email_to_validate.uid)

            for action_to_perform in rule.actions:
                action_type = action_to_perform.action_type

                if action_type == "move_to_folder":
                    imap_connection.move_email(
                        uid=email_to_validate.uid,
                        dest_folder=action_to_perform.dest_folder,
                        mark_as_read_on_move=action_to_perform.mark_as_unread_on_action
                    )
                    break  # Email gone now, no more actions

                if action_type == "Delete":
                    perm_delete = action_to_perform.delete_permanently
                    imap_connection.del_email(email_to_validate.uid, perm_delete)
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

