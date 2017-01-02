import threading


class GlobalEvents():
    def __init__(self):
        self.shutdown_evt = threading.Event()
        self.full_sync_required = threading.Event()
        self.imap_perm_fail = threading.Event()

