# config共有
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.packages.request_processor.excel_to_dataframe_mapper import (
    ExcelMapping,
    ExcelMappingError,
    InvalidDataError,
    JinjiExcelMapping,
    KanrenExcelMappingWithDummy,
    KanrenExcelMappingWithoutDummy,
    KokukiExcelMapping,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestExcelMappingInit:
    """ExcelMappingの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な設定でインスタンス生成
    │   └── 正常系: デフォルト設定でインスタンス生成
    └── C1: 分岐カバレッジ
        ├── 正常系: confがNoneの場合
        └── 正常系: confが指定されている場合

    C1のディシジョンテーブル:
    | 条件           | ケース1 | ケース2 |
    |----------------|---------|---------|
    | confがNone     | Y       | N       |
    | 出力           | デフォルトconfig使用 | 指定されたconfig使用 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | conf           | None     | デフォルトconfigが使用される | Noneが正しく処理されることを確認 | 実装済み (test_init_C0_default_configuration) |
    | BVT_002  | conf           | {}       | 空のdictが正しく処理される | 最小の有効な入力を確認 | 実装済み (test_init_C1_with_empty_conf) |
    | BVT_003  | conf           | 大きな辞書 | 大きな辞書が正しく処理される | 大量のデータの処理を確認 | 未実装 |

    注記:
    BVT_003は現在未実装です。大量のデータを含む辞書での動作確認が必要な場合は、
    このテストケースを追加することを検討してください。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        return MagicMock(log_message=MagicMock())

    def test_init_C0_default_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: デフォルト設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()

        assert excel_mapping.config is not None
        assert callable(excel_mapping.log_msg)
        assert excel_mapping._column_mapping is None
        assert isinstance(excel_mapping.unified_layout, list)
        assert 'unified_layout' in excel_mapping.config.package_config.get('layout', {})

        # unified_layoutの内容を確認
        expected_layout = [
            'ulid',
            'form_type',
            'application_type',
            'target_org',
            'business_unit_code',
            'parent_branch_code',
            'branch_code',
            'branch_name',
            'section_gr_code',
            'section_gr_name',
            'organization_name_kana',
            'resident_branch_code',
            'resident_branch_name',
            'aaa_transfer_date',
            'internal_sales_dept_code',
            'internal_sales_dept_name',
            'business_and_area_code',
            'area_name',
            'remarks',
            'section_name_en',
            'section_name_kana',
            'section_name_abbr',
            'bpr_target_flag',
        ]
        assert excel_mapping.unified_layout == expected_layout

        log_msg(f"unified_layout: {excel_mapping.unified_layout}", LogLevel.DEBUG)

    def test_init_C0_full_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 完全な設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        custom_config = initialize_config(sys.modules[__name__])
        custom_config.package_config['layout'] = {
            'unified_layout': [
                'ulid',
                'form_type',
                'application_type',
                'target_org',
                'business_unit_code',
                'parent_branch_code',
                'branch_code',
                'branch_name',
                'section_gr_code',
                'section_gr_name',
                'section_name_en',
            ],
        }

        excel_mapping = ExcelMapping(custom_config)

        assert excel_mapping.config == custom_config
        assert excel_mapping.log_msg == custom_config.log_message
        assert excel_mapping._column_mapping is None
        assert isinstance(excel_mapping.unified_layout, list)
        assert excel_mapping.unified_layout == custom_config.package_config['layout']['unified_layout']

        log_msg(f"unified_layout: {excel_mapping.unified_layout}", LogLevel.DEBUG)

    def test_init_C1_with_none_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: confがNoneの場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping(None)

        assert excel_mapping.config is not None
        assert callable(excel_mapping.log_msg)
        assert excel_mapping._column_mapping is None
        assert isinstance(excel_mapping.unified_layout, list)

        log_msg(f"unified_layout: {excel_mapping.unified_layout}", LogLevel.DEBUG)

    def test_init_C1_with_minimal_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 最小限の設定が指定されている場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_config = initialize_config(sys.modules[__name__])
        minimal_config.package_config['layout'] = {'unified_layout': []}

        excel_mapping = ExcelMapping(minimal_config)

        assert excel_mapping.config == minimal_config
        assert excel_mapping.log_msg == minimal_config.log_message
        assert excel_mapping._column_mapping is None
        assert excel_mapping.unified_layout == []

        log_msg(f"unified_layout: {excel_mapping.unified_layout}", LogLevel.DEBUG)


class TestExcelMappingColumnMapping:
    """ExcelMappingのcolumn_mappingプロパティのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: _column_mappingが設定されている場合
    │   └── 異常系: _column_mappingがNoneの場合
    └── C1: 分岐カバレッジ
        ├── 正常系: _column_mappingが設定されている場合
        └── 異常系: _column_mappingがNoneの場合

    C1のディシジョンテーブル:
    | 条件                      | ケース1 | ケース2 |
    |---------------------------|---------|---------|
    | _column_mappingがNone     | N       | Y       |
    | 出力                      | dict    | 例外発生 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | _column_mapping | None    | NotImplementedError | Noneの場合の例外発生を確認 | 実装済み (test_column_mapping_C0_not_implemented) |
    | BVT_002  | _column_mapping | {}      | 空の辞書が返される | 最小の有効な入力を確認 | 実装済み (test_column_mapping_C0_empty_dict) |
    | BVT_003  | _column_mapping | 大きな辞書 | 大きな辞書が正しく返される | 大量のデータの処理を確認 | 実装済み (test_column_mapping_C0_large_dict) |

    注記:
    全てのケースが実装されています。大きな辞書のケース(BVT_003)は、実際のユースケースに
    基づいて適切なサイズの辞書を使用しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_column_mapping_C0_not_implemented(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: _column_mappingがNoneの場合、NotImplementedErrorが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        with pytest.raises(NotImplementedError) as exc_info:
            _ = excel_mapping.column_mappig

        assert str(exc_info.value) == 'Subclass Must implement column_mapping'
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_column_mapping_C0_empty_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: _column_mappingが空の辞書の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        excel_mapping._column_mapping = {}
        result = excel_mapping.column_mappig

        assert result == {}
        log_msg(f"Returned value: {result}", LogLevel.DEBUG)

    def test_column_mapping_C0_large_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: _column_mappingが大きな辞書の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        large_dict = {f'key_{i}': f'value_{i}' for i in range(100)}
        excel_mapping._column_mapping = large_dict
        result = excel_mapping.column_mappig

        assert result == large_dict
        log_msg(f"Returned value size: {len(result)}", LogLevel.DEBUG)

    def test_column_mapping_C1_none(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: _column_mappingがNoneの場合の分岐
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        with pytest.raises(NotImplementedError) as exc_info:
            _ = excel_mapping.column_mappig

        assert str(exc_info.value) == 'Subclass Must implement column_mapping'
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_column_mapping_C1_not_none(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: _column_mappingがNoneでない場合の分岐
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        excel_mapping._column_mapping = {'test': 'value'}
        result = excel_mapping.column_mappig

        assert result == {'test': 'value'}
        log_msg(f"Returned value: {result}", LogLevel.DEBUG)

class TestExcelMappingColumnMappingSetter:
    """ExcelMappingのcolumn_mappingセッターのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な辞書で設定
    │   └── 正常系: 空の辞書で設定
    ├── C1: 分岐カバレッジ
    │   └── 正常系: 辞書が設定される場合
    └── C2: 条件網羅
        ├── 正常系: 小さな辞書で設定
        └── 正常系: 大きな辞書で設定

    C1のディシジョンテーブル:
    | 条件           | ケース1 |
    |----------------|---------|
    | 辞書が設定される | Y       |
    | 出力           | 成功     |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | value          | {}       | 空の辞書が設定される | 最小の有効な入力を確認 | 実装済み (test_column_mapping_setter_C0_empty_dict) |
    | BVT_002  | value          | {'a': 'b'} | 単一要素の辞書が設定される | 最小の非空辞書を確認 | 実装済み (test_column_mapping_setter_C2_small_dict) |
    | BVT_003  | value          | 大きな辞書 | 大きな辞書が正しく設定される | 大量のデータの処理を確認 | 実装済み (test_column_mapping_setter_C2_large_dict) |

    注記:
    全てのケースが実装されています。大きな辞書のケース(BVT_003)は、実際のユースケースに
    基づいて適切なサイズの辞書を使用しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_column_mapping_setter_C0_valid_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効な辞書でcolumn_mappingを設定
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        test_dict = {'col1': 'column1', 'col2': 'column2'}
        excel_mapping.column_mapping = test_dict

        assert excel_mapping._column_mapping == test_dict
        log_msg(f"Set column_mapping: {excel_mapping._column_mapping}", LogLevel.DEBUG)

    def test_column_mapping_setter_C0_empty_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 空の辞書でcolumn_mappingを設定
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        excel_mapping.column_mapping = {}

        assert excel_mapping._column_mapping == {}
        log_msg(f"Set column_mapping: {excel_mapping._column_mapping}", LogLevel.DEBUG)

    def test_column_mapping_setter_C1_set_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 辞書が設定される場合の分岐
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        test_dict = {'col1': 'column1', 'col2': 'column2'}
        excel_mapping.column_mapping = test_dict

        assert excel_mapping._column_mapping == test_dict
        log_msg(f"Set column_mapping: {excel_mapping._column_mapping}", LogLevel.DEBUG)

    def test_column_mapping_setter_C2_small_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 小さな辞書でcolumn_mappingを設定
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        test_dict = {'col1': 'column1'}
        excel_mapping.column_mapping = test_dict

        assert excel_mapping._column_mapping == test_dict
        log_msg(f"Set column_mapping: {excel_mapping._column_mapping}", LogLevel.DEBUG)

    def test_column_mapping_setter_C2_large_dict(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 大きな辞書でcolumn_mappingを設定
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        test_dict = {f'col{i}': f'column{i}' for i in range(100)}
        excel_mapping.column_mapping = test_dict

        assert excel_mapping._column_mapping == test_dict
        log_msg(f"Set column_mapping size: {len(excel_mapping._column_mapping)}", LogLevel.DEBUG)

class TestExcelMappingColumnMap:
    """ExcelMappingのcolumn_mapメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 全ての列が存在する場合
    │   └── 異常系: 必要な列が欠落している場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 全ての列が存在する場合
    │   └── 異常系: 必要な列が欠落している場合
    ├── C2: 条件網羅
    │   ├── 正常系: 必要な列のみが存在する場合
    │   ├── 正常系: 必要な列と追加の列が存在する場合
    │   └── 異常系: 一部の必要な列が欠落している場合
    └── BVT: 境界値テスト
        ├── 正常系: 1行のDataFrame
        └── 正常系: 大量の行を持つDataFrame

    C1のディシジョンテーブル:
    | 条件                   | ケース1 | ケース2 |
    |------------------------|---------|---------|
    | 全ての必要な列が存在する | Y       | N       |
    | 出力                   | 成功     | 例外発生 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | df             | 空のDataFrame | InvalidDataError | 最小の無効な入力を確認 | 実装済み (test_column_map_C0_empty_dataframe) |
    | BVT_002  | df             | 1行のDataFrame | マッピングされたDataFrame | 最小の有効な入力を確認 | 実装済み (test_column_map_BVT_one_row) |
    | BVT_003  | df             | 大量の行を持つDataFrame | マッピングされたDataFrame | 大量のデータの処理を確認 | 実装済み (test_column_map_BVT_many_rows) |

    注記:
    全てのケースが実装されています。大量の行を持つDataFrameのケース(BVT_003)は、
    実際のユースケースに基づいて適切な行数を使用しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.excel_mapping = ExcelMapping()
        self.excel_mapping.column_mapping = {'old_col1': 'new_col1', 'old_col2': 'new_col2'}

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_column_map_C0_all_columns_exist(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 全ての列が存在する場合のcolumn_map
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2], 'old_col2': [3, 4]})
        result = self.excel_mapping.column_map(_df)

        assert list(result.columns) == ['new_col1', 'new_col2']
        log_msg(f"Resulting columns: {result.columns.tolist()}", LogLevel.DEBUG)

    def test_column_map_C0_missing_columns(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 必要な列が欠落している場合のcolumn_map
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2]})
        with pytest.raises(InvalidDataError) as exc_info:
            self.excel_mapping.column_map(_df)

        assert str(exc_info.value) == "Excel file does not contain all required columns"
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_column_map_C1_all_columns_exist(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 全ての列が存在する場合の分岐
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2], 'old_col2': [3, 4]})
        result = self.excel_mapping.column_map(_df)

        assert list(result.columns) == ['new_col1', 'new_col2']
        log_msg(f"Resulting columns: {result.columns.tolist()}", LogLevel.DEBUG)

    def test_column_map_C1_missing_columns(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 必要な列が欠落している場合の分岐
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2]})
        with pytest.raises(InvalidDataError) as exc_info:
            self.excel_mapping.column_map(_df)

        assert str(exc_info.value) == "Excel file does not contain all required columns"
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_column_map_C2_only_required_columns(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 必要な列のみが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2], 'old_col2': [3, 4]})
        result = self.excel_mapping.column_map(_df)

        assert list(result.columns) == ['new_col1', 'new_col2']
        log_msg(f"Resulting columns: {result.columns.tolist()}", LogLevel.DEBUG)

    def test_column_map_C2_extra_columns(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 必要な列と追加の列が存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2], 'old_col2': [3, 4], 'extra_col': [5, 6]})
        result = self.excel_mapping.column_map(_df)

        assert list(result.columns) == ['new_col1', 'new_col2', 'extra_col']
        log_msg(f"Resulting columns: {result.columns.tolist()}", LogLevel.DEBUG)

    def test_column_map_C2_partial_missing_columns(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 一部の必要な列が欠落している場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1, 2], 'extra_col': [5, 6]})
        with pytest.raises(InvalidDataError) as exc_info:
            self.excel_mapping.column_map(_df)

        assert str(exc_info.value) == "Excel file does not contain all required columns"
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_column_map_BVT_one_row(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 1行のDataFrameでのcolumn_map
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': [1], 'old_col2': [2]})
        result = self.excel_mapping.column_map(_df)

        assert list(result.columns) == ['new_col1', 'new_col2']
        assert len(result) == 1
        log_msg(f"Resulting DataFrame: {result.to_dict()}", LogLevel.DEBUG)

    def test_column_map_BVT_many_rows(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 大量の行を持つDataFrameでのcolumn_map
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'old_col1': range(10000), 'old_col2': range(10000)})
        result = self.excel_mapping.column_map(_df)

        assert list(result.columns) == ['new_col1', 'new_col2']
        assert len(result) == 10000
        log_msg(f"Resulting DataFrame shape: {result.shape}", LogLevel.DEBUG)

    def test_column_map_C0_empty_dataframe(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 空のDataFrameでのcolumn_map
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame()
        with pytest.raises(InvalidDataError) as exc_info:
            self.excel_mapping.column_map(_df)

        assert str(exc_info.value) == "Excel file does not contain all required columns"
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

class TestExcelMappingMapToUnifiedLayout:
    """ExcelMappingのmap_to_unified_layoutメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        └── 異常系: NotImplementedErrorが発生する

    C1のディシジョンテーブル:
    | 条件           | ケース1 |
    |----------------|---------|
    | メソッド呼び出し | Y       |
    | 出力           | 例外発生 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | df             | 空のDataFrame | NotImplementedError | 最小の入力での例外発生を確認 | 実装済み (test_map_to_unified_layout_C0_not_implemented) |

    注記:
    このメソッドは基底クラスで実装されておらず、サブクラスで実装されることを期待しています。
    そのため、テストケースは例外発生の確認のみとなっています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_map_to_unified_layout_C0_not_implemented(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: map_to_unified_layoutメソッドがNotImplementedErrorを発生させる
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        excel_mapping = ExcelMapping()
        _df = pd.DataFrame()

        with pytest.raises(NotImplementedError) as exc_info:
            excel_mapping.map_to_unified_layout(_df)

        assert str(exc_info.value) == "Subclasses must implement map_to_unified_layout method"
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)


class TestJinjiExcelMappingInit:
    """JinjiExcelMappingの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: デフォルト設定でインスタンス生成
    │   └── 正常系: カスタム設定でインスタンス生成
    └── C1: 分岐カバレッジ
        ├── 正常系: confがNoneの場合
        └── 正常系: confが指定されている場合

    C1のディシジョンテーブル:
    | 条件           | ケース1 | ケース2 |
    |----------------|---------|---------|
    | confがNone     | Y       | N       |
    | 出力           | デフォルトconfig使用 | 指定されたconfig使用 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | conf           | None     | デフォルトconfigが使用される | Noneが正しく処理されることを確認 | 実装済み (test_init_C0_default_configuration) |
    | BVT_002  | conf           | 最小限の設定 | 最小限の設定が正しく処理される | 最小の有効な入力を確認 | 実装済み (test_init_C1_with_minimal_conf) |
    | BVT_003  | conf           | 完全な設定 | 完全な設定が正しく処理される | 全ての設定が正しく処理されることを確認 | 実装済み (test_init_C0_full_configuration) |

    注記:
    全てのケースが実装されています。完全な設定のケース(BVT_003)は、実際のユースケースに
    基づいて適切な設定を使用しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_default_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: デフォルト設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '有効日付': 'effective_date',
            '種類': 'application_type',
            '対象': 'target_org',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '部店名称(英語)': 'branch_name_en',
            '課/エリアコード': 'section_area_code',
            '課/エリア名称': 'section_area_name',
            '課/エリア名称(英語)': 'section_area_name_en',
            '常駐部店コード': 'resident_branch_code',
            '常駐部店名称': 'resident_branch_name',
            '純新規店の組織情報受渡し予定日(開店日基準)': 'new_org_info_transfer_date',
            '共通認証受渡し予定日(人事データ反映基準)': 'aaa_transfer_date',
            '備考': 'remarks',
            '部店ｶﾅ': 'organization_name_kana',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_jinji': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            jinji_mapping = JinjiExcelMapping()

            assert jinji_mapping.config.package_config['excel_definition_mapping_jinji'] == expected_mapping
            assert callable(jinji_mapping.log_msg)
            assert jinji_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {jinji_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C0_full_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 完全な設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '有効日付': 'effective_date',
            '種類': 'application_type',
            '対象': 'target_org',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '部店名称(英語)': 'branch_name_en',
            '課/エリアコード': 'section_area_code',
            '課/エリア名称': 'section_area_name',
            '課/エリア名称(英語)': 'section_area_name_en',
            '常駐部店コード': 'resident_branch_code',
            '常駐部店名称': 'resident_branch_name',
            '純新規店の組織情報受渡し予定日(開店日基準)': 'new_org_info_transfer_date',
            '共通認証受渡し予定日(人事データ反映基準)': 'aaa_transfer_date',
            '備考': 'remarks',
            '部店ｶﾅ': 'organization_name_kana',
        }

        custom_config = MagicMock()
        custom_config.package_config = {
            'excel_definition_mapping_jinji': expected_mapping,
            'layout': {
                'unified_layout': [
                    'ulid',
                    'form_type',
                    'application_type',
                    'target_org',
                    'business_unit_code',
                    'parent_branch_code',
                    'branch_code',
                    'branch_name',
                    'section_gr_code',
                    'section_gr_name',
                    'organization_name_kana',
                    'resident_branch_code',
                    'resident_branch_name',
                    'aaa_transfer_date',
                    'internal_sales_dept_code',
                    'internal_sales_dept_name',
                    'business_and_area_code',
                    'area_name',
                    'remarks',
                    'section_name_en',
                    'section_name_kana',
                    'section_name_abbr',
                    'bpr_target_flag',
                ],
            },
        }

        jinji_mapping = JinjiExcelMapping(custom_config)

        assert jinji_mapping.config.package_config['excel_definition_mapping_jinji'] == expected_mapping
        assert callable(jinji_mapping.log_msg)
        assert jinji_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {jinji_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_none_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: confがNoneの場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '有効日付': 'effective_date',
            '種類': 'application_type',
            '対象': 'target_org',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '部店名称(英語)': 'branch_name_en',
            '課/エリアコード': 'section_area_code',
            '課/エリア名称': 'section_area_name',
            '課/エリア名称(英語)': 'section_area_name_en',
            '常駐部店コード': 'resident_branch_code',
            '常駐部店名称': 'resident_branch_name',
            '純新規店の組織情報受渡し予定日(開店日基準)': 'new_org_info_transfer_date',
            '共通認証受渡し予定日(人事データ反映基準)': 'aaa_transfer_date',
            '備考': 'remarks',
            '部店ｶﾅ': 'organization_name_kana',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_jinji': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            jinji_mapping = JinjiExcelMapping(None)

            assert jinji_mapping.config.package_config['excel_definition_mapping_jinji'] == expected_mapping
            assert callable(jinji_mapping.log_msg)
            assert jinji_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {jinji_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_minimal_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 最小限の設定が指定されている場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_mapping = {'key1': 'value1'}
        minimal_config = MagicMock()
        minimal_config.package_config = {
            'excel_definition_mapping_jinji': minimal_mapping,
            'layout': {'unified_layout': []},
        }

        jinji_mapping = JinjiExcelMapping(minimal_config)

        assert jinji_mapping.config.package_config['excel_definition_mapping_jinji'] == minimal_mapping
        assert callable(jinji_mapping.log_msg)
        assert jinji_mapping.column_mapping == minimal_mapping

        log_msg(f"column_mapping: {jinji_mapping.column_mapping}", LogLevel.DEBUG)

class TestJinjiExcelMapping:
    """JinjiExcelMappingのテスト

    テスト構造:
    └── map_to_unified_layoutのテスト
        ├── C0: 基本機能テスト
        │   ├── 正常系: 全ての列が存在する場合
        │   └── 異常系: 必要な列が欠落している場合
        ├── C1: 分岐カバレッジ
        │   ├── 正常系: target_orgが'課'の場合
        │   ├── 正常系: target_orgが'エリア'の場合
        │   └── 正常系: target_orgがその他の場合
        └── C2: 条件網羅
            ├── 正常系: target_orgが'課'で、section_area_codeとsection_area_nameが存在する場合
            ├── 正常系: target_orgが'エリア'で、section_area_codeとsection_area_nameが存在する場合
            └── 正常系: target_orgがその他で、section_area_codeとsection_area_nameが存在する場合
    """

    @pytest.fixture()
    def jinji_mapping(self):
        return JinjiExcelMapping()

    def create_base_dataframe(self):
        return pd.DataFrame({
            'application_type': ['新規'],
            'target_org': ['課'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['P001'],
            'branch_code': ['1001'],
            'branch_name': ['テスト支店'],
            'section_area_code': ['S001'],
            'section_area_name': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'resident_branch_code': ['R001'],
            'resident_branch_name': ['常駐支店'],
            'aaa_transfer_date': ['2023-01-01'],
            'remarks': ['備考'],
            'organization_name_kana': ['テストシテン'],
        })

    def test_map_to_unified_layout_C0_all_columns_exist(self, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 全ての列が存在する場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()

        with patch('ulid.new', return_value='dummy_ulid'):
            result = jinji_mapping.map_to_unified_layout(_df)

        expected_layout = [
            'ulid',
            'form_type',
            'application_type',
            'target_org',
            'business_unit_code',
            'parent_branch_code',
            'branch_code',
            'branch_name',
            'section_gr_code',
            'section_gr_name',
            'organization_name_kana',
            'resident_branch_code',
            'resident_branch_name',
            'aaa_transfer_date',
            'internal_sales_dept_code',
            'internal_sales_dept_name',
            'business_and_area_code',
            'area_name',
            'remarks',
            'section_name_en',
            'section_name_kana',
            'section_name_abbr',
            'bpr_target_flag',
        ]

        assert list(result.columns) == expected_layout
        assert result['ulid'].iloc[0] == 'dummy_ulid'
        assert result['form_type'].iloc[0] == '1'
        assert result['branch_name'].iloc[0] == 'テスト支店'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['business_and_area_code'].iloc[0] == ''
        assert result['area_name'].iloc[0] == ''

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C0_missing_columns(self, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 必要な列が欠落している場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'target_org': ['課'],
            'section_area_code': ['S001'],
            'section_area_name': ['テスト課'],
        })

        with pytest.raises(ExcelMappingError) as exc_info:
            jinji_mapping.map_to_unified_layout(_df)

        assert "Error occurred while mapping to unified layout" in str(exc_info.value)
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_target_org_ka(self, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: target_orgが'課'の場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df['target_org'] = ['課']

        result = jinji_mapping.map_to_unified_layout(_df)

        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['business_and_area_code'].iloc[0] == ''
        assert result['area_name'].iloc[0] == ''

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_target_org_area(self, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: target_orgが'エリア'の場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df['target_org'] = ['エリア']

        result = jinji_mapping.map_to_unified_layout(_df)

        assert result['section_gr_code'].iloc[0] == ''
        assert result['section_gr_name'].iloc[0] == ''
        assert result['business_and_area_code'].iloc[0] == 'S001'
        assert result['area_name'].iloc[0] == 'テスト課'

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_target_org_other(self, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: target_orgがその他の場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df['target_org'] = ['部']

        result = jinji_mapping.map_to_unified_layout(_df)

        assert result['section_gr_code'].iloc[0] == ''
        assert result['section_gr_name'].iloc[0] == ''
        assert result['business_and_area_code'].iloc[0] == ''
        assert result['area_name'].iloc[0] == ''

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C2_multiple_rows(self, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 複数の行と異なるtarget_orgの組み合わせでのmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df = pd.concat([_df, _df, _df], ignore_index=True)
        _df['target_org'] = ['課', 'エリア', '部']

        result = jinji_mapping.map_to_unified_layout(_df)

        assert result['section_gr_code'].tolist() == ['S001', '', '']
        assert result['section_gr_name'].tolist() == ['テスト課', '', '']
        assert result['business_and_area_code'].tolist() == ['', 'S001', '']
        assert result['area_name'].tolist() == ['', 'テスト課', '']

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

class TestKokukiExcelMappingInit:
    """KokukiExcelMappingの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: デフォルト設定でインスタンス生成
    │   └── 正常系: カスタム設定でインスタンス生成
    └── C1: 分岐カバレッジ
        ├── 正常系: confがNoneの場合
        └── 正常系: confが指定されている場合

    C1のディシジョンテーブル:
    | 条件           | ケース1 | ケース2 |
    |----------------|---------|---------|
    | confがNone     | Y       | N       |
    | 出力           | デフォルトconfig使用 | 指定されたconfig使用 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | conf           | None     | デフォルトconfigが使用される | Noneが正しく処理されることを確認 | 実装済み (test_init_C0_default_configuration) |
    | BVT_002  | conf           | 最小限の設定 | 最小限の設定が正しく処理される | 最小の有効な入力を確認 | 実装済み (test_init_C1_with_minimal_conf) |
    | BVT_003  | conf           | 完全な設定 | 完全な設定が正しく処理される | 全ての設定が正しく処理されることを確認 | 実装済み (test_init_C0_full_configuration) |

    注記:
    全てのケースが実装されています。完全な設定のケース(BVT_003)は、実際のユースケースに
    基づいて適切な設定を使用しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_default_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: デフォルト設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '登録予定日(yyyy/mm/dd)': 'effective_date',
            '種類(新規変更廃止)': 'application_type',
            '対象(課・エリア/中間階層)': 'target_org',
            '部店店番': 'branch_code',
            '部店名称 日本語': 'branch_name_ja',
            '部店名称 英語': 'branch_name_en',
            '中間階層コード': 'intermediate_level_code',
            '中間階層名称:日本語': 'intermediate_level_name_ja',
            '中間階層名称:英語': 'intermediate_level_name_en',
            '中間階層略称:日本語': 'intermediate_level_abbr_ja',
            '中間階層略称:英語': 'intermediate_level_abbr_en',
            '課・エリアコード': 'section_area_code',
            '課・エリア名称:日本語': 'section_area_name_ja',
            '課・エリア名称:英語': 'section_area_name_en',
            '課・エリア略称:日本語': 'section_area_abbr_ja',
            '課・エリア略称:英語': 'section_area_abbr_en',
            '共通認証受渡予定日': 'aaa_transfer_date',
            '変更種別・詳細旧名称・略語': 'change_details',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_kokuki': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            kokuki_mapping = KokukiExcelMapping()

            assert kokuki_mapping.config.package_config['excel_definition_mapping_kokuki'] == expected_mapping
            assert callable(kokuki_mapping.log_msg)
            assert kokuki_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kokuki_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C0_full_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 完全な設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '登録予定日(yyyy/mm/dd)': 'effective_date',
            '種類(新規変更廃止)': 'application_type',
            '対象(課・エリア/中間階層)': 'target_org',
            '部店店番': 'branch_code',
            '部店名称 日本語': 'branch_name_ja',
            '部店名称 英語': 'branch_name_en',
            '中間階層コード': 'intermediate_level_code',
            '中間階層名称:日本語': 'intermediate_level_name_ja',
            '中間階層名称:英語': 'intermediate_level_name_en',
            '中間階層略称:日本語': 'intermediate_level_abbr_ja',
            '中間階層略称:英語': 'intermediate_level_abbr_en',
            '課・エリアコード': 'section_area_code',
            '課・エリア名称:日本語': 'section_area_name_ja',
            '課・エリア名称:英語': 'section_area_name_en',
            '課・エリア略称:日本語': 'section_area_abbr_ja',
            '課・エリア略称:英語': 'section_area_abbr_en',
            '共通認証受渡予定日': 'aaa_transfer_date',
            '変更種別・詳細旧名称・略語': 'change_details',
        }

        custom_config = MagicMock()
        custom_config.package_config = {
            'excel_definition_mapping_kokuki': expected_mapping,
            'layout': {
                'unified_layout': [
                    'ulid',
                    'form_type',
                    'application_type',
                    'target_org',
                    'business_unit_code',
                    'parent_branch_code',
                    'branch_code',
                    'branch_name',
                    'section_gr_code',
                    'section_gr_name',
                    'organization_name_kana',
                    'resident_branch_code',
                    'resident_branch_name',
                    'aaa_transfer_date',
                    'internal_sales_dept_code',
                    'internal_sales_dept_name',
                    'business_and_area_code',
                    'area_name',
                    'remarks',
                    'section_name_en',
                    'section_name_kana',
                    'section_name_abbr',
                    'bpr_target_flag',
                ],
            },
        }

        kokuki_mapping = KokukiExcelMapping(custom_config)

        assert kokuki_mapping.config.package_config['excel_definition_mapping_kokuki'] == expected_mapping
        assert callable(kokuki_mapping.log_msg)
        assert kokuki_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kokuki_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_none_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: confがNoneの場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '登録予定日(yyyy/mm/dd)': 'effective_date',
            '種類(新規変更廃止)': 'application_type',
            '対象(課・エリア/中間階層)': 'target_org',
            '部店店番': 'branch_code',
            '部店名称 日本語': 'branch_name_ja',
            '部店名称 英語': 'branch_name_en',
            '中間階層コード': 'intermediate_level_code',
            '中間階層名称:日本語': 'intermediate_level_name_ja',
            '中間階層名称:英語': 'intermediate_level_name_en',
            '中間階層略称:日本語': 'intermediate_level_abbr_ja',
            '中間階層略称:英語': 'intermediate_level_abbr_en',
            '課・エリアコード': 'section_area_code',
            '課・エリア名称:日本語': 'section_area_name_ja',
            '課・エリア名称:英語': 'section_area_name_en',
            '課・エリア略称:日本語': 'section_area_abbr_ja',
            '課・エリア略称:英語': 'section_area_abbr_en',
            '共通認証受渡予定日': 'aaa_transfer_date',
            '変更種別・詳細旧名称・略語': 'change_details',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_kokuki': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            kokuki_mapping = KokukiExcelMapping(None)

            assert kokuki_mapping.config.package_config['excel_definition_mapping_kokuki'] == expected_mapping
            assert callable(kokuki_mapping.log_msg)
            assert kokuki_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kokuki_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_minimal_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 最小限の設定が指定されている場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_mapping = {'key1': 'value1'}
        minimal_config = MagicMock()
        minimal_config.package_config = {
            'excel_definition_mapping_kokuki': minimal_mapping,
            'layout': {'unified_layout': []},
        }

        kokuki_mapping = KokukiExcelMapping(minimal_config)

        assert kokuki_mapping.config.package_config['excel_definition_mapping_kokuki'] == minimal_mapping
        assert callable(kokuki_mapping.log_msg)
        assert kokuki_mapping.column_mapping == minimal_mapping

        log_msg(f"column_mapping: {kokuki_mapping.column_mapping}", LogLevel.DEBUG)

class TestKokukiExcelMapping:
    """KokukiExcelMappingのテスト

    テスト構造:
    └── map_to_unified_layoutのテスト
        ├── C0: 基本機能テスト
        │   ├── 正常系: 全ての列が存在する場合
        │   └── 異常系: 必要な列が欠落している場合
        ├── C1: 分岐カバレッジ
        │   ├── 正常系: target_orgが'課・エリア'の場合
        │   ├── 正常系: target_orgが'中間階層'の場合
        │   └── 正常系: target_orgがその他の場合
        └── C2: 条件網羅
            └── 正常系: 複数の行と異なるtarget_orgの組み合わせ
    """

    @pytest.fixture()
    def kokuki_mapping(self):
        return KokukiExcelMapping()

    def create_base_dataframe(self):
        return pd.DataFrame({
            'application_type': ['新規'],
            'target_org': ['課・エリア'],
            'branch_code': ['1001'],
            'branch_name_ja': ['テスト支店'],
            'branch_name_en': ['Test Branch'],
            'intermediate_level_code': ['I001'],
            'intermediate_level_name_ja': ['中間テスト'],
            'intermediate_level_name_en': ['Intermediate Test'],
            'section_area_code': ['S001'],
            'section_area_name_ja': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'aaa_transfer_date': ['2023-01-01'],
            'change_details': ['詳細変更'],
        })

    def test_map_to_unified_layout_C0_all_columns_exist(self, kokuki_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 全ての列が存在する場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()

        with patch('ulid.new', return_value='dummy_ulid'):
            result = kokuki_mapping.map_to_unified_layout(_df)

        expected_layout = [
            'ulid',
            'form_type',
            'application_type',
            'target_org',
            'business_unit_code',
            'parent_branch_code',
            'branch_code',
            'branch_name',
            'section_gr_code',
            'section_gr_name',
            'organization_name_kana',
            'resident_branch_code',
            'resident_branch_name',
            'aaa_transfer_date',
            'internal_sales_dept_code',
            'internal_sales_dept_name',
            'business_and_area_code',
            'area_name',
            'remarks',
            'section_name_en',
            'section_name_kana',
            'section_name_abbr',
            'bpr_target_flag',
        ]

        assert list(result.columns) == expected_layout
        assert result['ulid'].iloc[0] == 'dummy_ulid'
        assert result['form_type'].iloc[0] == '2'
        assert result['application_type'].iloc[0] == '新規'
        assert result['target_org'].iloc[0] == '課・エリア'
        assert result['branch_code'].iloc[0] == '1001'
        #assert result['branch_name'].iloc[0] == 'テスト支店'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'
        assert result['aaa_transfer_date'].iloc[0] == '2023-01-01'

        # マッピングされていないカラムがNaNまたは空文字列であることを確認
        for col in ['business_unit_code', 'parent_branch_code', 'resident_branch_code',
                    'resident_branch_name', 'internal_sales_dept_code',
                    'internal_sales_dept_name', 'business_and_area_code', 'area_name',
                    'remarks', 'section_name_kana', 'section_name_abbr',
                    'bpr_target_flag', 'organization_name_kana']:
            assert pd.isna(result[col].iloc[0]) or result[col].iloc[0] == ''

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C0_missing_columns(self, kokuki_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 必要な列が欠落している場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'target_org': ['課・エリア'],
            'section_area_code': ['S001'],
            'section_area_name_ja': ['テスト課'],
        })

        with pytest.raises(ExcelMappingError) as exc_info:
            kokuki_mapping.map_to_unified_layout(_df)

        assert "Error occurred while mapping to unified layout" in str(exc_info.value)
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_target_org_ka_area(self, kokuki_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: target_orgが'課・エリア'の場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df['target_org'] = ['課・エリア']

        result = kokuki_mapping.map_to_unified_layout(_df)

        assert result['target_org'].iloc[0] == '課・エリア'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_target_org_intermediate(self, kokuki_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: target_orgが'中間階層'の場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df['target_org'] = ['中間階層']

        result = kokuki_mapping.map_to_unified_layout(_df)

        assert result['target_org'].iloc[0] == '中間階層'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_target_org_other(self, kokuki_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: target_orgがその他の場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df['target_org'] = ['その他']

        result = kokuki_mapping.map_to_unified_layout(_df)

        assert result['target_org'].iloc[0] == 'その他'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C2_multiple_rows(self, kokuki_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 複数の行と異なるtarget_orgの組み合わせでのmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df = pd.concat([_df, _df, _df], ignore_index=True)
        _df['target_org'] = ['課・エリア', '中間階層', 'その他']

        result = kokuki_mapping.map_to_unified_layout(_df)

        assert result['target_org'].tolist() == ['課・エリア', '中間階層', 'その他']
        assert result['section_gr_code'].tolist() == ['S001', 'S001', 'S001']
        assert result['section_gr_name'].tolist() == ['テスト課', 'テスト課', 'テスト課']
        assert result['section_name_en'].tolist() == ['Test Section', 'Test Section', 'Test Section']

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

class TestKanrenExcelMappingWithDummyInit:
    """KanrenExcelMappingWithDummyの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: デフォルト設定でインスタンス生成
    │   └── 正常系: カスタム設定でインスタンス生成
    └── C1: 分岐カバレッジ
        ├── 正常系: confがNoneの場合
        └── 正常系: confが指定されている場合

    C1のディシジョンテーブル:
    | 条件           | ケース1 | ケース2 |
    |----------------|---------|---------|
    | confがNone     | Y       | N       |
    | 出力           | デフォルトconfig使用 | 指定されたconfig使用 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | conf           | None     | デフォルトconfigが使用される | Noneが正しく処理されることを確認 | 実装済み (test_init_C0_default_configuration) |
    | BVT_002  | conf           | 最小限の設定 | 最小限の設定が正しく処理される | 最小の有効な入力を確認 | 実装済み (test_init_C1_with_minimal_conf) |
    | BVT_003  | conf           | 完全な設定 | 完全な設定が正しく処理される | 全ての設定が正しく処理されることを確認 | 実装済み (test_init_C0_full_configuration) |

    注記:
    全てのケースが実装されています。完全な設定のケース(BVT_003)は、実際のユースケースに
    基づいて適切な設定を使用しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_default_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: デフォルト設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '種類': 'application_type',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '課Grコード': 'section_gr_code',
            '課Gr名称': 'section_gr_name',
            '課名称(英語)': 'section_name_en',
            '共通認証受渡し予定日': 'aaa_transfer_date',
            '課名称(カナ)': 'section_name_kana',
            '課名称(略称)': 'section_name_abbr',
            'BPR対象/対象外フラグ': 'bpr_target_flag',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_kanren': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            kanren_mapping = KanrenExcelMappingWithDummy()

            assert kanren_mapping.config.package_config['excel_definition_mapping_kanren'] == expected_mapping
            assert callable(kanren_mapping.log_msg)
            assert kanren_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kanren_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C0_full_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 完全な設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '種類': 'application_type',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '課Grコード': 'section_gr_code',
            '課Gr名称': 'section_gr_name',
            '課名称(英語)': 'section_name_en',
            '共通認証受渡し予定日': 'aaa_transfer_date',
            '課名称(カナ)': 'section_name_kana',
            '課名称(略称)': 'section_name_abbr',
            'BPR対象/対象外フラグ': 'bpr_target_flag',
        }

        custom_config = MagicMock()
        custom_config.package_config = {
            'excel_definition_mapping_kanren': expected_mapping,
            'layout': {
                'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                ],
            },
        }

        kanren_mapping = KanrenExcelMappingWithDummy(custom_config)

        assert kanren_mapping.config.package_config['excel_definition_mapping_kanren'] == expected_mapping
        assert callable(kanren_mapping.log_msg)
        assert kanren_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kanren_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_none_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: confがNoneの場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '種類': 'application_type',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '課Grコード': 'section_gr_code',
            '課Gr名称': 'section_gr_name',
            '課名称(英語)': 'section_name_en',
            '共通認証受渡し予定日': 'aaa_transfer_date',
            '課名称(カナ)': 'section_name_kana',
            '課名称(略称)': 'section_name_abbr',
            'BPR対象/対象外フラグ': 'bpr_target_flag',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_kanren': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            kanren_mapping = KanrenExcelMappingWithDummy(None)

            assert kanren_mapping.config.package_config['excel_definition_mapping_kanren'] == expected_mapping
            assert callable(kanren_mapping.log_msg)
            assert kanren_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kanren_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_minimal_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 最小限の設定が指定されている場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_mapping = {'key1': 'value1'}
        minimal_config = MagicMock()
        minimal_config.package_config = {
            'excel_definition_mapping_kanren': minimal_mapping,
            'layout': {'unified_layout': []},
        }

        kanren_mapping = KanrenExcelMappingWithDummy(minimal_config)

        assert kanren_mapping.config.package_config['excel_definition_mapping_kanren'] == minimal_mapping
        assert callable(kanren_mapping.log_msg)
        assert kanren_mapping.column_mapping == minimal_mapping

        log_msg(f"column_mapping: {kanren_mapping.column_mapping}", LogLevel.DEBUG)

class TestKanrenExcelMappingWithDummy:
    """KanrenExcelMappingWithDummyのテスト

    テスト構造:
    └── map_to_unified_layoutのテスト
        ├── C0: 基本機能テスト
        │   ├── 正常系: 全ての列が存在する場合
        │   └── 異常系: 必要な列が欠落している場合
        ├── C1: 分岐カバレッジ
        │   └── 正常系: 基本的なマッピング
        └── C2: 条件網羅
            └── 正常系: 複数の行のマッピング
    """

    @pytest.fixture()
    def kanren_mapping(self):
        return KanrenExcelMappingWithDummy()

    def create_base_dataframe(self):
        return pd.DataFrame({
            'application_type': ['新規'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['P001'],
            'branch_code': ['1001'],
            'branch_name': ['テスト支店'],
            'section_gr_code': ['S001'],
            'section_gr_name': ['テスト課'],
            'section_name_en': ['Test Section'],
            'aaa_transfer_date': ['2023-01-01'],
            'section_name_kana': ['テストカ'],
            'section_name_abbr': ['テスト'],
            'bpr_target_flag': ['1'],
        })

    def test_map_to_unified_layout_C0_all_columns_exist(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 全ての列が存在する場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()

        with patch('ulid.new', return_value='dummy_ulid'):
            result = kanren_mapping.map_to_unified_layout(_df)

        expected_layout = [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
        ]

        assert list(result.columns) == expected_layout
        assert result['ulid'].iloc[0] == 'dummy_ulid'
        assert result['form_type'].iloc[0] == '3'
        assert result['application_type'].iloc[0] == '新規'
        assert result['business_unit_code'].iloc[0] == '001'
        assert result['parent_branch_code'].iloc[0] == 'P001'
        assert result['branch_code'].iloc[0] == '1001'
        assert result['branch_name'].iloc[0] == 'テスト支店'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'
        assert result['aaa_transfer_date'].iloc[0] == '2023-01-01'
        assert result['section_name_kana'].iloc[0] == 'テストカ'
        assert result['section_name_abbr'].iloc[0] == 'テスト'
        assert result['bpr_target_flag'].iloc[0] == '1'

        # マッピングされていないカラムがNaNまたは空文字列であることを確認
        for col in ['target_org', 'resident_branch_code', 'resident_branch_name',
                    'internal_sales_dept_code', 'internal_sales_dept_name',
                    'business_and_area_code', 'area_name', 'remarks', 'organization_name_kana']:
            assert pd.isna(result[col].iloc[0]) or result[col].iloc[0] == ''

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C0_missing_columns(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 必要な列が欠落している場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['新規'],
            'branch_code': ['1001'],
            'branch_name': ['テスト支店'],
        })

        with pytest.raises(ExcelMappingError) as exc_info:
            kanren_mapping.map_to_unified_layout(_df)

        assert "Error occurred while mapping to unified layout" in str(exc_info.value)
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C1_basic_mapping(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 基本的なマッピングのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()

        result = kanren_mapping.map_to_unified_layout(_df)

        assert result['form_type'].iloc[0] == '3'
        assert result['application_type'].iloc[0] == '新規'
        assert result['business_unit_code'].iloc[0] == '001'
        assert result['parent_branch_code'].iloc[0] == 'P001'
        assert result['branch_code'].iloc[0] == '1001'
        assert result['branch_name'].iloc[0] == 'テスト支店'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'
        assert result['aaa_transfer_date'].iloc[0] == '2023-01-01'
        assert result['section_name_kana'].iloc[0] == 'テストカ'
        assert result['section_name_abbr'].iloc[0] == 'テスト'
        assert result['bpr_target_flag'].iloc[0] == '1'

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C2_multiple_rows(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 複数の行のマッピングテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = self.create_base_dataframe()
        _df = pd.concat([_df, _df.assign(branch_code='1002', branch_name='テスト支店2')], ignore_index=True)

        result = kanren_mapping.map_to_unified_layout(_df)

        assert len(result) == 2
        assert result['branch_code'].tolist() == ['1001', '1002']
        assert result['branch_name'].tolist() == ['テスト支店', 'テスト支店2']
        assert all(result['form_type'] == '3')

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

class TestKanrenExcelMappingWithoutDummy:
    """KanrenExcelMappingWithoutDummyのテスト

    テスト構造:
    ├── __init__のテスト
    │   ├── C0: 基本機能テスト
    │   │   ├── 正常系: デフォルト設定でインスタンス生成
    │   │   └── 正常系: カスタム設定でインスタンス生成
    │   └── C1: 分岐カバレッジ
    │       ├── 正常系: confがNoneの場合
    │       └── 正常系: confが指定されている場合
    └── map_to_unified_layoutのテスト
        ├── C0: 基本機能テスト
        │   ├── 正常系: 全ての列が存在する場合
        │   └── 異常系: 必要な列が欠落している場合
        ├── C1: 分岐カバレッジ
        │   └── 正常系: 基本的なマッピング
        └── C2: 条件網羅
            └── 正常系: 複数の行のマッピング

    C1のディシジョンテーブル (init):
    | 条件           | ケース1 | ケース2 |
    |----------------|---------|---------|
    | confがNone     | Y       | N       |
    | 出力           | デフォルトconfig使用 | 指定されたconfig使用 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|---------------------------|----------|
    | BVT_001  | conf           | None     | デフォルトconfigが使用される | Noneが正しく処理されることを確認 | 実装済み (test_init_C0_default_configuration) |
    | BVT_002  | conf           | 最小限の設定 | 最小限の設定が正しく処理される | 最小の有効な入力を確認 | 実装済み (test_init_C1_with_minimal_conf) |
    | BVT_003  | conf           | 完全な設定 | 完全な設定が正しく処理される | 全ての設定が正しく処理されることを確認 | 実装済み (test_init_C0_full_configuration) |

    注記:
    KanrenExcelMappingWithoutDummyはJinjiExcelMappingと同じ動作をするため、テストケースも類似しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def kanren_mapping(self):
        return KanrenExcelMappingWithoutDummy()

    @pytest.fixture()
    def jinji_mapping(self):
        return JinjiExcelMapping()

    def test_init_C0_default_configuration(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: デフォルト設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        expected_mapping = {
            '報告日': 'report_date',
            'no': 'application_number',
            '有効日付': 'effective_date',
            '種類': 'application_type',
            '対象': 'target_org',
            '部門コード': 'business_unit_code',
            '親部店コード': 'parent_branch_code',
            '部店コード': 'branch_code',
            '部店名称': 'branch_name',
            '部店名称(英語)': 'branch_name_en',
            '課/エリアコード': 'section_area_code',
            '課/エリア名称': 'section_area_name',
            '課/エリア名称(英語)': 'section_area_name_en',
            '常駐部店コード': 'resident_branch_code',
            '常駐部店名称': 'resident_branch_name',
            '純新規店の組織情報受渡し予定日(開店日基準)': 'new_org_info_transfer_date',
            '共通認証受渡し予定日(人事データ反映基準)': 'aaa_transfer_date',
            '備考': 'remarks',
            '部店ｶﾅ': 'organization_name_kana',
        }

        with patch('src.packages.request_processor.excel_to_dataframe_mapper.initialize_config') as mock_init_config:
            mock_config = MagicMock()
            mock_config.package_config = {
                'excel_definition_mapping_jinji': expected_mapping,
                'layout': {
                    'unified_layout': [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
                    ],
                },
            }
            mock_init_config.return_value = mock_config

            kanren_mapping = KanrenExcelMappingWithoutDummy()

            assert kanren_mapping.config.package_config['excel_definition_mapping_jinji'] == expected_mapping
            assert callable(kanren_mapping.log_msg)
            assert kanren_mapping.column_mapping == expected_mapping

        log_msg(f"column_mapping: {kanren_mapping.column_mapping}", LogLevel.DEBUG)

    def test_init_C1_with_minimal_conf(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 最小限の設定が指定されている場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_mapping = {'key1': 'value1'}
        minimal_config = MagicMock()
        minimal_config.package_config = {
            'excel_definition_mapping_jinji': minimal_mapping,
            'layout': {'unified_layout': []},
        }

        kanren_mapping = KanrenExcelMappingWithoutDummy(minimal_config)

        assert kanren_mapping.config.package_config['excel_definition_mapping_jinji'] == minimal_mapping
        assert callable(kanren_mapping.log_msg)
        assert kanren_mapping.column_mapping == minimal_mapping

        log_msg(f"column_mapping: {kanren_mapping.column_mapping}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C0_all_columns_exist(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 全ての列が存在する場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['新規'],
            'target_org': ['課'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['P001'],
            'branch_code': ['1001'],
            'branch_name': ['テスト支店'],
            'section_area_code': ['S001'],
            'section_area_name': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'resident_branch_code': ['R001'],
            'resident_branch_name': ['常駐支店'],
            'aaa_transfer_date': ['2023-01-01'],
            'remarks': ['備考'],
            'organization_name_kana': ['テストシテン'],
        })

        with patch('ulid.new', return_value='dummy_ulid'):
            result = kanren_mapping.map_to_unified_layout(_df)

        expected_layout = [
                        'ulid',
                        'form_type',
                        'application_type',
                        'target_org',
                        'business_unit_code',
                        'parent_branch_code',
                        'branch_code',
                        'branch_name',
                        'section_gr_code',
                        'section_gr_name',
                        'organization_name_kana',
                        'resident_branch_code',
                        'resident_branch_name',
                        'aaa_transfer_date',
                        'internal_sales_dept_code',
                        'internal_sales_dept_name',
                        'business_and_area_code',
                        'area_name',
                        'remarks',
                        'section_name_en',
                        'section_name_kana',
                        'section_name_abbr',
                        'bpr_target_flag',
        ]

        assert list(result.columns) == expected_layout
        assert result['ulid'].iloc[0] == 'dummy_ulid'
        assert result['form_type'].iloc[0] == '4'
        assert result['application_type'].iloc[0] == '新規'
        assert result['target_org'].iloc[0] == '課'
        assert result['business_unit_code'].iloc[0] == '001'
        assert result['branch_name'].iloc[0] == 'テスト支店'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['business_and_area_code'].iloc[0] == ''
        assert result['area_name'].iloc[0] == ''

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C0_missing_columns(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 必要な列が欠落している場合のmap_to_unified_layout
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['新規'],
            'target_org': ['課'],
            'branch_code': ['1001'],
        })

        with pytest.raises(ExcelMappingError) as exc_info:
            kanren_mapping.map_to_unified_layout(_df)

        assert "Error occurred while mapping to unified layout" in str(exc_info.value)
        log_msg(f"Raised exception: {exc_info.value}", LogLevel.DEBUG)

    def test_map_to_unified_layout_C2_multiple_rows(self, kanren_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 複数の行のマッピングテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['新規', '変更'],
            'target_org': ['課', 'エリア'],
            'business_unit_code': ['001', '002'],
            'parent_branch_code': ['P001', 'P002'],
            'branch_code': ['1001', '1002'],
            'branch_name': ['テスト支店1', 'テスト支店2'],
            'section_area_code': ['S001', 'A001'],
            'section_area_name': ['テスト課', 'テストエリア'],
            'section_area_name_en': ['Test Section', 'Test Area'],
            'resident_branch_code': ['R001', 'R002'],
            'resident_branch_name': ['常駐支店1', '常駐支店2'],
            'aaa_transfer_date': ['2023-01-01', '2023-01-02'],
            'remarks': ['備考1', '備考2'],
            'organization_name_kana': ['テストシテン1', 'テストシテン2'],
        })

        result = kanren_mapping.map_to_unified_layout(_df)

        assert len(result) == 2
        #assert result['form_type'].tolist() == ['1', '1']
        assert result['form_type'].tolist() == ['4', '4']
        assert result['application_type'].tolist() == ['新規', '変更']
        assert result['target_org'].tolist() == ['課', 'エリア']
        assert result['section_gr_code'].tolist() == ['S001', '']
        assert result['section_gr_name'].tolist() == ['テスト課', '']
        assert result['business_and_area_code'].tolist() == ['', 'A001']
        assert result['area_name'].tolist() == ['', 'テストエリア']

        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)

    def test_mapping_equivalence(self, kanren_mapping, jinji_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: 同等性確認
        テスト内容: KanrenExcelMappingWithoutDummyとJinjiExcelMappingの同等性を確認
                    ただしform_type以外の一致を確認
                    form_type: jinji->1, ダミー課なし→4
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['新規'],
            'target_org': ['課'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['P001'],
            'branch_code': ['1001'],
            'branch_name': ['テスト支店'],
            'section_area_code': ['S001'],
            'section_area_name': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'resident_branch_code': ['R001'],  # この行を追加
            'resident_branch_name': ['常駐支店'],  # この行を追加
            'aaa_transfer_date': ['2023-01-01'],
            'remarks': ['備考'],
            'organization_name_kana': ['テストシテン'],
        })

        with patch('ulid.new', return_value='dummy_ulid'):
            result_kanren = kanren_mapping.map_to_unified_layout(_df)
            result_jinji = jinji_mapping.map_to_unified_layout(_df)

        # 結果を比較 form_type以外を比較して一致確認
        log_msg("各マッピング結果のform_type値を確認", LogLevel.DEBUG)
        log_msg(f'kanren.dtype: \n\n{result_kanren.dtypes}', LogLevel.INFO)
        log_msg(f'kanren.info: \n\n{result_kanren.info}', LogLevel.INFO)
        #log_msg(f'kanren.layout: \n\n{result_kanren}', LogLevel.INFO)
        assert result_kanren['form_type'].iloc[0] == '4', "関連マッピングのform_typeが4ではありません"
        assert result_jinji['form_type'].iloc[0] == '1', "人事マッピングのform_typeが1ではありません"

        log_msg("form_type以外のカラムの同等性を確認", LogLevel.DEBUG)
        # form_type以外の全カラムを取得
        columns_to_compare = [col for col in result_kanren.columns if col != 'form_type']

        # form_type以外のカラムについて同等性を確認
        pd.testing.assert_frame_equal(
            result_kanren[columns_to_compare],
            result_jinji[columns_to_compare],
            check_names=True,
        )


        log_msg("KanrenExcelMappingWithoutDummy and JinjiExcelMapping produce identical results", LogLevel.INFO)

    def test_map_to_unified_layout_C1_basic_mapping(self, kanren_mapping):

        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 基本的なマッピングのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['新規'],
            'target_org': ['課'],
            'business_unit_code': ['001'],
            'parent_branch_code': ['P001'],
            'branch_code': ['1001'],
            'branch_name': ['テスト支店'],
            'section_area_code': ['S001'],
            'section_area_name': ['テスト課'],
            'section_area_name_en': ['Test Section'],
            'resident_branch_code': ['R001'],
            'resident_branch_name': ['常駐支店'],
            'aaa_transfer_date': ['2023-01-01'],
            'remarks': ['備考'],
            'organization_name_kana': ['テストシテン'],
        })

        with patch('ulid.new', return_value='dummy_ulid'):
            result = kanren_mapping.map_to_unified_layout(_df)
        log_msg(f"\n\nResulting DataFrame:\n{tabulate_dataframe(result)}", LogLevel.INFO)

        assert result['ulid'].iloc[0] == 'dummy_ulid'
        assert result['form_type'].iloc[0] == '4'
        assert result['application_type'].iloc[0] == '新規'
        assert result['target_org'].iloc[0] == '課'
        assert result['business_unit_code'].iloc[0] == '001'
        assert result['parent_branch_code'].iloc[0] == 'P001'
        assert result['branch_code'].iloc[0] == '1001'
        assert result['branch_name'].iloc[0] == 'テスト支店'
        assert result['section_gr_code'].iloc[0] == 'S001'
        assert result['section_gr_name'].iloc[0] == 'テスト課'
        assert result['section_name_en'].iloc[0] == 'Test Section'
        assert result['resident_branch_code'].iloc[0] == 'R001'
        assert result['resident_branch_name'].iloc[0] == '常駐支店'
        assert result['aaa_transfer_date'].iloc[0] == '2023-01-01'
        assert result['remarks'].iloc[0] == '備考'
        assert result['organization_name_kana'].iloc[0] == 'テストシテン'

        #log_msg(f"Resulting DataFrame:\n{result}", LogLevel.DEBUG)
        log_msg(f"Resulting DataFrame:\n{result}", LogLevel.INFO)
