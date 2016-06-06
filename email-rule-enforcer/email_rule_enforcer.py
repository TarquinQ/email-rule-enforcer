import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
from modules.logging import log_messages as log
from modules.get_config import get_config
#import modules.connect_to_imap
#import modules.operate_on_imap
#import modules.send_email


def main():
    get_config()


if __name__ == "__main__":
    main()
