import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
from modules.get_config import get_config
#import modules.connect_to_imap
#import modules.operate_on_imap
#import modules.send_email


def main():
    (config, rules) = get_config()
    # connect_to_imap()
    # iterate_rules_over_mailbox()
    # send_smtp_completion_email()


if __name__ == "__main__":
    main()
