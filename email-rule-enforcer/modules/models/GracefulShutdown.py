def graceful_shutdown_imap(imap_connection=None):
    if imap_connection is not None:
        imap_connection.disconnect()


def graceful_shutdown_db(db=None):
    if db is not None:
        db.close()
