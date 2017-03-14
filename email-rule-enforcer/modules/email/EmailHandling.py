import email
import imaplib
from collections import namedtuple
from modules.logging import LogMaster
from modules.supportingfunctions import struct_time_to_datetime
from modules.supportingfunctions import convert_bytes_to_utf8
from modules.email.supportingfunctions_email import get_email_body, get_email_datetime, get_email_uniqueid
from modules.email.supportingfunctions_email import get_email_addrfield_from, get_email_addrfield_to, get_email_addrfield_cc


class RawEmailResponse(namedtuple('RawEmailResponse', ['raw_email_bytes', 'flags', 'size', 'server_date'])):
    def __new__(self, raw_email_bytes=None, flags=None, size=None, server_date=None):
        return super().__new__(self, raw_email_bytes, flags, size, server_date)


email_parser_Policy = email.policy.SMTP
email_Parser = email.parser.Parser(policy=email_parser_Policy)
email_HeaderParser = email.parser.Parser(policy=email_parser_Policy)


class ParsedEmailResponse():
    def __init__(self):
        self.original_raw_email = None
        self.size = None
        self.server_date = None
        self.imap_flags = None
        self.headers_only = None
        self.headers = None
        self.uid = None
        self.imap_folder = None
        self.date_datetime = None
        self.addr_from = None
        self.addr_to = None
        self.addr_cc = None
        self.is_read = None
        self.body = None
        self.unique_id = None
        self.email_db_id = None
        self.folder_db_id = None

    def init_from_imap(self, raw_email_response, headers_only, uid, imap_folder):

        self.original_email_str = convert_bytes_to_utf8(raw_email_response.raw_email_bytes)
        self.size = raw_email_response.size
        self.server_date = raw_email_response.server_date
        self.imap_flags = raw_email_response.flags
        self.headers_only = headers_only
        self.uid = int(convert_bytes_to_utf8(uid))
        self.imap_folder = imap_folder

        self.headers = parse_raw_email_header_from_str(raw_email_response)

        self.date_datetime = get_email_datetime(self.headers)
        self.addr_from = get_email_addrfield_from(self.headers)
        self.addr_to = get_email_addrfield_to(self.headers)
        self.addr_cc = get_email_addrfield_cc(self.headers)
        self.is_read = self.is_email_currently_read_fromflags(self.imap_flags)
        self.unique_id = get_email_uniqueid(self.headers, self.original_email_str)

        self.parsed_email = parse_raw_email_from_str(raw_email_response)
        self.body = get_email_body(self.parsed_email)


# Random note: create a new struct_time via time.localtime()

def parse_raw_email_from_response(raw_email_response):
    return parse_raw_email_from_bytes(raw_email_bytes=raw_email.raw_email_bytes)


def parse_raw_email_from_bytes(raw_email_bytes):
    return parse_raw_email_from_str(
        raw_email_str=convert_bytes_to_utf8(raw_email_bytes)
    )


def parse_raw_email_from_str(raw_email_str):
    ret_msg = email_Parser.parsestr(text=raw_email_str)
#    except email.errors.MessageError as e:
    return ret_msg


def parse_raw_email_header_from_str(raw_email_str):
    ret_msg = email_HeaderParser.parsestr(text=raw_email_str, headersonly=True)
    return ret_msg

