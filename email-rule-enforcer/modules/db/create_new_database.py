import sqlite3
import datetime

# This file will create Database Schema.

SchemaVersion = (0, 1)


def create_new_database(filename):
    # The following lines connect to a new database, parse python types
    # and turn on foreign key suport and named columns (dictionary-style)
    db = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, isolation_level=None)
    db.execute("PRAGMA foreign_keys = ON;")
    db.row_factory = sqlite3.Row
    create_db_schema(db)
    return db


def create_db_schema(db):
    create_table_SchemaVersion(db)
    create_table_Messages(db)
    create_table_Folders(db)
    create_table_FolderUIDEntries(db)
    create_table_ActionsTaken(db)
    create_table_MessageBodies(db)


def create_table_SchemaVersion(db):
    db.execute("create table if not exists tb_SchemaChanges( \
            ID INTEGER PRIMARY KEY ASC, \
            MajorVersion  INTEGER, \
            MinorVersion  INTEGER, \
            Comment  TEXT, \
            DateApplied  Timestamp \
        )")
    db.execute("create Unique Index if Not Exists idx_UniqueSchemaVersion \
        on tb_SchemaChanges(MajorVersion, MinorVersion)")
    db.execute("Create View if Not Exists vw_SchemaVersion (Major, Minor) AS \
            Select MajorVersion, MAX(MinorVersion) \
            FROM tb_SchemaChanges \
            WHERE MajorVersion = (SELECT MAX(MajorVersion) From tb_SchemaChanges LIMIT 1) \
        ")
    db.execute("INSERT into tb_SchemaChanges (MajorVersion, MinorVersion, Comment, DateApplied) values (?, ?, ?, ?)",
        (SchemaVersion[0], SchemaVersion[1], "Initial Database Version", datetime.datetime.now()))
    db.commit()


def create_table_Messages(db):
    db.execute("create table if Not Exists tb_Messages( \
        ID INTEGER PRIMARY KEY ASC, \
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
        LastSeen  Timestamp \
    )")
    db.execute("create Unique Index if Not Exists idx_UniqueMessageID \
        on tb_Messages(Header_MessageID)")


def create_table_Folders(db):
    db.execute("create table if Not Exists tb_Folders( \
        ID INTEGER PRIMARY KEY ASC, \
        FolderPath  TEXT, \
        FolderName  TEXT, \
        UIDNEXT  INTEGER, \
        UIDVALIDITY  INTEGER, \
        CountMessages  INTEGER, \
        CountUnread  INTEGER, \
        DateAdded  Timestamp, \
        LastSeen  Timestamp \
    )")
    db.execute("create Unique Index if Not Exists idx_UniqueFolderPath \
        on tb_Folders(FolderPath)")


def create_table_FolderUIDEntries(db):
    db.execute("create table if Not Exists tb_FolderUIDEntries( \
        ID INTEGER PRIMARY KEY ASC, \
        tbFolders_ID  INTEGER NOT NULL, \
        tbMessages_ID  INTEGER NOT NULL, \
        IMAP_InternalDate  Timestamp, \
        UID  INTEGER, \
        UIDVALIDITY  INTEGER, \
        DateAdded  Timestamp, \
        LastSeen  Timestamp, \
        IMAP_Flag_Seen  INTEGER, \
        IMAP_Flag_Deleted  INTEGER, \
        IMAP_AllFlags  TEXT, \
        FOREIGN KEY (tbFolders_ID) REFERENCES tb_Folders(ID)  ON UPDATE CASCADE  ON DELETE CASCADE, \
        FOREIGN KEY (tbMessages_ID) REFERENCES tb_Messages(ID)  ON UPDATE CASCADE  ON DELETE CASCADE\
    )")
    db.execute("create Unique Index if Not Exists idx_UniqueFolderPath \
        on tb_FolderUIDEntries(tbFolders_ID, tbMessages_ID)")
    db.execute("create Index if Not Exists idx_FolderUIDEntries_FoldersID \
        on tb_FolderUIDEntries(tbFolders_ID)")
    db.execute("create Index if Not Exists idx_FolderUIDEntries_MessagesID \
        on tb_FolderUIDEntries(tbMessages_ID)")


def create_table_ActionsTaken(db):
    db.execute("create table if Not Exists tb_ActionsTaken( \
        ID INTEGER PRIMARY KEY ASC, \
        tbMessages_ID  INTEGER NOT NULL, \
        MsgFrom  TEXT, \
        MsgDate  Timestamp, \
        FolderPath  TEXT, \
        ActionType  TEXT, \
        Value  TEXT, \
        Result  TEXT, \
        Notes  TEXT, \
        DateTaken  Timestamp \
    )")


def create_table_MessageBodies(db):
    db.execute("create table if Not Exists tb_MessageBodies( \
        ID INTEGER PRIMARY KEY ASC, \
        tbMessages_ID  INTEGER NOT NULL, \
        Body_Text  TEXT, \
        Body_HTML  TEXT, \
        FOREIGN KEY (tbMessages_ID) REFERENCES tb_Messages(ID)  ON UPDATE CASCADE  ON DELETE CASCADE\
    )")
    db.execute("create Unique Index if Not Exists idx_MessageBodies_MessagesID \
        on tb_MessageBodies(tbMessages_ID)")

