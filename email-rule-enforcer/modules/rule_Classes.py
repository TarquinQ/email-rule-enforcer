class Rule():
    rule_count = 0

    @classmethod
    def get_rule_count(cls):
        return cls.rule_count

    def incr_rule_count(cls):
        cls.rule_count += 1

    def __init__(self, rule_name=None):
        self.incr_rule_count()
        self.rule_num = self.get_rule_count()
        self.id = self.get_rule_count()
        self.set_name(rule_name)
        self.actions = []
        self.matches = []
        self.match_exceptions = []
        self.continue_rule_checks_if_matched = True

    # Set Basic variables
    def set_name(self, name):
        if rule_name is not None:
            self.name = str(rule_name)
        else:
            self.name = 'Rule' + str(self.get_rule_count())

    def add_action(self, action):
        self.actions.append(action)

    def add_match(self, match):
        self.matches.append(match)

    def add_match_exception(self, match):
        self.match_exceptions.append(match)

    def set_continue_rule_checks_if_matched(self, flag):
        self.continue_rule_checks_if_matched = flag

    # Handle or-matches in the match setion
    def start_match_or(self):
        self._temp_match_or = []

    def add_match_or(self, match):
        self._temp_match_or.append(match)

    def stop_match_or(self):
        sel.matches.append(self._temp_match_or)
        del self._temp_match_or

    # Handle or-matches in the exception setion
    def start_exception_or(self):
        self._temp_exception_or = []

    def add_exception_or(self, match):
        self._temp_exception_or.append(match)

    def end_exception_or(self):
        sel.matches.append(self._temp_exception_or)
        del self._temp_exception_or

    # Basic property access
    def get_actions(self, action):
        return self.actions

    def get_matches(self, match):
        return self.matches

    def get_match_exceptions(self, match):
        return self.match_exceptions

    def get_continue_rule_checks_if_matched(self):
        return self.continue_rule_checks_if_matched

    # Validation
    def validate(self):
        if len(self.matches) = 0:
            return (False, 'Rule invalid: No matches for this rule. Rule id:' + str(self.id) + ', Name:' + self.name)
        if len(self.actions) = 0:
            return (False, 'Rule invalid: No actions for this rule. Rule id:' + str(self.id) + ', Name:' + self.name)
        for rule in self.actions:
            if not insinstance(rule, RuleAction)
        return (True, 'Rule seems valid')


class RuleAction():
    valid_actions = frozenset(['move_to_folder', 'forward', 'delete', 'mark_as_read', 'mark_as_unread'])

    def __init__(self, action_type):
        self.action_type = action_type
        self.delete_permanently = False
        self.mark_as_read = False
        self.mark_as_unread = False
        self.email_recipients = []

    def set_dest_folder(self, dest_folder):
        self.dest_folder = dest_folder

    def set_mark_as_read(self, mark_as_read):
        self.mark_as_read = mark_as_read

    def set_mark_as_unread(self, mark_as_unread):
        self.mark_as_unread = mark_as_unread

    def set_delete_permanently(self, flag):
        self.delete_permanently = flag

    def add_email_recipient(self, email_addr):
        self.email_recipients.append(email_addr)

    def validate(self):
        if self.action_type not in self.valid_actions:
            return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but only valid actions are: ' + str(valid_actions))

        if self.action_type = 'move_to_folder':
            check_for = 'dest_folder'
            try:
                self.dest_folder
            except NameError:
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but no value is set for suboption ' + check_for)

        if self.action_type = 'delete':
            if not insinstance('delete_permanently', bool):
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but delete_permanently flag not boolean: set to ' + str(self.delete_permanently))

        if self.action_type = 'forward':
            check_for = 'email_recipient'
            try:
                if len(self.email_recipient) < 1:
                    return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but no forwarding email addresses have been added')


class MatchField():
    match_types = frozenset(['starts_with', 'contains', 'ends_with', 'is'])
    match_fields = frozenset(['to', 'from', 'subject', 'cc', 'bcc', 'body'])

    def __init__(self, field_to_match=None, match_type=None, str_to_match=None, case_sensitive=False, parent_rule_id=None):
        self.field_to_match = None
        self.match_type = match_type
        self.str_to_match = str_to_match
        self.case_sensitive = case_sensitive
        self.parent_rule_id = parent_rule_id
        self.generate_re()

    def set_field_to_match(self, field_to_match):
        self.field_to_match = field_to_match
        self.generate_re()

    def set_match_type(self, match_type):
        self.match_type = match_type
        self.generate_re()

    def set_str_to_match(self, str_to_match):
        self.str_to_match = str_to_match
        self.generate_re()

    def set_match_is_case_sensitive(self, flag):
        self.case_sensitive = flag
        self.generate_re()

    def generate_re():
        if ((self.match_type in self.match_types) and (self.str_to_match is not None)):
            match_str = str(self.str_to_match)[:]
            if self.match_type = 'starts_with':
                match_str = match_str + '.*'
            if self.match_type = 'contains':
                match_str = '.*' + match_str + '.*'
            if self.match_type = 'ends_with':
                match_str = '.*' + match_str
            match_str = '^' + match_str + '$'  # Do I need this? I don't think so.
            self.matching_string = match_str
            flags = 0
            if not self.case_sensitive:
                flags = re.IGNORECASE
            self.re = re.compile(match_str, flags)

    def get_field_to_match(self):
        return self.field_to_match

    def get_match_type(self):
        return self.match_type

    def get_str_to_match(self):
        return self.str_to_match

    def get_case_sensitive(self):
        return self.case_sensitive

    def validate(self):
        if self.field_to_match not in self.match_fields:
            return (False, 'Field to match is invalid. Field type "' + self.field_to_match +
                '" selected, but only valid fields are: ' + str(match_fields))

        if self.match_type not in self.match_types:
            return (False, 'Match type is invalid. Field type "' + self.match_type +
                '" selected, but only valid fields are: ' + str(match_types))

        if self.str_to_match is None:
            return (False, 'Match invalid. Missing field value string. Trying to match field ' +
                self.field_to_match + '" selected, but no actual value is set for matching')

        if not insinstance(self.case_sensitive, bool):
            return (False, 'Match invalid. Case sensitivity should be boolean, but isnt. Trying to match: ' +
                self.action_type + '" selected, but delete_permanently flag not boolean: set to ' +
                str(self.delete_permanently))


