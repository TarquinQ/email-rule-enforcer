import re
from collections import OrderedDict
from modules.logging import LogMaster
from modules.models.Counter import Counter
from modules.models.RuleMatches import MatchOr
import modules.models.tzinfo_UTC as tzinfo_UTC


class Rules(list):
    pass


class Rule():
    count = Counter()

    @classmethod
    def get_count(cls):
        return cls.count.get_count()

    @classmethod
    def incr_count(cls):
        return cls.count.incr()

    def __init__(self, rule_name=None):
        self.set_name(rule_name)
        self.id = self.incr_count()
        self.actions = []
        self.matches = []
        self.match_exceptions = []
        self.continue_rule_checks_if_matched = True
        self._now_adding_or = False
        self._now_adding_excep_or = False

    # Set Basic variables
    def set_name(self, rule_name):
        if rule_name is not None:
            self.name = str(rule_name)
        else:
            self.name = 'Rule_' + str(self.get_count())

    def add_action(self, action):
        action.parent_rule_id = self.id
        self.actions.append(action)

    def add_match(self, match):
        match.parent_rule_id = self.id
        if self._now_adding_or is True:
            self._temp_match_or.append(match)
        else:
            self.matches.append(match)

    def add_match_exception(self, match):
        match.parent_rule_id = self.id
        if self._now_adding_excep_or is True:
            self._temp_exception_or.append(match)
        else:
            self.match_exceptions.append(match)

    def set_continue_rule_checks_if_matched(self, flag):
        self.continue_rule_checks_if_matched = flag

    # Handle or-matches in the match setion
    def start_match_or(self):
        self._temp_match_or = MatchOr()
        self._now_adding_or = True

    def stop_match_or(self):
        self._now_adding_or = False
        self.matches.append(self._temp_match_or)
        del self._temp_match_or

    # Handle or-matches in the exception setion
    def start_exception_or(self):
        self._temp_exception_or = MatchOr()
        self._now_adding_excep_or = True

    def add_exception_or(self, match):
        match.parent_rule_id = self.id

    def stop_exception_or(self):
        self._now_adding_excep_or = False
        self.match_exceptions.append(self._temp_exception_or)
        del self._temp_exception_or

    # Basic property access
    def get_actions(self):
        return self.actions

    def get_matches(self):
        return self.matches

    def get_match_exceptions(self):
        return self.match_exceptions

    def get_continue_rule_checks_if_matched(self):
        return self.continue_rule_checks_if_matched

    # Validation
    def validate(self):
        if len(self.matches) == 0:
            return (False, 'Rule invalid: No matches for this rule. Rule id:' + str(self.id) + ', Name:' + self.name)
        if len(self.actions) == 0:
            return (False, 'Rule invalid: No actions for this rule. Rule id:' + str(self.id) + ', Name:' + self.name)
        return (True, 'Rule seems valid')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        retval = OrderedDict()
        retval['Name'] = self.name
        retval['ID'] = self.id
        retval['Matches'] = self.get_matches()
        retval['Exceptions'] = self.get_match_exceptions()
        retval['Actions'] = self.get_actions()
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr

