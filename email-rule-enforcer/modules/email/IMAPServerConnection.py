import imaplib
import socket
import ssl
import email
import traceback
import threading
import time
import re
from collections import deque
from functools import wraps
from modules.logging import LogMaster
from modules.supportingfunctions import strip_quotes, dict_from_list, null_func
from modules.email.supportingfunctions_email import convert_bytes_to_utf8
from modules.email.supportingfunctions_email import get_email_body, get_email_datetime, get_email_uniqueid
from modules.email.supportingfunctions_email import get_email_addrfield_from, get_email_addrfield_to, get_email_addrfield_cc


class RawEmailResponse():
    def __init__(self, raw_email_bytes=None, flags=None, size=None, server_date=None):
        self.raw_email_bytes = raw_email_bytes
        self.size = size
        self.flags = flags
        self.server_date = server_date

    def __str__(self):
        ret_str = str(self.__class__.__name__)
        ret_str += ': Size {0}, Flags: {1}, ServerDate: {2}, raw_email:\n{3}'.format(
            self.size,
            self.flags,
            self.server_date,
            self.raw_email_bytes
        )
        return ret_str

    def __repr__(self):
        return self.__str__()


class IMAPServerConnection():
    re_statusresponse = re.compile('.*\((.*)\)')

    class LoginError(imaplib.IMAP4.error):
        pass

    class ConnectError(imaplib.IMAP4.error):
        pass

    def __init__(self):
        self.imap_connection = None
        self.imapmove_is_supported = False
        self._is_connected = False
        self._is_auth = False
        self.initial_folder = 'INBOX'
        self.deletions_folder = 'Trash'
        self.currfolder_name = ''
        self.server_io_lock = threading.RLock()
        self.perm_fail = False
        self.global_shutdown_evt = threading.Event()  # Placeholder event
        self._set_timeouts_and_maxfails()
        LogMaster.ultra_debug('New IMAP Server Connection object created')

    def _set_timeouts_and_maxfails(self):
        self.failed_logins = deque()
        self.reconnections_from_failure = deque()
        self.max_loginfails_10min = 2
        self.max_loginfails_24hrs = 8
        self.max_reconnectfails_10min = 4
        self.max_reconnectfails_24hrs = 24
        self.sleep_between_logins = 10  # seconds
        self.sleep_between_reconnects = 30  # seconds
        self.sleep_between_dis_re_connect = 2  # seconds
        self._sleep_reconnect_next = 0  # seconds

    def set_parameters_from_config(self, config):
        self.set_imaplib_Debuglevel(config['imap_imaplib_debuglevel'])
        self.username = config["imap_username"]
        self.password = config["imap_password"]
        self.server_name = config["imap_server_name"]
        self.server_port = config["imap_server_port"]
        self.use_ssl = config["imap_use_tls"]
        self.mark_as_read_on_move = config["mark_as_read_on_move"]
        self.empty_trash_on_exit = config["empty_trash_on_exit"]
        self.initial_folder = config["imap_initial_folder"]
        self.deletions_folder = config["imap_deletions_folder"]

    def _handle_imap_errors(func):
        @wraps(func)
        def wrapped(inst, *args, **kwargs):
            try:
                # this bit returns the _result_ of the instance method 'func', not the func_def itself
                with self.server_io_lock:
                    return func(inst, *args, **kwargs)
            except (imaplib.IMAP4.abort, socket.gaierror, TimeoutError, imaplib.IMAP4.error):
                return null_func(inst, *args, **kwargs)

        return wrapped

    def set_event_global_shutdown(self, evt):
        self.global_shutdown_evt = evt

    def connect(self):
        return self.connect_to_server()

    def is_connected(self):
        return self._is_connected

    def connect_to_server(self):
        if self._is_connected:
            LogMaster.info('Already connected to IMAP Server: %s', self.server_name)
            return True

        try:
            if self._connect_to_server():
                self._reset_sleeptime_failure()
                return True
        except self.LoginError:
            LogMaster.exception('Login Error: Login Failure when trying to connect to IMAP Server \"%s\"', self.server_name)
            self._register_failure_login()
        except TimeoutError:
            LogMaster.exception('Connection Error: Timeout when trying to connect to IMAP Server \"%s:%s\"', self.server_name, self.server_port)
            self._register_failure_reconnect()
        except socket.gaierror:
            LogMaster.exception('Connection Error: Invalid IMAP Server Hostname \"%s\"', self.server_name)
            self._register_failure_reconnect()
        except imaplib.IMAP4.error:
            LogMaster.exception('Connection Error: IMAP Error against Server: \"%s\"', self.server_name)
            self._register_failure_reconnect()
        finally:
            LogMaster.exception('IMAP Server Connect Failed. Trying again or exiting, depending on past failure count.')
            if self._allow_next_login() and (not self._is_connected):
                time.sleep(self.sleep_between_logins)
                self.connect_to_server()
            else:
                LogMaster.critical('IMAP Server has had too many login failures. Now exiting.')
                self.perm_fail = True

        self._check_imapmove_supported()
        self._fix_imaplib_maxline()
        return True

    def _connect_to_server(self):
        LogMaster.info('Now attempting to connect to IMAP Server: %s', self.server_name)
        with self.server_io_lock:
            # First we connect to the server. This can throw gaierror or TimeoutError
            if self.use_ssl:
                ssl_context = ssl.create_default_context()
                self.imap_connection = imaplib.IMAP4_SSL(self.server_name, self.server_port, ssl_context=ssl_context)
            else:
                self.imap_connection = imaplib.IMAP4(self.server_name, self.server_port)
            self._is_connected = True
            self._is_auth = False

            # Now we're connected, log in. This can throw (or raise) IMAP4.error
            result = self.imap_connection.login(self.username, self.password)
            if (result is None) or (not isinstance(result, tuple)) or (not result[0][0] != 'OK'):
                raise self.LoginError('IMAP Server Login Failed, exiting')
            else:
                self._is_auth = True
                LogMaster.critical('Successfully connected to IMAP Server: %s', self.server_name)

    def reconnect(self):
        self.disconnect()
        time.sleep(self.sleep_between_dis_re_connect)
        return self.connect()

    def reconnect_from_failure(self):
        self._register_failure_reconnect()
        self.global_shutdown_evt.wait(timeout=self._get_sleeptime_after_fail())
        if self.global_shutdown_evt.is_set():
            return False
        return self.reconnect()

    def _allow_next_login(self):
        check_10min = self._check_timed_failures(self.failed_logins, self.max_login_fails_10min, 600)
        check_24hrs = self._check_timed_failures(self.failed_logins, self.max_login_fails_24hrs, 86400)
        return check_10min and check_24hrs

    def _allow_next_reconnect(self):
        check_10min = self._check_timed_failures(self.reconnections_from_failure, self.max_reconnectfails_10min, 600)
        check_24hrs = self._check_timed_failures(self.reconnections_from_failure, self.max_reconnectfails_24hrs, 86400)
        return check_10min and check_24hrs

    def _register_failure_reconnect(self):
        max_age = 86400
        self._clean_timed_deque(self.reconnections_from_failure, max_age)
        self._add_failure_to_deque(self.reconnections_from_failure)

    def _register_failure_login(self):
        max_age = 86400
        self._clean_timed_deque(self.failed_logins, max_age)
        self._add_failure_to_deque(self.failed_logins)

    def _reset_sleeptime_failure(self):
        self._sleep_reconnect_next = 0

    def _get_sleeptime_after_fail(self):
        ret_sleep = self.sleep_reconnect_last
        self._sleep_reconnect_next = (self._sleep_reconnect_next + self.sleep_between_reconnects) * 3
        return ret_sleep

    @staticmethod
    def _clean_timed_deque(q, max_age):
        ''' Clean old time values out of deque.

        Queue must be values of (epoch-)seconds sorted in reverse chronological order. '''
        while q[-1] < max_age:
            q.pop()
        return q

    @staticmethod
    def _add_failure_to_deque(q):
        now_int = int(time.time())
        q.appendleft(now_int)

    @staticmethod
    def _check_timed_failures(q, max_failures, max_age):
        notfailed_yn = True
        now_int = int(time.time())
        max_failures = max_failures - 1
        if max_failures > len(q):
            max_failures = len(q)
        if now_int - q[max_failures] > max_age:
            notfailed_yn = False
        return notfailed_yn

    @staticmethod
    def _fix_imaplib_maxline():
        """This method hotfixes a bug in python's imaplib (also fixed in later mainline py3.4 and 3.5 releases)"""
        if imaplib._MAXLINE < 1000000:
            imaplib._MAXLINE = 10000000

    def connect_to_default_folder(self):
        return self.connect_to_folder(self.initial_folder)

    def connect_to_folder(self, folder_name):
        try:
            result = self.imap_connection.select(folder_name)
            msg_count = convert_bytes_to_utf8(result[1][0])
            self.currfolder_name = strip_quotes(folder_name)
            LogMaster.info('Successfully connected to IMAP Folder: \"%s\". Message Count: %s', folder_name, msg_count)
            return msg_count
        except imaplib.IMAP4.error:
            LogMaster.info('Failed to connect IMAP Folder: \"%s\". Returning -1 as msg_count.', folder_name)
            return -1

    def disconnect(self):
        try:
            self.imap_connection.logout()
        except Exception as e:
            LogMaster.exception('Error occured during IMAP logout, although this won\'t matter.')
        self._is_connected = False
        self._is_auth = False
        LogMaster.critical('Successfully disconnected from IMAP Server')
        return True

    def logout(self):
        return self.disconnect()

    def _check_imapmove_supported(self):
        self.imap_connection._get_capabilities()  # Refresh capabilities list
        if 'MOVE' in self.capabilities():
            # This monkey-patches the core imaplib for MOVE support
            imaplib.Commands['MOVE'] = ('SELECTED',)
            self.imapmove_is_supported = True
        else:
            self.imapmove_is_supported = False
        LogMaster.log(10, 'IMAP Command \"MOVE\" support now checked. Server Supports \"MOVE\"?: %s', self.imapmove_is_supported)

    def noop(self):
        # FIXME: Need to parse return codes and status here
        self.imap_connection.noop()

    def status(self, foldername=None):
        ret_data = None
        if foldername is None:
            foldername = self.currfolder_name
        response, data = self.imap_connection.status(foldername, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')
        # Response_data looks like ('OK', ['"Archive.2008" (MESSAGES 1 RECENT 0 UIDNEXT 2 UIDVALIDITY 1222003831 UNSEEN 0)'])
        if response == 'OK':
            ret_data = dict_to_list(re_statusresponse.match(data[0].split(' ')))
        return ret_data

    def get_currfolder(self):
        return self.currfolder_name

    def get_list_alluids_in_currfolder(self):
        """Searches and returns  a list of all uids in folder, byte-format"""
        result, data = self.imap_connection.uid('search', None, "ALL")
        list_allemails = data[0].split()
        LogMaster.log(10, 'List of all UIDs of emails in current folder: %s', convert_bytes_to_utf8(list_allemails))
        return list_allemails

    def get_emails_in_currfolder(self, headers_only=False):
        """Return parsed emails from the curent folder, without marking as read"""
        for uid in self.get_list_alluids_in_currfolder():
            yield self.get_parsed_email_byuid(uid, headers_only)

    @staticmethod
    def parse_flags(flags_raw):
        flags = []
        try:
            flags = [parsedflag.decode('utf-8') for parsedflag in imaplib.ParseFlags(flags_raw)]
        except Exception:
            pass
        return flags

    def get_imap_flags_byuid(self, uid):
        """Gets a list of flags in UTF-8 for a given uid"""
        flags = []
        try:
            result, flags_raw = self.imap_connection.uid('fetch', uid, '(FLAGS)')
        except imaplib.IMAP4.error:
            pass
        else:
            for flag in flags_raw:
                flags.extend(self.parse_flags(flag))
        return flags

    def get_all_folders(self):
        """Returns a list of all IMAP folders"""
        ret_list = [None]
        try:
            ret_list = self.imap_connection.list()[1]
        except Exception:
            pass
        return ret_list

    def get_raw_email_byuid(self, uid, headers_only=False):
        if headers_only:
            header_text = 'HEADER'
        else:
            header_text = ''
        data_to_fetch = '(RFC822.SIZE FLAGS INTERNALDATE BODY.PEEK[{0}])'.format(header_text)

        try:
            result, data = self.imap_connection.uid('fetch', uid, data_to_fetch)
        except imaplib.IMAP4.error as imap_error:
            result = 'NO'
            data = [None]  # I didn't make up this value: [None] can also emanate from imaplib responses.

        if (result == 'OK') and isinstance(data, list) and (data[0] is not None):
            response = data[0][0]
            raw_email_contents = data[0][1]
            email_size = 0
            email_flags = None
            server_date = None
            if isinstance(response, bytes):
                # Sample size_and_flags_response: b'1 RFC822.SIZE 9500 (FLAGS (\\Seen) BODY[HEADER] {1234}'
                response_utf8 = response.decode('utf-8', 'replace')
                tokens = response_utf8.split(' ')
                if len(tokens) > 3:
                    email_size = tokens[2]
                email_flags = self.parse_flags(response)
                server_date = imaplib.Internaldate2tuple(response)
            raw_email = RawEmailResponse(
                raw_email_bytes=raw_email_contents,
                flags=email_flags,
                size=email_size,
                server_date=server_date
            )
        else:
            raw_email = None
        return raw_email

    def get_raw_headers_byuid(self, uid):
        return self.get_raw_email_byuid(uid=uid, headers_only=True)

    def get_parsed_email_byuid(self, uid, headers_only=False):
        raw_email = self.get_raw_email_byuid(uid, headers_only)
        if raw_email is not None:
            try:
                parsed_email = self.parse_raw_email(raw_email.raw_email_bytes)
            except imaplib.IMAP4.error as parse_error:
                parsed_email = None
            else:
                parsed_email.original_raw_email = raw_email.raw_email_bytes
                parsed_email.size = raw_email.size
                parsed_email.server_date = raw_email.server_date
                parsed_email.headers_only = headers_only
                parsed_email.uid = uid
                parsed_email.uid_str = convert_bytes_to_utf8(uid)
                parsed_email.imap_folder = self.currfolder_name
                parsed_email.date_datetime = get_email_datetime(parsed_email)
                parsed_email.addr_from = get_email_addrfield_from(parsed_email)
                parsed_email.addr_to = get_email_addrfield_to(parsed_email)
                parsed_email.addr_cc = get_email_addrfield_cc(parsed_email)
                parsed_email.imap_flags = raw_email.flags
                parsed_email.is_read = self.is_email_currently_read_fromflags(parsed_email.imap_flags)
                parsed_email.body = get_email_body(parsed_email)
                parsed_email.unique_id = get_email_uniqueid(parsed_email, parsed_email.original_raw_email)
        else:
            parsed_email = None
        return parsed_email

    @staticmethod
    def parse_raw_email(raw_email):
        ret_msg = None
        if isinstance(raw_email, bytes):
            raw_email_bytes = raw_email
        elif isinstance(raw_email, RawEmailResponse):
            raw_email_bytes = raw_email.raw_email_bytes
        try:
            ret_msg = email.message_from_bytes(raw_email_bytes)
        except email.errors.MessageError as e:
            # This isn't /handling/ the error per se: it's just changing
            # it into an imaplib error to match the rest of this class
            raise imaplib.IMAP4.error('Error parsing raw email. Email Error was: %s' % e)
        return ret_msg

    def move_email(self, uid, dest_folder, mark_as_read_on_move=False):
        intial_read_status = self.is_email_currently_read_byuid(uid)
        this_func_marked_email_as_read = False

        if (mark_as_read_on_move is True) and (intial_read_status is False):
            self.mark_email_as_read_byuid(uid)
            this_func_marked_email_as_read = True
            LogMaster.log(10, 'Now Moving email to new folder with "mark_as_read" required, so now marking email as READ. Move Email UID: %s', uid)

        # Now we try the IMAP move
        try:
            if self.imapmove_is_supported:
                result, data = self.imap_connection.uid('MOVE', uid, dest_folder)
                LogMaster.log(20, 'Successfully moved email to new folder. UID: %s, Dest Folder: %s', uid, dest_folder)
            else:
                result, data = self.imap_connection.uid('COPY', uid, dest_folder)
                if result == 'OK':
                    self.del_email(uid)
                LogMaster.log(20, 'Successfully moved email to new folder. UID: %s, Dest Folder: %s', uid, dest_folder)
        except imaplib.IMAP4.error as e:
            LogMaster.log(30, 'Failed to move email (UID: %s)', uid)
            if (this_func_marked_email_as_read is True):
                # We need to unwind the Read status of any email that we may have marked as read
                LogMaster.log(30, 'We marked this email as READ earlier, now unmarking (UID: %s)', uid)
                self.mark_email_as_unread_byuid(uid)
            return False

        return True

    def del_email(self, uid, perm_delete=False):
        if perm_delete:
            result, data = self.set_flag_byuid(uid, '(\\Deleted)')
            self.expunge()
            LogMaster.log(20, 'Deleted email (permanently). UID: %s', uid)
        else:
            self.move_email(uid, self.deletions_folder, mark_as_read_on_move=False)
            LogMaster.log(20, 'Sent email to Deleted Items folder. UID: %s', uid)

    def is_email_currently_read_byuid(self, uid):
        return self.is_email_currently_read_fromflags(
            self.get_imap_flags_byuid(uid)
        )

    @staticmethod
    def is_email_currently_read_fromflags(flags):
        if '\\Seen' in flags:
            return True
        else:
            return False

    def set_flag_byuid(self, uid, flag):
        return self.uid_safe('STORE', uid, '+FLAGS', flag)

    def unset_flag_byuid(self, uid, flag):
        return self.uid_safe('STORE', uid, '-FLAGS', flag)

    def mark_email_as_read_byuid(self, uid):
        return self.set_flag_byuid(uid, '(\\Seen)')

    def mark_email_as_unread_byuid(self, uid):
        return self.unset_flag_byuid(uid, '(\\Seen)')

    def expunge(self):
        return self.imap_connection.expunge()

    def capabilities(self):
        return self.imap_connection.capabilities

    def uid(self, *args, **kwargs):
        """Straight IMAP UID command passthrough"""
        return self.imap_connection.uid(*args, **kwargs)

    def uid_safe(self, *args, **kwargs):
        """IMAP UID command wrapped safely"""
        try:
            result, data = self.imap_connection.uid(*args, **kwargs)
        except imaplib.IMAP4.error as imap_error:
            LogMaster.debug('ERROR: IMAP error occured during IMAP UID operation.', )
            LogMaster.debug('ERROR: IMAP Command args: %s', str(args))
            LogMaster.debug('ERROR: IMAP Command kwargs: %s', str(kwargs))
            LogMaster.debug('ERROR: IMAP error result was: %s', str(imap_error))
            LogMaster.exception('ERROR: Full trace')
            result = 'NO'
            data = [None]  # I didn't make up this value: [None] can also emanate from imaplib responses.
        return (result, data)

    @classmethod
    def set_imaplib_Debuglevel(cls, debuglevel):
        imaplib.Debug = debuglevel  # Default: 0; Range 0->5 zero->high
