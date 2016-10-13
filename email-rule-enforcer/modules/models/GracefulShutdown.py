def graceful_shutdown(imap_connection=None):
    if imap_connection is not None:
        imap_connection.disconnect()

