def get_header_preconfig():
    ret_str = '''
*********************************************************************
**
** Email Rule Enforcer
**
** This program will log into an IMAP mailbox and process
** a ruleset against a selected folder (usually Inbox).
** Now proceeding to get local configs and rules.
**
*********************************************************************'''
    return ret_str


def get_header_postconfig(config):
    ret_str = '''
*********************************************************************
**
** Configuration section completed. We will now attempt to:
**  * Open log files
**  * Connect to IMAP server \'%s:%s\' (SSL?: %s)
**             with Username \"%s\"%s
**
*********************************************************************
''' % (config['imap_server_name'],
        config['imap_server_port'],
        config['imap_use_tls'],
        config['imap_username'],
        '')
    return ret_str

