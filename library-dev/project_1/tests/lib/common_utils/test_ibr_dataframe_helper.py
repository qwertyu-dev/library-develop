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
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe

#####################################################################
# テスト実行環境セットアップ
#####################################################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config
from tabulate import tabulate

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

#####################################################################
# データ作成
#####################################################################
@pytest.fixture(scope='function')
def dataframe_normal() -> pd.DataFrame:
    # setup
    return pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6],
        'C': [7, 8, 9],
    })

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません

@pytest.fixture(scope='function')
def dataframe_empty() -> pd.DataFrame:
    # setup
    return pd.DataFrame(columns=['A', 'B', 'C'])

    # 実行
    #yield

    # tear down
    # Notes:
    #   pytestのtmp系はデフォルトで3セッションのみ維持します
    #   従ってtear downでtmp利用資源は明示削除は必須ではありません


class Test_tabulate_dataframe:
    """tabulate_dataframeのテスト全体をまとめたClass

    C0: 命令カバレッジ
        - headerパラメータを与えない
        - tablefmtパラメータを与えない
        - 例外発生
    C1: 分岐カバレッジ
        - 引数カバレッジ
            - headerパラメータを与える,dataframeのcolumnsと合致 # C0で検証済
            - headerパラメータにNoneを与える
            - tablefmtパラメータにpipe以外を与える # C0で検証済
            - tablefmtパラメータにNone設定する
    C2: 条件カバレッジ
        - dataframeが空
        - dataframeのcolumnsとheadersが合致しない
    """

    def test_tabulate_dataframe_UT_C0_only_dataframe_params(
        self,
        dataframe_normal: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - テストシナリオ: デフォルトパラメータ通りに与える
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'DataFrame: {dataframe_normal.dtypes}', LogLevel.DEBUG)

        # 結果定義,関数実行
        expected = """|    |   A |   B |   C |
|---:|----:|----:|----:|
|  0 |   1 |   4 |   7 |
|  1 |   2 |   5 |   8 |
|  2 |   3 |   6 |   9 |"""

        # dataframeのみ指定
        result = tabulate_dataframe(dataframe_normal)
        log_msg(f'expected: {expected}', LogLevel.DEBUG)
        log_msg(f'result: {result}', LogLevel.DEBUG)

        # 結果評価
        assert isinstance(result, str), f"Expected result to be a list, but got {type(result).__name__}"
        assert result == expected, f"Expected {expected}, but got {result}"


    def test_tabulate_dataframe_UT_C0_Specify_all_params(
        self,
        dataframe_normal: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - tabulate自体の結果と比較する
                    - パラメータなしと全パラメータ(デフォルト値)
                    - パラメータheadersにlist指定(dataframeのcolumnsと一致)
                    - パラメータtablefmtにgrid指定
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'DataFrame: {dataframe_normal.dtypes}', LogLevel.DEBUG)

        # 結果評価
        assert tabulate_dataframe(dataframe_normal) == tabulate(dataframe_normal, headers='keys', tablefmt='pipe')
        assert tabulate_dataframe(dataframe_normal, headers=['A', 'B', 'C']) == tabulate(dataframe_normal, headers=['A', 'B', 'C'], tablefmt='pipe')
        assert tabulate_dataframe(dataframe_normal, tablefmt='grid') == tabulate(dataframe_normal, headers='keys', tablefmt='grid')


    def test_tabulate_dataframe_UT_C0_raise_exception(
        self,
        mocker: MagicMock,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        dataframe_normal: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - raise Exception
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'DataFrame: {dataframe_normal.dtypes}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = "Traceback"

        # 実行/例外強制
        mocker.patch('src.lib.common_utils.ibr_dataframe_helper._tabulate_wrapper', side_effect=Exception)
        with pytest.raises(Exception):
            assert tabulate_dataframe(dataframe_normal) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"


    def test_tabulate_dataframe_UT_C1_Specify_params_none(
        self,
        dataframe_normal: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - tabulate自体の結果と比較する,デフォルト値で稼働する
                    - headers=None
                    - tablefmt=None
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'DataFrame: {dataframe_normal.dtypes}', LogLevel.DEBUG)

        # 結果評価
        assert tabulate_dataframe(dataframe_normal, headers=None) == tabulate(dataframe_normal, headers='keys', tablefmt='pipe')
        assert tabulate_dataframe(dataframe_normal, tablefmt=None) == tabulate(dataframe_normal, headers='keys', tablefmt='pipe')


    def test_tabulate_dataframe_UT_C2_empty(
        self,
        dataframe_empty: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C0
                - テスト区分: 正常系/UT
                - tabulate自体の結果と比較する,デフォルト値で稼働する
                    - headers=None
                    - tablefmt=None
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'DataFrame: {dataframe_empty.dtypes}', LogLevel.DEBUG)
        # 結果定義,関数実行
        expected = """| A   | B   | C   |
|-----|-----|-----|"""

        # 結果評価
        assert tabulate_dataframe(dataframe_empty) == tabulate(dataframe_empty, headers='keys', tablefmt='pipe')
        log_msg(f'result: {tabulate_dataframe(dataframe_empty)}')
        result = tabulate_dataframe(dataframe_empty)
        assert expected == result


    def test_tabulate_dataframe_UT_C2_not_match_headers(
        self,
        caplog: pytest.LogCaptureFixture,
        capfd: pytest.LogCaptureFixture,
        dataframe_normal: pd.DataFrame,
        ) -> None:
        # テスト定義ログ出力はこのまま書いてください、改修不要
        test_doc = """
        - テスト定義:
                - テストカテゴリ: C2
                - テスト区分: 正常系/UT
                    |    |    |   A |   B |
                    |---:|---:|----:|----:|
                    |  0 |  1 |   4 |   7 |
                    |  1 |  2 |   5 |   8 |
                    |  2 |  3 |   6 |   9 |
                    なんだかイマイチな結果になっているので、DataFrameのcolumnsとheaders(listのとき)は一致していないとよろしく無い感触
        """
        test_functions = [func for func in dir(self) if callable(getattr(self, func)) and func.startswith('test')]
        func_info = f"        - テスト関数: {', '.join(test_functions)}"
        log_msg(f"\n{func_info}{test_doc}", LogLevel.DEBUG)

        # テスト記述
        log_msg(f'DataFrame: {dataframe_normal.dtypes}', LogLevel.DEBUG)

        # caplogを使ってログメッセージをキャプチャ
        caplog.set_level(LogLevel.ERROR.value)

        # 期待されるログメッセージ
        expected_log_msg = 'DataFrame.columnsとheadersの列数は一致している必要があります'

        # 結果評価
        with pytest.raises(ValueError):
            assert tabulate_dataframe(dataframe_normal, headers=['A', 'B']) is True

        # キャプチャされたログメッセージを取得
        captured_logs = caplog.text

        # ログメッセージが期待通りのものか確認
        assert expected_log_msg in captured_logs, f"Expected log message '{expected_log_msg}' to be in captured logs, but it was not. Captured logs: '{captured_logs}'"

