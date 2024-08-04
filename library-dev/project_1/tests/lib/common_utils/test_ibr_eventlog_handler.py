"""テスト実施方法

# project topディレクトリから実行する
$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from src.lib.common_utils.ibr_enums import LogLevel

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_eventlog_handler import WindowsEventLogger

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class Test_event_log_hander:
    """ibr_event_log_handerのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_write_info_log_UT_C0_write_normal(
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
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # win32conとwin32evtlogutil.ReportEventをmockする
        mock_win32con = mocker.patch('src.lib.common_utils.ibr_eventlog_handler.win32con', create=True)
        mock_report_event = mocker.patch('src.lib.common_utils.ibr_eventlog_handler.win32evtlogutil.ReportEvent')

        # EVENTLOG_INFORMATION_TYPEをmockする
        mock_win32con.EVENTLOG_INFORMATION_TYPE = 0x0001 # ダミーの整数値

        # 結果定義,関数実行
        WindowsEventLogger.write_info_log('MySource test', 1002, ['This is a test', 'info revel'])
        mock_report_event.assert_called_once_with(
            Source='MySource test',
            EventID=1002,
            EventType=0x0001,
            Strings=['This is a test', 'info revel'],
            Data=None,
        )


    def test_write_error_log_UT_C0_write_normal(
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
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # win32conとwin32evtlogutil.ReportEventをmockする
        mock_win32con = mocker.patch('src.lib.common_utils.ibr_eventlog_handler.win32con', create=True)
        mock_report_event = mocker.patch('src.lib.common_utils.ibr_eventlog_handler.win32evtlogutil.ReportEvent')

        # EVENTLOG_INFORMATION_TYPEをmockする
        mock_win32con.EVENTLOG_INFORMATION_TYPE = 0x0002 # ダミーの整数値

        WindowsEventLogger.write_info_log('MySource test', 1003, ['This is a error', 'error revel'])
        mock_report_event.assert_called_once_with(
            Source='MySource test',
            EventID=1003,
            EventType=0x0002,
            Strings=['This is a error', 'error revel'],
            Data=None,
        )


    def test_write_eventlog_UT_C0_write_normal(
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
                - テストシナリオ:
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # win32conとwin32evtlogutil.ReportEventをmockする
        mock_win32con = mocker.patch('src.lib.common_utils.ibr_eventlog_handler.win32con', create=True)
        mock_report_event = mocker.patch('src.lib.common_utils.ibr_eventlog_handler.win32evtlogutil.ReportEvent')

        # EVENTLOG_INFORMATION_TYPEをmockする
        mock_win32con.EVENTLOG_INFORMATION_TYPE = 0x0003 # ダミーの整数値

        # 結果定義,関数実行
        WindowsEventLogger.write_info_log('MySource test', 10003, ['This is a warning', 'warning revel'])
        mock_report_event.assert_called_once_with(
            Source='MySource test',
            EventID=10003,
            EventType=0x0003,
            Strings=['This is a warning', 'warning revel'],
            Data=None,
        )
