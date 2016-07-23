from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.headerregistry import Address
from modules.logging import LogMaster

# type: Address(display_name='', username='', domain='', addr_spec=None)
# sending: smtplib.SMTP().send_message(msg, email_fromaddr=None, email_toaddrs=None, mail_options=[], rcpt_options=[])


def new_email_multipart(email_from, email_to, subject, bodytext, files_email_toattach):
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = email_from
    if type(email_to, list):
        COMMASPACE = ', '
        _to = COMMASPACE.join(email_to)
    else:
        _to = email_to
    msg['To'] = _to

    body = MIMEText(bodytext)
    msg.attach(body)

    # Assume we know that the image files are all in Text format
    for file in files_email_toattach:
        # Open the files in binary mode.  Let the MIMEText class automatically
        # guess the specific type.
        with open(file, 'rb') as fp:
            part = MIMEText(fp.read())
        msg.attach(part)

    return msg


def new_email_nonmultipart(email_from, email_to, subject, bodytext, cc=None, bcc=None):
    # Create the container (outer) email message.
    #msg = MIMENonMultipart()
    msg = MIMEText(bodytext)
    msg['Subject'] = subject
    msg['From'] = email_from
    if type(email_to, list):
        COMMASPACE = ', '
        _to = COMMASPACE.join(email_to)
    else:
        _to = email_to
    msg['To'] = _to

    return msg


def new_email(email_from='', email_to='', subject='', bodytext='', files_email_toattach=None, cc=None, bcc=None):
    if files_email_toattach is None:
        return new_email_nonmultipart(email_from, email_to, subject, bodytext, cc, bcc)
    else:
        return new_email_multipart(email_from, email_to, subject, bodytext, files_email_toattach, cc, bcc)


