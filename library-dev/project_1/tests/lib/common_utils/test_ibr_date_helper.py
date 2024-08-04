"""テスト実施方法

$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock

import pytest

#####################################################################
# テスト対象モジュール import, プロジェクトTopディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_date_helper import (
    convert_unixtime_to_jst,
    convert_with_no_timezone_to_jst,
    convert_with_timezone_to_jst,
    load_calendar_file,
    _convert_date_to_string,
    is_bank_business_day,
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

JST = timezone(timedelta(hours=+9), 'JST')


#####################################################################
# データ作成
#####################################################################
# このテストシナリオではfixtureを使用しない
#@pytest.fixture(scope='function')
#def csv_file_normal(tmp_path: Path) -> str:
#    # setup
#
#    # 実行
#    #yield
#
#    # tear down
#    # Notes:
#    #   pytestのtmp系はデフォルトで3セッションのみ維持します
#    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

class Test_convert_with_no_timezone_to_jst:
    """import convert_with_no_timezone_to_jstのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 与えられた文字列に対して適切なformatによる変換
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - 与えられた文字列とformatパターンが合致しない
    C2: 条件カバレッジ
        - 文字列がNoneの場合
        - フォーマット文字列がNoneの場合
    """

    def test_convert_with_no_timezone_to_jst_UT_C0_str_only(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00'
        expected = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        result = convert_with_no_timezone_to_jst(target_string)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_with_no_timezone_to_jst_UT_C0_str_format(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00'
        target_format = '%Y/%m/%d %H:%M:%S'
        expected = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        result = convert_with_no_timezone_to_jst(target_string, target_format)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_with_no_timezone_to_jst_UT_C1_str_format_match_irregular(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformatフォーマットが一致するがやや不自然
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '2024/0103 00:00:00'
        target_format = '%Y/%m%d %H:%M:%S'
        expected = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        result = convert_with_no_timezone_to_jst(target_string, target_format)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_with_no_timezone_to_jst_UT_C1_str_format_not_match(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformatフォーマットが一致するが一致しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00'
        target_format = '%Y-%m-%d %H:%M:%S'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_no_timezone_to_jst(target_string, target_format)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_convert_with_no_timezone_to_jst_UT_C2_str_format_None(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対しNone
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_format = '%Y-%m-%d %H:%M:%S'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_no_timezone_to_jst(None, target_format)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_convert_with_no_timezone_to_jst_UT_C2_format_None(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - formatにNone
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_no_timezone_to_jst(target_string, None)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"

class Test_convert_with_timezone_to_jst:
    """import convert_with_no_timezone_to_jstのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 与えられた文字列に対して適切なformatによる変換
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - 与えられた文字列とformatパターンが合致しない
            - 与えられた文字列(tzなし)とformatパターンが合致しない
    C2: 条件カバレッジ
        - 文字列がNoneの場合
        - フォーマット文字列がNoneの場合
    """

    def test_convert_with_timezone_to_jst_UT_C0_str_only(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00+0000'
        expected = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        result = convert_with_timezone_to_jst(target_string)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_with_timezone_to_jst_UT_C1_str_format_not_match(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - 時間文字列に対してformatフォーマットが一致するが一致しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00+0000'
        target_format = '%Y-%m-%d %H:%M:%S%z'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_timezone_to_jst(target_string, target_format)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_convert_with_timezone_to_jst_UT_C1_non_tz_str_format_not_match(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - 時間文字列(tzなし)に対してformatフォーマットが一致するが一致しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00'
        target_format = '%Y-%m-%d %H:%M:%S%z'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_timezone_to_jst(target_string, target_format)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_convert_with_timezone_to_jst_UT_C2_target_str_None(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対しNone
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_format = '%Y-%m-%d %H:%M:%S'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_timezone_to_jst(None, target_format)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_convert_with_timezone_to_jst_UT_C2_format_None(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - formatにNone
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        target_string = '2024/01/03 00:00:00'
        _ = datetime(2024, 1, 3, 9, 0, 0, tzinfo=JST)

        # ValueError発生を想定
        _ = convert_with_timezone_to_jst(target_string, None)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


class Test_unixtime_to_jst:
    """import unixtime_to_jstのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 与えられた文字列10桁
        - 与えられた文字列13桁
        - 与えられた文字列16桁
        - 与えられた文字列0桁
        - 例外発生
        - 文字列がNoneの場合
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - C0で対応済
    C2: 条件カバレッジ
            - C0で対応済
    """

    def test_convert_unixtime_to_jst_UT_C0_digits10(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '1615860122'
        expected = datetime(2021, 3, 16, 11, 2, 2, tzinfo=JST)

        result = convert_unixtime_to_jst(target_string)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_unixtime_to_jst_UT_C0_digits13(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '1615860122000'
        expected = datetime(2021, 3, 16, 11, 2, 2, tzinfo=JST)

        result = convert_unixtime_to_jst(target_string)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_unixtime_to_jst_UT_C0_digits16(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)


        # 結果定義,関数実行
        target_string = '1615860122000000'
        expected = datetime(2021, 3, 16, 11, 2, 2, tzinfo=JST)

        result = convert_unixtime_to_jst(target_string)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {expected}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, datetime)
        assert result == expected


    def test_convert_unixtime_to_jst_UT_C0_digits0(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "unixtime_strは10/13/16桁のいずれかでなければなりません"
        expected = None

        # 結果定義,関数実行
        target_string = '0'
        result = convert_unixtime_to_jst(target_string)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is expected


    def test_convert_unixtime_to_jst_UT_C0_raise_exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"
        expected = None

        # 結果定義,関数実行
        target_string = '1615860122'
        mocker.patch('src.lib.common_utils.ibr_date_helper._fromtimestamp_wrapper', side_effect=Exception)
        result = convert_unixtime_to_jst(target_string)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is expected


    def test_convert_unixtime_to_jst_UT_C0_unixtime_none(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 時間文字列に対してformat指定しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # 期待されるログメッセージ
        expected = None

        # 結果定義,関数実行
        target_string = None
        result = convert_unixtime_to_jst(target_string)

        # ログメッセージが期待通りのものか確認
        assert result is expected

class Test_load_calendar_file:
    """load_calendar_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ

    追加検討テストケース
        カレンダーファイルが空の場合のテスト
        カレンダーファイルに重複する日付が存在する場合のテスト
        カレンダーファイルに無効な日付形式が含まれる場合のテスト
    """
    def test_load_calendar_file_UT_C0_normal(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 指定したカレンダファイルのロード及び内容の妥当性検証
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "calendar.txt"
        with calendar_file_path.open("w") as f:
            f.write("cl=2024/01/01\n")
            f.write("op=2024/01/02\n")

        # 期待される戻り値
        expected_closed_days = {"2024/01/01"}
        expected_operation_days = {"2024/01/02"}

        # 関数の実行
        closed_days, operation_days = load_calendar_file(calendar_file_path)

        # 結果の検証
        assert closed_days == expected_closed_days
        assert operation_days == expected_operation_days

    def test_load_calendar_file_UT_C1_file_not_found(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - 指定した銀行カレンダーファイルが存在しない
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "nonexistent.txt"

        # 例外の検証
        with pytest.raises(FileNotFoundError):
            load_calendar_file(calendar_file_path)

    def test_load_calendar_file_UT_C1_invalid_format(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - カレンダーフォーマットに不備あり
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "invalid.txt"
        with calendar_file_path.open("w") as f:
            f.write("invalid=2024/01/01\n")

        # 例外の検証
        with pytest.raises(ValueError):
            load_calendar_file(calendar_file_path)

class Test_convert_date_to_string:
    """_convert_date_to_stringのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ

    追加検討テストケース
        - 日付の境界値のテスト(例: 月の最初の日、月の最後の日、うるう年の2月29日など)
        - タイムゾーン付きの日付オブジェクトを渡した場合のテスト
        - 日付文字列の前後に空白がある場合のテスト
    """
    def test_convert_date_to_string_UT_C0_datetime(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - datetime型で日付パラメータ指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        date = datetime(2024, 1, 1)

        # 期待される戻り値
        expected_result = "2024/01/01"

        # 関数の実行
        result = _convert_date_to_string(date)

        # 結果の検証
        assert result == expected_result

    def test_convert_date_to_string_UT_C0_string(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - str型で日付パラメータ指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        date = "2024/01/01"

        # 期待される戻り値
        expected_result = "2024/01/01"

        # 関数の実行
        result = _convert_date_to_string(date)

        # 結果の検証
        assert result == expected_result

    def test_convert_date_to_string_UT_C1_invalid_string(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - 指定フォーマット以外で日付文字列指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        date = "2024-01-01"

        # 例外の検証
        with pytest.raises(ValueError):
            _convert_date_to_string(date)

    def test_convert_date_to_string_UT_C1_invalid_type(self):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - datetimeでもstrでもない型で指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        date = 20240101

        # 例外の検証
        with pytest.raises(TypeError):
            _convert_date_to_string(date)

class Test_is_bank_business_day:
    """is_bank_business_dayのテスト全体をまとめたClass

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
    C2: 条件カバレッジ

    追加検討テストケース
        - カレンダーファイルに重複する日付が存在する場合のテスト
        - カレンダーファイルに無効な日付形式が含まれる場合のテスト
        - 日付の境界値のテスト(例: 月の最初の日、月の最後の日、うるう年の2月29日など
        - タイムゾーン付きの日付オブジェクトを渡した場合のテスト
        - 日付文字列の前後に空白がある場合のテスト
    """
    def test_is_bank_business_day_UT_C0_operation_day(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 銀行カレンダー上で営業日定義をパラメータ指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "calendar.txt"
        with calendar_file_path.open("w") as f:
            f.write("cl=2024/01/01\n")
            f.write("op=2024/01/02\n")

        date = "2024/01/02"

        # 期待される戻り値
        expected_result = True

        # 関数の実行
        result = is_bank_business_day(date, calendar_file_path)

        # 結果の検証
        assert result is expected_result

    def test_is_bank_business_day_UT_C0_closed_day(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 銀行カレンダー上で休業日定義をパラメータ指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "calendar.txt"
        with calendar_file_path.open("w") as f:
            f.write("cl=2024/01/01\n")
            f.write("op=2024/01/02\n")

        date = "2024/01/01"

        # 期待される戻り値
        expected_result = False

        # 関数の実行
        result = is_bank_business_day(date, calendar_file_path)

        # 結果の検証
        assert result is expected_result

    def test_is_bank_business_day_UT_C0_unknown_day(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - 銀行カレンダー上にない日付を指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "calendar.txt"
        with calendar_file_path.open("w") as f:
            f.write("cl=2024/01/01\n")
            f.write("op=2024/01/02\n")

        date = "2024/01/03"

        # 期待される戻り値
        expected_result = None

        # 関数の実行
        result = is_bank_business_day(date, calendar_file_path)

        # 結果の検証
        assert result is expected_result

    def test_is_bank_business_day_UT_C1_file_not_found(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - 存在しない銀行カレンダーを指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "nonexistent.txt"
        date = "2024/01/01"

        # 例外の検証
        with pytest.raises(FileNotFoundError):
            is_bank_business_day(date, calendar_file_path)

    def test_is_bank_business_day_UT_C1_invalid_date_format(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - 許容されていないカレンダーフォーマットで指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "calendar.txt"
        with calendar_file_path.open("w") as f:
            f.write("cl=2024/01/01\n")
            f.write("op=2024/01/02\n")

        date = "2024-01-01"

        # 例外の検証
        with pytest.raises(ValueError):
            is_bank_business_day(date, calendar_file_path)

    def test_is_bank_business_day_UT_C1_invalid_date_type(self, tmpdir):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 異常系/UT
                - 許容されていない型を指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テストデータの準備
        calendar_file_path = Path(tmpdir) / "calendar.txt"
        with calendar_file_path.open("w") as f:
            f.write("cl=2024/01/01\n")
            f.write("op=2024/01/02\n")

        date = 20240101

        # 例外の検証
        with pytest.raises(TypeError):
            is_bank_business_day(date, calendar_file_path)

