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
        return self.db.execute(*args, **kwargs)

    def cursor(self):
        return self.db.cursor()

    def commit(self):
        return self.db.commit()


def sync_folders(db, imap):
    db.execute("drop table if exists tb_Temp_FolderList")
    db.execute("create temporary table tb_Temp_FolderList(FolderPath TEXT)")

    imap_folders = imap.get_folder_list()
    for imap_folder in imap_folders:
        db.execute("INSERT into tb_Temp_FolderList (FolderPath) values (?)", (imap_folder_path))

        status = imap.status(imap_folder)
        imap_folder_name = parse_folderName(imap_folder)

        db.execute("INSERT OR IGNORE INTO tb_Folders ( \
            FolderPath, FolderName, DateAdded ) values (?,?,?)",
            (imap_folder_path, imap_folder_name, datetime.datetime.now())
        )
        db.execute("UPDATE tb_Folders SET ( \
            UIDNEXT=?, UIDVALIDITY=?, CountMessages=?, CountUnread=?, LastSeen=? \
            ) WHERE FolderPath=?",
            (status.UIDNEXT, status.UIDVALIDITY, status.CountMessages, status.CountUnread, datetime.datetime.now(),
                imap_folder
            )
        )
    # And now we remove all folders which no longer exist
    # This will "cascade-delete" corresponding records in the tb_FolderUIDEntries table too
    db.execute("DELETE FROM tb_Folders WHERE FolderPath NOT IN (SELECT FolderPath FROM tb_Temp_FolderList)")
    # Now we remove all UID Entries which do not have matching UIDVALIDITY
    for folder_row in db.execute("SELECT ID, FolderPath, UIDVALIDITY FROM tb_Folders").fetchall():
        FolderID = folder_row["FolderID"]
        UIDVALIDITY = folder_row["UIDVALIDITY"]
        db.execute("DELETE FROM tb_FolderUIDEntries WHERE FolderID=? AND UIDVALIDITY!=?", (FolderID, UIDVALIDITY))

    # Clean up
    db.execute("drop table if exists tb_Temp_FolderList")


def remove_messages_with_no_folderEntries(db):
    count = 0
    try:
        count = db.execute("SELECT COUNT(*) FROM tb_Messages WHERE ID NOT IN (SELECT DISTINCT(tbMessages_ID) FROM tb_FolderUIDEntries)")
        db.execute("DELETE FROM tb_Messages WHERE ID NOT IN (SELECT DISTINCT(tbMessages_ID) FROM tb_FolderUIDEntries)")
    except sqlite3.Error:
        pass
    return count


def insert_message(db, message):
    pass
    db.execute("create table if Not Exists tb_Messages( \
        Header_MessageID  TEXT, \
        Header_From  TEXT, \
        Header_Date  Timestamp, \
        Header_Subject  TEXT, \
        Header_To  TEXT, \
        Header_CC  TEXT, \
        MsgSize  INTEGER, \
        AllHeaders  TEXT, \
        Has_Body  INTEGER, \
        DateAdded  Timestamp, \
        LastSeen  Timestamp, \
    )")

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


def check_if_message_exists(messageID, db):
    pass

