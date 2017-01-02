import sqlite3
import datetime
import modules.db.create_new_database as new_db
import os


def open_or_create_database(filename):
    db = None
    if os.path.exists(filename):
        try:
            db = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES, isolation_level=None)
        except Exception:
            # db failed ot open
            pass

        schema_matches = False
        try:
            schema_matches = ensure_schema_version(db)
        except Exception:
            pass
        if not schema_matches:
            # FIXME: This is a crappy failure, and will need to be rectified
            # at the next schema-version-rev
            # However it's an ok hack during first release
            db = None

    else:
        db = new_db.create_new_database(filename)

    return db


def ensure_schema_version(db):
    required_SchemaVersion = new_db.dbSchemaVersion
    schema_matches = False
    currSchemaVer = tuple(db.execute("select Major, Minor from vw_SchemaVersion LIMIT 1").fetchone())
    if (required_SchemaVersion == currSchemaVer):
        schema_matches = True
    return schema_matches


def date_minus_days(days=30):
    return datetime.datetime.now() - timedelta(days=days)


def clean_ActionsTaken(db, older_than=date_minus_days(days=30)):
    count_row = db.execute("Select Count(*) as CountOld From tb_ActionsTaken \
        WHERE DateTaken < ?", (older_than,)).fetchone()
    count_of_actions = count_row['CountOld']

    db.execute("Delete From tb_ActionsTaken \
        WHERE DateTaken < ?", (older_than,))
    db.commit()

    return count_of_actions

