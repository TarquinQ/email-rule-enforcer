import imaplib
import socket
import ssl
import email
import traceback
import time
import re
import datetime
from collections import deque, namedtuple
from functools import wraps
from modules.logging import LogMaster
from modules.supportingfunctions import strip_quotes, dict_from_list, null_func, is_list_like, struct_time_to_datetime
from modules.supportingfunctions import convert_bytes_to_utf8
from modules.email.supportingfunctions_email import get_email_body, get_email_datetime, get_email_uniqueid
from modules.email.supportingfunctions_email import get_email_addrfield_from, get_email_addrfield_to, get_email_addrfield_cc
from modules.email.EmailHandling import RawEmailResponse


def fix_imaplib_maxline():
    """This method hotfixes a "bug" in python's imaplib (also fixed in later mainline py3.4 and 3.5 releases)"""
    if imaplib._MAXLINE < 1000000:
        imaplib._MAXLINE = 10000000

fix_imaplib_maxline()


class IMAPServerConnection():
    '''
    A Class to handle IMAP Connections, at a higher-level than imaplib.

    This class implements a lot of high-level functionality over the top of python's imaplib.
    imaplib is extremely low-level - this class adapts the imaplib, manages state,
    handles errors and reconnections, and presents results as standard python datatypes.
    '''

    ## Class Exceptions

    class PermanentFailure(Exception):
        pass

    ## Initialisation Code

    def __init__(self):
        self.imap_connection = None
        self.imapmove_is_supported = False
        self._is_connected = False
        self._is_auth = False
        self.initial_folder = 'INBOX'
        self.deletions_folder = 'Trash'
        self.currfolder_name = ''
        self._set_timeouts_and_maxfails()
        LogMaster.ultra_debug('New IMAP Server Connection object created')

    def _set_timeouts_and_maxfails(self):
        self.failed_logins = deque()
        self.reconnections_from_failure = deque()
        self.max_loginfails_10min = 3
        self.max_loginfails_24hrs = 8
        self.max_reconnectfails_10min = 4
        self.max_reconnectfails_24hrs = 24
        self.sleep_between_logins = 20  # seconds
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

    ## Abstracted Error Handling.
    #
    # This section allows IMAP and connection errors to be handled for each and every
    # interaction across the network between server and client. Network errors will result in
    # reconenction attempts, and IMAP errors will result in a standard return of None.

    def _handle_imap_errors(func):
        """This will handle common IMAP errors, and return None instead.

        This wrapper obviates the need to handle individual IMAP errors each time
        we access the server. This wrapper simply throws away the error and returns
        None - this is designed for a common scenario when the result is unimportant
        (eg FETCH an email) and not when the error should be hanldled in a specific
        way (such as login errors).

        This wrapper function can only handle bound instance-methods, and cannot cope
        with @classmethod or @instancemethod. This is due to the 'inst' parameter, which
        is equivalent to 'self' for a bound instance method."""

        @wraps(func)
        def wrapped(inst, *args, **kwargs):
            def print_IMAP_Exception():
                LogMaster.warning('ERROR: IMAP error occured during IMAP operation.', )
                LogMaster.warning('ERROR: We wil handle the gracefully, but display a full diagnostic here.', )
                LogMaster.warning('ERROR: IMAP Command args were: %s', str(args))
                LogMaster.warning('ERROR: IMAP Command kwargs were: %s', str(kwargs))
                LogMaster.exception('ERROR: Full diagnostic trace:\n')

            try:
                # this bit returns the _result_ of the instance method 'func', not the func itself
                return func(inst, *args, **kwargs)
            except imaplib.IMAP4.error as e:
                print_IMAP_Exception()
                return None
            except (imaplib.IMAP4.abort, socket.gaierror, TimeoutError):
                LogMaster.exception('IMAP Connection Error occurred, now attempting to reconnect to server and retry operation.')
                try:
                    reconnect = inst._reconnect_from_failure()  # This step may reconnect several times
                    if reconnect is True:
                        return func(inst, *args, **kwargs)
                except imaplib.IMAP4.error:
                    print_IMAP_Exception()
                    return None
                except (imaplib.IMAP4.abort, socket.gaierror, TimeoutError):
                    LogMaster.exception('Permanent IMAP Connection Failure occurred, now closing.')
                    raise inst.PermanentFailure('Permanent IMAP Connection Failure occurred, now closing.')
                else:
                    raise inst.PermanentFailure('Permanent IMAP Connection Failure occurred, now closing.')
        return wrapped

    ## Connection-State Change Code.
    #
    # All code in this section deals with changing State in the client/server connection.
    # This includes initiation, reconnection, Auth and Selection (folder selection).
    # All functions should return True, False (or None for Errors).

    def connect(self):
        return self.connect_to_server()

    def is_connected(self):
        return self._is_connected

    def connect_to_server(self):
        if self._is_connected:
            LogMaster.info('IMAP Connection requestion, but already connected to IMAP Server: %s', self.server_name)
            return True

        try:
            if self._connect_to_server():
                if self._login():
                    self._reset_sleeptime_failure()
                    self._check_imapmove_supported()
                    return True
            return False

        except TimeoutError:
            LogMaster.exception('Connection Error: Timeout when trying to connect to IMAP Server \"%s:%s\"', self.server_name, self.server_port)
            self._reconnect_from_failure()

        except socket.gaierror:
            LogMaster.exception('Connection Error: Invalid IMAP Server Hostname \"%s\"', self.server_name)
            self._reconnect_from_failure()

        except imaplib.IMAP4.error:
            LogMaster.exception('Connection Error: IMAP Error against Server: \"%s\"', self.server_name)
            self._reconnect_from_failure()

    def _connect_to_server(self):
        LogMaster.info('Now attempting to connect to IMAP Server: %s', self.server_name)
        # First we connect to the server. This can throw gaierror or TimeoutError
        if self.use_ssl:
            ssl_context = ssl.create_default_context()
            self.imap_connection = imaplib.IMAP4_SSL(self.server_name, self.server_port, ssl_context=ssl_context)
        else:
            self.imap_connection = imaplib.IMAP4(self.server_name, self.server_port)
        self._is_connected = True
        self._is_auth = False
        return True  # We either succeed here, or throw an Exception in earlier lines

    def _login(self):
        ret_val = False
        result = None
        try:
            LogMaster.info('Now atttempting IMAP login using username: \"%s\"', self.username)
            result, data = self.imap_connection.login(self.username, self.password)
            print ('Login Result:', result)
        except imaplib.IMAP4.error:
            LogMaster.exception('Connection Error: IMAP Login Failure using username: \"%s\"', self.username)
            self._retry_login()

        if (result is None) or (result != 'OK'):
            LogMaster.critical('Connection Error: IMAP Login Failure using username: \"%s\"', self.username)
            self._retry_login()
        else:
            self._is_auth = True
            LogMaster.critical('Successfully connected to IMAP Server: %s', self.server_name)
            ret_val = True
        return ret_val

    def _retry_login(self):
        self._register_failure_login()
        LogMaster.info('IMAP Login Failure occurred. Now sleeping for %s seconds, then retrying login using username: \"%s\"',
            self.sleep_between_logins, self.username)
        time.sleep(self.sleep_between_logins)
        if self._allow_next_login():
            self._login()
        else:
            LogMaster.critical('Failure: Too many IMAP Login Failures using username: \"%s\"', self.username)
            raise self.PermanentFailure('Failure: Too many IMAP Login Failures using username: \"%s\"' % self.username)

    def reconnect(self):
        self.disconnect()
        time.sleep(self.sleep_between_dis_re_connect)
        return self.connect()

    def _reconnect_from_failure(self):
        self._register_failure_reconnect()
        time.sleep(self._get_sleeptime_after_fail())
        if self._allow_next_reconnect():
            return self.reconnect()
        else:
            raise self.PermanentFailure('IMAP Connection Failure: too many failed reconnection attempts, Now exiting.')

    def _allow_next_login(self):
        allow_10min = not self._timed_failures_exceeded(self.failed_logins, self.max_loginfails_10min, 600)
        allow_24hrs = not self._timed_failures_exceeded(self.failed_logins, self.max_loginfails_24hrs, 86400)
        return allow_10min and allow_24hrs

    def _allow_next_reconnect(self):
        allow_10min = not self._timed_failures_exceeded(self.reconnections_from_failure, self.max_reconnectfails_10min, 600)
        allow_24hrs = not self._timed_failures_exceeded(self.reconnections_from_failure, self.max_reconnectfails_24hrs, 86400)
        return allow_10min and allow_24hrs

    def _register_failure_reconnect(self):
        max_age = 86400
        self._add_timestamp_to_deque(self.reconnections_from_failure)
        self._clean_timed_deque(self.reconnections_from_failure, max_age)

    def _register_failure_login(self):
        max_age = 86400
        self._add_timestamp_to_deque(self.failed_logins)
        self._clean_timed_deque(self.failed_logins, max_age)

    def _reset_sleeptime_failure(self):
        self._sleep_reconnect_next = 0

    def _get_sleeptime_after_fail(self):
        """This will allow an increasing amount of sleep time between reconnection attempts"""
        ret_sleep = self._sleep_reconnect_next
        self._sleep_reconnect_next = (self._sleep_reconnect_next + self.sleep_between_reconnects) * 3
        return ret_sleep

    def disconnect(self):
        try:
            self.imap_connection.logout()
        except Exception as e:
            LogMaster.warning('Error occured during IMAP logout, although this won\'t matter.')
        self._is_connected = False
        self._is_auth = False
        LogMaster.critical('Successfully disconnected from IMAP Server')
        return True

    def logout(self):
        return self.disconnect()

    def connect_to_default_folder(self):
        return self.connect_to_folder(self.initial_folder)

    @_handle_imap_errors
    def connect_to_folder(self, folder_name):
        folder_name = strip_quotes(folder_name)
        if folder_name.find(' ') != -1:
            folder_name = '"%s"' % folder_name
        result, data = self.imap_connection.select(folder_name)
        if (result is None) or (result != 'OK'):
            return None
        else:
            msg_count = convert_bytes_to_utf8(data[0])
            self.currfolder_name = folder_name
            LogMaster.info('Successfully connected to IMAP Folder: \"%s\". Message Count: %s', folder_name, msg_count)
            return msg_count

    @_handle_imap_errors
    def _check_imapmove_supported(self):
        self.imap_connection._get_capabilities()  # Refresh capabilities list
        if 'MOVE' in self.capabilities():
            # This monkey-patches the core imaplib for MOVE support
            imaplib.Commands['MOVE'] = ('SELECTED',)
            self.imapmove_is_supported = True
        else:
            self.imapmove_is_supported = False
        LogMaster.log(10, 'IMAP Command \"MOVE\" support now checked. Server Supports \"MOVE\"?: %s', self.imapmove_is_supported)

    @_handle_imap_errors
    def noop(self):
        try:
            ret_val = self.imap_connection.noop()
        except TypeError:
            # Ok, this is quite crap. A bug in imaplib itself! Issue detailed here: https://bugs.python.org/msg261615
            # This acts a keepalive, to workaround lack of noop()
            ret_val = self._check_imapmove_supported()
        return True

    ## Data Request Functions
    #
    # These functions request/send data from the server, and receive the results.
    # These functions should return either None or data.
    # The data returned should primarily be either a Message object, a dictionary or an array.
    # Where possible, returned data should be converted to utf8 prior to return.
    # All data should be validated on the way in to each function to reduce IMAP connection errors.
    #
    # In general, error handling should be abstracted away from each method, and handled by
    # the @_handle_imap_errors decorator. This should ensure that any IMAP errors result in a return of None,
    # and any connection errors result in controlled connection retry attempts.
    # In general, no Exceptions other than PermanentFailure should emerge from these methods.

    @_handle_imap_errors
    def status(self, folder_name=None):
        '''Gets the IMAP Status of a given Folder. Is one of the few IMAP methods that does not require Folder Select'''
        ret_data = None
        if folder_name is None:
            folder_name = self.currfolder_name
        else:
            folder_name = strip_quotes(folder_name)
        if folder_name.find(' ') != -1:
            folder_name = '"%s"' % folder_name

        response, data = self.imap_connection.status(folder_name, '(MESSAGES RECENT UIDNEXT UIDVALIDITY UNSEEN)')
        # Response, data looks like ('OK', ['"Archive 2008" (MESSAGES 1 RECENT 0 UIDNEXT 2 UIDVALIDITY 1222003831 UNSEEN 0)'])
        if response == 'OK':
            data_utf8 = convert_bytes_to_utf8(data[0])
            try:
                extracted_data = re.search('.*\((.*)\)', data_utf8).group(1)
                ret_data = dict_from_list(extracted_data.split(' '))
            except AttributeError:  # brackets are missing in data[0], so no group(1)
                pass
        return ret_data

    def get_currfolder(self):
        return self.currfolder_name

    @_handle_imap_errors
    def get_uids_in_currfolder(self, start=0, end='*'):
        """Searches and returns a list of uids in folder, byte-format"""
        if (start == 0) and (end == '*'):
            data_to_fetch = 'ALL'
        else:
            data_to_fetch = "UID {0}:{1}".format(start, end)

        data = self.parse_results_and_data(
            output_from_imap=self.imap_connection.uid('search', None, data_to_fetch),
            _convert_utf8=True
        )
        if data is not None:
            list_uids = [int(i) for i in data[0].split()]
            LogMaster.log(10, 'Range of UIDs of emails in current folder. \
                Start: {0}, End: {1}, List in range: {2}'.format(start, end, list_uids)
            )
        else:
            list_uids = []
#        import pdb; pdb.set_trace()
        return list_uids

    def get_emails_in_currfolder(self, headers_only=False, start=0, end='*'):
        """Return parsed emails from the curent folder, without marking as read"""
        for uid in self.get_uids_in_currfolder(start, end):
            yield self.get_parsed_email_byuid(uid, headers_only)

    def get_emails_in_currfolder_in_uidset(self, uid_set, headers_only=False):
        """
        Return parsed emails from the curent folder in the uid_set

        uid_set can be a list, set, tuple, or similar iterable grouping.
        """
        for uid in uid_set:
            yield self.get_parsed_email_byuid(uid, headers_only)

    @_handle_imap_errors
    def get_imap_flags_byuid(self, uid):
        """Gets a list of flags in UTF-8 for a given uid"""
        flags = []
        try:
            result, flags_raw = self.imap_connection.uid('fetch', uid, '(FLAGS)')
        except imaplib.IMAP4.error:
            pass
        else:
            if result == 'OK':
                for flag in flags_raw:
                    flags.extend(self.parse_flags(flag))
        return flags

    @_handle_imap_errors
    def get_all_folders(self):
        """Returns a list of all IMAP folders"""
        ret_list = []
        try:
            result, data = self.imap_connection.list()
            if result == 'OK':
                ret_list = convert_bytes_to_utf8(data)
        except Exception:
            pass
        return ret_list

    def get_all_folders_parsed(self):
        """Returns a list of all IMAP folders in array format"""
        ret_list = []
        for folder_record in self.get_all_folders():
            # folder_record looks like:  '(\All \HasNoChildren) "/" "[Gmail]/All Mail"''
            try:
                folder_path = re.search('.*\".*\" \"(.*)\".*', folder_record).group(1)
                folder_path = strip_quotes(folder_path.strip())
                ret_list.append(folder_path)
            except AttributeError:
                pass
        return ret_list

    @_handle_imap_errors
    def get_raw_email_byuid(self, uid, headers_only=False):
        if headers_only:
            header_text = 'HEADER'
        else:
            header_text = ''
        data_to_fetch = '(RFC822.SIZE FLAGS INTERNALDATE BODY.PEEK[{0}])'.format(header_text)

        data = self.uid_execute_and_parse('fetch', uid, data_to_fetch, _convert_utf8=False)

        if (data is not None):
            try:
                response = data[0][0]
                raw_email_contents = data[0][1]
                email_flags = None
                server_date = None
                if isinstance(response, bytes):
                    # Sample size_and_flags_response: b'1 RFC822.SIZE 9500 (FLAGS (\\Seen) BODY[HEADER] {1234}'
                    response_utf8 = convert_bytes_to_utf8(response)
                    try:
                        email_size = int(re.search('.*SIZE (\d) .*', response_utf8).group(1))
                    except AttributeError:
                        email_size = 0
                    email_flags = self.parse_flags(response)
                    server_date = self.parse_imap_internaldate(response)
                raw_email = RawEmailResponse(
                    raw_email_bytes=raw_email_contents,
                    flags=email_flags,
                    size=email_size,
                    server_date=server_date
                )
            except (IndexError, TypeError):
                raw_email = None
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
                parsed_email.uid = int(convert_bytes_to_utf8(uid))
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

    @_handle_imap_errors
    def get_MessageID_byuid(self, uid):
        data_to_fetch = '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])'
        result = dict()

        data = self.uid_execute_and_parse('fetch', uid, data_to_fetch, _convert_utf8=True)

        if (data is not None):
            # Now we parse data in reverse-order
            while len(data) > 0:
                unparsed = data.pop()
                # unparsed is a tuple that looks like:
                # ('38 (UID 85 BODY[HEADER.FIELDS (MESSAGE-ID)] {98}', \
                #    'Message-ID: <01000158cf076519-165f9a3e-e56e-4817-8c5b-96e1165ed919-000000@email.com>\r\n\r\n')
                unparsed_serverdata = unparsed[0]
                unparsed_msgdata = unparsed[1]
                try:
                    UID = re.search('.* \(UID (.*) .*', unparsed_serverdata).group(1)
                    MessageID = re.search('.*\<(.*)\>.*', unparsed_msgdata).group(1)
                    result[UID] = MessageID
                    print('UID, MessageID: %s, %s' % (UID, MessageID))
                except AttributeError:  # brackets are missing in data[0], so no group(1)
                    pass
            print('Final Result:', result)
        return result

    @_handle_imap_errors
    def minimum_foldersync_data(self, uid_set):
        """Return the smallest amount of data required to sync a folder"""
        data_to_fetch = '(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)] FLAGS INTERNALDATE)'
        result = dict()
        response_tuple = namedtuple('IMAP_FolderSyncData', ['messageid', 'seen', 'flags', 'server_date'])

        data = self.uid_execute_and_parse('fetch', uid_set, data_to_fetch, _convert_utf8=False)

        if (data is not None):
            # Now we parse data in reverse-order
            while len(data) > 0:
                unparsed = data.pop()
                # unparsed is a tuple that looks like:
                # (b'38 (UID 85 BODY[HEADER.FIELDS (MESSAGE-ID)] {98}', \
                #    b'Message-ID: <01000158cf076519-165f9a3e-e56e-4817-8c5b-96e1165ed919-000000@email.com>\r\n\r\n')
                unparsed_serverdata = unparsed[0]
                unparsed_serverdata_utf8 = convert_bytes_to_utf8(unparsed[0])
                unparsed_msgdata = convert_bytes_to_utf8(unparsed[1])
                try:
                    UID = re.search('.* \(UID ([0-9]+) .*', unparsed_serverdata_utf8).group(1)
                    messageid = re.search('.*\<(.*)\>.*',
                        convert_bytes_to_utf8(unparsed_msgdata)
                    ).group(1)
                    flags = self.parse_flags(unparsed_serverdata)
                    seen = self.is_email_currently_read_fromflags(flags)
                    server_date = self.parse_imap_internaldate(unparsed_serverdata)
                    result[UID] = response_tuple(messageid, seen, flags, server_date)
                    print('UID, result_tuple: %s, %s' % (UID, result[UID]))
                except AttributeError:  # brackets are missing in data[0], so no group(1)
                    pass
            print('Final Result:', result)
        return result

    @_handle_imap_errors
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
                if result == 'OK':
                    LogMaster.log(20, 'Successfully moved email to new folder. UID: %s, Dest Folder: %s', uid, dest_folder)
                else:
                    raise imaplib.IMAP4.error('Move failed, result: %s', result)
            else:
                result, data = self.imap_connection.uid('COPY', uid, dest_folder)
                if result == 'OK':
                    self.del_email(uid)
                    LogMaster.log(20, 'Successfully moved email to new folder. UID: %s, Dest Folder: %s', uid, dest_folder)
                else:
                    raise imaplib.IMAP4.error('Move failed, result: %s', result)
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

    def set_flag_byuid(self, uid, flag):
        return self.uid_execute_and_parse('STORE', uid, '+FLAGS', flag)

    def unset_flag_byuid(self, uid, flag):
        return self.uid_execute_and_parse('STORE', uid, '-FLAGS', flag)

    def mark_email_as_read_byuid(self, uid):
        return self.set_flag_byuid(uid, '(\\Seen)')

    def mark_email_as_unread_byuid(self, uid):
        return self.unset_flag_byuid(uid, '(\\Seen)')

    @_handle_imap_errors
    def expunge(self):
        return self.imap_connection.expunge()

    @_handle_imap_errors
    def capabilities(self):
        return self.imap_connection.capabilities

    # def uid(self, *args, **kwargs):
    #     """Straight IMAP UID command passthrough"""
    #     return self.imap_connection.uid(*args, **kwargs)

    @_handle_imap_errors
    def uid_execute_and_parse(self, command, uid_request, *args, **kwargs):
        if imaplib.Debug > 2:
            print('UID_Execute called:\ncommand: %s\n uid_request: %s\n*args: %s\n**kwargs: %s' %
                (command, uid_request, args, kwargs))

        uid_req = self.validate_uidrequest(uid_request)
        if uid_req is None:
            return None

        if '_convert_utf8' in kwargs:
            conv = kwargs['_convert_utf8']
            del kwargs['_convert_utf8']
        else:
            conv = True
        # Exceptions are handlded by the @_handle wrapper
        data = self.parse_results_and_data(
            output_from_imap=self.imap_connection.uid(command, uid_req, *args, **kwargs),
            _convert_utf8=conv
        )

        if imaplib.Debug > 2:
            print('UID_Execute:\ndata:\n%s' % (data))
        return data

    ## Helper Methods (internal)
    #
    # These methods are used as part of the other functions. They contain class-related functionalty.
    # API for these is per-function-dependent, and subject to change.

    @staticmethod
    def validate_uidrequest(uid_request):
        if uid_request is None:
            return None

        if is_list_like(uid_request):
            if len(uid_request) == 0:
                return None
            uid_req = ','.join([str(u) for u in uid_request])
        else:
            uid_req = str(uid_request)

        return uid_req

    @staticmethod
    def parse_results_and_data(output_from_imap, _convert_utf8=True):
        def clean_up_data(data):
            for index, item in enumerate(data):
                if (item == b'(') or (item == b')'):
                    del data[index]

        result, data = output_from_imap
        if imaplib.Debug > 2:
            print('Output From Imaplib:\nresult:%s\ndata:\n%s' % (result, data))
        if (result is None) or (result != 'OK'):
            LogMaster.warning('WARNING: IMAP Result was not OK. Result was: %s', result)
            data = None
        # [None] can emanate from imaplib responses
        if (data is not None) and (data == [None]) or (len(data) == 0):
            LogMaster.warning('WARNING: No data returned from IMAP: %s', result)
            data = None
        if (result == 'OK') and (data is not None):
            clean_up_data(data)
            if _convert_utf8 is True:
                data = convert_bytes_to_utf8(data)
        return data

    @staticmethod
    def set_imaplib_Debuglevel(debuglevel):
        imaplib.Debug = debuglevel  # Default: 0; Range 0->5 zero->high

    @staticmethod
    def get_imaplib_Debuglevel():
        return imaplib.Debug

    @staticmethod
    def is_email_currently_read_fromflags(flags):
        if '\\Seen' in flags:
            return True
        else:
            return False

    @staticmethod
    def _clean_timed_deque(q, max_age):
        ''' Clean old time values out of deque.

        Queue must be values of epoch-seconds sorted in newest-first chronological order. '''
        now_int = int(time.time())
        while ((len(q) > 0) and (now_int - q[-1])) <= max_age:
            q.pop()
        return q

    @staticmethod
    def _add_timestamp_to_deque(q):
        now_int = int(time.time())
        q.appendleft(now_int)

    @staticmethod
    def _timed_failures_exceeded(q, max_failures, max_age):
        if (max_failures <= 0) or (max_failures > len(q)):
            return False
        max_failures = max_failures - 1  # Account for 0-notation list
        exceeded = False
        now_int = int(time.time())
        if now_int - q[max_failures] <= max_age:
            exceeded = True
        return exceeded

    @staticmethod
    def parse_flags(flags_raw):
        flags = []
        try:
            flags = [parsedflag.decode('utf-8') for parsedflag in imaplib.ParseFlags(flags_raw)]
        except Exception:
            pass
        return flags

    @staticmethod
    def parse_imap_internaldate(response):
        try:
            date = imaplib.Internaldate2tuple(response)
        except TypeError:
            date = None
        if date is not None:
            date = struct_time_to_datetime(date)
        return date

