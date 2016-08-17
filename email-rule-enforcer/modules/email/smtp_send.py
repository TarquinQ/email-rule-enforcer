from modules.logging import LogMaster
from modules.email.SMTPServerConnection import SMTPServerConnection


def send_email_from_config(config, email_msg):
    smtp_server_name = config["smtp_server_name"]
    smtp_port = config["smtp_server_port"]
    smtp_username = config["smtp_username"]
    smtp_password = config["smtp_password"]
    smtp_use_tls = config["smtp_use_tls"]
    smtp_auth_required = config["smtp_auth_required"]
    send_email(smtp_server_name, smtp_port, smtp_username, smtp_password, email_msg, smtp_use_tls, smtp_auth_required)


def send_email(smtp_server_name, smtp_port, smtp_username, smtp_password, email_msg, smtp_use_tls=False, smtp_auth_required=False):
    LogMaster.log(30, "Now sending email via smtp. Details are:\nFrom: %s\nTo: %s\nSubject: %s",
        email_msg["from"], email_msg["to"], email_msg["subject"])
    LogMaster.debug("""
Now sending email via smtp. SMTP Server details are:
Server Name and port, TLS Required: %s:%s, %s\n
Auth Required, Username: %s, %s""",
        smtp_server_name, smtp_port, smtp_use_tls, smtp_auth_required, smtp_username)

    success = False
    server_conn = SMTPServerConnection(server_name=smtp_server_name,
        port=smtp_port, username=smtp_username, password=smtp_password,
        use_tls=smtp_use_tls, auth_required=smtp_auth_required)
    server_conn.connect()
    if server_conn.is_connected:
        try:
            server_conn.send_message(email_msg)
            success = True
        except:
            pass
    server_conn.disconnect()

    LogMaster.log(30, "Was SMTP Send Successful? %s", success)

    return success


