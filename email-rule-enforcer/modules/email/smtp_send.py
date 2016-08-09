import smtplib


def send_email_from_config(config, email_msg):
    smtp_server_name = config["smtp_server_name"]
    smtp_port = config["smtp_server_port"]
    smtp_username = config["smtp_username"]
    smtp_password = config["smtp_password"]
    smtp_use_tls = config["smtp_use_tls"]
    smtp_auth_required = config["smtp_auth_required"]
    send_email(smtp_server_name, smtp_port, smtp_username, smtp_password, email_msg, smtp_use_tls, smtp_auth_required)


def send_email(smtp_server_name, smtp_port, smtp_username, smtp_password, email_msg, smtp_use_tls=False, smtp_auth_required=False):
    success = False
    server_connected = False
    try:
        if not (smtp_use_tls):
            server = smtplib.SMTP(smtp_server_name, smtp_port)
            server.ehlo()
            server_connected = True
        else:
            if smtp_port == 587:
                try_starttls_first = True
            else:
                try_starttls_first = False

            if try_starttls_first:
                try:
                    server = smtplib.SMTP_SSL(host=smtp_server_name, port=smtp_port)
                    server.ehlo()
                    server_connected = True
                except Exception:
                    pass

                if not server_connected:
                    try:
                        server = smtplib.SMTP(smtp_server_name, smtp_port)
                        server.ehlo()
                        server.starttls()  # enable TLS
                        server.ehlo()
                        server_connected = True
                    except Exception:
                        pass
            else:
                try:
                    server = smtplib.SMTP(smtp_server_name, smtp_port)
                    server.ehlo()
                    server.starttls()  # enable TLS
                    server.ehlo()
                    server_connected = True
                except Exception:
                    pass

                if not server_connected:
                    try:
                        server = smtplib.SMTP_SSL(host=smtp_server_name, port=smtp_port)
                        server.ehlo()
                        server_connected = True
                    except Exception:
                        pass

        if (smtp_auth_required):
            server.login(smtp_username, smtp_password)

        server.send_message(email_msg)
        server.close()

    except Exception:
        # Bad, unPythonic... and also not important here
        pass
    return success




