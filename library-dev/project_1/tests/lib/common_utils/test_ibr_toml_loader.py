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
import toml
import yaml

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_toml_loader import TomlParser

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

#####################################################################
# データ作成
#####################################################################
@pytest.fixture(scope='function')
def production_config():
    # setup
    return {
        "production": {
            "logger_path": {
                "LOGGER_DEF_FILE": "def/ibrUtilsLoggingHelper/logging_TimedRotate.json",
                "LOGGER_MSG_FILE": "def/ibrUtilsLoggingHelper/config_MessageList.toml",
            },
            "input_file_path": {
                "UPDATE_EXCEL_PATH": "share/receive",
            },
            "output_file_path": {
                "SEND_REFERENCE_MASTER_PATH": "share/receive",
            },
        },
    }
    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def empty_config():
    # setup
    return {}
    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


@pytest.fixture(scope='function')
def toml_file_normal(tmp_path: Path, production_config: str) -> Path:
    """データ作成処理

    tomlファイル作成

    Args:
        tmp_path (Path): データ出力先
        production_config(str): toml定義データを作成するためのデータ

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    file_path = tmp_path / 'test_file_1.toml'
    with file_path.open(mode='w') as f:
        toml.dump(production_config, f)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def toml_file_empty(tmp_path: Path, empty_config: str) -> Path:
    """データ作成処理

    tomlファイル作成

    Args:
        tmp_path (Path): データ出力先
        empty_config(str): toml定義データを作成するためのデータ

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    file_path = tmp_path / 'test_file_2.toml'
    with file_path.open(mode='w') as f:
        toml.dump(empty_config, f)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def yaml_file_normal(tmp_path: Path, production_config: str) -> Path:
    """データ作成処理

    tomlファイル作成

    Args:
        tmp_path (Path): データ出力先
        production_config(str): toml定義データを作成するためのデータ

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    file_path = tmp_path / 'test_file_3.toml'
    with file_path.open(mode='w') as f:
        yaml.dump(production_config, f)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


class Test_parse_toml_file:
    """import csv_to_rowのテスト全体をまとめたClass

    tomlを読み込みdictを生成する

    C0: 命令カバレッジ
        - ファイルパスをstrで与え,存在する/読み取り権限がある
        - ファイルパスをPathで与え,存在する/読み取り権限がある
        - 例外発生
            - FileNotFound
            - PermissionError
            - IsAdirectoryError
            - toml.decoder.TomlDecodeError
            - Exception
    C1: 分岐カバレッジ
        - 引数カバレッジ  # 該当なし
    C2: 条件カバレッジ
        - tomlファイル内容カバレッジ
            - tomlファイルの中身がtomlの場合  # C0で検証済
            - tomlファイルの中身が空の場合
            - tomlファイルの中身がtomlでない場合
    """

    def test_parse_toml_file_UT_C0_specify_str_path(
        self,
        toml_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {toml_file_normal}', LogLevel.DEBUG)

        # strで与える
        toml_file_normal = str(toml_file_normal)

        # 結果定義,関数実行
        expected = {'production': {'input_file_path': {'UPDATE_EXCEL_PATH': 'share/receive'},
                'logger_path': {'LOGGER_DEF_FILE': 'def/ibrUtilsLoggingHelper/logging_TimedRotate.json',
                                'LOGGER_MSG_FILE': 'def/ibrUtilsLoggingHelper/config_MessageList.toml'},
                'output_file_path': {'SEND_REFERENCE_MASTER_PATH': 'share/receive'}}}
        result = TomlParser.parse_toml_file(toml_file_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, dict), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_parse_toml_file_UT_C0_specify_Path(
        self,
        toml_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {toml_file_normal}', LogLevel.DEBUG)

        # strで与える
        toml_file_normal = Path(toml_file_normal)

        # 結果定義,関数実行
        expected = {'production': {'input_file_path': {'UPDATE_EXCEL_PATH': 'share/receive'},
                'logger_path': {'LOGGER_DEF_FILE': 'def/ibrUtilsLoggingHelper/logging_TimedRotate.json',
                                'LOGGER_MSG_FILE': 'def/ibrUtilsLoggingHelper/config_MessageList.toml'},
                'output_file_path': {'SEND_REFERENCE_MASTER_PATH': 'share/receive'}}}
        result = TomlParser.parse_toml_file(toml_file_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, dict), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_parse_toml_file_UT_C0_raise_FileNotFoundError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        toml_file_normal,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - FileNotFoundError例外発生/mocker.patch,side_effectで差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'toml file path: {toml_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # ファイルの存在自体は結果に影響を与えない
        toml_file_normal = Path(toml_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "can not get target files"

        # 結果定義,関数実行
        # unittest.mock.patchは、インスタンスメソッドやクラスメソッドをモック化することができますが
        # 静的メソッド(@staticmethodでデコレートされたメソッド)を直接モック化することはできません。
        # 従ってclass自体をMock化しautospecで構造は維持し、その上で明示的にstaticmethodをside_effectで再定義しています
        #mock_class = mocker.patch('src.lib.common_utils.ibr_toml_loader.TomlParser', autospec=True)
        #mock_class.parse_toml_file.side_effect = FileNotFoundError

        # モック化する関数を指定
        mocker.patch('pathlib.Path.open', side_effect=FileNotFoundError)
        with pytest.raises(FileNotFoundError):
            _ = TomlParser.parse_toml_file(toml_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_parse_toml_file_UT_C0_raise_PermissionError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        toml_file_normal,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - PermissionError例外発生/mocker.patch,side_effectで差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'toml file path: {toml_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        toml_file_normal = Path(toml_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "No permission to read the file"

        # 結果定義,関数実行
        # unittest.mock.patchは、インスタンスメソッドやクラスメソッドをモック化することができますが
        # 静的メソッド(@staticmethodでデコレートされたメソッド)を直接モック化することはできません。
        # 従ってclass自体をMock化しautospecで構造は維持し、その上で明示的にstaticmethodをside_effectで再定義しています
        #mock_class = mocker.patch('src.lib.common_utils.ibr_toml_loader.TomlParser', autospec=True)
        #mock_class.parse_toml_file.side_effect = PermissionError

        # モック化する関数を指定
        mocker.patch('pathlib.Path.open', side_effect=PermissionError)
        with pytest.raises(PermissionError):
            _ = TomlParser.parse_toml_file(toml_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_parse_toml_file_UT_C0_raise_IsADirectoryError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        toml_file_normal,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - IsADirectory例外発生/mocker.patch,side_effectで差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'toml file path: {toml_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        toml_file_normal = Path(toml_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "The specified path is a directory, not a file"

        # 結果定義,関数実行
        # unittest.mock.patchは、インスタンスメソッドやクラスメソッドをモック化することができますが
        # 静的メソッド(@staticmethodでデコレートされたメソッド)を直接モック化することはできません。
        # 従ってclass自体をMock化しautospecで構造は維持し、その上で明示的にstaticmethodをside_effectで再定義しています
        #mock_class = mocker.patch('src.lib.common_utils.ibr_toml_loader.TomlParser', autospec=True)
        #mock_class.parse_toml_file.side_effect = PermissionError

        # モック化する関数を指定
        mocker.patch('pathlib.Path.open', side_effect=IsADirectoryError)
        with pytest.raises(IsADirectoryError):
            _ = TomlParser.parse_toml_file(toml_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_parse_toml_file_UT_C0_raise_TypeError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        toml_file_normal,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - tomlファイル形式以外を与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'toml file path: {toml_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        toml_file_normal = Path(toml_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Found invalid character in key"

        # 結果定義,関数実行
        # unittest.mock.patchは、インスタンスメソッドやクラスメソッドをモック化することができますが
        # 静的メソッド(@staticmethodでデコレートされたメソッド)を直接モック化することはできません。
        # 従ってclass自体をMock化しautospecで構造は維持し、その上で明示的にstaticmethodをside_effectで再定義しています
        #mock_class = mocker.patch('src.lib.common_utils.ibr_toml_loader.TomlParser', autospec=True)
        #mock_class.parse_toml_file.side_effect = PermissionError

        # モック化する関数を指定
        mocker.patch('pathlib.Path.open', side_effect=TypeError)
        with pytest.raises(TypeError):
            _ = TomlParser.parse_toml_file(toml_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_parse_toml_file_UT_C0_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        toml_file_normal,
        ):
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - Exception例外発生/mocker.patch,side_effectで差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'toml file path: {toml_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        toml_file_normal = Path(toml_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        # unittest.mock.patchは、インスタンスメソッドやクラスメソッドをモック化することができますが
        # 静的メソッド(@staticmethodでデコレートされたメソッド)を直接モック化することはできません。
        # 従ってclass自体をMock化しautospecで構造は維持し、その上で明示的にstaticmethodをside_effectで再定義しています
        #mock_class = mocker.patch('src.lib.common_utils.ibr_toml_loader.TomlParser', autospec=True)
        #mock_class.parse_toml_file.side_effect = PermissionError

        # モック化する関数を指定
        mocker.patch('pathlib.Path.open', side_effect=Exception)
        with pytest.raises(Exception):
            _ = TomlParser.parse_toml_file(toml_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_parse_toml_file_UT_C2_toml_file_empty(
        self,
        toml_file_empty: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: tomlファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {toml_file_empty}', LogLevel.DEBUG)

        # strで与える
        toml_file_normal = Path(toml_file_empty)

        # 結果定義,関数実行
        expected = {}
        result = TomlParser.parse_toml_file(toml_file_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, dict), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

