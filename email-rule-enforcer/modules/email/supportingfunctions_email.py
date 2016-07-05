from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.mime.text import MIMEText
from email.headerregistry import Address

# type: Address(display_name='', username='', domain='', addr_spec=None)
# sending: smtplib.SMTP().send_message(msg, from_addr=None, to_addrs=None, mail_options=[], rcpt_options=[])


def new_email_multipart(from_, to_, subject, bodytext, files_to_attach):
    # Create the container (outer) email message.
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = from_
    if type(to_, list):
        COMMASPACE = ', '
        _to = COMMASPACE.join(to_)
    else:
        _to = to_
    msg['To'] = _to

    body = MIMEText(bodytext)
    msg.attach(body)

    # Assume we know that the image files are all in Text format
    for file in files_to_attach:
        # Open the files in binary mode.  Let the MIMEText class automatically
        # guess the specific type.
        with open(file, 'rb') as fp:
            part = MIMEText(fp.read())
        msg.attach(part)

    return msg


def new_email_nonmultipart(from_, to_, subject, bodytext, cc=None, bcc=None):
    # Create the container (outer) email message.
    #msg = MIMENonMultipart()
    msg = MIMEText(bodytext)
    msg['Subject'] = subject
    msg['From'] = from_
    if type(to_, list):
        COMMASPACE = ', '
        _to = COMMASPACE.join(to_)
    else:
        _to = to_
    msg['To'] = _to

    return msg


def new_email(from_='', to_='', subject='', bodytext='', files_to_attach=None, cc=None, bcc=None):
    if files_to_attach is None:
        return new_email_nonmultipart(from_, to_, subject, bodytext, cc, bcc)
    else:
        return new_email_multipart(from_, to_, subject, bodytext, files_to_attach, cc, bcc)


