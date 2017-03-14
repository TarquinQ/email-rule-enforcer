import os
import json
import sqlite3
import datetime
import modules.db.database_schema as db_schema
from modules.supportingfunctions import strip_quotes, convert_bytes_to_utf8


def open_or_create_database(filename):
    if os.path.exists(filename):
        preexisting = True
    else:
        preexisting = False

    db = connect(filename)
    # Leave Exceptions unhandled;  if db-open fails, let it fall right through to cause programme failure, since
    # there is nothing else we can do at this point.

    if preexisting is True:
        schema_matches = ensure_schema_version(db)
        if schema_matches is False:
            # FIXME: There is no workaround at present, and will need to be rectified
            # at the first/next schema-version-revision (ie v0.2)
            # However it's an ok hack during first release (ie v0.1) and will ensure that newer schemas
            # don't silently fail/corrupt with this version of the code
            raise RuntimeError('Database schema version does not match, cannot proceed')
    else:
        db_schema.create_db_schema(db)

    return db


def connect(filename=":memory:"):
    # The following lines connect to a new database, parse python types
    # and turn on foreign key suport and named columns (dictionary-style)
    db = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON;")
    register_adapters()
    return db


def register_adapters():
    '''Adds custom dataype handling from Python to Sqlite3.

    NB: converters are always called with 'bytes' as their input-type, regardless of how
        they get stored by sqlite3 in the underlying database (which in-turn depends on
        their adapter-return-type)
    '''
    # To/from Booleans:
    sqlite3.register_adapter(bool, int)
    sqlite3.register_converter("BOOLEAN", lambda val: val != b'0')
    # To/from List:
    sqlite3.register_adapter(list, json.dumps)
    sqlite3.register_converter("LIST", lambda val: json.loads(convert_bytes_to_utf8(val)))


def ensure_schema_version(db):
    required_SchemaVersion = db_schema.SchemaVersion
    schema_matches = False
    currSchemaVer = tuple(db.execute("select Major, Minor from vw_SchemaVersion LIMIT 1").fetchone())
    if (required_SchemaVersion == currSchemaVer):
        schema_matches = True
    return schema_matches


def date_minus_days(days=30):
    return datetime.datetime.now() - datetime.timedelta(days=days)


def clean_ActionsTaken(db, older_than=date_minus_days(days=30)):
    count_row = db.execute("Select Count(*) as CountOld From tb_ActionsTaken \
        WHERE DateTaken < ?", (older_than,)).fetchone()
    count_of_actions = count_row['CountOld']

    db.execute("Delete From tb_ActionsTaken \
        WHERE DateTaken < ?", (older_than,))
    db.commit()

    return count_of_actions

