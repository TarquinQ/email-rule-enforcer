import sqlite3

# This file will create Database Schema. Schema is as per the following:

# Table:      tb_Messages
# Fields:     ID      SHA     From    Date    Subject     MessageID   InternalDate    Flags    HeadersText     DateAdded      LastSeen      Deleted

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


def create_new_database():
    con = sqlite3.connect(":memory:")
    con.row_factory = sqlite3.Row
    con.execute("create table if not exists tb_SchemaChanges( \
            ID INTEGER PRIMARY KEY ASC, \
            MajorVersion  INTEGER, \
            MinorVersion  INTEGER, \
            Comment  TEXT, \
            DateApplied  Date \
        )")
    con.execute("create Unique Index if Not Exists idx_EnsureUniqueSchemaVersion \
        on tb_SchemaChanges(MajorVersion, MinorVersion)")
    con.execute("Create View if Not Exists vw_SchemaVersion (Major, Minor) AS \
            Select MajorVersion, MAX(MinorVersion) \
            FROM tb_SchemaChanges \
            WHERE MajorVersion = (SELECT MAX(MajorVersion) From tb_SchemaChanges) \
        ")
    con.execute("create table if Not Exists tb_Messages(ID INTEGER PRIMARY KEY ASC, MessageID)")


