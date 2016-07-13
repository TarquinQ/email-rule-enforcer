from modules.models.RulesAndMatches import Rule, RuleAction, MatchField


def parse_all_emails(imap_connection, rules):
    if (imap_connection.is_connected() is False):
        return None

    for email_to_validate in imap_connection.get_emails_in_currfolder():
        for rule in rules:
            email_matched = False
            email_excepted = False
            email_actioned = False

            # First we check each match, to see if they all match
            num_required_matches = 0
            num_actual_matches = 0
            for match_check in rule.matches:
                num_required_matches += 1
                if match_check is type(list):  # Then we know this is an 'OR'clause, and match on any of these
                    matched_or = False
                    for match_or in match_check:
                        str_to_test = email_to_validate[match_or.field_to_match]
                        if (match_or.test_match(str_to_test)):
                            matched_or = True
                    if matched_or:
                        num_actual_matches += 1
                else if match_check is type(MatchField):
                    str_to_test = email_to_validate[match_check.field_to_match]
                    if (match_check.test_match(str_to_test)):
                        num_actual_matches += 1
                    else:
                        break
            if num_actual_matches == num_required_matches:
                email_matched = True
            else:
            # If not matched, exit this rule
                continue

            # Now we see if the exceptions apply
            for match_check in rule.match_exceptions:
                if match_check is type(list):
                    pass
                else:
                    if (not (match_field(match_check.field_to_match) == email_to_validate[match_check.field_to_match])):
                        break
            else:
                email_matched = False
                email_excepted = True

            # If excepted, exit this rule
            if (email_excepted):
                continue

            # Now we know that it is matched and not excepted, so we perform actions
            # valid_actions = frozenset(['move_to_folder', 'forward', 'delete', 'mark_as_read', 'mark_as_unread'])

            for action_to_perform in rule.actions:
                if action_to_perform = "forward":
                    pass  # Forward
                if action_to_perform = "mark_as_read":
                    pass  # MaR
                if action_to_perform = "mark_as_unread":
                    pass  # MaU

            email_deleted_or_moved = False
            for action_to_perform in rule.actions:
                if action_to_perform = "move_to_folder":
                    email_deleted_or_moved = True
                    pass  # Move
                if action_to_perform = "Delete":
                    email_deleted_or_moved = True
                    pass  # Forward
                if (email_deleted_or_moved):
                    break  # Email gone now, no more actions

            if (email_deleted_or_moved):
                break  # Email gone now, no more rules




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

