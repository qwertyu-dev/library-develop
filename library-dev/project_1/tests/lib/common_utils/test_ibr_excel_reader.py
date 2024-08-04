"""テスト実施方法

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
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_enums import LogLevel

#####################################################################
# テスト対象モジュール import, project ディレクトリから起動する
#####################################################################
from src.lib.common_utils.ibr_excel_reader import ExcelDataLoader

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
@pytest.fixture(scope='function')
def data_dataframe() -> pd.DataFrame:
    data = {
        'Column1': ['Value1', 'Value2', 'Value3'],
        'Column2': ['Value4', 'Value5', 'Value6'],
        'Column3': ['Value7', 'Value8', 'Value9'],
    }
    return pd.DataFrame(data).reset_index(drop=True)

@pytest.fixture(scope='function')
def data_dataframe_columns_less() -> pd.DataFrame:
    data = {
        'Value1': ['Value2', 'Value3'],
        'Value4': ['Value5', 'Value6'],
        'Value7': ['Value8', 'Value9'],
    }
    return pd.DataFrame(data)

@pytest.fixture(scope='function')
def data_dataframe_skiprows_one() -> pd.DataFrame:
    data = {
        'Column1': ['Value2', 'Value3'],
        'Column2': ['Value5', 'Value6'],
        'Column3': ['Value8', 'Value9'],
    }
    return pd.DataFrame(data)

@pytest.fixture(scope='function')
def data_dataframe_usecols01() -> pd.DataFrame:
    data = {
        'Column1': ['Value1', 'Value2', 'Value3'],
        'Column2': ['Value4', 'Value5', 'Value6'],
    }
    return pd.DataFrame(data)

@pytest.fixture(scope='function')
def data_dataframe_only_one_columns() -> pd.DataFrame:
    data = {
        'Column2': ['Value4', 'Value5', 'Value6'],
    }
    return pd.DataFrame(data)

    # テスト用のExcelBookを作成
@pytest.fixture(scope='function')
def test_excel_book_normal(data_dataframe, tmp_path) -> Path:
    file_path = tmp_path / "test.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        data_dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
    return file_path

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

# テスト用のExcelデータ(複数シート保有)を作成するfixture
@pytest.fixture(scope='function')
def test_excel_book_multisheet_normal(tmp_path):
    # データフレームを作成
    df1 = pd.DataFrame(
        {
            'A': ['A0', 'A1', 'A2', 'A3'],
            'B': ['B0', 'B1', 'B2', 'B3'],
            'C': ['C0', 'C1', 'C2', 'C3'],
            'D': ['D0', 'D1', 'D2', 'D3'],
        },
        )

    df2 = pd.DataFrame(
        {
            'A': ['A4', 'A5', 'A6', 'A7'],
            'B': ['B4', 'B5', 'B6', 'B7'],
            'C': ['C4', 'C5', 'C6', 'C7'],
            'D': ['D4', 'D5', 'D6', 'D7'],
            },
        )

    # Excelファイルを作成
    with pd.ExcelWriter(tmp_path / 'test.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)

    return tmp_path / 'test.xlsx'

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


# テスト用のExcelデータ(複数シート保有,ヘダー行までゴミ込み)を作成するfixture
@pytest.fixture(scope='function')
def test_excel_book_multisheet_gomi(tmp_path):
    # データフレームを作成
    df1 = pd.DataFrame(
        {
            'Agomi': ['A', 'A0', 'A1', 'A2', 'A3'],
            'Bgomi': ['B', 'B0', 'B1', 'B2', 'B3'],
            'Cgomi': ['C', 'C0', 'C1', 'C2', 'C3'],
            'Dgomi': ['D', 'D0', 'D1', 'D2', 'D3'],
        },
        )

    df2 = pd.DataFrame(
        {
            'Agomi': ['A', 'A4', 'A5', 'A6', 'A7'],
            'Bgomi': ['B', 'B4', 'B5', 'B6', 'B7'],
            'Cgomi': ['C', 'C4', 'C5', 'C6', 'C7'],
            'Dgomi': ['D', 'D4', 'D5', 'D6', 'D7'],
            },
        )

    # Excelファイルを作成
    with pd.ExcelWriter(tmp_path / 'test_gomi.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1', index=False)
        df2.to_excel(writer, sheet_name='Sheet2', index=False)

    return tmp_path / 'test_gomi.xlsx'

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


# テスト用のExcelデータ(複数シート保有)を取り込んだDataFrameを生成するfixture
@pytest.fixture(scope='function')
def data_dataframe_multi_sheets(tmp_path):
    # データフレームを作成
    return pd.DataFrame(
        {
            'A': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'],
            'B': ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
            'C': ['C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'],
            'D': ['D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7'],
        },
        )

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

# テスト用のExcelデータ(複数シート保有)を作成するfixture
@pytest.fixture(scope='function')
def test_excel_book_multisheet_difference_format(tmp_path):
    # データフレームを作成
    df1 = pd.DataFrame(
        {
            'A': ['A0', 'A1', 'A2', 'A3'],
            'B': ['B0', 'B1', 'B2', 'B3'],
            'C': ['C0', 'C1', 'C2', 'C3'],
            'D': ['D0', 'D1', 'D2', 'D3'],
        },
        )

    df2 = pd.DataFrame(
        {
            'A': ['A4', 'A5', 'A6', 'A7'],
            'B': ['B4', 'B5', 'B6', 'B7'],
            'C': ['C4', 'C5', 'C6', 'C7'],
            },
        )

    # Excelファイルを作成
    with pd.ExcelWriter(tmp_path / 'test_difference_format.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1')
        df2.to_excel(writer, sheet_name='Sheet2')

    return tmp_path / 'test_difference_format.xlsx'


# テスト用のExcelデータ(データなし)を作成するfixture
@pytest.fixture(scope='function')
def test_excel_book_multisheet_emptys(tmp_path):
    # データフレームを作成
    df1 = pd.DataFrame()
    df2 = pd.DataFrame()

    # Excelファイルを作成
    with pd.ExcelWriter(tmp_path / 'test.xlsx') as writer:
        df1.to_excel(writer, sheet_name='Sheet1')
        df2.to_excel(writer, sheet_name='Sheet2')

    return tmp_path / 'test.xlsx'

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

# テスト用のExcelデータ(複数シート保有)を作成するfixture
@pytest.fixture(scope='function')
def test_excel_book_multisheet_skiprows_minus_one(tmp_path):
    # データフレームを作成
    return pd.DataFrame(
        {
            'A': ['A3', 'A7'],
            'B': ['B3', 'B7'],
            'C': ['C3', 'C7'],
            'D': ['D3', 'D7'],
        },
    )


# テスト用のExcelデータ(複数シート保有)を取り込んだDataFrameを生成するfixture
@pytest.fixture(scope='function')
def data_dataframe_multi_sheets_specify_usecols_one_two(tmp_path):
    # データフレームを作成
    return pd.DataFrame(
        {
            'A': ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7'],
            'B': ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
        },
        )

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


# テスト用のExcelデータ(複数シート保有)を取り込んだDataFrameを生成するfixture
@pytest.fixture(scope='function')
def data_dataframe_multi_sheets_specify_usecols_one(tmp_path):
    # データフレームを作成
    return pd.DataFrame(
        {
            'B': ['B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'],
        },
        )

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

# テスト用のExcelデータ(複数シート保有)を取り込んだDataFrameを生成するfixture
@pytest.fixture(scope='function')
def data_dataframe_multi_sheets_sheet1(tmp_path):
    # データフレームを作成
    return pd.DataFrame(
        {
            'A': ['A0', 'A1', 'A2', 'A3'],
            'B': ['B0', 'B1', 'B2', 'B3'],
            'C': ['C0', 'C1', 'C2', 'C3'],
            'D': ['D0', 'D1', 'D2', 'D3'],
        },
        )

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


# テスト用のExcelデータ(複数シート保有)を取り込んだDataFrameを生成するfixture
@pytest.fixture(scope='function')
def data_dataframe_multi_sheets_sheet2(tmp_path):
    # データフレームを作成
    return pd.DataFrame(
        {
            'A': ['A4', 'A5', 'A6', 'A7'],
            'B': ['B4', 'B5', 'B6', 'B7'],
            'C': ['C4', 'C5', 'C6', 'C7'],
            'D': ['D4', 'D5', 'D6', 'D7'],
        },
        )

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


# errorsテストデータを生成するためのfixture
@pytest.fixture(scope='function')
def validation_errors_normal_one_error():
    return [
        (0, [
            {'type': 'int_type', 'loc': ('e',), 'msg': 'Input should be a valid integer', 'input': 'あ', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'},
            ]),
        ]

# errorsテストデータを生成するためのfixture
@pytest.fixture(scope='function')
def validation_errors_not_dict():
    return [
        (0, [
            ['type', 'int_type', 'loc', ('e',), 'msg', 'Input should be a valid integer', 'input', 'あ', 'url', 'https://errors.pydantic.dev/2.5/v/int_type'],
            ]),
        ]


# errorsテストデータを生成するためのfixture
@pytest.fixture(scope='function')
def validation_errors_contain_other_key():
    return [
        (0, [
            {'type': 'int_type', 'iloc': ('e',), 'msg': 'Input should be a valid integer', 'input': 'あ', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'},
            ]),
        ]

# errorsテストデータを生成するためのfixture
@pytest.fixture(scope='function')
def validation_errors_normal_two_error_on_one_record():
    return [
        (0, [
            {'type': 'int_type', 'loc': ('e',), 'msg': 'Input should be a valid integer', 'input': 'あ', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'},
            {'type': 'string_type', 'loc': ('g',), 'msg': 'Input should be a valid string', 'input': 1, 'url': 'https://errors.pydantic.dev/2.5/v/string_type'},
            ]),
        ]

# errorsテストデータを生成するためのfixture
@pytest.fixture(scope='function')
def validation_errors_normal_two_errors_anather_record():
    return [
        (0, [
            {'type': 'int_type', 'loc': ('e',), 'msg': 'Input should be a valid integer', 'input': 'あ', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'},
            ]),
        (1, [
            {'type': 'int_type', 'loc': ('d',), 'msg': 'Input should be a valid integer', 'input': 's', 'url': 'https://errors.pydantic.dev/2.5/v/int_type'},
            ]),
        ]


class Test_read_excel_one_sheet:
    """read_excel_one_sheetのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 通常取り込み
            - file_path指定,sheet_name指定,その他は指定なし
        - 例外発生
            - FileNotFoundError
            - PermissionError
            - IsADirectoryError
            - pd.errors.ParserError
            - MemoryError
            - Exception

    C1: 分岐カバレッジ
        - 引数カバレッジ
            - file_path指定,sheet_name指定,skiprows=0指定
            - file_path指定,sheet_name指定,skiprows=1指定
            - file_path指定,sheet_name指定,skiprows=-1指定
            - file_path指定,sheet_name指定,usecol=[0, 1]指定
            - file_path指定,sheet_name指定,usecol=[0, 3]指定
            - file_path指定,sheet_name指定,usecol=[-1, 1]指定
            - file_path指定,sheet_name指定,usecol=[]指定
    C2: 条件カバレッジ
        - CSVファイル内容カバレッジ
            - sheet_nameに指定したシートがない
            - sheet_nameに指定したシートが空状態
    """

    def test_read_excel_one_sheet_UT_C0_normal_case(
        self,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            )
        data_dataframe = data_dataframe.reset_index(drop=True)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe)}', LogLevel.DEBUG)
        log_msg(f'result: \n{tabulate_dataframe(result)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe)


    def test_read_excel_one_sheet_UT_C0_raise_FileNotFound(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - FileNotFoundError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "can not get target files"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=FileNotFoundError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(FileNotFoundError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name = 'Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C0_raise_PermissionError(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - sheet_nameを指定
                - PermissionError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "No permission to read the file"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=PermissionError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(PermissionError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C0_raise_IsADirectoryError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - IsADirectoryError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "The specified path is a directory, not a file"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=IsADirectoryError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(IsADirectoryError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C0_raise_pd_errors_ParserError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - pd.errors.ParserError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to parse the Excel file"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=pd.errors.ParserError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(pd.errors.ParserError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C0_raise_pd_errors_EmptyDataError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - sheet_nameを指定
                - pd.errors.EmptyDataError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to parse the empty Excel file"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=pd.errors.EmptyDataError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(pd.errors.EmptyDataError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C0_raise_pd_errors_MemoryError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - Sheet_name指定
                - MemoryError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Not enough memory to read Excel file"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=MemoryError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(MemoryError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C0_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - Exception発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=Exception)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(Exception):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C1_Specify_skiprows_zero(
        self,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - skiprows=0を追加指定
                - データスキップなし
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            skiprows=0,
            )

        log_msg(f'expected: \n{data_dataframe}', LogLevel.DEBUG)
        log_msg(f'result: \n{result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe)


    def test_read_excel_one_sheet_UT_C1_Specify_skiprows_one(
        self,
        test_excel_book_normal: Path,
        data_dataframe_columns_less: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - skiprows=1を追加指定
                - データ1行目がヘダーレコードになる
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            skiprows=1,
            )

        log_msg(f'expected: \n{data_dataframe_columns_less}', LogLevel.DEBUG)
        log_msg(f'result: \n{result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_columns_less)


    def test_read_excel_one_sheet_UT_C1_Specify_skiprows_minus(
        self,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - skiprows=-1を追加指定
                - データスキップなし
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            skiprows=-1,
            )

        log_msg(f'expected: \n{data_dataframe}', LogLevel.DEBUG)
        log_msg(f'result: \n{result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe)


    def test_read_excel_one_sheet_UT_C1_Specify_usecols_zero_one(
        self,
        test_excel_book_normal: Path,
        data_dataframe_usecols01: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - usecols=[0, 1]を追加指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            usecols=[0, 1],
            )

        log_msg(f'expected: {data_dataframe_usecols01}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_usecols01)


    def test_read_excel_one_sheet_UT_C1_Specify_usecols_zero_three(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - usecols=[0, 3]を追加指定
                - pandas.errors.ParserError発生を想定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Failed to parse the Excel file"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        with pytest.raises(pd.errors.ParserError):
            assert excel_instance.read_excel_one_sheet(
                sheet_name='Sheet1',
                usecols=[0,3],
            ) is True

        # 結果評価
        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_one_sheet_UT_C1_Specify_usecols_minus_one(
        self,
        test_excel_book_normal: Path,
        data_dataframe_only_one_columns: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - usecols=[-1, 1]を追加指定
                - usecols左端にマイナス設定してもpandasが自動補正する挙動
                - usecolsの結果,右端の1だけが有効になっていてcolumn2のみ選択される
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            usecols=[-1, 1],
        )

        log_msg(f'expected: {data_dataframe}', LogLevel.DEBUG)
        log_msg(f'result: {tabulate_dataframe(result)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_only_one_columns)


    def test_read_excel_one_sheet_UT_C1_Specify_usecols_empty(
        self,
        test_excel_book_normal: Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを指定
                - usecols=[]を追加指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            usecols=[],
        )

        log_msg(f'expected: {pd.DataFrame()}', LogLevel.DEBUG)
        log_msg(f'result: {tabulate_dataframe(result)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(pd.DataFrame())


    def test_read_excel_one_sheet_UT_C2_Specify_no_sheet_name(
        self,
        test_excel_book_normal: Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameを存在しないもの指定
                - 空のDataFrameが生成される
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='non_exist_Sheet1',
            )
        data_dataframe = data_dataframe.reset_index(drop=True)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe)}', LogLevel.DEBUG)
        log_msg(f'result: \n{tabulate_dataframe(result)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(pd.DataFrame())


    def test_read_excel_one_sheet_UT_C2_Specify_empty_sheet(
        self,
        test_excel_book_multisheet_emptys : Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathを指定
                - sheet_nameが空っぽシートを指す
                - 空のDataFrameが生成される
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_multisheet_emptys= Path(test_excel_book_multisheet_emptys)
        log_msg(f'test_excel_book_normal: {test_excel_book_multisheet_emptys}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_multisheet_emptys,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_one_sheet(
            sheet_name='Sheet1',
            )
        data_dataframe = data_dataframe.reset_index(drop=True)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe)}', LogLevel.DEBUG)
        log_msg(f'result: \n{tabulate_dataframe(result)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(pd.DataFrame())


class Test_read_excel_all_sheets:
    """parse_excel_sheetのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 通常取り込み
            - BookのSheetが1枚の場合,read_excel_all_sheets()を使用するようエラー検出
        - 通常取り込み
            - file_path指定,その他は指定なし
        - 例外発生
            ただし一部の例外はread_excel_one_sheetにより発生する想定
            - FileNotFoundError
            - PermissionError
            - IsADirectoryError
            - pd.errors.ParaserError
            - pd.errors.EmptyDataError
            - MemoryError
            - Exception

    C1: 分岐カバレッジ
        - 引数カバレッジ
            - skiprowsを指定=0
            - skiprowsを指定,指定行のskipを確認
            - skiprowsを指定,マイナス値を指定
            - usecolsを指定, [0, 1]
            - usecolsを指定, [0, 5]
            - usecolsを指定, [-1, 1]
            - exclution_sheetsを指定, ['xxxx(存在する)'],指定シート名データが含まれない
            - exclution_sheetsを指定, ['xxxx(存在しない)'],存在しないシート名は無意味,エラーにならず続行
            - exclution_sheetsを指定, []を設定
            - exclution_sheetsを指定, [存在する全てのシート]を設定

    C2: 条件カバレッジ
        - CSVファイル内容カバレッジ
            - BookのSheetが1枚の場合 # C0で実施済
            - Sheet毎のレイアウトが異なる場合

    """
    def test_read_excel_all_sheet_UT_C0_one_sheet(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_normal:Path,
        data_dataframe: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - ExcelBookシートが1枚でありながら,read_excel_one_sheet()を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "BookのSheet数が1枚の場合は read_excel_one_sheet()を使用してください"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        with pytest.raises(ValueError):
            assert excel_instance.read_excel_all_sheets() is True
        # キャプチャされたログメッセージを取得

        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_read_excel_all_sheets_UT_C0_all_sheets(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets()
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets)


    def test_read_excel_all_sheets_UT_C0_raise_FileNotFound(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - FileNotFoundError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "FileNotFound"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=FileNotFoundError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(FileNotFoundError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheets_UT_C0_raise_PermissionError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - PermisionError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "PermissionError"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=PermissionError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(PermissionError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheets_UT_C0_raise_IsADirectoryError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - IsADirectoryError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "IsADirectoryError"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=IsADirectoryError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(IsADirectoryError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheets_UT_C0_raise_pd_errors_ParserError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - ParserError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "pandas.errors.ParserError"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=pd.errors.ParserError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(pd.errors.ParserError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheets_UT_C0_raise_pd_errors_EmptyDataError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - EmptyDataError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "pandas.errors.EmptyDataError"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=pd.errors.EmptyDataError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(pd.errors.EmptyDataError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheets_UT_C0_raise_MemoryError(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - MemoryError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "MemoryError"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=MemoryError)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(MemoryError):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheets_UT_C0_raise_Exception(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - Exception発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Exception"

        # mocker差し替え
        mocker.patch('pandas.ExcelFile', side_effect=Exception)
        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('test_excel_book_normal'),
        )
        with pytest.raises(Exception):
            # 結果定義,関数実行
            # excel sheet to DataFrame
            assert excel_instance.read_excel_all_sheets() is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheet_UT_C1_Specfy_skiprows_set_zero(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - skiprows=0を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            skiprows=0,
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets)


    def test_read_excel_all_sheet_UT_C1_Specfy_skiprows_set_one(
        self,
        test_excel_book_multisheet_gomi: Path,
        data_dataframe_multi_sheets : pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - skiprows=1を指定
                - Excelデータには1行目にゴミレコード混入
                - ゴミレコードを飛ばしてレコード欠落なし
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_multisheet_gomi= Path(test_excel_book_multisheet_gomi)
        log_msg(f'test_excel_book_multisheet_gomi: {test_excel_book_multisheet_gomi}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_multisheet_gomi,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            skiprows=1,
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets)


    def test_read_excel_all_sheet_UT_C1_Specfy_skiprows_set_minus(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets : pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - skiprows=-1を指定
                - レコード欠落なし
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_multisheet_normal= Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_multisheet_normal: {test_excel_book_multisheet_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_multisheet_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            skiprows=-1,
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets)


    def test_read_excel_all_sheet_UT_C1_Specfy_usecols_zero_one(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets_specify_usecols_one_two: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - usecols=[0, 1]を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            usecols=[0, 1],
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets_specify_usecols_one_two)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets_specify_usecols_one_two)


    def test_read_excel_all_sheet_UT_C1_Specfy_usecols_zero_five(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        test_excel_book_multisheet_normal: Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - usecols=[0, 5]を指定
                - pandas.errors.ParserError発生
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "pandas.errors.ParserError"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        with pytest.raises(pd.errors.ParserError):
            assert excel_instance.read_excel_all_sheets(
                usecols=[0, 5],
            ) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs


    def test_read_excel_all_sheet_UT_C1_Specfy_usecols_minus_one(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets_specify_usecols_one: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - usecols=[-1, 1]を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            usecols=[-1, 1],
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets_specify_usecols_one)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets_specify_usecols_one)


    def test_read_excel_all_sheet_UT_C1_Specfy_exclution_sheets_exists(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets_sheet2: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - exclution_sheetsに ['Sheet1'] を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            exclusion_sheets=['Sheet1'],
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets_sheet2)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets_sheet2)


    def test_read_excel_all_sheet_UT_C1_Specfy_exclution_sheets_non_exists(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - exclution_sheetsに ['Sheet1'] を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            exclusion_sheets=['non_exists_Sheet'],
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets)


    def test_read_excel_all_sheet_UT_C1_Specfy_exclution_sheets_empty(
        self,
        test_excel_book_multisheet_normal: Path,
        data_dataframe_multi_sheets: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - exclution_sheetsに ['Sheet1'] を指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            exclusion_sheets=[],
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(data_dataframe_multi_sheets)}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(data_dataframe_multi_sheets)


    def test_read_excel_all_sheet_UT_C1_Specfy_exclution_all_sheets(
        self,
        test_excel_book_multisheet_normal: Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C1
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - exclution_sheetsに ['Sheet1', 'Sheet2'] を指定
                -
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_normal)
        log_msg(f'test_excel_book_normal: {test_excel_book_normal}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
            exclusion_sheets=['Sheet1', 'Sheet2'],
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(pd.DataFrame())}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(pd.DataFrame())


    def test_read_excel_all_sheet_UT_C2_difference_sheet_format(
        self,
        test_excel_book_multisheet_difference_format: Path,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                - テストシナリオ: ExcelBookの1枚シート読み込み典型ケース
                - file_pathのみを指定
                - ExcelSheetのレイアウトが各シートで全一致していない
                - 空DataFrameを返す
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        test_excel_book_normal = Path(test_excel_book_multisheet_difference_format)
        log_msg(f'test_excel_book_normal: {test_excel_book_multisheet_difference_format}', LogLevel.DEBUG)

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = test_excel_book_normal,
        )
        # 結果定義,関数実行
        # excel sheet to DataFrame
        result = excel_instance.read_excel_all_sheets(
        )
        log_msg(f'result:   \n{tabulate_dataframe(result)}', LogLevel.DEBUG)
        log_msg(f'expected: \n{tabulate_dataframe(pd.DataFrame())}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, pd.DataFrame), f"Expected result to be a pd.DataFrame, but got {type(result).__name__}"
        assert result.equals(pd.DataFrame())


class Test_logger_validation_erros:
    """logger_validation_errorsのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - 通常ログ出力
        - errors listを指定しない
        - errors がlistでない
        - errors listから取り出したlistにdictが格納されていない
        - errors list 格納listのdictに msg,loc,inputキーワードが含まれていない
    C1: 分岐カバレッジ
        - 引数カバレッジ C0で実施済
    C2: 条件カバレッジ
        - 1行に複数のエラーがある
        - 複数の行でエラーがある

    """
    def test_logger_validation_errors_UT_C0_one_error(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        validation_errors_normal_one_error: list,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: error list構成典型ケース
                - errors listのみを指定
                - errors listには1件のみエラー配列を格納
                - カスタムロガー出力, caplogFixtureの支援で確認を行う
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'errors list: {validation_errors_normal_one_error}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Validation error at (1, e):  Input should be a valid integer, wrong values: あ:"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('aaa'), # 本件テストではExcelファイルには依存性無いので仮のPath指定で良いこととする
        )
        # 結果定義,関数実行
        _ = excel_instance.logger_validation_errors(validation_errors_normal_one_error)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_logger_validation_errors_UT_C0_no_error(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        validation_errors_normal_one_error: list,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: error list構成典型ケース, error list 空で渡す
                - カスタムロガー出力, caplogFixtureの支援で確認を行う
                - No validation errorsを検出
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'errors list: {validation_errors_normal_one_error}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        # 本体はINFOレベルで出力しているので、ここのcapture設定に留意
        caplog.set_level(LogLevel.INFO.value)

        # 期待されるログメッセージ
        expected_log_msg = "No validation errors"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('aaa'), # 本件テストではExcelファイルには依存性無いので仮のPath指定で良いこととする
        )
        # 結果定義,関数実行
        _ = excel_instance.logger_validation_errors(errors=[])

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text
        log_msg(f"\ncaptured_log: {captured_logs}", LogLevel.DEBUG)

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_logger_validation_errors_UT_C0_not_dict(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        validation_errors_not_dict: list,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: error list構成典型ケース
                - errors listのみを指定
                - errors listには1件のみdist出ないObjectを格納
                - カスタムロガー出力, caplogFixtureの支援で確認を行う
                - Unexpected error format at row MSGを検出
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'errors list: {validation_errors_not_dict}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Unexpected error format at row"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('aaa'), # 本件テストではExcelファイルには依存性無いので仮のPath指定で良いこととする
        )
        # 結果定義,関数実行
        _ = excel_instance.logger_validation_errors(validation_errors_not_dict)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_logger_validation_errors_UT_C0_contain_other_key(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        validation_errors_contain_other_key: list,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: error list構成典型ケース
                - errors listのみを指定
                - errors listには1件のみloc keyでないObjectを格納
                - カスタムロガー出力, caplogFixtureの支援で確認を行う
                - Missing key in error at row MSGを検出
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'errors list: {validation_errors_contain_other_key}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Missing key in error at row"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('aaa'), # 本件テストではExcelファイルには依存性無いので仮のPath指定で良いこととする
        )
        # 結果定義,関数実行
        _ = excel_instance.logger_validation_errors(validation_errors_contain_other_key)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text
        log_msg(f"\ncaptured_log: {captured_logs}", LogLevel.ERROR)

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_logger_validation_errors_UT_C2_two_errors_one_record(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        validation_errors_normal_two_error_on_one_record: list,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: error list構成典型ケース
                - errors listのみを指定
                - errors listには2件のエラー配列を格納,同一レコードでエラー2明細
                - カスタムロガー出力, caplogFixtureの支援で確認を行う
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'errors list: {validation_errors_normal_two_error_on_one_record}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg1 = "Validation error at (1, e):  Input should be a valid integer, wrong values: あ"
        expected_log_msg2 = "Validation error at (1, g):  Input should be a valid string, wrong values: 1"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('aaa'), # 本件テストではExcelファイルには依存性無いので仮のPath指定で良いこととする
        )
        # 結果定義,関数実行
        _ = excel_instance.logger_validation_errors(validation_errors_normal_two_error_on_one_record)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg1 in captured_logs, f"Expected log message '{expected_log_msg1}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert expected_log_msg2 in captured_logs, f"Expected log message '{expected_log_msg2}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_logger_validation_errors_UT_C2_two_errors_another_record(
        self,
        mocker:MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        validation_errors_normal_two_errors_anather_record: list,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: error list構成典型ケース
                - errors listのみを指定
                - errors listには2件のみエラー配列を格納,別レコードで1明細づつ
                - カスタムロガー出力, caplogFixtureの支援で確認を行う
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'errors list: {validation_errors_normal_two_errors_anather_record}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg1 = "Validation error at (1, e):  Input should be a valid integer, wrong values: あ"
        expected_log_msg2 = "Validation error at (2, d):  Input should be a valid integer, wrong values: s"

        # インスタンス生成
        excel_instance = ExcelDataLoader(
            file_path = Path('aaa'), # 本件テストではExcelファイルには依存性無いので仮のPath指定で良いこととする
        )
        # 結果定義,関数実行
        _ = excel_instance.logger_validation_errors(validation_errors_normal_two_errors_anather_record)

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg1 in captured_logs, f"Expected log message '{expected_log_msg1}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
        assert expected_log_msg2 in captured_logs, f"Expected log message '{expected_log_msg2}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"
