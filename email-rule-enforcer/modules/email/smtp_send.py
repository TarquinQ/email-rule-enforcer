import smtplib


def send_email(smtp_server_name, smtp_port, smtp_username, smtp_password, email_msg, smtp_use_ssl=False, smtp_auth_required=False):
    if (smtp_use_ssl):
        server = smtplib.SMTP_SSL(smtp_server_name, smtp_port)
    else:
        server = smtplib.SMTP(smtp_server_name, smtp_port)
    server.ehlo()  # Optional, called by login
    if (smtp_auth_required):
        server.login(smtp_username, smtp_password)
    server.send_message(email_msg)
    server.close()


def send_email_from_config(config, email_msg):
    smtp_server_name = config["smtp_server_name"]
    smtp_port = config["smtp_server_port"]
    smtp_username = config["smtp_username"]
    smtp_password = config["smtp_password"]
    smtp_use_ssl = config["smtp_use_tls"]
    smtp_auth_required = config["smtp_auth_required"]
    send_email(smtp_server_name, smtp_port, smtp_username, smtp_password, email_msg, smtp_use_ssl, smtp_auth_required)
