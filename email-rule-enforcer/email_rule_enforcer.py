import modules.python_require_min_pyversion  # checks for py >= 3.4, which we need for newer IMAP TLS support
from modules.settings.get_config import get_config
from modules.email.IMAPServerConnection import IMAPServerConnection


def main():
    (config, rules) = get_config()

    imap_connection = IMAPServerConnection()
    imap_connection.set_parameters_from_config(config)
    try:
        imap_connection.connect_to_server()
    except Exception as e:
        print("IMAP Connection fail")

    # iterate_rules_over_mailbox()
    imap_connection.disconnect()
    # send_smtp_completion_email()

if __name__ == "__main__":
    main()
