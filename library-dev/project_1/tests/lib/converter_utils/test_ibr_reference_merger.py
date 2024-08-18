import numpy as np
import pandas as pd
import pickle
import pytest
from unittest.mock import Mock
from pathlib import Path
from src.lib.converter_utils.ibr_reference_merger import ReferenceMerger
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)
log_msg = config.log_message

class TestReferenceMergerInit:
    """ReferenceMergerの__init__メソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        └── 正常系: 有効なTableSearcherオブジェクトでインスタンス生成
    """

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_init_C0_valid_table_searcher(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なTableSearcherオブジェクトでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # TableSearcherのモックを作成
        mock_table_searcher = Mock(spec=TableSearcher)

        # ReferenceMergerのインスタンスを生成
        merger = ReferenceMerger(mock_table_searcher)

        # table_searcherが正しく設定されていることを確認
        assert merger.table_searcher == mock_table_searcher
        log_msg("ReferenceMergerのインスタンスが正常に生成されました", LogLevel.DEBUG)

class TestReferenceMergerMergeReferenceData:
    """ReferenceMergerのmerge_reference_dataメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なDataFrameで処理
    │   └── 異常系: 空のDataFrameでValueError
    └── C1: 分岐カバレッジ
        ├── 正常系: マッチする行が存在し、'0'の行がある場合
        └── 正常系: マッチする行が存在するが、'0'の行がない場合
    """

    @pytest.fixture
    def mock_table_searcher(self):
        mock = Mock(spec=TableSearcher)
        mock.simple_search.return_value = pd.DataFrame({
            'branch_code_bpr': ['1234', '1234'],
            'section_gr_code_bpr': ['0', '1'],
            'branch_name_bpr': ['Test Branch', 'Test Branch'],
            'parent_branch_code': ['5678', '5678']
        })
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    @pytest.fixture
    def valid_dataframe(self):
        return pd.DataFrame({
            'branch_code': ['123456', '789012'],
            'other_data': ['Data1', 'Data2']
        })

    @pytest.fixture
    def empty_dataframe(self):
        return pd.DataFrame()

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_merge_reference_data_C0_valid_dataframe(self, reference_merger, valid_dataframe):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger.merge_reference_data(valid_dataframe)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(valid_dataframe)
        assert 'reference_branch_code' in result.columns
        assert 'reference_branch_name' in result.columns
        assert 'reference_parent_branch_code' in result.columns
        
        log_msg("有効なDataFrameで正常に処理されました", LogLevel.DEBUG)

    def test_merge_reference_data_C0_empty_dataframe(self, reference_merger, empty_dataframe):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 空のDataFrameでValueError
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError) as excinfo:
            reference_merger.merge_reference_data(empty_dataframe)
        
        assert "入力DataFrameが空です" in str(excinfo.value)
        log_msg("空のDataFrameで正しくValueErrorが発生しました", LogLevel.DEBUG)

    def test_merge_reference_data_C1_matching_row_with_zero(self, reference_merger, valid_dataframe):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: マッチする行が存在し、'0'の行がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger.merge_reference_data(valid_dataframe)
        
        assert result.loc[0, 'reference_branch_code'] == '1234'
        assert result.loc[0, 'reference_branch_name'] == 'Test Branch'
        assert result.loc[0, 'reference_parent_branch_code'] == '5678'
        
        log_msg("マッチする行が存在し、'0'の行がある場合の処理が正常に完了しました", LogLevel.DEBUG)

    def test_merge_reference_data_C1_matching_row_without_zero(self, reference_merger, valid_dataframe):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: マッチする行が存在するが、'0'の行がない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        reference_merger.table_searcher.simple_search.return_value = pd.DataFrame({
            'branch_code_bpr': ['1234'],
            'section_gr_code_bpr': ['1'],
            'branch_name_bpr': ['Test Branch'],
            'parent_branch_code': ['5678']
        })

        result = reference_merger.merge_reference_data(valid_dataframe)
        
        assert result.loc[0, 'reference_branch_code'] is None
        assert result.loc[0, 'reference_branch_name'] is None
        assert result.loc[0, 'reference_parent_branch_code'] is None
        
        log_msg("マッチする行が存在するが、'0'の行がない場合の処理が正常に完了しました", LogLevel.DEBUG)

class TestReferenceMergerGetReferenceInfo:
    """ReferenceMergerの_get_reference_infoメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 正常なSeriesで処理
    │   └── 異常系: 必要なカラムが欠落したSeriesで処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: マッチする行が存在し、'0'の行がある場合
    │   ├── 正常系: マッチする行が存在するが、'0'の行がない場合
    │   ├── 正常系: マッチする行が存在しない場合
    │   └── 異常系: KeyErrorが発生する場合
    └── C2: 条件網羅
        ├── 正常系: マッチする行あり、'0'の行あり、全データ正常
        ├── 正常系: マッチする行あり、'0'の行あり、一部データNaN
        ├── 正常系: マッチする行あり、'0'の行なし
        ├── 正常系: マッチする行なし
        └── 異常系: 必要なカラムが存在しない
    """

    @pytest.fixture
    def mock_table_searcher(self):
        mock = Mock(spec=TableSearcher)
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame({
            'branch_code': ['123456', '789012', '345678', '901234', '567890'],
            'other_data': ['Data1', 'Data2', 'Data3', 'Data4', 'Data5']
        })

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_get_reference_info_C0_normal_series(self, reference_merger, sample_dataframe, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 正常なSeriesで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_table_searcher.simple_search.return_value = pd.DataFrame({
            'branch_code_bpr': ['1234'],
            'section_gr_code_bpr': ['0'],
            'branch_name_bpr': ['Test Branch'],
            'parent_branch_code': ['5678']
        })

        result = reference_merger._get_reference_info(sample_dataframe.iloc[0])
        
        assert result['reference_branch_code'] == '1234'
        assert result['reference_branch_name'] == 'Test Branch'
        assert result['reference_parent_branch_code'] == '5678'
        log_msg("正常なSeriesで正しく処理されました", LogLevel.DEBUG)

    def test_get_reference_info_C0_missing_column(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 必要なカラムが欠落したSeriesで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_series = pd.Series({'invalid_column': '123456'})
        result = reference_merger._get_reference_info(invalid_series)
        
        assert result == reference_merger._get_empty_result()
        log_msg("必要なカラムが欠落したSeriesで正しく空の結果が返されました", LogLevel.DEBUG)

    def test_get_reference_info_C1_matching_row_with_zero(self, reference_merger, sample_dataframe, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: マッチする行が存在し、'0'の行がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_table_searcher.simple_search.return_value = pd.DataFrame({
            'branch_code_bpr': ['1234', '1234'],
            'section_gr_code_bpr': ['0', '1'],
            'branch_name_bpr': ['Test Branch', 'Other Branch'],
            'parent_branch_code': ['5678', '5678']
        })

        result = reference_merger._get_reference_info(sample_dataframe.iloc[0])
        
        assert result['reference_branch_code'] == '1234'
        assert result['reference_branch_name'] == 'Test Branch'
        assert result['reference_parent_branch_code'] == '5678'
        log_msg("マッチする行が存在し、'0'の行がある場合の処理が正常に完了しました", LogLevel.DEBUG)

    def test_get_reference_info_C1_matching_row_without_zero(self, reference_merger, sample_dataframe, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: マッチする行が存在するが、'0'の行がない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_table_searcher.simple_search.return_value = pd.DataFrame({
            'branch_code_bpr': ['1234'],
            'section_gr_code_bpr': ['1'],
            'branch_name_bpr': ['Test Branch'],
            'parent_branch_code': ['5678']
        })

        result = reference_merger._get_reference_info(sample_dataframe.iloc[0])
        
        assert result == reference_merger._get_empty_result()
        log_msg("マッチする行が存在するが、'0'の行がない場合の処理が正常に完了しました", LogLevel.DEBUG)

    def test_get_reference_info_C1_no_matching_row(self, reference_merger, sample_dataframe, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: マッチする行が存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_table_searcher.simple_search.return_value = pd.DataFrame()

        result = reference_merger._get_reference_info(sample_dataframe.iloc[0])
        
        assert result == reference_merger._get_empty_result()
        log_msg("マッチする行が存在しない場合の処理が正常に完了しました", LogLevel.DEBUG)

    def test_get_reference_info_C1_key_error(self, reference_merger, sample_dataframe, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: KeyErrorが発生する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_table_searcher.simple_search.return_value = pd.DataFrame({
            'invalid_column': ['1234'],
        })

        result = reference_merger._get_reference_info(sample_dataframe.iloc[0])
        
        assert result == reference_merger._get_empty_result()
        log_msg("KeyErrorが発生する場合の処理が正常に完了しました", LogLevel.DEBUG)

    def test_get_reference_info_C2_all_conditions(self, reference_merger, sample_dataframe, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 全ての条件組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # C2のテストケース
        test_cases = [
            # マッチする行あり、'0'の行あり、全データ正常
            (pd.DataFrame({
                'branch_code_bpr': ['1234', '1234'],
                'section_gr_code_bpr': ['0', '1'],
                'branch_name_bpr': ['Test Branch', 'Other Branch'],
                'parent_branch_code': ['5678', '5678']
            }), {'reference_branch_code': '1234', 'reference_branch_name': 'Test Branch', 'reference_parent_branch_code': '5678'}),
            
            # マッチする行あり、'0'の行あり、一部データNaN
            (pd.DataFrame({
                'branch_code_bpr': ['1234', '1234'],
                'section_gr_code_bpr': ['0', '1'],
                'branch_name_bpr': ['Test Branch', 'Other Branch'],
                'parent_branch_code': [pd.NA, '5678']
            }), {'reference_branch_code': '1234', 'reference_branch_name': 'Test Branch', 'reference_parent_branch_code': None}),
            
            # マッチする行あり、'0'の行なし
            (pd.DataFrame({
                'branch_code_bpr': ['1234'],
                'section_gr_code_bpr': ['1'],
                'branch_name_bpr': ['Test Branch'],
                'parent_branch_code': ['5678']
            }), {'reference_branch_code': None, 'reference_branch_name': None, 'reference_parent_branch_code': None}),
            
            # マッチする行なし
            (pd.DataFrame(), {'reference_branch_code': None, 'reference_branch_name': None, 'reference_parent_branch_code': None}),
        ]

        for i, (mock_result, expected_result) in enumerate(test_cases):
            mock_table_searcher.simple_search.return_value = mock_result
            result = reference_merger._get_reference_info(sample_dataframe.iloc[i])
            assert result == expected_result
            log_msg(f"C2テストケース {i+1} が正常に完了しました", LogLevel.DEBUG)

        log_msg("全てのC2テストケースが正常に完了しました", LogLevel.INFO)

class TestReferenceMergerGetBranchCodePrefix:
    """ReferenceMergerの_get_branch_code_prefixメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        ├── 正常系: 6桁の部店コードから上位4桁を取得
        ├── 正常系: 4桁の部店コードからそのまま4桁を取得
        └── 正常系: 4桁未満の部店コードから全桁を取得
    """

    @pytest.fixture
    def sample_dataframe(self):
        return pd.DataFrame({
            'branch_code': ['123456', '7890', '12', ''],
            'other_data': ['Data1', 'Data2', 'Data3', 'Data4']
        })

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        # テスト用のpickleファイルを作成
        dummy_data = pd.DataFrame({'dummy': [1, 2, 3]})
        pickle_path = tmp_path / "dummy_table.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump(dummy_data, f)
        
        # TableSearcherのモックを作成
        mock = Mock(spec=TableSearcher)
        mock.pickle_path = pickle_path
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    @pytest.mark.parametrize("index, expected", [
        (0, "1234"),  # 6桁の部店コード
        (1, "7890"),  # 4桁の部店コード
        (2, "12"),    # 4桁未満の部店コード
        (3, ""),      # 空の部店コード
    ])
    def test_get_branch_code_prefix_C0(self, reference_merger, sample_dataframe, index, expected):
        test_doc = f"""テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: インデックス{index}の部店コードから適切なプレフィックスを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = sample_dataframe.iloc[index]
        result = reference_merger._get_branch_code_prefix(row)
        
        assert result == expected
        log_msg(f"インデックス{index}の部店コードから正しくプレフィックス '{result}' を取得しました", LogLevel.DEBUG)

    def test_get_branch_code_prefix_C0_non_string(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 文字列以外の部店コードを処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 文字列以外の値を含むSeriesを作成
        non_string_series = pd.Series({'branch_code': 12345})
        
        result = reference_merger._get_branch_code_prefix(non_string_series)
        
        assert result == "1234"
        log_msg(f"文字列以外の部店コードから正しくプレフィックス '{result}' を取得しました", LogLevel.DEBUG)

class TestReferenceMergerSearchReferenceTable:
    """ReferenceMergerの_search_reference_tableメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        ├── 正常系: 存在する部店コードプレフィックスで検索
        ├── 正常系: 存在しない部店コードプレフィックスで検索
        └── 異常系: TableSearcherがエラーを発生させた場合
    """

    @pytest.fixture
    def sample_reference_data(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '9012'],
            'section_gr_code_bpr': ['0', '1', '0'],
            'branch_name_bpr': ['Branch A', 'Branch B', 'Branch C'],
            'parent_branch_code': ['P1234', 'P5678', 'P9012']
        })

    @pytest.fixture
    def mock_table_searcher(self, tmp_path, sample_reference_data):
        # テスト用のpickleファイルを作成
        pickle_path = tmp_path / "reference_table.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump(sample_reference_data, f)
        
        # TableSearcherのモックを作成
        mock = Mock(spec=TableSearcher)
        mock.pickle_path = pickle_path
        
        def mock_simple_search(conditions):
            if 'branch_code_bpr' in conditions:
                prefix = conditions['branch_code_bpr'].split(':')[1]
                return sample_reference_data[sample_reference_data['branch_code_bpr'].str.startswith(prefix)]
            return sample_reference_data

        mock.simple_search = Mock(side_effect=mock_simple_search)
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_search_reference_table_C0_existing_prefix(self, reference_merger, sample_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 存在する部店コードプレフィックスで検索
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger._search_reference_table('1234')
        
        assert not result.empty
        assert len(result) == 1
        assert result.iloc[0]['branch_code_bpr'] == '1234'
        assert result.iloc[0]['branch_name_bpr'] == 'Branch A'
        log_msg("存在する部店コードプレフィックスで正しく検索できました", LogLevel.DEBUG)

    def test_search_reference_table_C0_non_existing_prefix(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 存在しない部店コードプレフィックスで検索
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger._search_reference_table('0000')
        
        assert result.empty
        log_msg("存在しない部店コードプレフィックスで空のDataFrameが返されました", LogLevel.DEBUG)

    def test_search_reference_table_C0_table_searcher_error(self, reference_merger, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: TableSearcherがエラーを発生させた場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # TableSearcherのsimple_searchメソッドが例外を発生させるように設定
        mock_table_searcher.simple_search.side_effect = Exception("テスト用エラー")

        with pytest.raises(Exception) as excinfo:
            reference_merger._search_reference_table('1234')
        
        assert "テスト用エラー" in str(excinfo.value)
        log_msg("TableSearcherがエラーを発生させた場合、適切に例外が発生しました", LogLevel.DEBUG)

    @pytest.mark.parametrize("branch_code_prefix, expected_count", [
        ('1234', 1),
        ('5678', 1),
        ('9012', 1),
        ('12', 1),
        ('0000', 0),
    ])
    def test_search_reference_table_C0_various_prefixes(self, reference_merger, branch_code_prefix, expected_count):
        test_doc = f"""テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 様々な部店コードプレフィックスで検索 ({branch_code_prefix})
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger._search_reference_table(branch_code_prefix)
        
        assert len(result) == expected_count
        if expected_count > 0:
            assert result.iloc[0]['branch_code_bpr'].startswith(branch_code_prefix)
        log_msg(f"部店コードプレフィックス '{branch_code_prefix}' で正しく検索できました", LogLevel.DEBUG)

class TestReferenceMergerFilterZeroRow:
    """ReferenceMergerの_filter_zero_rowメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        ├── 正常系: '0'を含む行がある場合
        ├── 正常系: '0'を含む行がない場合
        ├── 正常系: 空のDataFrameの場合
        └── 正常系: 必要な列がないDataFrameの場合
    """

    @pytest.fixture
    def sample_reference_data(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '9012', '3456'],
            'section_gr_code_bpr': ['0', '1', '0', '2'],
            'branch_name_bpr': ['Branch A', 'Branch B', 'Branch C', 'Branch D'],
            'parent_branch_code': ['P1234', 'P5678', 'P9012', 'P3456']
        })

    @pytest.fixture
    def mock_table_searcher(self, tmp_path, sample_reference_data):
        # テスト用のpickleファイルを作成
        pickle_path = tmp_path / "reference_table.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump(sample_reference_data, f)
        
        # TableSearcherのモックを作成
        mock = Mock(spec=TableSearcher)
        mock.pickle_path = pickle_path
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_filter_zero_row_C0_with_zero(self, reference_merger, sample_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: '0'を含む行がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger._filter_zero_row(sample_reference_data)
        
        assert not result.empty
        assert len(result) == 2
        assert all(result['section_gr_code_bpr'] == '0')
        log_msg("'0'を含む行が正しくフィルタリングされました", LogLevel.DEBUG)

    def test_filter_zero_row_C0_without_zero(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: '0'を含む行がない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_without_zero = pd.DataFrame({
            'branch_code_bpr': ['1234', '5678'],
            'section_gr_code_bpr': ['1', '2'],
            'branch_name_bpr': ['Branch A', 'Branch B'],
            'parent_branch_code': ['P1234', 'P5678']
        })

        result = reference_merger._filter_zero_row(df_without_zero)
        
        assert result.empty
        log_msg("'0'を含む行がない場合、空のDataFrameが返されました", LogLevel.DEBUG)

    def test_filter_zero_row_C0_empty_dataframe(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 空のDataFrameの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_df = pd.DataFrame()
        result = reference_merger._filter_zero_row(empty_df)
        
        assert result.empty
        assert list(result.columns) == list(empty_df.columns)
        log_msg("空のDataFrameの場合、空のDataFrameが返されました", LogLevel.DEBUG)

    def test_filter_zero_row_C0_missing_column(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 必要な列がないDataFrameの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_missing_column = pd.DataFrame({
            'branch_code_bpr': ['1234', '5678'],
            'branch_name_bpr': ['Branch A', 'Branch B'],
        })

        result = reference_merger._filter_zero_row(df_missing_column)
        
        assert result.empty
        assert list(result.columns) == list(df_missing_column.columns)
        log_msg("必要な列がないDataFrameの場合、空のDataFrameが返されました", LogLevel.DEBUG)

    @pytest.mark.parametrize("input_data, expected_count", [
        ({'section_gr_code_bpr': ['0', '1', '0', '2']}, 2),
        ({'section_gr_code_bpr': ['1', '2', '3', '4']}, 0),
        ({'section_gr_code_bpr': ['0', '0', '0', '0']}, 4),
        ({'section_gr_code_bpr': []}, 0),
        ({'other_column': ['0', '1', '0', '2']}, 0),
    ])
    def test_filter_zero_row_C0_various_inputs(self, reference_merger, input_data, expected_count):
        test_doc = f"""テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 様々な入力データでのフィルタリング
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df = pd.DataFrame(input_data)
        result = reference_merger._filter_zero_row(df)
        
        assert len(result) == expected_count
        if expected_count > 0 and 'section_gr_code_bpr' in result.columns:
            assert all(result['section_gr_code_bpr'] == '0')
        log_msg(f"入力データに対して正しくフィルタリングされました。結果の行数: {len(result)}", LogLevel.DEBUG)

class TestReferenceMergerCreateResultDict:
    """ReferenceMergerの_create_result_dictメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        ├── 正常系: 全ての値が存在する行で辞書を作成
        ├── 正常系: 一部の値がNaNの行で辞書を作成
        └── 正常系: 全ての値がNaNの行で辞書を作成
    """

    @pytest.fixture
    def sample_reference_data(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '9012'],
            'branch_name_bpr': ['Branch A', 'Branch B', 'Branch C'],
            'parent_branch_code': ['P1234', np.nan, 'P9012']
        })

    @pytest.fixture
    def mock_table_searcher(self, tmp_path, sample_reference_data):
        # テスト用のpickleファイルを作成
        pickle_path = tmp_path / "reference_table.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump(sample_reference_data, f)
        
        # TableSearcherのモックを作成
        mock = Mock(spec=TableSearcher)
        mock.pickle_path = pickle_path
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_create_result_dict_C0_all_values(self, reference_merger, sample_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 全ての値が存在する行で辞書を作成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = sample_reference_data.iloc[0]
        result = reference_merger._create_result_dict(row)
        
        assert result == {
            "reference_branch_code": "1234",
            "reference_branch_name": "Branch A",
            "reference_parent_branch_code": "P1234",
        }
        log_msg("全ての値が存在する行から正しく辞書が作成されました", LogLevel.DEBUG)

    def test_create_result_dict_C0_some_nan(self, reference_merger, sample_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 一部の値がNaNの行で辞書を作成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = sample_reference_data.iloc[1]
        result = reference_merger._create_result_dict(row)
        
        assert result == {
            "reference_branch_code": "5678",
            "reference_branch_name": "Branch B",
            "reference_parent_branch_code": None,
        }
        log_msg("一部の値がNaNの行から正しく辞書が作成されました", LogLevel.DEBUG)

    def test_create_result_dict_C0_all_nan(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 全ての値がNaNの行で辞書を作成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({
            'branch_code_bpr': np.nan,
            'branch_name_bpr': np.nan,
            'parent_branch_code': np.nan
        })
        result = reference_merger._create_result_dict(row)
        
        assert result == {
            "reference_branch_code": None,
            "reference_branch_name": None,
            "reference_parent_branch_code": None,
        }
        log_msg("全ての値がNaNの行から正しく辞書が作成されました", LogLevel.DEBUG)

    @pytest.mark.parametrize("input_data, expected_result", [
        ({"branch_code_bpr": "1234", "branch_name_bpr": "Branch A", "parent_branch_code": "P1234"},
         {"reference_branch_code": "1234", "reference_branch_name": "Branch A", "reference_parent_branch_code": "P1234"}),
        ({"branch_code_bpr": "5678", "branch_name_bpr": "Branch B", "parent_branch_code": np.nan},
         {"reference_branch_code": "5678", "reference_branch_name": "Branch B", "reference_parent_branch_code": None}),
        ({"branch_code_bpr": np.nan, "branch_name_bpr": np.nan, "parent_branch_code": np.nan},
         {"reference_branch_code": None, "reference_branch_name": None, "reference_parent_branch_code": None}),
    ])
    def test_create_result_dict_C0_various_inputs(self, reference_merger, input_data, expected_result):
        test_doc = f"""テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 様々な入力データでの辞書作成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series(input_data)
        result = reference_merger._create_result_dict(row)
        
        assert result == expected_result
        log_msg(f"入力データに対して正しく辞書が作成されました: {result}", LogLevel.DEBUG)

class TestReferenceMergerGetEmptyResult:
    """ReferenceMergerの_get_empty_resultメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        └── 正常系: 空の結果辞書を取得
    """

    @pytest.fixture
    def sample_reference_data(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '9012'],
            'branch_name_bpr': ['Branch A', 'Branch B', 'Branch C'],
            'parent_branch_code': ['P1234', 'P5678', 'P9012']
        })

    @pytest.fixture
    def mock_table_searcher(self, tmp_path, sample_reference_data):
        # テスト用のpickleファイルを作成
        pickle_path = tmp_path / "reference_table.pkl"
        with open(pickle_path, 'wb') as f:
            pickle.dump(sample_reference_data, f)
        
        # TableSearcherのモックを作成
        mock = Mock(spec=TableSearcher)
        mock.pickle_path = pickle_path
        return mock

    @pytest.fixture
    def reference_merger(self, mock_table_searcher):
        return ReferenceMerger(mock_table_searcher)

    def setup_method(self):
        log_msg("テスト開始", LogLevel.INFO)

    def teardown_method(self):
        log_msg("テスト終了", LogLevel.INFO)

    def test_get_empty_result_C0(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 空の結果辞書を取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger._get_empty_result()
        
        assert result == {
            "reference_branch_code": None,
            "reference_branch_name": None,
            "reference_parent_branch_code": None,
        }
        log_msg("空の結果辞書が正しく取得されました", LogLevel.DEBUG)

    def test_get_empty_result_C0_multiple_calls(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 複数回の呼び出しで一貫した結果を取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result1 = reference_merger._get_empty_result()
        result2 = reference_merger._get_empty_result()
        
        assert result1 == result2
        assert result1 is not result2  # 新しいオブジェクトが返されることを確認
        log_msg("複数回の呼び出しで一貫した結果が取得されました", LogLevel.DEBUG)

    def test_get_empty_result_C0_immutability(self, reference_merger):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 返された辞書の不変性を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = reference_merger._get_empty_result()
        original = result.copy()
        
        # 返された辞書を変更してみる
        result["reference_branch_code"] = "1234"
        
        # 再度メソッドを呼び出して、元の値が変更されていないことを確認
        new_result = reference_merger._get_empty_result()
        
        assert new_result == original
        log_msg("返された辞書の不変性が確認されました", LogLevel.DEBUG)

