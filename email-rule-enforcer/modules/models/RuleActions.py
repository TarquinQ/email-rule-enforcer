from collections import OrderedDict
from modules.logging import LogMaster
from modules.models.Counter import Counter


class RuleAction():
    valid_actions = frozenset(['move_to_folder', 'forward', 'delete', 'mark_as_read', 'mark_as_unread'])
    count = Counter()

    @classmethod
    def get_count(cls):
        return cls.count.get()

    @classmethod
    def incr_count(cls):
        return cls.count.incr()

    def __init__(self, action_type, parent_rule_id=None):
        self.action_type = action_type
        self.id = self.incr_count()
        self.parent_rule_id = parent_rule_id
        self.delete_permanently = False
        self.mark_as_read_on_action = False
        self.mark_as_unread_on_action = False
        self.email_recipients = []
        self.dest_folder = ''

    def set_dest_folder(self, dest_folder):
        self.dest_folder = dest_folder

    def set_mark_as_read(self, mark_as_read):
        self.mark_as_read_on_action = mark_as_read

    def set_mark_as_unread(self, mark_as_unread):
        self.mark_as_unread_on_action = mark_as_unread

    def set_delete_permanently(self, flag):
        self.delete_permanently = flag

    def add_email_recipient(self, email_addr):
        self.email_recipients.append(email_addr)

    def get_relevant_value(self):
        ret_val = ""
        if self.action_type == 'forward':
            ret_val = "Recipients = %s" % self.email_recipients
        elif self.action_type == 'move_to_folder':
            ret_val = "Dest Folder = %s" % self.dest_folder
        elif self.action_type == 'delete':
            ret_val = "Delete, delete_permanently = %s" % self.delete_permanently
        elif self.action_type == 'mark_as_read':
            ret_val = "Mark as Read"
        elif self.action_type == 'mark_as_unread':
            ret_val = "Mark as Unread"
        return ret_val

    def validate(self):
        if self.action_type not in self.valid_actions:
            return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but only valid actions are: ' + str(valid_actions))

        if self.action_type == 'move_to_folder':
            check_for = 'dest_folder'
            try:
                self.dest_folder
            except NameError:
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but no value is set for suboption ' + check_for)

        if self.action_type == 'delete':
            if not insinstance('delete_permanently', bool):
                return (False, 'Action invalid. Action type "' + self.action_type + '" selected, but delete_permanently flag not boolean: set to ' + str(self.delete_permanently))

        if self.action_type == 'forward':
            check_for = 'email_recipient'
            try:
                if len(self.email_recipient) < 1:
                    return (False, 'Action invalid. Action type "' + self.action_type +
                        '" selected, but no forwarding email addresses have been added')
            except:
                    return (False, 'Action invalid. Action type "' + self.action_type +
                        '" selected, but no forwarding email addresses have been added')
        else:
            return (True, 'FIXME')

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['action_type'] = self.action_type
        retval['parent_rule_id'] = self.parent_rule_id
        retval['dest_folder'] = self.dest_folder
        retval['delete_permanently'] = self.delete_permanently
        retval['mark_as_read'] = self.mark_as_read_on_action
        retval['mark_as_unread'] = self.mark_as_unread_on_action
        retval['email_recipients'] = self.email_recipients
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


