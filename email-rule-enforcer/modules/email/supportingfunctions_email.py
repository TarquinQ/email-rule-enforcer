import time
import datetime
import email.utils


def convert_emaildate_to_datetime(email_date_rfc2822):
    parsed_datetime = email.utils.parsedate_to_datetime(email_date_rfc2822)
    return parsed_datetime


def convert_emaildate_to_datetimestr(email_date_rfc2822):
    return convert_emaildate_to_datetime(email_date_rfc2822).isoformat(' ')


def convert_bytes_to_utf8(byte_thing):
    if isinstance(byte_thing, list):
        return [convert_bytes_to_utf8(a) for a in byte_thing]
    elif isinstance(byte_thing, bytes):
        return byte_thing.decode('utf-8', 'replace')
    else:
        return byte_thing


def get_email_datetime(email_message):
    parsed_datetime = None
    try:
        date_rfc2822 = email_message["Date"]
        parsed_datetime = convert_emaildate_to_datetime(date_rfc2822)
    except ValueError:
        pass
    return parsed_datetime


def get_relevant_email_headers_for_logging(email_message):
    def add_field_if_not_none(email_message, field, ret_list):
        if email_message[field] is not None:
            ret_list.append('%s: %s' % (field, email_message[field]))

    def add_attrib_if_not_none(email_message, attrib_name, attrib, ret_list):
        try:
            if email_message.__dict__[attrib] is not None:
                ret_list.append('%s: %s' % (attrib_name, email_message.__dict__[attrib]))
        except ValueError:
            pass

    ret_val = []
    add_attrib_if_not_none(email_message, 'IMAP UID', 'uid_str', ret_val)
    add_field_if_not_none(email_message, 'From', ret_val)
    add_field_if_not_none(email_message, 'To', ret_val)
    add_field_if_not_none(email_message, 'Cc', ret_val)
    add_field_if_not_none(email_message, 'Subject', ret_val)
    add_field_if_not_none(email_message, 'Date', ret_val)
    add_attrib_if_not_none(email_message, 'IMAP Flags', 'imap_flags', ret_val)
    return '\n'.join(ret_val)


def get_email_body(email_message):
    body = ""

    if email_message.is_multipart():
        for part in email_message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/plain' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break
    # not multipart - i.e. plain text, no attachments, keeping fingers crossed
    else:
        try:
            body = email_message.get_payload(decode=True)
        except Exception:
            try:
                body = email_message.get_payload(decode=True)
            except Exception:
                body = email_message.get_payload()

    body = convert_bytes_to_utf8(body)
    return body
