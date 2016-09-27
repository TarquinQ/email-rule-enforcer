import re
import datetime
from collections import OrderedDict
from modules.logging import LogMaster
from modules.models.Counter import Counter
from modules.models.Singleton import Singleton
from modules.email.supportingfunctions_email import convert_emaildate_to_datetime
import modules.models.tzinfo_UTC as tzinfo_UTC


class MatchOr(list):
    def __repr__(self):
        return "MatchOr" + super(self.__class__, self).__repr__()

    def __str__(self):
        return "MatchOr" + super(self.__class__, self).__str__()


class MatchesCounter(Singleton):
    """Enables a global count of matches"""
    count = Counter()

    @classmethod
    def get(cls):
        return cls.count.get()

    @classmethod
    def incr(cls):
        return cls.count.incr()


class Match():
    count = MatchesCounter

    @classmethod
    def get_count(cls):
        return cls.count.get()

    @classmethod
    def incr_count(cls):
        return cls.count.incr()

    def __init__(self, field_to_match=None, match_type=None, value_to_match=None, name=None, parent_rule_id=None):
        self.id = self.incr_count()
        self.name = name
        self.set_field_to_match(field_to_match)
        self.set_match_type(match_type)
        self.set_value_to_match(value_to_match)
        self.parent_rule_id = parent_rule_id

    def set_field_to_match(self, field_to_match):
        if isinstance(field_to_match, str):
            self.field_to_match = field_to_match.lower()
        else:
            self.field_to_match = field_to_match

    def set_match_type(self, match_type):
        if isinstance(match_type, str):
            self.match_type = match_type.lower()
        else:
            self.match_type = match_type

    def set_value_to_match(self, value_to_match):
        self.value_to_match = value_to_match

    def get_field_to_match(self):
        return self.field_to_match

    def get_match_type(self):
        return self.match_type

    def get_value_to_match(self):
        return self.value_to_match

    def test_match_value(self, value):
        raise AttributeError('%s is Abstract Class, and should not be used in this manner' % (self.__class__.__name__))

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['name'] = self.name
        retval['field_to_match'] = self.field_to_match
        retval['match_type'] = self.match_type
        retval['value_to_match'] = self.value_to_match
        retval['parent_rule_id'] = self.parent_rule_id
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


class MatchHeader(Match):
    match_types = frozenset(['starts_with', 'contains', 'ends_with', 'is', 'regex'])

    def __init__(self, field_to_match=None, match_type=None, value_to_match=None, name=None, parent_rule_id=None, case_sensitive=False):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)
        self.set_case_sensitive(case_sensitive)
        self._generate_re()

    def set_field_to_match(self, field_to_match):
        super().set_field_to_match(field_to_match)
        self._generate_re()

    def set_match_type(self, match_type):
        super().set_match_type(match_type)
        self._generate_re()

    def set_value_to_match(self, value_to_match):
        super().set_value_to_match(value_to_match)
        self._generate_re()

    def set_case_sensitive(self, bool_flag):
        self.case_sensitive = bool_flag
        self._generate_re()

    def _generate_re(self):
        self.re = re.compile('This is a default value, never to be matched')
        try:
            if ((self.match_type in self.match_types) and (self.value_to_match is not None)):
                match_str = str(self.value_to_match)[:]
                if self.match_type == 'starts_with':
                    match_str = match_str + '.*'
                elif self.match_type == 'contains':
                    match_str = '.*' + match_str + '.*'
                elif self.match_type == 'ends_with':
                    match_str = '.*' + match_str
                elif self.match_type == 'regex':
                    match_str = match_str
                self.matching_string = match_str
                flags = re.DOTALL
                if not self.case_sensitive:
                    flags = flags | re.IGNORECASE
                self.re = re.compile(match_str, flags)
        except (AttributeError, TypeError):
            pass

    def test_match_value(self, str_value):
        matched_yn = False
        if self.re.match(str_value):
            matched_yn = True
        return matched_yn

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching a value to an email header. Email UID: %s, Header name \"%s\".',
            email_to_validate.uid_str, self.field_to_match)
        matched_yn = False
        try:
            str_to_test = email_to_validate[self.field_to_match]
            LogMaster.ultra_debug('Email Matching value is: \"%s\", to be matched against regexp: \"%s\"',
                str_to_test, self.re.pattern)
            if (self.test_match_value(str_to_test)):
                matched_yn = True
                LogMaster.ultra_debug('Header Matched: \"%s\"', str_to_test)
            else:
                LogMaster.ultra_debug('Header Not Matched: \"%s\"', str_to_test)
        except AttributeError:
            LogMaster.ultra_debug('Error: AttributeError incurred when testing Email UID: %s against Header %s.',
                email_to_validate.uid_str, self.field_to_match)

        return matched_yn

    def validate(self):
        if self.value_to_match is None:
            return (False, 'Match invalid. Missing Header value string. Trying to match value against Header ' +
                self.field_to_match + '" selected, but no actual value is set for matching')

        if not insinstance(self.case_sensitive, bool):
            return (False, 'Match invalid. Case sensitivity should be boolean, but isn\'t. Is set to %s',
                str(self.case_sensitive))

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['name'] = self.name
        retval['field_to_match'] = self.field_to_match
        retval['match_type'] = self.match_type
        retval['value_to_match'] = self.value_to_match
        retval['case_sensitive'] = self.case_sensitive
        retval['parent_rule_id'] = self.parent_rule_id
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


class MatchBody(MatchHeader):
    def __init__(self, field_to_match='body', match_type=None, value_to_match=None, name=None, parent_rule_id=None, case_sensitive=False):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id, case_sensitive)

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching a value to contents of an email body. Email UID: %s', email_to_validate.uid_str)
        matched_yn = False
        try:
            str_to_test = email_to_validate.body
            LogMaster.ultra_debug('Email Matching value is: \"%s\", To be matched against regexp: \"%s\"',
                str_to_test, self.re.pattern)
            if (self.test_match_value(str_to_test)):
                matched_yn = True
                LogMaster.ultra_debug('Body Matched: \"%s\"', str_to_test)
            else:
                LogMaster.ultra_debug('Body Not Matched: \"%s\"', str_to_test)
        except AttributeError:
            LogMaster.ultra_debug('Error: AttributeError incurred when testing Email UID: %s against contents of Body.',
                email_to_validate.uid_str)
        return matched_yn

    def validate(self):
        if self.value_to_match is None:
            return (False, 'Match invalid. Missing value string. Trying to match Body, but no actual value is set for matching')

        if not insinstance(self.case_sensitive, bool):
            return (False, 'Match invalid. Case sensitivity should be boolean, but isnt. Set to %s', self.case_sensitive)


class MatchFrom(MatchHeader):
    def __init__(self, field_to_match='from', match_type=None, value_to_match=None, name=None, parent_rule_id=None, case_sensitive=False):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id, case_sensitive)

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching a value to From Address of an email body. Email UID: %s', email_to_validate.uid_str)
        matched_yn = False
        try:
            str_to_test = email_to_validate.addr_from
            LogMaster.ultra_debug('Email matching value is: \"%s\", To be matched against regexp: \"%s\"',
                str_to_test, self.re.pattern)
            if (self.test_match_value(str_to_test)):
                matched_yn = True
                LogMaster.ultra_debug('From Address Matched: \"%s\"', str_to_test)
            else:
                LogMaster.ultra_debug('From Address Not Matched: \"%s\"', str_to_test)
        except AttributeError:
            LogMaster.ultra_debug('Error: AttributeError incurred when testing Email UID: %s against contents of From Address.',
                email_to_validate.uid_str)
        return matched_yn

    def validate(self):
        if self.value_to_match is None:
            return (False, 'Match invalid. Missing value string. Trying to match Body, but no actual value is set for matching')

        if not insinstance(self.case_sensitive, bool):
            return (False, 'Match invalid. Case sensitivity should be boolean, but isnt. Set to %s', self.case_sensitive)


class MatchDate(Match):
    match_types = frozenset(['older_than', 'newer_than'])

    def __init__(self, field_to_match='Date', match_type='older_than', value_to_match=datetime.datetime.min, name=None, parent_rule_id=None):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)
        self._ensure_sane_values()

    def _ensure_sane_values(self):
        """This makes sure that the config doesn't populate flawed or conflicting values here.
        This function should detect incorrect values, and reset to safe defaults
        that won't match if checked"""
        if self.match_type not in self.match_types:
            self._reset_to_safedefaults()
        elif not (isinstance(self.value_to_match, datetime.datetime) or
                  isinstance(self.value_to_match, datetime.timedelta)):
            self._reset_to_safedefaults()

    def _reset_to_safedefaults(self):
        self.match_type = 'newer_than'
        self.value_to_match = datetime.datetime.max
        self.relative_date = False

    def test_match_value(self, value):
        matched_yn = False
        if isinstance(self.value_to_match, datetime.timedelta):
            LogMaster.insane_debug('Date to be matched against is a timedelta: \"%s\"', self.value_to_match)
            date_to_match = datetime.datetime.now(tzinfo_UTC.utc) - self.value_to_match
            LogMaster.insane_debug('So we need to generate an appropriate fixed-date to test against, which is: %s', date_to_match)
        else:
            LogMaster.insane_debug('Date to be matched against is a fixed date: \"%s\"', self.value_to_match)
            date_to_match = self.value_to_match.replace(tzinfo=tzinfo_UTC.utc)

        if date_to_match > value:
            # The dervied return values from this if test might look backwards, but
            # remember that this test is from the point of the email, not this code.
            # "Is this email older_than a specific value?" Yes => True
            if self.match_type == 'older_than':
                matched_yn = True
            elif self.match_type == 'newer_than':
                matched_yn = False
        else:
            if self.match_type == 'older_than':
                matched_yn = False
            elif self.match_type == 'newer_than':
                matched_yn = True
        return matched_yn

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching a date value to an email field. Email UID: %s, field name \"%s\".', email_to_validate.uid_str, self.field_to_match)
        matched_yn = False
        datetime_to_check = None
        if self.field_to_match.lower() == 'date':
            try:
                datetime_to_check = email_to_validate.date_datetime
            except AttributeError:
                pass

        if (datetime_to_check is None):
            try:
                datetime_to_check = convert_emaildate_to_datetime(email_to_validate[self.field_to_match])
            except Exception:  # yeah, unpythonic bad practice, but I don't care
                pass

        if (datetime_to_check is None):
            datetime_to_check = datetime.datetime.max

        LogMaster.ultra_debug('Email Field value to be matched is: \"%s\", To be matched against date: \"%s\"',
            datetime_to_check, self.value_to_match)

        if (self.test_match_value(datetime_to_check)):
            matched_yn = True
            LogMaster.ultra_debug('Field Matched: \"%s\"', email_to_validate[self.field_to_match])
        else:
            LogMaster.ultra_debug('Field Not Matched: \"%s\"', email_to_validate[self.field_to_match])

        return matched_yn

    def validate(self):
        if self.field_to_match not in self.match_fields:
            return (False, 'Field to match is invalid. Field type "' + self.field_to_match +
                '" selected, but only valid fields are: ' + str(match_fields))

        if self.match_type not in self.match_types:
            return (False, 'Match type is invalid. Field type "' + self.match_type +
                '" selected, but only valid fields are: ' + str(match_types))

        if self.value_to_match is None:
            return (False, 'Match invalid. Missing field value string. Trying to match field ' +
                self.field_to_match + '" selected, but no actual value is set for matching')


class MatchSize(Match):
    match_types = frozenset(['greater_than', 'less_than'])

    def __init__(self, field_to_match='size', match_type='greater_than', value_to_match=2147483647, name=None, parent_rule_id=None):
        # 2147483647 is (2^32)-1, ie 2GB from bytes - plenty big for email comparison
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)
        self._ensure_sane_values()

    def _ensure_sane_values(self):
        """This makes sure that the config doesn't populate flawed or conflicting values here.
        This function should detect incorrect values, and reset to safe defaults
        that won't match if checked"""
        if self.match_type not in self.match_types:
            self._reset_to_safedefaults()
        elif not (isinstance(self.value_to_match, int)):
            self._reset_to_safedefaults()

    def _reset_to_safedefaults(self):
        self.match_type = 'greater_than'
        self.value_to_match = 2147483647

    def test_match_value(self, value):
        matched_yn = False

        if value is None:
            return False

        try:
            size_to_match = int(self.value_to_match)
            value = int(value)
        except ValueError as e:
            LogMaster.ultra_debug('ValueError raised during int conversion. Error: %s' % str(e))
        else:
            if value >= size_to_match:
                if self.match_type == 'greater_than':
                    matched_yn = True
                elif self.match_type == 'less_than':
                    matched_yn = False
            else:
                if self.match_type == 'greater_than':
                    matched_yn = False
                elif self.match_type == 'less_than':
                    matched_yn = True
            LogMaster.insane_debug('Size matching performed. Result: %s', matched_yn)
        return matched_yn

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching a size value to an email size. Email UID: %s', email_to_validate.uid_str)
        matched_yn = False
        try:
            size_to_check = email_to_validate.size
        except AttributeError:
            size_to_check = None

        LogMaster.ultra_debug('Email Size value to be matched is: %s, to see if it is %s the size of: %s bytes',
            size_to_check,
            self.match_type,
            self.value_to_match
            )

        if (self.test_match_value(size_to_check)):
            matched_yn = True
            LogMaster.ultra_debug('Size Matched.')
        else:
            LogMaster.ultra_debug('Size Not Matched.')

        return matched_yn

    def validate(self):
        if self.field_to_match not in self.match_fields:
            return (False, 'Field to match is invalid. Field type "' + self.field_to_match +
                '" selected, but only valid fields are: ' + str(match_fields))

        if self.match_type not in self.match_types:
            return (False, 'Match type is invalid. Match type "' + self.match_type +
                '" selected, but only valid matches are: ' + str(match_types))

        if self.value_to_match is None:
            return (False, 'Match invalid. Missing field value string. Trying to match field ' +
                self.field_to_match + '" selected, but no actual value is set for matching')


class MatchFolder(Match):
    match_types = frozenset(['starts_with', 'contains', 'ends_with', 'is'])

    def __init__(self, field_to_match='IMAP_Folder', match_type=None, value_to_match=None, name=None, parent_rule_id=None,
            case_sensitive=False, include_hierarchy=True):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)
        self.set_case_sensitive(case_sensitive)
        self.set_include_hierarchy(include_hierarchy)
        self._generate_re()

    def set_field_to_match(self, field_to_match):
        super().set_field_to_match(field_to_match)
        self._generate_re()

    def set_match_type(self, match_type):
        super().set_match_type(match_type)
        self._generate_re()

    def set_value_to_match(self, value_to_match):
        super().set_value_to_match(value_to_match)
        self._generate_re()

    def set_case_sensitive(self, bool_flag):
        self.case_sensitive = bool_flag
        self._generate_re()

    def set_include_hierarchy(self, bool_flag):
        self.include_hierarchy = bool_flag

    def _generate_re(self):
        self.re = re.compile('This is a default value, never to be matched')
        try:
            if ((self.match_type in self.match_types) and (self.value_to_match is not None)):
                match_str = str(self.value_to_match)[:]
                if self.match_type == 'starts_with':
                    match_str = match_str + '.*'
                if self.match_type == 'contains':
                    match_str = '.*' + match_str + '.*'
                if self.match_type == 'ends_with':
                    match_str = '.*' + match_str
                #match_str = '^' + match_str + '$'  # Do I need this? I don't think so.
                self.matching_string = match_str
                flags = re.DOTALL
                if not self.case_sensitive:
                    flags = flags | re.IGNORECASE
                self.re = re.compile(match_str, flags)
        except AttributeError:
            pass

    def test_match_value(self, str_value):
        matched_yn = False
        if self.re.match(str_value):
            matched_yn = True
        return matched_yn

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching a value to IMAP Folder Name. Email UID: %s.', email_to_validate.uid_str)
        matched_yn = False
        try:
            str_to_test = email_to_validate.imap_folder
            if (not self.include_hierarchy) and (str_to_test.find('/') >= 0):
                str_to_test = email_to_validate.imap_folder.split('/')[-1]
            LogMaster.ultra_debug('Email IMAP Folder value is: \"%s\", and final match-check-value will be: \"%s\"',
                email_to_validate.imap_folder, str_to_test)
            LogMaster.ultra_debug('Email Matching value is: \"%s\", To be matched against regexp: \"%s\"',
                str_to_test, self.re.pattern)
            if (self.test_match_value(str_to_test)):
                matched_yn = True
                LogMaster.ultra_debug('Folder Matched: \"%s\"', email_to_validate.imap_folder)
            else:
                LogMaster.ultra_debug('Folder Not Matched: \"%s\"', email_to_validate.imap_folder)
        except AttributeError:
            LogMaster.ultra_debug('Error: AttributeError incurred when testing Email UID: %s against IMAP Folder %s.',
                email_to_validate.uid_str, email_to_validate.imap_folder)

        return matched_yn

    def validate(self):
        if self.match_type not in self.match_types:
            return (False, 'Match type is invalid. Match type "' + self.match_type +
                '" selected, but only match fields are: ' + str(match_types))

        if self.value_to_match is None:
            return (False, 'Match invalid. Missing field value string. Trying to match field ' +
                self.field_to_match + '" selected, but no actual value is set for matching')

        if not insinstance(self.case_sensitive, bool):
            return (False, 'Match invalid. Case sensitivity should be boolean, but isnt. Trying to match: ' +
                self.action_type + '" selected, but delete_permanently flag not boolean: set to ' +
                str(self.delete_permanently))

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['name'] = self.name
        retval['field_to_match'] = self.field_to_match
        retval['match_type'] = self.match_type
        retval['value_to_match'] = self.value_to_match
        retval['case_sensitive'] = self.case_sensitive
        retval['include_hierarchy'] = self.include_hierarchy
        retval['parent_rule_id'] = self.parent_rule_id
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


class MatchFlag(Match):
    def __init__(self, field_to_match='IMAP_Flags', match_type=None, value_to_match=None, name=None, parent_rule_id=None):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)

    def set_value_to_match(self, value_to_match):
        if (str(value_to_match)[0] != '\\'):
            value_to_match = '\\' + str(value_to_match)
        super().set_value_to_match(value_to_match)
        self._generate_re()

    def test_match_value(self, imap_flags):
        matched_yn = False
        if self.value_to_match in imap_flags:
            matched_yn = True
        return matched_yn

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching on an IMAP Flag. Email UID: %s.', email_to_validate.uid_str)
        matched_yn = False
        try:
            LogMaster.ultra_debug('Email IMAP Flags are: \"%s\", To be matched against flag: \"%s\"',
                email_to_validate.imap_flags, self.value_to_match)
            if (self.test_match_value(email_to_validate.imap_flags)):
                matched_yn = True
                LogMaster.ultra_debug('Flag Matched: \"%s\"', self.value_to_match)
            else:
                LogMaster.ultra_debug('Flag Not Matched: \"%s\"', self.value_to_match)
        except AttributeError:
            LogMaster.ultra_debug('Error: AttributeError incurred when testing Email UID: %s against IMAP Flags %s.',
                email_to_validate.uid_str, email_to_validate.imap_flags)

        return matched_yn

    def validate(self):
        if self.value_to_match is None:
            return (False, 'Match invalid. Missing field value string. Trying to match field ' +
                self.field_to_match + '" selected, but no actual value is set for matching')

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['name'] = self.name
        retval['field_to_match'] = self.field_to_match
        retval['match_type'] = self.match_type
        retval['value_to_match'] = self.value_to_match
        retval['parent_rule_id'] = self.parent_rule_id
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


class MatchIsUnread(Match):
    def __init__(self, field_to_match='IMAP_Flag_Unread', match_type='is', value_to_match='unread', name=None, parent_rule_id=None):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)

    def test_match_value(self, is_read_flag):
        return (not is_read_flag)

    def test_match_email(self, email_to_validate):
        LogMaster.ultra_debug('Now matching on an IMAP Unread flag. Email UID: %s.', email_to_validate.uid_str)
        matched_yn = False
        try:
            LogMaster.ultra_debug('Email \'Read\' flag is set to : \"%s\"',
                email_to_validate.is_read)
            if (self.test_match_value(email_to_validate.is_read)):
                matched_yn = True
                LogMaster.ultra_debug('Unread Matched')
            else:
                LogMaster.ultra_debug('Unread Not Matched (ie read!).')
        except AttributeError:
            LogMaster.ultra_debug('Error: AttributeError incurred when testing Email UID: %s against Read Flag %s.',
                email_to_validate.uid_str, email_to_validate.is_read)

        return matched_yn

    def validate(self):
        return True

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['name'] = self.name
        retval['field_to_match'] = self.field_to_match
        retval['match_type'] = self.match_type
        retval['value_to_match'] = self.value_to_match
        retval['parent_rule_id'] = self.parent_rule_id
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


class MatchIsRead(MatchIsUnread):
    def __init__(self, field_to_match='IMAP_Flag_Read', match_type='is', value_to_match='read', name=None, parent_rule_id=None):
        super().__init__(field_to_match, match_type, value_to_match, name, parent_rule_id)

    def test_match_value(self, is_read_flag):
        return (is_read_flag)

