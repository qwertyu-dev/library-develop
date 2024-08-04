"""テスト実施方法

$ pwd
/developer/library_dev/project_1

# pytest結果をファイル出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py > tests/log/pytest_result.log

# pytest結果を標準出力する場合
$ pytest -lv ./tests/lib/common_utils/test_ibr_csv_helper.py
"""
import logging
from pathlib import Path

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_enums import (
    DigitsNumberforUnixtime,
    ExecEnvironment,
    LogLevel,
)

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

#####################################################################
# データ作成
#####################################################################
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

class Test_import_csv_to_row:
    """ibr_enums.pyのテスト全体をまとめたClass

    - 値の存在確認
        - Enumの各要素が期待通りの値を持っているかを確認します1。例えば、LogLevel.DEBUGがlogging.DEBUGと等しいかどうかを確認することができます
    - 型の確認
        - Enumの要素が正しい型(この場合はEnum)であることを確認します
    - 全要素の列挙
        - Enumが期待通りのすべての要素を持っていることを確認します

    C0: 命令カバレッジ
    C1: 分岐カバレッジ
        - 引数カバレッジ
    C2: 条件カバレッジ
    """

    def test_log_level_UT_C0_values(self) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        assert LogLevel.DEBUG.value == logging.DEBUG
        assert LogLevel.INFO.value == logging.INFO
        assert LogLevel.WARNING.value == logging.WARNING
        assert LogLevel.ERROR.value == logging.ERROR
        assert LogLevel.CRITICAL.value == logging.CRITICAL


    def test_exec_environment_UT_C0_values(self) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        assert ExecEnvironment.HOSTNAME_PRODUCTION.value == 'production'
        assert ExecEnvironment.HOSTNAME_REGRESSION.value == 'regression'
        assert ExecEnvironment.HOSTNAME_DEVELOP.value == 'develop'
        assert ExecEnvironment.HOSTNAME_LOCAL.value == 'local'


    def test_digits_number_for_unix_UT_C0_values(self) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        assert DigitsNumberforUnixtime.DIGITS_10.value == 10  # noqa: PLR2004
        assert DigitsNumberforUnixtime.DIGITS_13.value == 13  # noqa: PLR2004
        assert DigitsNumberforUnixtime.DIGITS_16.value == 16  # noqa: PLR2004


    def test_enum_UT_C0_types(self) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        assert isinstance(LogLevel.DEBUG, LogLevel)
        assert isinstance(ExecEnvironment.HOSTNAME_PRODUCTION, ExecEnvironment)
        assert isinstance(DigitsNumberforUnixtime.DIGITS_10, DigitsNumberforUnixtime)


    def test_enums_UT_C0_elements(self) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        assert len(LogLevel) == 5                 # noqa: PLR2004
        assert len(ExecEnvironment) == 4          # noqa: PLR2004
        assert len(DigitsNumberforUnixtime) == 3  # noqa: PLR2004





