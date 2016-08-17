from modules.logging import LogMaster
import smtplib


class SMTPServerConnection():
    def __init__(self, server_name, port=25, username="", password="", use_tls=False, auth_required=False):
        self.server_name = server_name
        self.port = port
        self.username = username
        self.password = password
        self.use_tls = use_tls
        self.auth_required = auth_required
        self.auth_is_safe = True
        self.server_connection = None
        self.is_connected = False
        self.login_errror = False
        self.set_try_tls_first()

    def send_message(self, email_msg):
        return self.server_connection.send_message(email_msg)

    def connect(self):
        if (self.use_tls):
            self.connect_ssl()
        else:
            self.connect_nonssl()
        self.login()

    def disconnect(self):
        try:
            self.server_connection.close()
        except Exception:
            pass

    def close(self):
        self.disconnect()

    def set_try_tls_first(self):
        self.try_tls_first = True
        if (self.port == 25) or (self.port == 587):
            self.try_tls_first = False

    def connect_nonssl(self):
        try:
            self.server_connection = smtplib.SMTP(host=self.server_name, port=self.port)
            self.set_debuglevel()
            self.server_connection.ehlo()
            self.is_connected = True
        except:
            pass

    def connect_ssl(self):
        if self.try_tls_first:
            self._connect_ssl_tls()
            if not self.is_connected:
                self._connect_ssl_starttls()
        else:
            self._connect_ssl_starttls()
            if not self.is_connected:
                self._connect_ssl_tls()

    def _connect_ssl_tls(self):
        try:
            self.server_connection = smtplib.SMTP_SSL(self.server_name, self.port)
            self.set_debuglevel()
            self.server_connection.ehlo()
            self.server_connected = True
        except Exception:
            pass

    def _connect_ssl_starttls(self):
        try:
            self.connect_nonssl()
        except Exception:
            pass

        if not self.is_connected:
            self._connect_ssl_tls()
        else:
            try:
                self.server_connection.starttls()  # enable TLS
                self.server_connection.ehlo()
                self.is_connected = True
            except (SMTPNotSupportedError, SMTPResponseException, SMTPHeloError):
                self.auth_is_safe = False
                self.disconnect()

    def set_debuglevel(self):
        self.server_connection.set_debuglevel(1)

    def login(self):
        if self.is_connected and self.auth_required:
            try:
                self.server_connection.login(self.username, self.password)
                self.login_errror = False
            except Exception:
                self.login_errror = True


