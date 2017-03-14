import time
import datetime
import email.utils
import hashlib


def convert_emaildate_to_datetime(email_date_rfc2822):
    parsed_datetime = email.utils.parsedate_to_datetime(email_date_rfc2822)
    return parsed_datetime


def convert_emaildate_to_datetimestr(email_date_rfc2822):
    return convert_emaildate_to_datetime(email_date_rfc2822).isoformat(' ')


def parse_email_address(email_str):
    return email.utils.parseaddr(email_str)


def get_email_uniqueid(parsed_message, raw_message):
    try:
        uniqueid = parsed_message["Message-ID"]
    except ValueError:
        uniqueid = None
    if uniqueid is None:
        try:
            uniqueid = hashlib.sha1(raw_message).hexdigest()
        except:
            pass
    return uniqueid


def get_email_datetime(email_message):
    parsed_datetime = None
    try:
        date_rfc2822 = email_message["Date"]
        parsed_datetime = convert_emaildate_to_datetime(date_rfc2822)
    except ValueError:
        pass
    return parsed_datetime


def get_email_addrfield_from(email_message):
    parsed_from = 'Unknown_Email'
    try:
        from_addr = email_message["From"]
        parsed_from = parse_email_address(from_addr)[1]
    except ValueError:
        pass
    return parsed_from


def get_email_addrfield_to(email_message):
    return parse_list_email_addrs(email_message, 'to')


def get_email_addrfield_cc(email_message):
    return parse_list_email_addrs(email_message, 'cc')


def parse_list_email_addrs(email_message, header_field):
    parsed_addrs = []
    raw_addrs = email_message.get_all(header_field, [])
    addr_tuples = email.utils.getaddresses(raw_addrs)
    for addr in addr_tuples:
        parsed_addrs += addr[1]
    return parsed_addrs


def get_extended_email_headers_for_logging(email_message):
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
    add_attrib_if_not_none(email_message, 'IMAP Folder', 'imap_folder', ret_val)
    add_field_if_not_none(email_message, 'From', ret_val)
    add_field_if_not_none(email_message, 'To', ret_val)
    add_field_if_not_none(email_message, 'Cc', ret_val)
    add_field_if_not_none(email_message, 'Subject', ret_val)
    add_field_if_not_none(email_message, 'Date', ret_val)
    add_attrib_if_not_none(email_message, 'IMAP Flags', 'imap_flags', ret_val)
    return '\n'.join(ret_val)


def get_basic_email_headers_for_logging(email_message):
    def add_field_if_not_none(email_message, field, ret_list):
        if email_message[field] is not None:
            ret_list.append('%s: %s' % (field, email_message[field]))

    ret_val = []
    add_field_if_not_none(email_message, 'From', ret_val)
    add_field_if_not_none(email_message, 'Date', ret_val)
    return '; '.join(ret_val)


def get_email_body_text(email_message):
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
                body = email_message.get_payload()
            except Exception:
                pass

    body = convert_bytes_to_utf8(body)
    return body


def get_email_body_html(email_message):
    body = ""

    if email_message.is_multipart():
        for part in email_message.walk():
            ctype = part.get_content_type()
            cdispo = str(part.get('Content-Disposition'))

            # skip any text/plain (txt) attachments
            if ctype == 'text/html' and 'attachment' not in cdispo:
                body = part.get_payload(decode=True)  # decode
                break

    body = convert_bytes_to_utf8(body)
    return body
