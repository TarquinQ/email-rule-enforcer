import sqlite3
import datetime
import modules.db.create_new_database as new_db
import os


def open_or_create_database(filename):
    if os.path.exists(filename):
        preexisting = True
    else:
        preexisting = False

    db = new_db.connect(filename)
    # Leave Exceptions unhandled;  if db-open fails, let it fall right through to cause programme failure, since
    # There is nothing else we can do at this point.

    if preexisting is True:
        schema_matches = ensure_schema_version(db)
        if schema_matches is False:
            # FIXME: There is no workaround at present, and will need to be rectified
            # at the first/next schema-version-revision (ie v0.2)
            # However it's an ok hack during first release (ie v0.1) and will ensure that newer schemas
            # don't silently fail/corrupt with this version of the code
            raise RuntimeError('Database schema version does not match, cannot proceed')
    else:
        new_db.create_db_schema(db)

    return db


def ensure_schema_version(db):
    required_SchemaVersion = new_db.SchemaVersion
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

