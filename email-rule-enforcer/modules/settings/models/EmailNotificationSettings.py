import re

class EmailNotificationSettings():
    def __init__(self, recipient=None, recipients=None, subject=None, body_prefix=None, attach_log=True):
        self.recipients = []
        if recipient:
            self.add_recipient(recipient)
        if recipients:
            for recipient in recipients:
                self.add_recipient(recipient)
        self.subject = subject
        self.body_prefix = body_prefix
        self.attach_log = attach_log

    def add_recipient(self, recipient_email):
        self.recipients.append(recipient_email)

    def set_subject(self, subject):
        self.subject = subject

    def set_body_prefix(self, prefix):
        self.body_prefix = prefix

    def set_attach_log(self, attach_yn):
        self.attach_log = attach_yn

    def validate(self):
        validate = true
        if ((len(recipients) == 0) or (not self.subject)):
            validate = false
            return None
        email_regex = re.compile(r'[^@]+@[^@]+\.[^@]+')
        for recipient in self.recipients:
            if not email_regex.match(recipient):
                validate = false
