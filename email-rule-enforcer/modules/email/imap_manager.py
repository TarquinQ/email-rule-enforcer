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

    def set_parameters(username, password, server_name, server_port, use_ssl, mark_as_read_on_move=True, empty_trash_on_exit=False):
        self.username = username
        self.password = password
        self.server_name = server_name
        self.server_port = server_port
        self.use_ssl = use_sslempty_trash_on_exit
        self.mark_as_read_on_move = mark_as_read_on_move
        self.empty_trash_on_exit = empty_trash_on_exit

    def set_parameters_from_config(config):
        username = config[imap_username]
        password = config[imap_password]
        server_name = config[imap_server_name]
        server_port = config[imap_server_port]
        use_ssl = config[imap_use_tls]
        mark_as_read_on_move = config[mark_as_read_on_move]
        empty_trash_on_exit = config[empty_trash_on_exit]
        self.set_parameters(username, password, server_name, server_port, use_ssl, mark_as_read_on_move, empty_trash_on_exit)

    def connect(self):
        if use_ssl:
            ssl_context = ssl.create_default_context()
            self.imap_connection = imaplib.IMAP4_SSL(imap_server, imap_port, ssl_context=ssl_context)
        else:
            self.imap_connection = imaplib.IMAP4(imap_server, imap_port)
        self.is_connected = True
        self.imap_connection.login(self.username, self.password)
        self._check_imapmove_supported()

    def connect_to_default_folder(self):
        return self.connect_to_folder(self.initial_folder)

    def connect_to_folder(self, folder_name):
        self.imap_connection.select(folder_name)
        self.currfolder_name = folder_name

    def disconnect(self):
        self.imap_connection.logout()
        self.is_connected = False

    def _check_imapmove_supported(self):
        self.imap_connection._get_capabilities()  # Refresh capabilities list
        if 'MOVE' in imap_connection.capabilities:
            self.imapmove_is_supported = True
            # This monkey-patches the core imaplib for MOVE support
            imaplib.Commands['MOVE'] = ('SELECTED',)
        else:
            self.imapmove_is_supported = False

    def get_currfolder(self):
        return self.currfolder_name

    def get_list_allemails_in_currfolder(self):
        result, data = self.imap_connection.uid('search', None, "ALL")  # search and return uids
        list_allemails = data[0].split()
        return list_allemails

    def get_emails_in_currfolder(self):
        """Return raw emails from the curent folder, without marking as read"""
        for uid in get_list_allemails_in_currfolder:
            this_email_raw = self.get_raw_email(uid)
            this_email = self.parse_raw_email(this_email_raw)  # Convert to native email


    def get_imap_flags_byuid(self, uid):
        """Gets a list of flags in UTF-8 for a given uid"""
        flags = []
        result, flags_raw = self.imap_connection.uid('fetch', uid, '(FLAGS)')
        #print ('FLAGS response: ', str(flags))
        for flag in flags_raw:
            new_flags = [parsedflag.decode('utf-8') for parsedflag in imaplib.ParseFlags(flag)]
            flags.extend(new_flags)
            # for parsedflag in imaplib.ParseFlags(flag).decode('utf-8'):
            #     flags.append(parsedflag)

    def get_all_folders(self):
        """Returns a list of all IMAP folders"""
        return self.imap_connection.list()[1]

    def get_raw_email(self, uid):
        result, data = imap_connection.uid('fetch', uid, 'BODY.PEEK[HEADER]')
        raw_email = data[0][1]
        return raw_email

    def get_parsed_email(self, uid):
        pass

    def parse_raw_email(self, raw_email_string):
        return email.message_from_bytes(raw_email_string)

    def move_email(self, uid, new_folder, mark_as_read_on_move=None):
        if self.imapmove_is_supported:
            result, data = imap_connection.uid('MOVE', uid, dest_folder)
        else:
            result, data = imap_connection.uid('COPY', uid, dest_folder)
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
        return imap_connection.uid('STORE', uid , '+FLAGS', flag)

    def unset_flag_byuid(self, uid, flag):
        return imap_connection.uid('STORE', uid , '-FLAGS', flag)

    def mark_email_as_read(self, uid):
        return set_flag_byuid(uid, '\\Seen')

    def mark_email_as_unread(self, uid):
        return unset_flag_byuid(uid, '(\\Seen)')

    def expunge(self):
        return self.imap_connection.expunge()
