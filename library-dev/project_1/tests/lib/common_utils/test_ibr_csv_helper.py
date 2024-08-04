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

import pandas as pd
import pytest

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_csv_helper import (
    _write_records,
    create_cnt_file,
    get_file_record_count,
    import_csv_to_dataframe,
    import_csv_to_row,
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
def csv_file_normal(tmp_path: Path) -> Path:
    """データ作成処理

    CSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = "Name,Age,Gender\nJohn,25,Male\nJane,30,Female"
    file_path = tmp_path / 'test_file_1.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def csv_file_empty(tmp_path: Path) -> Path:
    """データ作成処理

    空のCSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = ""
    file_path = tmp_path / 'test_file_2.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def csv_file_header_only(tmp_path: Path) -> Path:
    """データ作成処理

    へダーだけCSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = "Name,Age,Gender"
    file_path = tmp_path / 'test_file_3.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def csv_file_data_only(tmp_path: Path) -> Path:
    """データ作成処理

    へダーなし、データだけのCSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = "John,25,Male\nJane,30,Female"
    file_path = tmp_path / 'test_file_4.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def csv_file_tab_sep(tmp_path: Path) -> Path:
    """データ作成処理

    タブ区切りCSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = "Name\tAge\tGender\nJohn\t25\tMale\nJane\t30\tFemale"
    file_path = tmp_path / 'test_file_5.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def csv_file_pipe_sep(tmp_path: Path) -> Path:
    """データ作成処理

    縦棒区切りCSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = "Name|Age|Gender\nJohn|25|Male\nJane|30|Female"
    file_path = tmp_path / 'test_file_6.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


@pytest.fixture(scope='function')
def csv_file_space_sep(tmp_path: Path) -> Path:
    """データ作成処理

    ブランク区切りCSVファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    content = "Name Age Gender\nJohn 25 Male\nJane 30 Female"
    file_path = tmp_path / 'test_file_7.csv'
    file_path.write_text(content)

    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


@pytest.fixture(scope='function')
def binary_file(tmp_path: Path) -> Path:
    """データ作成処理

    バイナリファイル作成

    Args:
        tmp_path (Path): データ出力先

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    # 複数行のバイナリデータを作成し、ファイルに書き込む
    data_line_1 = b'\x01\x02\x03\x04\x05\n'  # 改行で行を区切る例
    data_line_2 = b'\x06\x07\x08\x09\x0A'
    data_line_3 = b'\x0B\x0C\x0D\x0E\x0F\n'
    binary_data_list = [data_line_1, data_line_2, data_line_3]

    file_path = tmp_path / 'test_file_8.bin'
    with file_path.open(mode='wb') as binary_file:
        for binary_data in binary_data_list:
            binary_file.write(binary_data)
    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def cnt_file_writable() -> Path:
    """データ作成処理

    cnvファイル作成パスを返す

    Args:
        ...

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    return  Path('tests/share/send/tmp_1.cnt')

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def cnt_file_non_exists_cnt_dir() -> Path:
    """データ作成処理

    存在しないディレクトリを含んだファイル作成Pathを返す

    Args:
        ...

    Returns:
        str: 作成したデータへのpath
    """
    # setup
    return  Path('non_exists_dir/tmp_1.cnt')

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

class Test_import_csv_to_row:
    """import csv_to_rowのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,delimiter指定なし
        - ファイルパスをPathで与え,存在する/読み取り権限がある/数件のデータがある場合
        - 例外発生
            - FileNotFound
            - PermissionError
            - IsAdirectoryError
            - MemoryError
            - Exception
    C1: 分岐カバレッジ
        - 引数カバレッジ
            #- ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,delimiter指定なし -> C0で検証済
            - ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,delimiter指定あり -> ','
            #- ファイルパスがNoneの時 -> C0で検証済
            - usecols=[0, 1]を設定
            - header=None, skiprows=1を設定
    C2: 条件カバレッジ
        - CSVファイル内容カバレッジ
            - CSVファイルの中身が空の場合
            - csvファイルにヘッダーだけがある場合
            - CSVファイルの中身がへダーがなくデータだけの場合
            #- csvファイルの区切り文字がカンマの場合 -> C1で検証済
            - csvファイルの区切り文字がタブの場合
            - csvファイルの区切り文字がスペースの場合
            #- CSVファイルの中身が複数行ある場合 -> C0で検証済
            - csvファイルの区切り文字がパイプの場合 -> C1で検証済
    """

    #def test_import_csv_to_row_UT_C0_specify_str_path(
    def test_import_csv_to_row_UT_C0_CSVファイルへのパスをstrで与える(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # strで与える
        csv_file_normal = str(csv_file_normal)

        # 結果定義,関数実行
        expected = [['Name', 'Age', 'Gender'], ['John', '25', 'Male'], ['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']
        assert result[1] == ['John', '25', 'Male']
        assert result[2] == ['Jane', '30', 'Female']


    def test_import_csv_to_row_UT_C0_specify_Path(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        expected = [['Name', 'Age', 'Gender'], ['John', '25', 'Male'], ['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']
        assert result[1] == ['John', '25', 'Male']


    def test_import_csv_to_row_UT_C0_raise_FileNotFoundError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - FileNotFoundError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "can not get target files"

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=FileNotFoundError)
        with pytest.raises(FileNotFoundError):
            assert import_csv_to_row(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_import_csv_to_row_UT_C0_raise_PermissionError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - PermissionErrom例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "No permission to read the file"

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=PermissionError)
        with pytest.raises(PermissionError):
            assert import_csv_to_row(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_row_UT_C0_raise_IsADirectoryError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - IsADirectoryError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "The specified path is a directory, not a file"

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=IsADirectoryError)
        with pytest.raises(IsADirectoryError):
            assert import_csv_to_row(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_row_UT_C0_raise_MemoryError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - MemoryErrom例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Not enough memory to read csv file"

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=MemoryError)
        with pytest.raises(MemoryError):
            assert import_csv_to_row(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_row_UT_C0_raise_Exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - Exception例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=Exception)
        with pytest.raises(Exception): # noqa: B017,PT011
            assert import_csv_to_row(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_row_UT_C1_specify_delimiter(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - delimiter -> ','を与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        expected = [['Name', 'Age', 'Gender'], ['John', '25', 'Male'], ['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_normal, delimiter=',')
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']
        assert result[1] == ['John', '25', 'Male']
        assert result[2] == ['Jane', '30', 'Female']


    def test_import_csv_to_row_UT_C2_empty_file(
        self,
        csv_file_empty: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - 空ファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_empty}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_empty)

        # 結果定義,関数実行
        expected = []
        result = import_csv_to_row(csv_file_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_import_csv_to_row_UT_C2_header_only_file(
        self,
        csv_file_header_only: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - へダーのみのファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_header_only}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_header_only = Path(csv_file_header_only)

        # 結果定義,関数実行
        expected = [['Name','Age','Gender']]
        result = import_csv_to_row(csv_file_header_only)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']


    def test_import_csv_to_row_UT_C2_data_only_file(
        self,
        csv_file_data_only: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - データのみのファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_data_only}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_data_only = Path(csv_file_data_only)

        # 結果定義,関数実行
        expected = [['John', '25', 'Male'],['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_data_only)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['John', '25', 'Male']
        assert result[1] == ['Jane', '30', 'Female']


    def test_import_csv_to_row_UT_C2_tab_sep(
        self,
        csv_file_tab_sep: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - space区切りファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_tab_sep}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_tab_sep = Path(csv_file_tab_sep)

        # 結果定義,関数実行
        expected = [['Name', 'Age', 'Gender'], ['John', '25', 'Male'], ['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_tab_sep, delimiter='\t')
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']
        assert result[1] == ['John', '25', 'Male']
        assert result[2] == ['Jane', '30', 'Female']


    def test_import_csv_to_row_UT_C2_pipe_sep(
        self,
        csv_file_pipe_sep: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - pipe区切りファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_pipe_sep}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_pipe_sep = Path(csv_file_pipe_sep)

        # 結果定義,関数実行
        expected = [['Name', 'Age', 'Gender'], ['John', '25', 'Male'], ['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_pipe_sep, delimiter='|')
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']
        assert result[1] == ['John', '25', 'Male']
        assert result[2] == ['Jane', '30', 'Female']


    def test_import_csv_to_row_UT_C2_space_sep(
        self,
        csv_file_space_sep: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - space区切りファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_space_sep}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_space_sep = Path(csv_file_space_sep)

        # 結果定義,関数実行
        expected = [['Name', 'Age', 'Gender'], ['John', '25', 'Male'], ['Jane', '30', 'Female']]
        result = import_csv_to_row(csv_file_space_sep, delimiter=' ')
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, list), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"
        assert result[0] == ['Name', 'Age', 'Gender']
        assert result[1] == ['John', '25', 'Male']
        assert result[2] == ['Jane', '30', 'Female']


class Test_import_csv_to_dataframe:
    """import csv_to_dataframeのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,delimiter指定なし
        - ファイルパスをPathで与え,存在する/読み取り権限がある/数件のデータがある場合
        - 例外発生
            - FileNotFound
            - PermissionError
            - IsAdirectoryError
            - MemoryError
            - Exception
    C1: 分岐カバレッジ
        - 引数カバレッジ
            #- ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,delimiter指定なし -> C0で検証済
            - ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,delimiter指定あり -> ','
            #- ファイルパスがNoneの時 -> C0で検証済
    C2: 条件カバレッジ
        - CSVファイル内容カバレッジ
            - CSVファイルの中身が空の場合
            - csvファイルにヘッダーだけがある場合
            - CSVファイルの中身がへダーがなくデータだけの場合
            #- csvファイルの区切り文字がカンマの場合 -> C1で検証済
            - csvファイルの区切り文字がタブの場合
            - csvファイルの区切り文字がスペースの場合
            #- CSVファイルの中身が複数行ある場合 -> C0で検証済
            - csvファイルの区切り文字がパイプの場合 -> C1で検証済
    """
    def test_import_csv_to_dataframe_UT_C0_specify_str_path(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # strで与える
        csv_file_normal = str(csv_file_normal)

        # 結果定義,関数実行
        # 2次元listからDataFrame作成
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        expected.columns = ['Name', 'Age', 'Gender']
        result = import_csv_to_dataframe(
            file_path=csv_file_normal,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C0_specify_path(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # strで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        # 2次元listからDataFrame作成
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        expected.columns = ['Name', 'Age', 'Gender']
        result = import_csv_to_dataframe(
            file_path=csv_file_normal,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C0_raise_FileNotFoundError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - FileNotFoundError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "can not get target files"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=FileNotFoundError)
        with pytest.raises(FileNotFoundError):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C0_raise_PermissionError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - PermissionErrom例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "No permission to read the file"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=PermissionError)
        with pytest.raises(PermissionError):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C0_raise_IsADirectoryError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - IsADirectoryErrom例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "The specified path is a directory, not a file"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=IsADirectoryError)
        with pytest.raises(IsADirectoryError):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C0_raise_pd_errors_ParserError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - ParserError
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to parse the Excel file"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=pd.errors.ParserError)
        with pytest.raises(pd.errors.ParserError):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C0_raise_pd_errors_EmptyDataError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - 空ファイルによる問題
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to parse the empty Excel file"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=pd.errors.EmptyDataError)
        with pytest.raises(pd.errors.EmptyDataError):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C0_raise_MemoryError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - MemoryErrom例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Not enough memory to read csv file"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=MemoryError)
        with pytest.raises(MemoryError):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C0_raise_Exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - Exception例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        mocker.patch("pandas.read_csv", side_effect=Exception)
        with pytest.raises(Exception):
            assert import_csv_to_dataframe(csv_file_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C1_specify_sep(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - delimiter -> ','を与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        expected.columns = ['Name', 'Age', 'Gender']
        result = import_csv_to_dataframe(
            file_path=csv_file_normal,
            sep=',',
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C1_specify_usecols(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - usecols=[0, 1]を指定,0,1列のみ取り込む
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25'], ['Jane', '30']])
        expected.columns = ['Name', 'Age']
        result = import_csv_to_dataframe(
            file_path=csv_file_normal,
            usecols=[0, 1],
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C1_specify_header_skiprows(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - header=None, skiprows=1
                - 結果、ColumnなしのデータだけDataFrameが生成される
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        result = import_csv_to_dataframe(
            file_path=csv_file_normal,
            header=None,
            skiprows=1,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C2_empty_file(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_empty: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - 空ファイル
                - pd.errors.EmptyDataErrorが発生する(Exceptionで捉えている)
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_empty}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_empty)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to parse the empty Excel file"

        # 結果定義,関数実行
        expected = pd.DataFrame()
        with pytest.raises(pd.errors.EmptyDataError):
            assert import_csv_to_dataframe(csv_file_normal) is True
        log_msg(f'expected: {expected}', LogLevel.DEBUG)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_import_csv_to_dataframe_UT_C2_header_only_file(
        self,
        csv_file_header_only: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - へダーのみのファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_header_only}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_header_only = Path(csv_file_header_only)

        # 結果定義,関数実行
        expected = pd.DataFrame(columns = ['Name', 'Age', 'Gender'])
        result = import_csv_to_dataframe(
            file_path=csv_file_header_only,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C2_data_only_file(
        self,
        csv_file_data_only: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - データのみのファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_data_only}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_data_only = Path(
            csv_file_data_only,
            header=None,
            )

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        result = import_csv_to_dataframe(
            csv_file_data_only,
            header=None,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C2_tab_sep(
        self,
        csv_file_tab_sep: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - space区切りファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_tab_sep}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_tab_sep = Path(csv_file_tab_sep)

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        expected.columns = ['Name', 'Age', 'Gender']
        result = import_csv_to_dataframe(
            csv_file_tab_sep,
            sep='\t',
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C2_pipe_sep(
        self,
        csv_file_pipe_sep: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - pipe区切りファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_pipe_sep}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_pipe_sep = Path(csv_file_pipe_sep)

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        expected.columns = ['Name', 'Age', 'Gender']
        result = import_csv_to_dataframe(
            csv_file_pipe_sep,
            sep='|',
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


    def test_import_csv_to_dataframe_UT_C2_space_sep(
        self,
        csv_file_space_sep: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - delimiterは指定なし(デフォルト)
                - pathをPathで与える
                - space区切りファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_space_sep}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_space_sep = Path(csv_file_space_sep)

        # 結果定義,関数実行
        expected = pd.DataFrame([['John', '25', 'Male'], ['Jane', '30', 'Female']])
        expected.columns = ['Name', 'Age', 'Gender']
        result = import_csv_to_dataframe(
            csv_file_space_sep,
            sep=' ',
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a list, but got {type(result).__name__}"
        assert result.equals(expected), f"Expected {expected}, but got {result}"


class Test_get_file_record_count:
    """get_file_record_countのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合,header指定なし
        - ファイルパスをPathで与え,存在する/読み取り権限がある/数件のデータがある場合,header指定なし
        - header値がマイナスの場合
        - 例外発生
            - FileNotFound
            - PermissionError
            - IsAdirectoryError
            - MemoryError
            - Exception
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - header指定あり(>0)
            #- header指定なし C0で検証済
    C2: 条件カバレッジ
            - CSVファイルの中身が空の場合
            - ファイルが何らかのバイナリファイルの場合
    """
    def test_get_file_record_countUT_C0_specify_str(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # strで与える
        csv_file_normal = str(csv_file_normal)

        # 結果定義,関数実行
        expected = 3
        result = get_file_record_count(
            file_path=csv_file_normal,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, int), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_specify_path(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # 2次元listからDataFrame作成
        expected = 3
        result = get_file_record_count(
            file_path=csv_file_normal,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, int), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_minus_header(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathで与える
                - headerにマイナスを与える,Noneが返る
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "header values must >= 0"
        expected = None

        # 結果定義,関数実行
        result = get_file_record_count(
            file_path=csv_file_normal,
            header=-1,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # キャプチャされたログメッセージを取得,期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is None, f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_raise_FileNotFoundError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - FileNotFoundError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "can not get target files"

        # 結果期待値
        expected = None

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=FileNotFoundError)
        result = get_file_record_count(csv_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is None, f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_raise_PermissionError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - PermissionError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "No permission to read the file"

        # 結果期待値
        expected = None

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=PermissionError)
        result = get_file_record_count(csv_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is None, f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_raise_IsADirectoryError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - IsADirectoryError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "The specified path is a directory, not a file"

        # 結果期待値
        expected = None

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=IsADirectoryError)
        result = get_file_record_count(csv_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is None, f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_raise_MemoryError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - MemoryError例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Not enough memory to read csv file"

        # 結果期待値
        expected = None

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=MemoryError)
        result = get_file_record_count(csv_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is None, f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C0_raise_Exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 異常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをPathで与える
                - Exception例外発生/mocker.patch,side_effectでpathlib.Path.open処理を差し替え
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # Pathで与える
        # mockerを使用する場合はファイルの実在にテスト結果依存はない
        csv_file_normal = Path(csv_file_normal)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果期待値
        expected = None

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=Exception)
        result = get_file_record_count(csv_file_normal)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert result is None, f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C1_specify_header(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをstrで与える
                - header = 1を明示して与える
                - 件数 3 -> 2となる
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # strで与える
        csv_file_normal = str(csv_file_normal)

        # 結果定義,関数実行
        expected = 2
        result = get_file_record_count(
            file_path=csv_file_normal,
            header=1,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, int), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C2_empty_file(
        self,
        csv_file_empty: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをstrで与える
                - 空ファイルを読み込む
                - 件数0となる
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_empty}', LogLevel.DEBUG)

        # strで与える
        csv_file_normal = str(csv_file_empty)

        # 結果定義,関数実行
        expected = 0
        result = get_file_record_count(
            file_path=csv_file_normal,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, int), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_get_file_record_count_UT_C2_binary_file(
        self,
        binary_file: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - pathをstrで与える
                - バイナリファイルを読み込む
                - 件数3となる
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'bin file path: {binary_file}', LogLevel.DEBUG)

        # strで与える
        binary_file = str(binary_file)

        # 結果定義,関数実行
        expected = 3
        result = get_file_record_count(
            file_path=binary_file,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, int), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

class Test_create_cnt_file:
    """create_cnt_fileのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - カウント対象ファイルパスをstrで与え,存在する/読み取り権限がある/数件のデータがある場合
        - カウント対象ファイルパスをPathで与え,存在する/読み取り権限がある/数件のデータがある場合
        - CNTファイルパスをstrで与え書き込み権限がある
        - CNTファイルパスをPathで与え書き込み権限がある
        - CNTファイルパスをPathで与えるが存在しない
        - csv_header_recordを指定する,csv_header_record=-1
        - 例外発生
            - Exception
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - csv_header_recordを指定しない: C0で検証済
            - csv_header_recordを指定する,csv_header_record=1
            - csv_header_recordを指定する,csv_header_record=0
            - get_file_record_count()でエラー検出する: C0で検証済
        - 条件組み合わせ
            - CNTファイルパスを存在しないディレクトリ下ファイルに指定する
            - CNTファイルパスをPathで与え書き込み権限が無い
    C2: 条件カバレッジ
        - カウント対象ファイルが空
        - カウント対象ファイルがバイナリファイル

    """
    def test_create_cnt_file_UT_C0_specify_str_to_csv_path(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = str(csv_file_normal)
        cnt_file_writable = str(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=2\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C0_specify_Path_to_csv_path(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=2\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C0_specify_str_to_cnt_path(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - CNTファイルpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = str(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=2\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C0_specify_Path_to_cnt_path(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - CNTファイルpathをPathで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = str(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=2\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C0_non_exists_cnt_dir(
        self,
        csv_file_normal: str|Path,
        cnt_file_non_exists_cnt_dir: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - CNTファイルpathをPathで与える
                - 存在しないディレクトリをCNT出力先に指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = str(csv_file_normal)
        cnt_file_non_writable = Path(cnt_file_non_exists_cnt_dir)

        # 結果定義,関数実行
        expected = False
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_non_writable,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_create_cnt_file_UT_C0_csv_header_record_to_minus(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        csv_header_record=-1,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - csv_header_record=-1を設定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = False
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            csv_header_record=csv_header_record,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_create_cnt_file_UT_C0_raise_Exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - CNTファイル書き込み時に例外を発生させる
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 結果定義,関数実行
        expected = False
        mocker.patch("src.lib.common_utils.ibr_csv_helper._write_records", side_effect=Exception)
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert expected_log_msg in captured_logs, f"Traceback '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_create_cnt_file_UT_C1_csv_header_record_to_1(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        csv_header_record=1,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - csv_header_record=1を指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            csv_header_record=csv_header_record,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=2\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C1_csv_header_record_to_0(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        csv_header_record=0,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - csv_header_record=0を指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable,
            csv_header_record=csv_header_record,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=3\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C1_cnt_to_exists_dir(
        self,
        csv_file_normal: str|Path,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - CNTファイル名ではなくディレクトリ指定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)
        cnt_file_writable = Path(cnt_file_writable)
        log_msg(f'target cnt file path: {cnt_file_writable.parent}', LogLevel.INFO)

        # 結果定義,関数実行
        expected = False
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=cnt_file_writable.parent,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_create_cnt_file_UT_C1_to_no_writable_dir(
        self,
        csv_file_normal: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - CNTファイル出力先を書き込み権限のないディレクトリとする
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_normal = Path(csv_file_normal)

        # 結果定義,関数実行
        expected = False
        result = create_cnt_file(
            csv_file_path=csv_file_normal,
            cnt_file_path=Path('/'),  # 実在するが書き込み権限のない位置
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_create_cnt_file_UT_C2_empty_file(
        self,
        csv_file_empty: str|Path,
        cnt_file_writable: str|Path,
        csv_header_record=0,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - 対象データは空ファイル
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_empty}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        csv_file_empty = Path(csv_file_empty)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=csv_file_empty,
            cnt_file_path=cnt_file_writable,
            csv_header_record=csv_header_record,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=0\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test_create_cnt_file_UT_C2_binary_file(
        self,
        binary_file: str|Path,
        cnt_file_writable: str|Path,
        csv_header_record=0,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーなしデータの取り込み,csv_header_record=0
                - カウント対象ファイルのpathをstrで与える
                - 対象データをBinaryファイルとする
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'binary file path: {binary_file}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        binary_file = Path(binary_file)
        cnt_file_writable = Path(cnt_file_writable)

        # 結果定義,関数実行
        expected = True
        result = create_cnt_file(
            csv_file_path=binary_file,
            cnt_file_path=cnt_file_writable,
            csv_header_record=csv_header_record,
            )
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, bool), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        expected_content = "SIZE=3\nCLASS=0\nSTAT=0\nEOF\n"
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"

class Test__write_records:
    """_write_recordsのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 出力対象ファイルパスをstrで与える
        - 出力ファイルパスをPathで与える
        - recordsにlistを与える
        - 例外発生
            - Exception
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - recordsに空listを与える
    C2: 条件カバレッジ
        - 対象なし
    """
    def test__write_records_UT_C0_specify_str_to_cnt_path(
        self,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        cnt_file_writable = str(cnt_file_writable)

        records = [
            'SIZE=3',
            'CLASS=0',
            'STAT=0',
            'EOF',
        ]

        # 期待するCNTファイル出力
        expected_content = "SIZE=3\nCLASS=0\nSTAT=0\nEOF\n"

        # 結果定義,関数実行
        _ = _write_records(
            cnt_file_path=cnt_file_writable,
            records=records,
            )

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        # ヘダー想定としているので出力行は2行と判定する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test__write_records_UT_C0_specify_path_to_cnt_path(
        self,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        cnt_file_writable = Path(cnt_file_writable)

        records = [
            'SIZE=3',
            'CLASS=0',
            'STAT=0',
            'EOF',
        ]
        # 期待するCNTファイル出力
        expected_content = "SIZE=3\nCLASS=0\nSTAT=0\nEOF\n"

        # 結果定義,関数実行
        _ = _write_records(
            cnt_file_path=cnt_file_writable,
            records=records,
            )

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"


    def test__write_records_UT_C0_raise_Exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - CNTファイル書き込み時に例外を発生させる
                - 例外発生検出する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        cnt_file_writable = Path(cnt_file_writable)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # records
        records = [
            'SIZE=3',
            'CLASS=0',
            'STAT=0',
            'EOF',
        ]

        # 結果定義,関数実行
        mocker.patch("pathlib.Path.open", side_effect=Exception)
        with pytest.raises(Exception):
            _ = _write_records(
                cnt_file_path=cnt_file_writable,
                records=records,
                )

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # 結果評価
        # Traceback出力を確認
        assert expected_log_msg in captured_logs, f"Traceback '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test__write_records_UT_C1_specify_records_to_empty_list(
        self,
        cnt_file_writable: str|Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: へダーありデータの取り込み
                - カウント対象ファイルのpathをstrで与える
                - recordsに空listを設定する
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'csv file path: {csv_file_normal}', LogLevel.DEBUG)

        # カウント対象ファイルパスをstrで与える
        cnt_file_writable = Path(cnt_file_writable)

        # 空リストを渡す
        records = []
        # 結果定義,関数実行
        _ = _write_records(
            cnt_file_path=cnt_file_writable,
            records=records,
            )

        # 期待するCNTファイル出力
        expected_content = ''

        # 出力ファイル評価
        # 出力ファイルを読み直して結果を評価する
        cnt_file_writable = Path(cnt_file_writable)
        with cnt_file_writable.open() as f:
            cnt_content = f.read()
        assert cnt_content == expected_content, f"Expected content of the cnt file to be '{expected_content}', but it was '{cnt_content}'"
