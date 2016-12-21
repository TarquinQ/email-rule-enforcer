import sqlite3
import datetime

# This file will create Database Schema. Schema is as per the following:

# Table:      tb_Messages
# Fields:     ID      SHA     From    Date    Subject     MessageID   InternalDate    Flags    HeadersText     DateAdded      LastSeen

# Table:      tb_Folders
# Fields:     ID      FolderPath      FolderName      LastSeen    UIDNEXT     UIDVALIDITY     Missing     DateAdded   LastCount   LastUnreadCount

# Table:      tb_UIDEntries
# Fields:     ID      FolderPath      UIDVALIDITY     UID     Messages_ID       Deleted     DateAdded

# Table:      tb_ActionsTaken
# Fields:     ID      MsgID       FolderPath      ActionType      Value       Result      DateTaken

# Table:      tb_SchemaChanges
# Fields:     ID      MajorVersion    MinorVersion    Comment     DateApplied

# View:       vw_SchemaVersion
# Fields:     Max(tb_SchemaChanges.MajorVersion) as Major, Max(tb_SchemaChanges.MinorVersion) as Minor, from tb_SchemaChanges, Where Max(tb_SchemaChanges.MajorVersion) = Max(tb_SchemaChanges.MajorVersion)


# CREATE TABLE t(x INTEGER PRIMARY KEY ASC, y, z);


SchemaVersion = (0, 1)


def create_new_database(filename):
    # The following lines connect to a new database, parse python types
    # and turn on foreign key suport and named columns (dictionary-style)
    db = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
    db.execute("PRAGMA foreign_keys = ON;")
    db.row_factory = sqlite3.Row
    create_db_schema(db)
    return db


def create_db_schema(db):
    create_table_SchemaVersion(db)
    create_table_Messages(db)


def create_table_SchemaVersion(db):
    db.execute("create table if not exists tb_SchemaChanges( \
            ID INTEGER PRIMARY KEY ASC, \
            MajorVersion  INTEGER, \
            MinorVersion  INTEGER, \
            Comment  TEXT, \
            DateApplied  Timestamp \
        )")
    db.execute("create Unique Index if Not Exists idx_EnsureUniqueSchemaVersion \
        on tb_SchemaChanges(MajorVersion, MinorVersion)")
    db.execute("Create View if Not Exists vw_SchemaVersion (Major, Minor) AS \
            Select MajorVersion, MAX(MinorVersion) \
            FROM tb_SchemaChanges \
            WHERE MajorVersion = (SELECT MAX(MajorVersion) From tb_SchemaChanges) \
        ")
    db.execute("INSERT into tb_SchemaChanges (MajorVersion, MinorVersion, Comment, DateApplied) values (?, ?, ?, ?)",
        (SchemaVersion[0], SchemaVersion[1], "Initial Database Version", datetime.datetime.now()))
    db.commit()


def create_table_Messages(db):
    db.execute("create table if Not Exists tb_Messages(ID INTEGER PRIMARY KEY ASC, MessageID)")


