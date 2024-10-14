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
from src.lib.common_utils.ibr_get_config import (
    Config,
)
from src.lib.common_utils.ibr_logger_package import (
    LoggerPackage,
    SingletonType,
)
from src.lib.common_utils.ibr_toml_loader import TomlParser

#####################################################################
# テスト実行環境セットアップ
#####################################################################
# このテストはConfig自体がテスト対象という事案
#from src.lib.common_utils.ibr_get_config import Config
#
#package_path = Path(__file__)
#config = Config.load(package_path)
#
#log_msg = config.log_message
#log_msg(str(config), LogLevel.DEBUG)

#####################################################################
# データ作成
#####################################################################
@pytest.fixture(scope='function')
def  _reset_singleton_instance():
    # シングルトンインスタンスをリセット
    SingletonType.reset_instances()
    yield
    # 念のためテスト後にもリセット
    SingletonType.reset_instances()


class Test_config_toml:
    """import csv_to_rowのテスト全体をまとめたClass

    使用しているパーツは別のモジュールで実装していることから
    このテストではすでにテスト済パーツの改の検証は省略し
    制御及びConfigオブジェクト格納状況を検証する。

    - 実行環境判別ラベルの取得
    - common_config, package_configのdict取得
    - カスタムパッケージオブジェクトの取得

    C0: 命令カバレッジ
        - Configからの値取得確認
        - 例外発生
            - gethostnameでのException
            - common_configでのException
            - package_configでのException
            - loggerでのException
    C1: 分岐カバレッジ
    C2: 条件カバレッジ
    """
    def test_config_load_UT_C0_set_config(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Config生成、格納Object確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # 定義ファイルのメンテナンスや環境に依存あり、どうするかの検討を要する
        #expected_common_config = {'logger_path': {'LOGGER_DEF_FILE': 'tests/def/ibrUtilsLoggingHelper/logging_TimedRotate.json', 'LOGGER_MSG_FILE': 'tests/def/ibrUtilsLoggingHelper/config_MessageList.toml'}, 'input_file_path': {'UPDATE_EXCEL_PATH': 'tests/share/receive'}, 'output_file_path': {'SEND_REFERENCE_MASTER_PATH': 'tests/share/receive'}}
        expected_common_config ={'logger_path': {'LOGGER_DEF_FILE': 'src/def/ibrUtilsLoggingHelper/logging_TimedRotate.json', 'LOGGER_MSG_FILE': 'src/def/ibrUtilsLoggingHelper/config_MessageList.toml'}, 'decision_table_path': {'DECISION_TABLE_PATH': 'src/def/decision_table'}, 'optional_path': {'LONGTERM_ACCUM_PATH': 'src/work/longterm_accm', 'SHORTTERM_ACCUM_PATH': 'src/work/shortterm_accm', 'TABLE_PATH': 'src/table', 'SHARE_RECEIVE_PATH': 'src/share/receive', 'SHARE_SEND_PATH': 'src/share/send', 'ARCHIVES_REFERNCE_SNAPSHOT_PATH': 'src/archives/reference_snapshots', 'ARCHIVES_REQUEST_SNAPSHOT_PATH': 'src/archives/request_snapshots', 'ARCHIVES_REFERENCE_DIFFS_PATH': 'src/archives/reference_diffs', 'ARCHIVES_CSV_FILES_PATH': 'src/archives/csv_files'}}
        expected_package_config = {'test': {'local_test': 'test'}}

        package_path = Path(__file__)
        config = Config.load(package_path)

        print(f'{config.common_config}')

        assert config.env == 'local'
        assert config.common_config == expected_common_config
        assert config.package_config == expected_package_config

        # logger.name 確認
        log_msg = config.log_message
        expected_1 = '[INFO] common_utils.test_ibr_get_config::test_config_load_UT_C0_set_config'
        expected_2 = 'test_1'
        log_msg('test_1')
        captured = capfd.readouterr()
        assert expected_1 in captured.out
        assert expected_2 in captured.out


    def test_config_load_UT_C0_raise_exception_gethostname(
        self,
        mocker: MagicMock,
        capfd: pytest.LogCaptureFixture,
        caplog: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Config生成、格納Object確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "実行環境判定処理に失敗しました"

        # 最初の呼び出しでExceptionを発生させる
        mocker.patch('socket.gethostname', side_effect=Exception)

        package_path = Path(__file__)
        with pytest.raises(Exception):
            assert Config.load(package_path) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_config_load_UT_C0_raise_exception_common_config(
        self,
        mocker: MagicMock,
        capfd: pytest.LogCaptureFixture,
        caplog: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Config生成、格納Object確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "common_config取得に失敗しました"

        # 最初の呼び出しでExceptionを発生させる
        mocker.patch.object(TomlParser, 'parse_toml_file', side_effect=[Exception("common_config error"), None])

        package_path = Path(__file__)
        with pytest.raises(Exception):
            assert Config.load(package_path) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_config_load_UT_C0_raise_exception_package_config(
        self,
        mocker: MagicMock,
        capfd: pytest.LogCaptureFixture,
        caplog: pytest.LogCaptureFixture,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Config生成、格納Object確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "package_config取得に失敗しました"

        # 2つ目の呼び出しでExceptionを発生させる
        mocker.patch.object(TomlParser, 'parse_toml_file', side_effect=[None, Exception("package_config error"), None])

        package_path = Path(__file__)
        with pytest.raises(Exception):
            assert Config.load(package_path) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_config_load_UT_C0_raise_exception_loadpackage(
        self,
        mocker: MagicMock,
        capfd: pytest.LogCaptureFixture,
        caplog: pytest.LogCaptureFixture,
        _reset_singleton_instance,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: Config生成、格納Object確認
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        print(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "カスタムロガーインスタンス生成に失敗しました"

        mocker.patch.object(LoggerPackage, '__init__', side_effect=Exception)

        package_path = Path(__file__)
        with pytest.raises(Exception):
            assert Config.load(package_path) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"























