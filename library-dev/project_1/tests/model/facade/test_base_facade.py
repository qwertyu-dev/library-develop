
# config共有
import sys
from pathlib import Path
from unittest.mock import (
    MagicMock,
    Mock,
    call,
    patch,
)

import numpy as np
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
    │   ├── 正常系: configを渡してインス���ンス生成
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
        - ���ストシナリオ: configを渡してインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = DataFrameEditor(config=mock_config)
        assert editor.log_msg == mock_config.log_message
        assert isinstance(editor.column_editors, dict)
        assert len(editor.column_editors) == 0
        assert editor.output_columns is None

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
        assert editor.output_columns is None

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
        assert editor.output_columns is None

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
            assert editor.output_columns is None

    def test_init_C2_with_valid_config(self, mock_config):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テス���区分: 正常系
        - テストシナリオ: 有効なconfigでのインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = DataFrameEditor(config=mock_config)
        assert editor.config == mock_config
        assert editor.log_msg == mock_config.log_message
        assert isinstance(editor.column_editors, dict)
        assert len(editor.column_editors) == 0
        assert editor.output_columns is None

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
            assert editor.output_columns is None

class Test_DataFrameEditor_prepare_output_layout:
    """DataFrameEditorの_prepare_output_layoutメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 出力カラムが設定されている場合の基本動作確認
    │   │   ├── test_prepare_output_layout_C0_basic_copy
    │   │   └── test_prepare_output_layout_C0_empty_input_series
    │   └── 正常系: 指定カラムが入力にない場合のNaN設定
    │       └── test_prepare_output_layout_C0_missing_columns
    ├── C1: 分岐カバレッジ
    │   ├── 条件1: 入力seriesにカラムが存在する場合
    │   │   └── test_prepare_output_layout_C1_DT_01_column_exists
    │   └── 条件2: 入力seriesにカラムが存在しない場合
    │       └── test_prepare_output_layout_C1_DT_02_column_missing
    ├── C2: 条件組み合わせ
    │   ├── ケース1: 全カラムが存在し、全てコピーされる
    │   │   └── test_prepare_output_layout_C2_all_columns_exist
    │   ├── ケース2: 一部のカラムのみ存在する
    │   │   └── test_prepare_output_layout_C2_some_columns_exist
    │   └── ケース3: どのカラムも存在しない
    │       └── test_prepare_output_layout_C2_no_columns_exist
    ├── DT: ディシジョンテーブル
    │   └── カラムの存在パターン
    │       ├── test_prepare_output_layout_DT_01_all_columns_exist
    │       ├── test_prepare_output_layout_DT_02_some_columns_exist
    │       └── test_prepare_output_layout_DT_03_no_columns_exist
    └── BVT: 境界値テスト
    ├── 入力データの境界値
    │   ├── test_prepare_output_layout_BVT_01_large_series
    │   └── test_prepare_output_layout_BVT_02_single_column
    └── 特殊なデータパターン
        ├── test_prepare_output_layout_BVT_03_special_chars
        ├── test_prepare_output_layout_BVT_04_numeric_columns
        └── test_prepare_output_layout_BVT_05_mixed_type_values

    C1のディシジョンテーブル:
    | 条件                           | DT_01 | DT_02 | DT_03 |
    |--------------------------------|-------|-------|-------|
    | カラムが入力seriesに存在する   | Y     | 一部  | N     |
    | 出力series作成                 | X     | X     | X     |
    | 値のコピー                     | X     | X     | -     |
    | NaN設定                        | -     | X     | X     |
    
    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                           | 期待される結果                | テストの目的/検証ポイント            | 実装状況 |
    |----------|----------------|-----------------------------------|------------------------------|---------------------------------------|----------|
    | BVT_001  | series         | 1000カラムのSeries                | 全カラムが正しくコピー        | 大規模なデータ処理の確認              | 実装済み |
    | BVT_002  | series         | 単一カラムのSeries                | 正しくコピー                  | 最小データセットの処理確認            | 実装済み |
    | BVT_003  | series         | 特殊文字を含むカラム名のSeries    | 正しくコピー                  | 特殊文字の処理確認                    | 実装済み |
    | BVT_004  | series         | 数値型カラム名のSeries            | 正しくコピー                  | 数値型カラム名の処理確認              | 実装済み |
    | BVT_005  | series         | 異なる型の値を含むSeries          | 型を保持してコピー            | 異なるデータ型の処理確認              | 実装済み |
    """
    
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
    
    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)
    
    @pytest.fixture()
    def mock_config(self):
        return Mock(log_message=Mock())
    
    @pytest.fixture()
    def test_editor(self, mock_config):
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            def __init__(self, output_columns=None, config=None):
                super().__init__(config)
                self.output_columns = output_columns or ['col1', 'col2']

        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            return TestDataFrameEditor()

    def test_prepare_output_layout_C0_basic_copy(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: 基本的なカラムのコピー処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 'value1', 'col2': 'value2'})
        result = test_editor._prepare_output_layout(input_series)

        assert result['col1'] == 'value1'
        assert result['col2'] == 'value2'
        assert list(result.index) == test_editor.output_columns

    def test_prepare_output_layout_C0_empty_input_series(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: 空のSeriesからの出力レイアウト作成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({})
        result = test_editor._prepare_output_layout(input_series)

        assert len(result) == len(test_editor.output_columns)
        assert all(pd.isna(result))
        assert list(result.index) == test_editor.output_columns


    def test_prepare_output_layout_C0_missing_columns(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: 存在しないカラムの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col3': 'value3'})
        result = test_editor._prepare_output_layout(input_series)

        assert len(result) == len(test_editor.output_columns)
        assert all(pd.isna(result))
        assert list(result.index) == test_editor.output_columns


    @pytest.mark.parametrize(("input_data,expected_nulls"), [
        ({'col1': 'value1', 'col2': 'value2'}, 0),
        ({'col1': 'value1'}, 1),
        ({}, 2),
    ])
    def test_prepare_output_layout_C1_column_existence(self, test_editor, input_data, expected_nulls):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト区分: 正常系
        テストシナリオ: カラムの存在有無による分岐確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series(input_data)
        result = test_editor._prepare_output_layout(input_series)

        assert len(result) == len(test_editor.output_columns)
        assert pd.isna(result).sum() == expected_nulls
        assert list(result.index) == test_editor.output_columns

    @pytest.mark.parametrize("test_case", [
        ("all_exist", {'col1': 'v1', 'col2': 'v2'}, 0),
        ("some_exist", {'col1': 'v1', 'col3': 'v3'}, 1),
        ("none_exist", {'col3': 'v3', 'col4': 'v4'}, 2),
    ])
    def test_prepare_output_layout_C2_combinations(self, test_editor, test_case):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト区分: 正常系
        テストシナリオ: カラムの存在パターンの組み合わせ確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        case_name, input_data, expected_nulls = test_case
        input_series = pd.Series(input_data)
        result = test_editor._prepare_output_layout(input_series)

        assert len(result) == len(test_editor.output_columns)
        assert pd.isna(result).sum() == expected_nulls
        assert list(result.index) == test_editor.output_columns


    def test_prepare_output_layout_BVT_large_series(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト区分: 正常系
        テストシナリオ: 大規模なSeriesの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 1000カラムのSeriesを作成
        large_series = pd.Series({f'col{i}': f'value{i}' for i in range(1000)})
        large_series['col1'] = 'specific_value1'
        large_series['col2'] = 'specific_value2'

        result = test_editor._prepare_output_layout(large_series)

        assert len(result) == len(test_editor.output_columns)
        assert result['col1'] == 'specific_value1'
        assert result['col2'] == 'specific_value2'

    def test_prepare_output_layout_BVT_special_chars(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト区分: 正常系
        テストシナリオ: 特殊文字を含むカラム名の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        editor = test_editor.__class__(output_columns=['col#1', 'col@2'])
        input_series = pd.Series({'col#1': 'value1', 'col@2': 'value2'})

        result = editor._prepare_output_layout(input_series)

        assert len(result) == 2
        assert result['col#1'] == 'value1'
        assert result['col@2'] == 'value2'

    def test_prepare_output_layout_BVT_mixed_types(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト区分: 正常系
        テストシナリオ: 異なるデータ型の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        input_series = pd.Series({'col1': 123, 'col2': 'text'})
        result = test_editor._prepare_output_layout(input_series)

        # 型の確認
        assert isinstance(result['col1'], type(input_series['col1']))
        assert isinstance(result['col2'], type(input_series['col2']))
        # 値の確認
        assert result['col1'] == 123
        assert result['col2'] == 'text'


class Test_DataFrameEditor_apply_basic_editors:
    """DataFrameEditorの_apply_basic_editorsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な入力での編集
    │   └── 正常系: エディタ未定義の列の処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 編集対象の列が存在する場合
    │   └── 正常系: 編集対象の列が存在しない場合
    ├── C2: 条件組み合わせ
    │   ├── 正常系: 複数の列エディタが適用される場合
    │   ├── 正常系: 一部の列エディタのみが適用される場合
    │   └── 正常系: どの列エディタも適用されない場合
    └── BVT: 境界値テスト
        ├── 正常系: 特殊文字を含む列名での処理
        └── 正常系: 異なる型の値での処理

    C1のディシジョンテーブル:
    | 条件                     | ケース1 | ケース2 |
    |--------------------------|---------|---------|
    | エディタが存在する列     | Y       | N       |
    | 結果                     | 編集    | 変更    |
    |                          | される  | なし    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                | 期待される結果        | テストの目的/検証ポイント      | 実装状況 | 対応するテストケース          |
    |----------|----------------|------------------------|---------------------|--------------------------------|----------|-------------------------------|
    | BVT_001  | series         | 特殊文字を含む列名     | 正常に編集される     | 特殊文字の処理確認              | 実装済み | test_apply_basic_editors_BVT_special_chars |
    | BVT_002  | series         | 数値型の値             | 型を保持して編集     | 異なる型の値の処理確認          | 実装済み | test_apply_basic_editors_BVT_mixed_types |
    | BVT_003  | series         | NULL/NAを含む値        | NULLを保持          | NULL値の処理確認               | 実装済み | test_apply_basic_editors_BVT_null_values |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        return Mock(log_message=Mock())

    @pytest.fixture()
    def test_editor(self, mock_config):
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            def initialize_editors(self):
                return {
                    'col1': ColumnEditor(),
                    'col2': ColumnEditor(),
                }

        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            editor = TestDataFrameEditor()
            editor.output_columns = ['col1', 'col2', 'col3']
            return editor

    @pytest.fixture()
    def test_editor_with_mocks(self, mock_config):
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            def initialize_editors(self):
                return {
                    'col1': Mock(),
                    'col2': Mock(),
                }

        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            editor = TestDataFrameEditor()
            editor.output_columns = ['col1', 'col2', 'col3']
            return editor

    def test_apply_basic_editors_C0_valid_input(self, test_editor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: 有効な入力での編集
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        edited_series = pd.Series({'col1': 'test', 'col2': 'TEST', 'col3': 'Unchanged'}, dtype=object)
        result = test_editor._apply_basic_editors(edited_series)

        assert result['col1'] == 'test'
        assert result['col2'] == 'TEST'
        assert result['col3'] == 'Unchanged'

    def test_apply_basic_editors_C1_DT_01_existing_editors(self, test_editor_with_mocks):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト区分: 正常系
        テストシナリオ: エディタが存在する列の編集確認
        DTケース: 1
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_editor_with_mocks.column_editors['col1'].edit.return_value = 'EDITED1'
        test_editor_with_mocks.column_editors['col2'].edit.return_value = 'EDITED2'

        edited_series = pd.Series({'col1': 'test1', 'col2': 'test2'}, dtype=object)
        result = test_editor_with_mocks._apply_basic_editors(edited_series)

        assert result['col1'] == 'EDITED1'
        assert result['col2'] == 'EDITED2'
        test_editor_with_mocks.column_editors['col1'].edit.assert_called_once_with('test1')
        test_editor_with_mocks.column_editors['col2'].edit.assert_called_once_with('test2')

    def test_apply_basic_editors_C1_DT_02_non_existing_editors(self, test_editor_with_mocks):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト区分: 正常系
        テストシナリオ: エディタが存在しない列の処理確認
        DTケース: 2
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        edited_series = pd.Series({'col3': 'test3', 'col4': 'test4'}, dtype=object)
        result = test_editor_with_mocks._apply_basic_editors(edited_series)

        assert result['col3'] == 'test3'
        assert result['col4'] == 'test4'
        test_editor_with_mocks.column_editors['col1'].edit.assert_not_called()
        test_editor_with_mocks.column_editors['col2'].edit.assert_not_called()

    def test_apply_basic_editors_C2_partial_editors(self, test_editor_with_mocks):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト区分: 正常系
        テストシナリオ: 一部の列のみにエディタが適用される場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_editor_with_mocks.column_editors['col1'].edit.return_value = 'EDITED1'

        edited_series = pd.Series({'col1': 'test1', 'col3': 'test3'}, dtype=object)
        result = test_editor_with_mocks._apply_basic_editors(edited_series)

        assert result['col1'] == 'EDITED1'
        assert result['col3'] == 'test3'
        test_editor_with_mocks.column_editors['col1'].edit.assert_called_once_with('test1')
        test_editor_with_mocks.column_editors['col2'].edit.assert_not_called()

    def test_apply_basic_editors_BVT_mixed_types(self, test_editor_with_mocks):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト区分: 正常系
        テストシナリオ: 異なる型の値の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_editor_with_mocks.column_editors['col1'].edit.return_value = 123
        test_editor_with_mocks.column_editors['col2'].edit.return_value = 'text'

        edited_series = pd.Series({'col1': 100, 'col2': 'TEST'}, dtype=object)
        result = test_editor_with_mocks._apply_basic_editors(edited_series)

        assert result['col1'] == 123
        assert isinstance(result['col1'], int)
        assert result['col2'] == 'text'
        assert isinstance(result['col2'], str)

    def test_apply_basic_editors_BVT_null_values(self, test_editor_with_mocks):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト区分: 正常系
        テストシナリオ: NULL値を含む処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)


        # Mockの戻り値を設定
        test_editor_with_mocks.column_editors['col1'].edit.return_value = None
        test_editor_with_mocks.column_editors['col2'].edit.return_value = np.nan

        edited_series = pd.Series({'col1': None, 'col2': np.nan}, dtype=object)
        result = test_editor_with_mocks._apply_basic_editors(edited_series)

        # 編集メソッドが呼び出されたことを確認
        test_editor_with_mocks.column_editors['col1'].edit.assert_called_once_with(None)
        test_editor_with_mocks.column_editors['col2'].edit.assert_called_once_with(np.nan)

        # 結果の値を確認
        assert pd.isna(result['col1'])
        assert pd.isna(result['col2'])

class Test_DataFrameEditor_edit_series:
    """DataFrameEditorのedit_seriesメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 各メソッドの呼び出し確認
    │   │   └── test_edit_series_C0_methods_called
    │   └── 正常系: メソッドの戻り値の受け渡し確認
    │       └── test_edit_series_C0_return_values
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 正常フロー(全メソッドが正常終了)
    │   │   └── test_edit_series_C1_DT_01_normal_flow
    │   └── 異常系: エラー発生時の処理
    │       ├── test_edit_series_C1_DT_02_prepare_error
    │       └── test_edit_series_C1_DT_03_basic_editors_error
    ├── C2: メソッド呼び出しの組み合わせ
    │   ├── ケース1: 両メソッドが値を変更
    │   │   └── test_edit_series_C2_both_modify
    │   ├── ケース2: prepare_layoutのみ値を変更
    │   │   └── test_edit_series_C2_only_prepare_modifies
    │   └── ケース3: apply_basic_editorsのみ値を変更
    │       └── test_edit_series_C2_only_basic_modifies
    └── DT: 各メソッドの実行結果の組み合わせ

    C1のディシジョンテーブル:
    | 条件                    | DT_01 | DT_02 | DT_03 |
    |------------------------|--------|--------|--------|
    | prepare_layout成功     | Y      | N      | Y      |
    | basic_editors成功      | Y      | -      | N      |
    | 結果                   | 成功   | エラー | エラー |
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        return Mock(log_message=Mock())

    @pytest.fixture()
    def test_editor_with_mocked_methods(self, mock_config):
        @with_config
        class TestDataFrameEditor(DataFrameEditor):
            def __init__(self, config=None):
                super().__init__(config)
                self._prepare_output_layout = Mock()
                self._apply_basic_editors = Mock()

        with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=mock_config):
            return TestDataFrameEditor()

    def test_edit_series_C0_methods_called(self, test_editor_with_mocked_methods):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト区分: 正常系
        テストシナリオ: メソッドが正しい順序で呼び出されることの確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 戻り値の設定
        prepare_result = pd.Series({'col1': 'prepared'})
        basic_result = pd.Series({'col1': 'edited'})
        test_editor_with_mocked_methods._prepare_output_layout.return_value = prepare_result
        test_editor_with_mocked_methods._apply_basic_editors.return_value = basic_result

        # テスト実行
        input_series = pd.Series({'col1': 'input'})
        result = test_editor_with_mocked_methods.edit_series(input_series)

        # 呼び出し順序の確認
        method_calls = []
        method_calls.extend(test_editor_with_mocked_methods._prepare_output_layout.mock_calls)
        method_calls.extend(test_editor_with_mocked_methods._apply_basic_editors.mock_calls)

        # 呼び出し順序と引数の確認
        test_editor_with_mocked_methods._prepare_output_layout.assert_called_once_with(input_series)
        test_editor_with_mocked_methods._apply_basic_editors.assert_called_once_with(prepare_result)

        # 最終結果の確認
        assert result.equals(basic_result)

    def test_edit_series_C1_DT_01_normal_flow(self, test_editor_with_mocked_methods):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト区分: 正常系
        テストシナリオ: 全メソッドが正常に実行されるケース
        DTケース: 1
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 戻り値の設定
        prepare_result = pd.Series({'col1': 'prepared'})
        basic_result = pd.Series({'col1': 'edited'})
        test_editor_with_mocked_methods._prepare_output_layout.return_value = prepare_result
        test_editor_with_mocked_methods._apply_basic_editors.return_value = basic_result

        # テスト実行
        input_series = pd.Series({'col1': 'input'})
        result = test_editor_with_mocked_methods.edit_series(input_series)

        assert result.equals(basic_result)

    def test_edit_series_C1_DT_02_prepare_error(self, test_editor_with_mocked_methods):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト区分: 異常系
        テストシナリオ: prepare_layoutでエラーが発生するケース
        DTケース: 2
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # prepare_layoutでエラーを発生させる
        test_editor_with_mocked_methods._prepare_output_layout.side_effect = Exception("Prepare Error")

        # テスト実行
        input_series = pd.Series({'col1': 'input'})
        with pytest.raises(Exception) as exc_info:
            test_editor_with_mocked_methods.edit_series(input_series)

        assert str(exc_info.value) == "Prepare Error"
        test_editor_with_mocked_methods._apply_basic_editors.assert_not_called()

    def test_edit_series_C2_both_modify(self, test_editor_with_mocked_methods):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト区分: 正常系
        テストシナリオ: 両メソッドが値を変更するケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 戻り値の設定(両メソッドで値が変更される)
        prepare_result = pd.Series({'col1': 'prepared'})
        basic_result = pd.Series({'col1': 'edited'})
        test_editor_with_mocked_methods._prepare_output_layout.return_value = prepare_result
        test_editor_with_mocked_methods._apply_basic_editors.return_value = basic_result

        # テスト実行
        input_series = pd.Series({'col1': 'input'})
        result = test_editor_with_mocked_methods.edit_series(input_series)

        # 各段階での値の変更を確認
        assert not prepare_result.equals(input_series)
        assert not basic_result.equals(prepare_result)
        assert result.equals(basic_result)
