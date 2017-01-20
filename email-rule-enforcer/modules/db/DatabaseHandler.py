import sqlite3
import modules.db.database_management as db_manage


class DatabaseHandler():
    """Abstracts the database operations"""

    def __init__(self, db_filename=":memory:", auto_open=True):
        self.connected = False
        self.db_filename = db_filename
        self.db = None
        if auto_open:
            self.open()

    def open(self):
        if (self.connected is True):
            return True

        self.db = db_manage.open_or_create_database(self.db_filename)
        if self.db is None:
            return False
        else:
            self.connected = True

    def close(self):
        if (self.connected is False):
            return True

        try:
            self.db.close()
        except Exception:
            pass
        self.connected = False
        return True

    def clean_old_records(self):
        """Cleans up old records in the database"""
        count = 0
        count += db_manage.clean_ActionsTaken(self.db)
        return count

    def execute(self, *args, **kwargs):
        return self.db.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        return self.db.executemany(*args, **kwargs)

    def cursor(self):
        return self.db.cursor()

    def commit(self):
        return self.db.commit()


def remove_messages_with_no_folderEntries(db):
    count = 0
    try:
        count = db.execute("SELECT COUNT(*) FROM tb_Messages WHERE ID NOT IN (SELECT DISTINCT(tbMessages_ID) FROM tb_FolderUIDEntries)")
        db.execute("DELETE FROM tb_Messages WHERE ID NOT IN (SELECT DISTINCT(tbMessages_ID) FROM tb_FolderUIDEntries)")
    except sqlite3.Error:
        pass
    return count


def insert_message(db, message):
    db.execute("insert or ignore into tb_Messages( \
        Header_MessageID, \
        Header_From, \
        Header_Date, \
        Header_Subject, \
        Header_To, \
        Header_CC, \
        MsgSize, \
        AllHeaders, \
        DateAdded, \
        LastSeen, \
        ) \
        ) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (message.unique_id, message.addr_from, message.date_datetime,
            message["subject"], json.dumps(message.addr_to), json.dumps(message.addr_cc),
            message.size, message.AllHeaders, datetime.datetime.now(), datetime.datetime.now()
        )
    )
    return get_tbMessageID_from_MessageID(Header_MessageID)

#                 parsed_email.original_raw_email = raw_email.raw_email_bytes
#                 parsed_email.size = raw_email.size
#                 parsed_email.server_date = raw_email.server_date
#                 parsed_email.headers_only = headers_only
#                 parsed_email.uid = uid
#                 parsed_email.uid_str = convert_bytes_to_utf8(uid)
#                 parsed_email.imap_folder = self.currfolder_name
#                 parsed_email.date_datetime = get_email_datetime(parsed_email)
#                 parsed_email.addr_from = get_email_addrfield_from(parsed_email)
#                 parsed_email.addr_to = get_email_addrfield_to(parsed_email)
#                 parsed_email.addr_cc = get_email_addrfield_cc(parsed_email)
#                 parsed_email.imap_flags = raw_email.flags
#                 parsed_email.is_read = self.is_email_currently_read_fromflags(parsed_email.imap_flags)
#                 parsed_email.body = get_email_body(parsed_email)
#                 parsed_email.unique_id = get_email_uniqueid(parsed_email, parsed_email.original_raw_email)
# server.fetch(num, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')


def get_tbMessageID_from_MessageID(db, MessageID):
    """If a message exists, this function returns the ID"""
    try:
        row = db.execute("SELECT ID from tb_Messages WHERE Header_MessageID=?", (MessageID,)).fetchone()
        ID = row[0]
    except (IndexError, TypeError):
        ID = 0
    return ID


def get_tbFolderID_from_FolderPath(db, FolderPath):
    """If a message exists, this function returns the ID"""
    try:
        row = db.execute("SELECT ID from tb_Folders WHERE FolderPath=?", (FolderPath,)).fetchone()
        ID = row[0]
    except (IndexError, TypeError):
        ID = 0
    return ID


def store_message(db, message):
    pass


def store_message_into_folder(db, message):
    pass

