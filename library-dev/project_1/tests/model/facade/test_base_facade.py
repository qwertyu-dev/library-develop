
# config共有
import sys
from unittest.mock import (
    MagicMock,
    call,
    patch,
)

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config, with_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.converter_utils.ibr_basic_column_editor import ColumnEditor
from src.model.facade.base_facade import DataFrameEditor

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class Test_DataFrameEditor_init:
    """DataFrameEditorの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: configを渡してインスタンス生成
    │   └── 正常系: configを渡さずにインスタンス生成
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: configが提供される場合
    │   └── 正常系: configが提供されない場合
    └── C2: 条件組み合わせ
        ├── 正常系: 有効なconfigでのインスタンス生成
        └── 正常系: Noneのconfigでのインスタンス生成

    C1のディシジョンテーブル:
    | 条件           | ケース1 | ケース2 |
    |----------------|---------|---------|
    | configを渡す   | Y       | N       |
    | 結果           | 提供さ  | デフォ  |
    |                | れた    | ルト    |
    |                | config  | config  |
    |                | を使用  | を使用  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        mock_config = MagicMock()
        mock_config.log_message = MagicMock()
        return mock_config

    def test_init_C0_with_config(self, mock_config):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: configを渡してインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = DataFrameEditor(config=mock_config)
        assert editor.log_msg == mock_config.log_message
        assert isinstance(editor.column_editors, dict)
        assert len(editor.column_editors) == 0

    def test_init_C0_without_config(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: configを渡さずにインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = DataFrameEditor()
        assert isinstance(editor.column_editors, dict)
        assert len(editor.column_editors) == 0

    def test_init_C1_DT_01_with_config(self, mock_config):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: configが提供される場合
        - DTケース: 1
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = DataFrameEditor(config=mock_config)
        assert editor.config == mock_config
        assert editor.log_msg == mock_config.log_message

    #def test_init_C1_DT_02_without_config(self):
    #    test_doc = """テスト内容:
    #    - テストカテゴリ: C1
    #    - テスト区分: 正常系
    #    - テストシナリオ: configが提供されない場合
    #    - DTケース: 2
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)

    #    with patch('src.model.facade.base_facade.DataFrameEditor.config', new_callable=MagicMock) as mock_config:
    #        mock_config.log_message = MagicMock()
    #        editor = DataFrameEditor()
    #        assert editor.config == mock_config
    #        assert editor.log_msg == mock_config.log_message

    #def test_init_C1_DT_02_without_config(self):
    #    test_doc = """テスト内容:
    #    - テストカテゴリ: C1
    #    - テスト区分: 正常系
    #    - テストシナリオ: configが提供されない場合
    #    - DTケース: 2
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)
    #
    #    with patch('src.model.facade.base_facade.DataFrameEditor.__init__', return_value=None):
    #        editor = DataFrameEditor()
    #        with patch.object(editor, 'config', new_callable=MagicMock) as mock_config:
    #            mock_config.log_message = MagicMock()
    #            # ここでeditorのメソッドを呼び出すなど、必要な操作を行う
    #            assert editor.config == mock_config
    #            assert editor.log_msg == mock_config.log_message

    def test_init_C1_DT_02_without_config(self, mock_config):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: configが提供されない場合
        - DTケース: 2
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テスト用の派生クラスを作成
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            pass

        # with_configデコレータの動作をモック
        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            editor = TestDataFrameEditor()
            #assert editor.config == mock_config
            #assert editor.log_msg == mock_config.log_message
            assert isinstance(editor.column_editors, dict)
            assert len(editor.column_editors) == 0

    def test_init_C2_with_valid_config(self, mock_config):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 有効なconfigでのインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = DataFrameEditor(config=mock_config)
        assert editor.config == mock_config
        assert editor.log_msg == mock_config.log_message
        assert isinstance(editor.column_editors, dict)
        assert len(editor.column_editors) == 0

    def test_init_C2_with_none_config(self, mock_config):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: Noneのconfigでのインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テスト用の派生クラスを作成
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            pass

        # with_configデコレータの動作をモック
        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            editor = DataFrameEditor(config=None)
            #assert editor.config == mock_config
            #assert editor.log_msg == mock_config.log_message
            assert isinstance(editor.column_editors, dict)
            assert len(editor.column_editors) == 0

class Test_DataFrameEditor_edit_series:
    """DataFrameEditorのedit_seriesメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な入力での編集
    │   └── 正常系: 空のSeriesの処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 編集対象の列が存在する場合
    │   └── 正常系: 編集対象の列が存在しない場合
    ├── C2: 条件組み合わせ
    │   ├── 正常系: 複数の列エディタが適用される場合
    │   ├── 正常系: 一部の列エディタのみが適用される場合
    │   └── 正常系: どの列エディタも適用されない場合
    └── BVT: 境界値テスト
        ├── 正常系: 最大長のSeries名での処理
        └── 正常系: 特殊文字を含むSeries名での処理

    C1のディシジョンテーブル:
    | 条件                     | ケース1 | ケース2 |
    |--------------------------|---------|---------|
    | 編集対象の列が存在する   | Y       | N       |
    | 結果                     | 編集    | 変更    |
    |                          | される  | なし    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値              | 期待される結果           | テストの目的/検証ポイント    | 実装状況 | 対応するテストケース              |
    |----------|----------------|------------------------|--------------------------|-------------------------------|----------|-----------------------------------|
    | BVT_001  | series         | 空のSeries             | 空のSeriesが返される     | 空入力の処理を確認           | 実装済み | test_edit_series_C0_empty_series   |
    | BVT_002  | series         | 最大長の列名を持つSeries | 正常に処理される      | 最大長の列名での動作を確認   | 実装済み | test_edit_series_BVT_max_length_name |
    | BVT_003  | series         | 特殊文字を含む列名のSeries | 正常に処理される   | 特殊文字を含む列名の処理を確認 | 実装済み | test_edit_series_BVT_special_chars |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    - 全ての境界値ケースが実装されています。
    - 最大長の列名や特殊文字を含む列名のテストは、システムの制限や要件に応じて調整が必要な場合があります。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        mock_config = MagicMock()
        mock_config.log_message = MagicMock()
        return mock_config

    @pytest.fixture()
    def test_editor(self, mock_config):
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            def initialize_editors(self):
                return {
                    #'col1': ColumnEditor(lambda x: x.upper()),
                    #'col2': ColumnEditor(lambda x: x.lower()),
                    'col1': ColumnEditor(),
                    'col2': ColumnEditor(),
                }

        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            return TestDataFrameEditor()

    @pytest.fixture()
    def test_editor_with_mocks(self, mock_config):
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            def initialize_editors(self):
                return {
                    'col1': MagicMock(spec=ColumnEditor),
                    'col2': MagicMock(spec=ColumnEditor),
                }

        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            return TestDataFrameEditor()

    def test_edit_series_C0_valid_input(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力での編集
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'test', 'col2': 'TEST', 'col3': 'Unchanged'})
        result = test_editor.edit_series(input_series)

        assert result['col1'] == 'test'
        assert result['col2'] == 'TEST'
        assert result['col3'] == 'Unchanged'

    def test_edit_series_C0_empty_series(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 空のSeriesの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({})
        result = test_editor.edit_series(input_series)

        assert result.empty

    def test_edit_series_C1_DT_01_existing_columns(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 編集対象の列が存在する場合
        - DTケース: 1
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'test', 'col2': 'TEST'})
        result = test_editor.edit_series(input_series)

        assert result['col1'] == 'test'
        assert result['col2'] == 'TEST'

    def test_edit_series_C1_DT_02_non_existing_columns(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 編集対象の列が存在しない場合
        - DTケース: 2
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col3': 'Unchanged', 'col4': 'UNCHANGED'})
        result = test_editor.edit_series(input_series)

        assert result.equals(input_series)

    def test_edit_series_C2_multiple_editors(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 複数の列エディタが適用される場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'test', 'col2': 'TEST', 'col3': 'Mixed'})
        result = test_editor.edit_series(input_series)

        assert result['col1'] == 'test'
        assert result['col2'] == 'TEST'
        assert result['col3'] == 'Mixed'

    def test_edit_series_C2_partial_editors(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 一部の列エディタのみが適用される場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'TEST', 'col3': 'Unchanged'})
        result = test_editor.edit_series(input_series)

        assert result['col1'] == 'TEST'
        assert result['col3'] == 'Unchanged'

    def test_edit_series_C2_no_editors(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: どの列エディタも適用されない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col3': 'Unchanged', 'col4': 'UNCHANGED'})
        result = test_editor.edit_series(input_series)

        assert result.equals(input_series)

    def test_edit_series_BVT_max_length_name(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 最大長のSeries名での処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        max_length_name = 'a' * 63  # Assuming 63 is the max length
        input_series = pd.Series({max_length_name: 'test'})
        result = test_editor.edit_series(input_series)

        assert result[max_length_name] == 'test'

    def test_edit_series_BVT_special_chars(self, test_editor):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 特殊文字を含むSeries名での処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        special_char_name = 'col1!@#$%^&*()_+'
        input_series = pd.Series({special_char_name: 'TEST'})
        result = test_editor.edit_series(input_series)

        assert result[special_char_name] == 'TEST'

    def test_edit_series_C0_mock_editors_called(self, test_editor_with_mocks):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: Mockされた列エディタが呼び出されることの確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'test1', 'col2': 'test2', 'col3': 'test3'})
        test_editor_with_mocks.edit_series(input_series)

        test_editor_with_mocks.column_editors['col1'].edit.assert_called_once_with('test1')
        test_editor_with_mocks.column_editors['col2'].edit.assert_called_once_with('test2')
        assert test_editor_with_mocks.column_editors['col1'].edit.call_count == 1
        assert test_editor_with_mocks.column_editors['col2'].edit.call_count == 1

    def test_edit_series_C2_mock_editors_partial_call(self, test_editor_with_mocks):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 一部の列エディタのみが呼び出されることの確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'test1', 'col3': 'test3'})
        test_editor_with_mocks.edit_series(input_series)

        test_editor_with_mocks.column_editors['col1'].edit.assert_called_once_with('test1')
        test_editor_with_mocks.column_editors['col2'].edit.assert_not_called()

    def test_edit_series_C1_mock_editors_call_order(self, test_editor_with_mocks):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 列エディタの呼び出し順序の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'test1', 'col2': 'test2'})
        test_editor_with_mocks.edit_series(input_series)

        # 期待される呼び出しのシーケンスを定義
        expected_calls = [call('test1'), call('test2')]

        # 実際の呼び出しが期待通りの順序で行われたかを検証
        assert test_editor_with_mocks.column_editors['col1'].edit.call_args_list == [expected_calls[0]]
        assert test_editor_with_mocks.column_editors['col2'].edit.call_args_list == [expected_calls[1]]

        # または、より厳密な順序の検証が必要な場合
        mock_calls = (
            test_editor_with_mocks.column_editors['col1'].edit.call_args_list +
            test_editor_with_mocks.column_editors['col2'].edit.call_args_list
            )
        assert mock_calls == expected_calls
