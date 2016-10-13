import threading


class GlobalEvents():
    def __init__(self):
        self.shutdown_evt = threading.Event()
        self.reread_config_evt = threading.Event()
        self.imap_perm_fail = threading.Event()

