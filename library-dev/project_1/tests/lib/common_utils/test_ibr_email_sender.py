"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_email_sender import (
    EmailSender,
    SmtpConnection,
)

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)


#####################################################################
# データ作成
#####################################################################
@pytest.fixture(scope='function')
def mock_smtp_connection():
    return MagicMock(spec=SmtpConnection)

class Test_email_sender_smptconnection:
    """ibr_email_sender SmptConnectionクラスのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_enter_UT_C0_normal(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: SmptConnection確立過程でのメソッド呼び出し確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストを書く
        # テストデータの設定
        email_server_host = 'smtp.example.com'
        email_server_port = 25
        user_id = 'user@example.com'
        password = 'password'
        sender_email = 'sender@example.com'
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body = 'Test Body'

        # smtplib.SMTPをモック化する
        mock_smtp = mocker.patch('smtplib.SMTP').return_value

        # ↑でmock化したsmtp.SMTPに対してmock化する必要があります
        # __enter__
        mock_ehlo = mocker.patch.object(mock_smtp, 'ehlo')
        mock_starttls = mocker.patch.object(mock_smtp, 'starttls')
        mock_auth = mocker.patch.object(mock_smtp, 'auth')
        mock_login = mocker.patch.object(mock_smtp, 'login')
        # __exit__
        mock_quit = mocker.patch.object(mock_smtp, 'quit')

        # SmtpConnection生成
        smtp_connection = SmtpConnection(
            email_server_host,
            email_server_port,
            user_id,
            password,
        )

        # コンテキストマネージャーを使用して__enter__メソッド呼び出し
        with smtp_connection as connection:
            # ここで__enter__,__exit__がよびだされる
            # connectionにはsmtplib.SMTPのインスタンスが代入される
            assert connection is mock_smtp

        # __enter__
        mock_ehlo.assert_called_once()
        mock_starttls.assert_not_called()  # 呼ばれない
        mock_auth.assert_not_called()      # 呼ばれない
        mock_login.assert_called_once()

        # __exit__
        mock_quit.assert_called_once()


    def test_enter_UT_C0_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        mock_smtp_connection,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: __enter__でException発生時の制御確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストを書く

        # caplogを使ってログメッセージをキャプチャー
        caplog.set_level(LogLevel.ERROR.value)

        # テストデータの設定
        email_server_host = 'smtp.example.com'
        email_server_port = 25
        user_id = 'user@example.com'
        password = 'password'
        sender_email = 'sender@example.com'
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body = 'Test Body'

        # 期待されるログメッセージ
        expeted_log_msg_email_smtp_connection = 'SMTPサーバへの接続/認証に失敗しました'

        # SMTPConnectionが例外をraiseするよう設定
        mocker.patch('smtplib.SMTP', side_effect=Exception)

        # SmtpConnection生成
        smtp_connection = SmtpConnection(
            email_server_host,
            email_server_port,
            user_id,
            password,
        )

        # 実行
        with pytest.raises(Exception): # noqa: SIM117 コンテキストマネージャーの検証のため許容
            with smtp_connection:
                # __enter__呼び出し
                pass

        # キャプチャーされたログメッセージを取得
        captured_log = caplog.text

        assert expeted_log_msg_email_smtp_connection in captured_log


class Test_email_sender:
    """ibr_email_sender EmailSenderクラスのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 生成したSMTPメールメッセージに対する設定値の確認
        - Exception制御
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_create_message_UT_C0_normal(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        mock_smtp_connection,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: メッセージがMIMEフォマット生成される
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの設定
        email_server_host = 'smtp.example.com'
        email_server_port = 25
        user_id = 'user@example.com'
        password = 'password'
        sender_email = 'sender@example.com'
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body = 'Test テスト'

        # メール文書作成
        email_sender = EmailSender(
            email_server_host,
            email_server_port,
            user_id,
            password,
            )
        message = email_sender._create_message(  # noqa: SLF001 メソッド検証のため許容
            sender_email,
            recipient_email,
            subject,
            body,
            )

        # 本文はBase64形式なのでDecodeしてassert
        assert message['From']    == 'sender@example.com'
        assert message['To']      == 'recipient@example.com'
        assert message['Subject'] == 'Test Subject'
        assert message.get_payload()[0].get_content_type()== 'text/plain'
        assert base64.b64decode(message.get_payload()[0].get_payload()).decode('utf-8') == 'Test テスト'


    def test_create_message_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        mock_smtp_connection,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: send_email_via_smtp()の過程でException発生,msg作成処理での例外制御確認

            Notes:
                Except発生パターンと異なる例外発生、ハンドリングを行っているので留意すること
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの設定
        email_server_host = 'smtp.example.com'
        email_server_port = 25
        user_id = 'user@example.com'
        password = 'password'
        sender_email = 'sender@example.com'
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body = 'Test Body'

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "SMTP Message作成に失敗しました"

        # EmailSenderのインスタンスを作成
        email_sender = EmailSender(
            email_server_host,
            email_server_port,
            user_id,
            password,
            )

        # MIMEMultipartとMIMETextクラスをモックして例外を発生させる
        # smtplib.SMTPをモック化する
        mocker.patch('email.mime.multipart.MIMEMultipart', side_effect=Exception)
        mocker.patch('email.mime.text.MIMEText', side_effect=Exception)
        # この呼び出し方で対処できる
        mocker.patch.object(EmailSender, '_create_message', side_effect=Exception)

        with pytest.raises(Exception):
            email_sender.send_email_via_smtp(
                sender_email,
                recipient_email,
                subject,
                body,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        assert expected_log_msg in captured_logs


    def test_send_email_via_smtp_UT_C0_normal(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        mock_smtp_connection,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: email送信制御メソッド呼び出し確認
            Notes:
                SmtpConnectionクラスとsmtplib.SMTPインスタンスをモック化
                SmtpConnectionクラスのインスタンスが__enter__メソッドで
                smtplib.SMTPのインスタンスを返し、そのインスタンスのsend_messageメソッドが
                呼び出されるため、SmtpConnectionクラスのモック化時に
                その返り値としてsmtplib.SMTPのモックインスタンスを設定する必要があります。
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの設定
        email_server_host = 'smtp.example.com'
        email_server_port = 25
        user_id = 'user@example.com'
        password = 'password'
        sender_email = 'sender@example.com'
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body = 'Test Body'

        # Notes参照
        mock_smtp_instance = mocker.MagicMock()
        mocker.patch(
            'src.lib.common_utils.ibr_email_sender.SmtpConnection',
            return_value=mocker.MagicMock(__enter__=mocker.MagicMock(return_value=mock_smtp_instance)),
            )

        # EmailSenderのインスタンスを作成
        email_sender = EmailSender(
            email_server_host,
            email_server_port,
            user_id,
            password,
            )

        # send_email_via_smtpメソッドを呼び出し
        email_sender.send_email_via_smtp(
            sender_email,
            recipient_email,
            subject,
            body,
        )

        mock_smtp_instance.send_message.assert_called_once()


    def test_send_email_via_smtp_UT_C0_raise_exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        mock_smtp_connection,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: 例外発生時の制御確認
            Notes:
                EmailSenderクラス内でSmtpConnectionクラスを使用してメールを送信しています。
                smtplib.SMTP.send_messageメソッドが例外を発生させるようにモック化するのではなく
                SmtpConnectionクラスのコンテキストマネージャーが返す
                smtplib.SMTPインスタンスのsend_messageメソッドをモック化する必要があります

                1.SmtpConnectionクラスの__enter__メソッドが返すsmtplib.SMTPインスタンスのsend_messageメソッドを
                モック化します
                2.  smtplib.SMTP.send_messageのモック化ではなく、SmtpConnectionクラスのモックインスタンスを作成し
                そのインスタンスの__enter__メソッドが返すオブジェクトのsend_messageメソッドをモック化します。
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの設定
        email_server_host = 'smtp.example.com'
        email_server_port = 25
        user_id = 'user@example.com'
        password = 'password'
        sender_email = 'sender@example.com'
        recipient_email = 'recipient@example.com'
        subject = 'Test Subject'
        body = 'Test Body'

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "SMTP Message送信に失敗しました"

        # Notes参照
        mock_smtp_instance = mocker.MagicMock()
        mock_smtp_instance.send_message.side_effect = Exception
        mocker.patch(
            'src.lib.common_utils.ibr_email_sender.SmtpConnection',
            return_value=mocker.MagicMock(__enter__=mocker.MagicMock(return_value=mock_smtp_instance)),
            )

        # EmailSenderのインスタンスを作成
        email_sender = EmailSender(
            email_server_host,
            email_server_port,
            user_id,
            password,
            )

        with pytest.raises(Exception):
            # send_email_via_smtpメソッドを呼び出し
            email_sender.send_email_via_smtp(
                sender_email,
                recipient_email,
                subject,
                body,
            )
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        assert expected_log_msg in captured_logs

