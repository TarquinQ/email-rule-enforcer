from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.message import MIMEMessage
from email.mime.text import MIMEText
from email.headerregistry import Address


def new_email_forward(email_from, email_to, subject, bodytext, email_to_attach, cc=None, bcc=None):
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email_from
    if isinstance(email_to, list):
        _to = ', '.join(email_to)
    else:
        _to = email_to
    msg['To'] = _to

    body = MIMEText(bodytext)
    attachment = MIMEMessage(email_to_attach)
    msg.attach(body)
    msg.attach(attachment)

    return msg


def new_email_nonmultipart(email_from, email_to, subject, bodytext, cc=None, bcc=None):
    # Create the container (outer) email message.
    msg = MIMEText(bodytext)
    msg['Subject'] = subject
    msg['From'] = email_from
    if isinstance(email_to, list):
        _to = ', '.join(email_to)
    else:
        _to = email_to
    msg['To'] = _to

    return msg

