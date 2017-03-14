import datetime
from modules.supportingfunctions import get_username, get_hostname, get_os_str


def get_logfile_headers(config, logname):
    ret_val = [
        '*************************************',
        '** Log File for Email Rule Enforcer',
        '** Log name is: %s' % logname,
        '** ',
        '** Current time is %s' % datetime.datetime.now(),
        '** ',
        '** Running on host: %s' % get_hostname(),
        '** Running as user: %s' % get_username(),
        '** ',
        '*************************************',
        '** ',
        '** Important Config info for this session:',
        '** IMAP Server: %s' % config['imap_server_name'],
        '** IMAP Username: %s' % config['imap_username'],
        '** IMAP Port Number: %s, Use SSL: %s' % (str(config['imap_server_port']), config['imap_use_tls']),
        '** IMAP Initial Folder: %s' % config['imap_initial_folder'],
        '** IMAP Deletions Folder: %s' % config['imap_deletions_folder'],
        '** IMAP Empty Deleted Items on Exit: %s' % config['empty_trash_on_exit'],
        '** SMTP Server: %s' % config['smtp_server_name'],
        '** SMTP Port Number: %s, Use SSL: %s,' % (str(config['smtp_server_port']), config['smtp_use_tls']),
        '** SMTP Auth Required: %s' % config['smtp_auth_required'],
        '** SMTP Username: %s' % config['smtp_username'],
        '** Send Email on Completion: %s' % config['notification_email_on_completion'],
        '** ',
        '*************************************',
        '** ',
    ]
    return '\n'.join(ret_val)

