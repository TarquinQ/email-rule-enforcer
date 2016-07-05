import imaplib
import ssl
import email
import traceback


class IMAPServerConnection():
    def __init__(self):
        self.imapmove_is_supported = False
        self.initial_folder = 'INBOX'
        self.deletions_folder = 'Trash'
        self.currfolder_name = self.initial_folder
        self.is_connected = False

    def set_parameters_from_config(self, config):
        self.username = config["imap_username"]
        self.password = config["imap_password"]
        self.server_name = config["imap_server_name"]
        self.server_port = config["imap_server_port"]
        self.use_ssl = config["imap_use_tls"]
        self.mark_as_read_on_move = config["mark_as_read_on_move"]
        self.empty_trash_on_exit = config["empty_trash_on_exit"]
        self.initial_folder = config["imap_initial_folder"]
        self.deletions_folder = config["imap_deletions_folder"]

    def connect(self):
        return self.connect_to_server()

    def connect_to_server(self):
        if self.use_ssl:
            ssl_context = ssl.create_default_context()
            self.imap_connection = imaplib.IMAP4_SSL(self.server_name, self.server_port, ssl_context=ssl_context)
        else:
            self.imap_connection = imaplib.IMAP4(self.server_name, self.server_port)
        self.is_connected = True
        self.imap_connection.login(self.username, self.password)
        self._check_imapmove_supported()

    def connect_to_default_folder(self):
        return self.connect_to_folder(self.initial_folder)

    def connect_to_folder(self, folder_name):
        msg_count = self.imap_connection.select(folder_name)
        self.currfolder_name = folder_name
        return msg_count

    def disconnect(self):
        self.imap_connection.logout()
        self.is_connected = False

    def logout(self):
        return self.disconnect()

    def _check_imapmove_supported(self):
        self.imap_connection._get_capabilities()  # Refresh capabilities list
        if 'MOVE' in self.capabilities():
            self.imapmove_is_supported = True
            # This monkey-patches the core imaplib for MOVE support
            imaplib.Commands['MOVE'] = ('SELECTED',)
        else:
            self.imapmove_is_supported = False

    def get_currfolder(self):
        return self.currfolder_name

    def get_list_alluids_in_currfolder(self):
        """Searches and returns  a list of all uids in folder, byte-format"""
        result, data = self.imap_connection.uid('search', None, "ALL")
        list_allemails = data[0].split()
        return list_allemails

    def get_emails_in_currfolder(self):
        """Return raw emails from the curent folder, without marking as read"""
        for uid in get_list_alluids_in_currfolder:
            yield self.get_parsed_email_byuid(uid)

    def get_imap_flags_byuid(self, uid):
        """Gets a list of flags in UTF-8 for a given uid"""
        flags = []
        result, flags_raw = self.imap_connection.uid('fetch', uid, '(FLAGS)')
        #print ('FLAGS response: ', str(flags))
        for flag in flags_raw:
            new_flags = [parsedflag.decode('utf-8') for parsedflag in imaplib.ParseFlags(flag)]
            flags.extend(new_flags)

    def get_list_all_folders(self):
        """Returns a list of all IMAP folders"""
        return self.imap_connection.list()[1]

    def get_raw_email_byuid(self, uid):
        result, data = self.imap_connection.uid('fetch', uid, 'BODY.PEEK[]')
        raw_email = data[0][1]
        return raw_email

    def get_parsed_email_byuid(self, uid):
        return self.parse_raw_email(self.get_raw_email_byuid(uid))

    def get_parsedemailandflags_byuid(self, uid):
        ret_email = self.get_parsed_email_byuid(uid)
        ret_email.imap_flags = self.get_imap_flags_byuid(uid)
        return ret_email

    def get_raw_headers_byuid(self, uid):
        result, data = self.imap_connection.uid('fetch', uid, 'BODY.PEEK[HEADER]')
        raw_headers = data[0][1]
        return raw_headers

    def get_parsed_headers_byuid(self, uid):
        return self.parse_raw_email(self.get_raw_headers_byuid(uid))

    def get_parseheadersandflags_byuid(self, uid):
        ret_email = self.get_parsed_headers_byuid(uid)
        ret_email.imap_flags = self.get_imap_flags_byuid(uid)
        return ret_email

    def parse_raw_email(self, raw_email_string):
        try:
            ret_msg = email.message_from_bytes(raw_email_string)
        except email.MessageError as e:
            # This isn't handling the error per se, it's just changing
            # it into an imaplib error to match the rest of this class
            raise imap_connection.error('Error parsing raw email. Email Error was: %s' % e)
        return ret_msg

    def move_email(self, uid, new_folder, mark_as_read_on_move=None):
        if self.imapmove_is_supported:
            result, data = self.imap_connection.uid('MOVE', uid, dest_folder)
        else:
            result, data = self.imap_connection.uid('COPY', uid, dest_folder)
            if result == 'OK':
                result, data = self.set_flag_byuid('(\Deleted)')
                imap_connection.expunge()

    def del_email(self, uid, perm_delete=False):
        if perm_delete:
            result, data = self.set_flag_byuid('(\Deleted)')
            self.expunge()
        else:
            self.move_email(uid, self.deletions_folder, mark_as_read_on_move=False)

    def is_email_currently_unread_byuid(self, uid):
        if '\\Seen' in self.get_imap_flags_byuid(uid):
            return True
        else:
            return False

    def set_flag_byuid(self, uid, flag):
        return imap_connection.uid('STORE', uid, '+FLAGS', flag)

    def unset_flag_byuid(self, uid, flag):
        return imap_connection.uid('STORE', uid, '-FLAGS', flag)

    def mark_email_as_read(self, uid):
        return set_flag_byuid(uid, '(\\Seen)')

    def mark_email_as_unread(self, uid):
        return unset_flag_byuid(uid, '(\\Seen)')

    def expunge(self):
        return self.imap_connection.expunge()

    def capabilities(self):
        return self.imap_connection.capabilities

    def uid(self, *args, **kwargs):
        """Straight IMAP UID command passthrough"""
        return self.imap_connection.uid(*args, **kwargs)

    @classmethod
    def set_imaplib_Debug(cls, debuglevel):
        imaplib.Debug = debuglevel  # Default: 0; Range 0->5 zero->high
