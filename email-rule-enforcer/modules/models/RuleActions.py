from collections import OrderedDict
from modules.models.Counter import Counter
from modules.email.make_new_emails import new_email_forward
import modules.email.smtp_send as smtp_send


class Action():
    count = Counter()
    action_type = 'Action_Base_Type'
    _is_destructive = False
    _actually_perform_actions = True

    @classmethod
    def get_count(cls):
        return cls.count.get()

    @classmethod
    def incr_count(cls):
        return cls.count.incr()

    @classmethod
    def set_actually_perform_actions(cls, flag):
        cls._actually_perform_actions = flag

    @classmethod
    def actually_perform_actions(cls):
        return cls._actually_perform_actions

    def __init__(self, parent_rule_id=None):
        self.id = self.incr_count()
        self.parent_rule_id = parent_rule_id

    def set_parent_rule_id(self):
        self.parent_rule_id = parent_rule_id

    def perform_action(self, email_to_action, config, imap_connection, LogMaster):
        raise NotImplementedError('This is the base class for Action, no action possible')

    def is_destructive(self):
        return self._is_destructive

    def get_relevant_value(self):
        return "Action_Base_Type"

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        retval = OrderedDict()
        retval['id'] = self.id
        retval['parent_rule_id'] = self.parent_rule_id
        retval['is_destructive'] = self._is_destructive
        retval[self.action_type] = self.get_relevant_value()
        repr = '%s:(%s)' % (self.__class__.__name__, str(retval))
        return repr


class ActionForwardEmail(Action):
    action_type = 'ForwardEmail'
    _is_destructive = False

    def __init__(self, parent_rule_id=None):
        super().__init__(parent_rule_id)
        self.email_recipients = []

    def add_email_recipient(self, email_addr):
        self.email_recipients.append(email_addr)

    def get_relevant_value(self):
        return "Recipients = %s" % self.email_recipients

    def perform_action(self, email_to_action, config, imap_connection, LogMaster):
        LogMaster.info('Rule Action for Rule ID %s is a Forward, so now forwarding to: %s',
            self.parent_rule_id, self.email_recipients)
        LogMaster.ultra_debug('Now constructing a new email for Rule ID %s, to be sent From: %s',
            self.parent_rule_id, config['smtp_forward_from'])

        if (email_to_action.headers_only):
            raw_email = imap_connection.get_raw_email_byuid(email_to_action.uid)
        else:
            raw_email = email_to_action.original_raw_email
        email_to_attach = imap_connection.parse_raw_email(raw_email)

        email_to_forward = new_email_forward(
            email_from=config['smtp_forward_from'],
            email_to=self.email_recipients,
            subject='FWD: ' + email_to_action['subject'],
            bodytext="Forwarded Email Attached",
            email_to_attach=email_to_attach)

        LogMaster.insane_debug('Constructed email for Rule ID %s:\n%s', self.parent_rule_id, email_to_forward)

        if self.actually_perform_actions():
            smtp_send.send_email_from_config(config, email_to_forward)


class ActionMarkAsRead(Action):
    action_type = 'MarkAsRead'
    _is_destructive = False

    def __init__(self, parent_rule_id=None):
        super().__init__(parent_rule_id)

    def perform_action(self, email_to_action, config, imap_connection, LogMaster):
        LogMaster.info('Now Marking Email UID %s as Read', email_to_action.uid_str)
        if self.actually_perform_actions():
            imap_connection.mark_email_as_read_byuid(email_to_action.uid)

    def get_relevant_value(self):
        return "Mark as Read = True"


class ActionMarkAsUnread(Action):
    action_type = 'MarkAsUnread'
    _is_destructive = False

    def __init__(self, parent_rule_id=None):
        super().__init__(parent_rule_id)

    def perform_action(self, email_to_action, config, imap_connection, LogMaster):
        LogMaster.info('Now Marking Email UID %s as Unread', email_to_action.uid_str)
        if self.actually_perform_actions():
            imap_connection.mark_email_as_unread_byuid(email_to_action.uid)

    def get_relevant_value(self):
        return "Mark as Unread = True"


class ActionDelete(Action):
    action_type = 'Delete'
    _is_destructive = True

    def __init__(self, parent_rule_id=None):
        super().__init__(parent_rule_id)
        self.delete_permanently = False

    def set_delete_permanently(self, flag):
        self.delete_permanently = flag

    def perform_action(self, email_to_action, config, imap_connection, LogMaster):
        LogMaster.info('Now Deleting Email UID %s, permanently=%s', email_to_action.uid_str, self.delete_permanently)
        if self.actually_perform_actions():
            imap_connection.del_email(email_to_action.uid, self.delete_permanently)

    def get_relevant_value(self):
        return "Delete, delete_permanently = %s" % self.delete_permanently


class ActionMoveToNewFolder(Action):
    action_type = 'MoveToNewFolder'
    _is_destructive = True

    def __init__(self, parent_rule_id=None):
        super().__init__(parent_rule_id)
        self.dest_folder = ''
        self.mark_as_read_on_action = False

    def set_dest_folder(self, dest_folder):
        self.dest_folder = dest_folder

    def set_mark_as_read_on_move(self, flag):
        self.mark_as_read_on_move = flag

    def perform_action(self, email_to_action, config, imap_connection, LogMaster):
        LogMaster.info('Now Moving Email UID %s to folder %s', email_to_action.uid_str, self.dest_folder)
        if self.actually_perform_actions():
            imap_connection.move_email(
                uid=email_to_action.uid,
                dest_folder=self.dest_folder,
                mark_as_read_on_move=self.mark_as_read_on_move
            )

    def get_relevant_value(self):
        ret_val = "Dest Folder = %s\n" % self.dest_folder
        ret_val += "Mark as Read = %s" % self.mark_as_read_on_move
        return ret_val

