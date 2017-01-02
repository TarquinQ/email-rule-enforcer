def graceful_shutdown(imap_connection=None, db=None):
    if imap_connection is not None:
        imap_connection.disconnect()
    if db is not None:
        db.close()

