"""email送信サポートライブラリ"""
import smtplib
import sys
import traceback
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.lib.common_utils.ibr_decorator_config import (
    initialize_config,
)
from src.lib.common_utils.ibr_enums import (
    LogLevel,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

################################
# class定義
################################
class SmtpConnection:
    """SMTPサーバへの接続/認証を担当します

    Copy right:
        (あとで書く)

    Example:
        >>> with SmtpConnection(
                email_server_host,
                email_server_port,
                user_id,
                password,
                ) as email_server:
    """
    def __init__(
        self,
        email_server_host: str,
        email_server_port: int,
        user_id: str|None=None,
        password: str|None=None,
        ) -> None:
        self._email_server_host = email_server_host
        self._email_server_port = email_server_port
        self._user_id = user_id
        self._password = password
        self._connection = None

    def __enter__(self):
        """SMTPサーバ接続時のコンテキストマネージャー定義

        Returns:
            (None):

        Raises:
            - Exception: SMTPサーバとのセッション確立失敗

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        try:
            self._connection = smtplib.SMTP(self._email_server_host, self._email_server_port)
        except Exception as e:
            log_msg(f'SMTPサーバへの接続/認証に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        # デバッグ設定
        if self._connection:
            log_msg(f'connection debug level: {self._connection.debuglevel(1)}', LogLevel.DEBUG)

        # 環境によってtls及びAUTH提供されていない可能性あり
        self._connection.ehlo()
        if self._connection.has_extn('startttls'):
            self._connection.startttls()
        if self._connection.has_extn('auth'):
            self._connection.login(self._user_id, self._password)

        return self._connection

    def __exit__(self, exc_type, exc_value, traceback):
        """SMTPサーバ切断時のコンテキストマネージャー定義"""
        if self._connection is not None:
            self._connection.quit()


class EmailSender:
    """メール文書を作成しConnection確立済のSMTPサーバを使用しメール送信

    Copy right:
        (あとで書く)

    Example:
        >>> _email_sender = EmailSender(
                                    email_server_host,
                                    email_server_port,
                                    user_id,
                                    password,
                                    )

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    def __init__(
        self,
        email_server_host: str,
        email_server_port: int,
        user_id: str,
        password: str|None,
        ) -> None:
        self._email_server_host = email_server_host
        self._email_server_port = email_server_port
        self._user_id = user_id
        self._password = password

    def _create_message(
        self,
        sender_email: str,
        recipient_email: str,
        subject: str,
        body: str,
        ) -> MIMEMultipart:
        """SMTPメール文書を作成する

        Copy right:
            (あとで書く)

        Args:
            sender_email (str):    送信者メールアドレス
            recipient_email (str): 受信者メールアドレス
            subject (str):         メールタイトル
            body (str):            メール本文

        Returns:
            (MIMEMultipart): MIME形式のメールオブジェクト

        Raises:
            ...

        Example:
            >>> msg = email_sender._create_message(
                    sender_email,
                    recipient_email,
                    subject,
                    body,
                    )

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        return msg

    def send_email_via_smtp(self, sender_email: str, recipient_email: str, subject: str, body: str) -> None:
        r"""SMTP接続先サーバを使用してメール送信する

        Copy right:
            (あとで書く)

        Args:
            sender_email (str):     送信者メールアドレス
            recipient_email (str):  送信先メールアドレス
            subject (str):          メールタイトル
            body (str):             メール本文

        Returns:
            (None)

        Raises:
            - _description_

        Example:
        >>> _email_sender = EmailSender(
                                    email_server_host,
                                    email_server_port,
                                    user_id,
                                    password,
                                    )
        >>> _email_sender.send_email_via_smtp(
                                    sender_email,
                                    recipient_email,
                                    subject,
                                    body,
        )

        Notes:
            _description_

        Changelog:
            - v1.0.0 (2024/01/01): Initial release
            -
        """
        # 送信メール作成
        try:
            msg = self._create_message(sender_email, recipient_email, subject, body)
        except Exception as e:
            log_msg(f'SMTP Message作成に失敗しました: {e}',LogLevel.ERROR)
            tb = traceback.TracebackException.from_exception(e)
            log_msg(''.join(tb.format()), LogLevel.ERROR)
            raise

        # SMTPサーバ接続/メール送信
        with SmtpConnection(
            self._email_server_host,
            self._email_server_port,
            self._user_id,
            self._password,
            ) as email_server:

            # デバッグ設定
            if email_server:
                log_msg(f'email debug level: {email_server.debuglevel(1)}', LogLevel.DEBUG)

            # mail送信
            try:
                email_server.send_message(msg)
            except Exception as e:
                log_msg(f'SMTP Message送信に失敗しました: {e}',LogLevel.ERROR)
                tb = traceback.TracebackException.from_exception(e)
                log_msg(''.join(tb.format()), LogLevel.ERROR)
                raise

