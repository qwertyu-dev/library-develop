import pytest
import pandas as pd
from enum import IntEnum
from pathlib import Path
from unittest.mock import patch, MagicMock
from unittest.mock import Mock, patch
from src.lib.validator_utils.ibr_check_reference_exists import BranchCodeLength
from src.lib.validator_utils.ibr_check_reference_exists import CheckExistsReferenceRecord
from src.lib.validator_utils.ibr_check_reference_exists import Case7818Checker

####################################
# テストサポートモジュールimport
####################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestBranchCodeLength:
    """BranchCodeLengthのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: BRANCHの値が4であることを確認
    │   ├── 正常系: SECTION_GRの値が5であることを確認
    │   ├── 正常系: BRANCHとSECTION_GRの大小関係を確認
    │   └── 正常系: BranchCodeLengthがIntEnumのサブクラスであることを確認
    ├── C1: 分岐カバレッジ (Enumのため該当なし)
    └── C2: 条件カバレッジ (Enumのため該当なし)
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_branch_code_length_branch_value(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: BRANCHの値が4であることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        assert BranchCodeLength.BRANCH == 4

    def test_branch_code_length_section_gr_value(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: SECTION_GRの値が5であることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        assert BranchCodeLength.SECTION_GR == 5

    def test_branch_code_length_comparison(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: BRANCHとSECTION_GRの大小関係を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        assert BranchCodeLength.BRANCH < BranchCodeLength.SECTION_GR

    def test_branch_code_length_type(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: BranchCodeLengthがIntEnumのサブクラスであることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        assert issubclass(BranchCodeLength, IntEnum)


class TestCheckExistsReferenceRecordInit:
    """CheckExistsReferenceRecordの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な引数でインスタンスを生成 (4桁と5桁のbranch_code)
    │   ├── 異常系: branch_codeが文字列でない場合
    │   ├── 異常系: branch_codeが4桁または5桁でない場合
    │   └── 異常系: df_requestsがDataFrameでない場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: df_requestsが空のDataFrameの場合
    │   └── 正常系: df_requestsに複数の行がある場合
    └── C2: 条件カバレッジ
        ├── 正常系: branch_codeが4桁の場合
        ├── 正常系: branch_codeが5桁の場合
        └── 正常系: df_requestsに一致する行がない場合

    # C1のディシジョンテーブル
    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 |
    |--------------------------------|--------|--------|--------|--------|--------|
    | branch_codeが文字列である       | Y      | N      | Y      | Y      | Y      |
    | branch_codeが4桁または5桁である | Y      | -      | N      | Y      | Y      |
    | df_requestsがDataFrameである    | Y      | Y      | Y      | N      | Y      |
    | df_requestsが空ではない         | Y      | Y      | Y      | Y      | N      |
    | 出力                           | 正常   | 例外   | 例外   | 例外   | 正常   |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def valid_df_requests(self):
        return pd.DataFrame({
            'branch_code': ['1234', '5678', '12345'],
            'target_org': ['部店', '課', '部店'],
            'section_gr_code': ['A001', 'B002', 'C003']
        })

    def test_init_C0_valid_arguments(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な引数でインスタンスを生成 (4桁と5桁のbranch_code)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker_4 = CheckExistsReferenceRecord('1234', valid_df_requests)
        assert isinstance(checker_4, CheckExistsReferenceRecord)
        assert checker_4.branch_code == '1234'
        assert not checker_4.matching_df_requests.empty
        assert isinstance(checker_4.special_case_checkers[0], Case7818Checker)

        checker_5 = CheckExistsReferenceRecord('12345', valid_df_requests)
        assert isinstance(checker_5, CheckExistsReferenceRecord)
        assert checker_5.branch_code == '12345'
        assert not checker_5.matching_df_requests.empty

    def test_init_C0_invalid_branch_code_type(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: branch_codeが文字列でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        with pytest.raises(TypeError, match="branch_code must be a string"):
            CheckExistsReferenceRecord(1234, valid_df_requests)

    def test_init_C0_invalid_branch_code_length(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: branch_codeが4桁または5桁でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        with pytest.raises(ValueError, match="branch_code must be either 4 or 5 digits"):
            CheckExistsReferenceRecord('123', valid_df_requests)
        
        with pytest.raises(ValueError, match="branch_code must be either 4 or 5 digits"):
            CheckExistsReferenceRecord('123456', valid_df_requests)

    def test_init_C0_invalid_df_requests(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: df_requestsがDataFrameでない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        with pytest.raises(TypeError, match="df_requests must be a pandas DataFrame"):
            CheckExistsReferenceRecord('1234', [])

    def test_init_C1_empty_df_requests(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: df_requestsが空のDataFrameの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        empty_df = pd.DataFrame(columns=['branch_code', 'target_org', 'section_gr_code'])
        checker = CheckExistsReferenceRecord('1234', empty_df)
        assert checker.matching_df_requests.empty

    def test_init_C1_multiple_rows_df_requests(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: df_requestsに複数の行がある場合
        1234を指定しているため1234及び12345が該当する
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('1234', valid_df_requests)
        assert len(checker.matching_df_requests) == 2 
        assert checker.matching_df_requests.iloc[0]['branch_code'] == '1234'

    def test_init_C2_branch_code_4_digits(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁の場合
        1234を指定しているため1234及び12345が該当する
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('1234', valid_df_requests)
        assert checker.branch_code == '1234'
        assert len(checker.matching_df_requests) == 2

    def test_init_C2_branch_code_5_digits(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁の場合
        1234を指定しているため1234及び12345が該当する
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('12345', valid_df_requests)
        assert checker.branch_code == '12345'
        assert len(checker.matching_df_requests) == 2

    def test_init_C2_no_matching_rows(self, valid_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: df_requestsに一致する行がない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('9999', valid_df_requests)
        assert checker.matching_df_requests.empty

class TestCheckExistsReferenceRecordSetMatchingDfRequests:
    """CheckExistsReferenceRecordの_set_matching_df_requestsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 一致するレコードが存在する場合
    │   ├── 正常系: 一致するレコードが存在しない場合
    │   └── 正常系: 空のDataFrameが渡された場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: branch_codeが4桁の場合
    │   └── 正常系: branch_codeが5桁の場合
    └── C2: 条件カバレッジ
        ├── 正常系: 完全一致するレコードが存在する場合
        ├── 正常系: 上位4桁のみ一致するレコードが存在する場合
        └── 正常系: 複数の一致するレコードが存在する場合

    # C1のディシジョンテーブル
    | 条件                      | ケース1 | ケース2 | ケース3 | ケース4 |
    |---------------------------|--------|--------|--------|--------|
    | branch_codeが4桁          | Y      | N      | Y      | N      |
    | 一致するレコードが存在する | Y      | Y      | N      | N      |
    | 出力                      | 一致   | 一致   | 空     | 空     |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def sample_df_requests(self):
        return pd.DataFrame({
            'branch_code': ['1234', '12345', '5678', '9999'],
            'target_org': ['部店', '課', '部店', '課'],
            'section_gr_code': ['A001', 'B002', 'C003', 'D004']
        })

    def test_set_matching_df_requests_C0_matching_records(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 一致するレコードが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('1234', sample_df_requests)
        result = checker.matching_df_requests
        
        assert len(result) == 2
        assert all(row['branch_code'].startswith('1234') for _, row in result.iterrows())

    def test_set_matching_df_requests_C0_no_matching_records(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 一致するレコードが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('7777', sample_df_requests)
        result = checker.matching_df_requests
        
        assert result.empty

    def test_set_matching_df_requests_C0_empty_dataframe(self):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 空のDataFrameが渡された場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        empty_df = pd.DataFrame(columns=['branch_code', 'target_org', 'section_gr_code'])
        checker = CheckExistsReferenceRecord('1234', empty_df)
        result = checker.matching_df_requests
        
        assert result.empty

    def test_set_matching_df_requests_C1_4digit_branch_code(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('1234', sample_df_requests)
        result = checker.matching_df_requests
        
        assert len(result) == 2
        assert all(row['branch_code'].startswith('1234') for _, row in result.iterrows())

    def test_set_matching_df_requests_C1_5digit_branch_code(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('12345', sample_df_requests)
        result = checker.matching_df_requests
        
        assert len(result) == 2
        assert all(row['branch_code'].startswith('1234') for _, row in result.iterrows())

    def test_set_matching_df_requests_C2_exact_match(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 完全一致するレコードが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('1234', sample_df_requests)
        result = checker.matching_df_requests
        
        assert '1234' in result['branch_code'].values

    def test_set_matching_df_requests_C2_partial_match(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 上位4桁のみ一致するレコードが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('12346', sample_df_requests)
        result = checker.matching_df_requests
        
        assert '12345' in result['branch_code'].values

    def test_set_matching_df_requests_C2_multiple_matches(self, sample_df_requests):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 複数の一致するレコードが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        
        checker = CheckExistsReferenceRecord('1234', sample_df_requests)
        result = checker.matching_df_requests
        
        assert len(result) == 2
        assert set(result['branch_code'].values) == {'1234', '12345'}

class TestCheckExistsReferenceRecordProcessCheck:
    """CheckExistsReferenceRecordのproces_check_reference_data_existsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: _check_c_swがTrueを返し、_check_ref_findがTrueを返す場合
    │   ├── 正常系: _check_c_swがTrueを返し、_check_ref_findがFalseを返す場合
    │   └── 正常系: _check_c_swがFalseを返す場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: _check_c_swがTrueを返す分岐
    │   └── 正常系: _check_c_swがFalseを返す分岐
    └── C2: 条件カバレッジ
        ├── 正常系: df_referenceが空のDataFrameの場合
        └── 正常系: df_referenceに複数の行がある場合

    # C1のディシジョンテーブル
    | 条件               | ケース1 | ケース2 | ケース3 |
    |--------------------|--------|--------|--------|
    | _check_c_sw の結果 | True   | True   | False  |
    | _check_ref_find の結果 | True   | False  | -      |
    | 出力               | True   | False  | False  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_checker(self):
        df = pd.DataFrame({
            'branch_code': [],
            'target_org': [],
            'section_gr_code': [],
        })
        return CheckExistsReferenceRecord('1234', df)

    @pytest.fixture
    def sample_df_reference(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678'],
            'branch_code_jinji': ['1234', '5678'],
            'section_gr_code_jinji': ['0', 'B002'],
            'section_group_code_bpr': ['A001', 'B002'],
        })

    #@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    @patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    #def test_process_check_C0_both_true(self, mock_ref_find, mock_c_sw, mock_checker, sample_df_reference):
    def test_process_check_C0_both_true(self, mock_ref_find, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: _check_c_swがTrueを返し、_check_ref_findがTrueを返す場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        #mock_c_sw.return_value = True
        mock_ref_find.return_value = True

        result = mock_checker.proces_check_reference_data_exists(sample_df_reference)

        assert result is True
        #mock_c_sw.assert_called_once_with(sample_df_reference)
        mock_ref_find.assert_called_once_with(sample_df_reference)

    #@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    @patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    #def test_process_check_C0_c_sw_true_ref_find_false(self, mock_ref_find, mock_c_sw, mock_checker, sample_df_reference):
    def test_process_check_C0_c_sw_true_ref_find_false(self, mock_ref_find, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: _check_c_swがTrueを返し、_check_ref_findがFalseを返す場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        #mock_c_sw.return_value = True
        mock_ref_find.return_value = False

        result = mock_checker.proces_check_reference_data_exists(sample_df_reference)

        assert result is False
        #mock_c_sw.assert_called_once_with(sample_df_reference)
        mock_ref_find.assert_called_once_with(sample_df_reference)

    ##@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    #@patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    ##def test_process_check_C0_c_sw_false(self, mock_ref_find, mock_c_sw, mock_checker, sample_df_reference):
    #def test_process_check_C0_c_sw_false(self, mock_ref_find, mock_checker, sample_df_reference):
    #    test_doc = """テスト内容:
    #    
    #    - テストカテゴリ: C0
    #    - テスト区分: 正常系
    #    - テストシナリオ: _check_c_swがFalseを返す場合
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)

    #    #mock_c_sw.return_value = False

    #    result = mock_checker.proces_check_reference_data_exists(sample_df_reference)

    #    assert result is False
    #    #mock_c_sw.assert_called_once_with(sample_df_reference)
    #    mock_ref_find.assert_not_called()

    ##@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    #@patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    #def test_process_check_C1_c_sw_true_branch(self, mock_ref_find, mock_checker, sample_df_reference):
    #    test_doc = """テスト内容:
    #    
    #    - テストカテゴリ: C1
    #    - テスト区分: 正常系
    #    - テストシナリオ: _check_c_swがTrueを返す分岐
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)

    #    #mock_c_sw.return_value = True
    #    mock_ref_find.return_value = True

    #    result = mock_checker.proces_check_reference_data_exists(sample_df_reference)

    #    assert result is True
    #    #mock_c_sw.assert_called_once_with(sample_df_reference)
    #    mock_ref_find.assert_called_once_with(sample_df_reference)

    ##@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    #@patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    ##def test_process_check_C1_c_sw_false_branch(self, mock_ref_find, mock_c_sw, mock_checker, sample_df_reference):
    #def test_process_check_C1_c_sw_false_branch(self, mock_ref_find, mock_checker, sample_df_reference):
    #    test_doc = """テスト内容:
    #    
    #    - テストカテゴリ: C1
    #    - テスト区分: 正常系
    #    - テストシナリオ: _check_c_swがFalseを返す分岐
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)

    #    #mock_c_sw.return_value = False

    #    result = mock_checker.proces_check_reference_data_exists(sample_df_reference)

    #    assert result is False
    #    #mock_c_sw.assert_called_once_with(sample_df_reference)
    #    mock_ref_find.assert_not_called()

    #@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    @patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    #def test_process_check_C2_empty_df_reference(self, mock_ref_find, mock_c_sw, mock_checker):
    def test_process_check_C2_empty_df_reference(self, mock_ref_find, mock_checker):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: df_referenceが空のDataFrameの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_df = pd.DataFrame()
        #mock_c_sw.return_value = False
        mock_ref_find.return_value = False

        result = mock_checker.proces_check_reference_data_exists(empty_df)

        assert result is False
        #mock_c_sw.assert_called_once_with(empty_df)
        mock_ref_find.assert_called_once_with(empty_df)
        #mock_ref_find.assert_not_called()

    #@patch.object(CheckExistsReferenceRecord, '_check_c_sw')
    @patch.object(CheckExistsReferenceRecord, '_check_ref_find')
    #def test_process_check_C2_multiple_rows_df_reference(self, mock_ref_find, mock_c_sw, mock_checker, sample_df_reference):
    def test_process_check_C2_multiple_rows_df_reference(self, mock_ref_find, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: df_referenceに複数の行がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        #mock_c_sw.return_value = True
        mock_ref_find.return_value = True

        result = mock_checker.proces_check_reference_data_exists(sample_df_reference)

        assert result is True
        #mock_c_sw.assert_called_once_with(sample_df_reference)
        mock_ref_find.assert_called_once_with(sample_df_reference)

#class TestCheckExistsReferenceRecordCheckCSW:
#    """CheckExistsReferenceRecordの_check_c_swメソッドのテスト
#
#    テスト構造:
#    ├── C0: 基本機能テスト
#    │   ├── 正常系: matching_df_requestsが空でなく、マッチするレコードがある場合
#    │   ├── 正常系: matching_df_requestsが空の場合
#    │   └── 正常系: マッチするレコードがない場合
#    ├── C1: 分岐カバレッジ
#    │   ├── 正常系: bpr_matchがTrueの場合
#    │   ├── 正常系: jinji_matchがTrueの場合
#    │   └── 正常系: bpr_matchとjinji_matchが両方Falseの場合
#    └── C2: 条件カバレッジ
#        ├── 正常系: branch_code_bprのみマッチする場合
#        ├── 正常系: branch_code_jinjiのみマッチする場合
#        └── 正常系: branch_code_bprとbranch_code_jinjiの両方がマッチする場合
#
#    # C1のディシジョンテーブル
#    | 条件                      | ケース1 | ケース2 | ケース3 | ケース4 |
#    |---------------------------|--------|--------|--------|--------|
#    | matching_df_requests が空でない | Y      | N      | Y      | Y      |
#    | bpr_match                 | Y      | -      | N      | N      |
#    | jinji_match               | -      | -      | Y      | N      |
#    | 出力                      | True   | False  | True   | False  |
#    """
#
#    def setup_method(self):
#        log_msg("test start", LogLevel.INFO)
#
#    def teardown_method(self):
#        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)
#
#    @pytest.fixture
#    def sample_df_reference(self):
#        return pd.DataFrame({
#            'branch_code_bpr': ['1234', '5678', '9012'],
#            'branch_code_jinji': ['1234', '5678', '3456'],
#            'section_gr_code_jinji': ['0', 'B002', 'C003'],
#            'section_group_code_bpr': ['A001', 'B002', 'C003']
#        })
#
#    def test_check_c_sw_C0_matching_records(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: matching_df_requestsが空でなく、マッチするレコードがある場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['1234', '5678']})
#        checker = CheckExistsReferenceRecord('1234', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == True
#
#    def test_check_c_sw_C0_empty_matching_df_requests(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: matching_df_requestsが空の場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': []})
#        checker = CheckExistsReferenceRecord('1234', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == False
#
#    def test_check_c_sw_C0_no_matching_records(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: マッチするレコードがない場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['7777']})
#        checker = CheckExistsReferenceRecord('7777', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == False
#
#    def test_check_c_sw_C1_bpr_match_true(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: bpr_matchがTrueの場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['9012']})
#        checker = CheckExistsReferenceRecord('9012', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == True
#
#    def test_check_c_sw_C1_jinji_match_true(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: jinji_matchがTrueの場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['3456']})
#        checker = CheckExistsReferenceRecord('3456', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == True
#
#    def test_check_c_sw_C1_both_match_false(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: bpr_matchとjinji_matchが両方Falseの場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['7777']})
#        checker = CheckExistsReferenceRecord('7777', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == False
#
#    def test_check_c_sw_C2_only_bpr_match(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: branch_code_bprのみマッチする場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['9012']})
#        checker = CheckExistsReferenceRecord('9012', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == True
#
#    def test_check_c_sw_C2_only_jinji_match(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: branch_code_jinjiのみマッチする場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['3456']})
#        checker = CheckExistsReferenceRecord('3456', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == True
#
#    def test_check_c_sw_C2_both_match(self, sample_df_reference):
#        test_doc = """テスト内容:
#        
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: branch_code_bprとbranch_code_jinjiの両方がマッチする場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#        
#        df_requests = pd.DataFrame({'branch_code': ['1234']})
#        checker = CheckExistsReferenceRecord('1234', df_requests)
#        
#        result = checker._check_c_sw(sample_df_reference)
#        assert result == True

class TestCheckExistsReferenceRecordCheckRefFind:
    """CheckExistsReferenceRecordの_check_ref_findメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: matching_df_requestsが空でない場合
    │   ├── 正常系: matching_df_requestsが空の場合
    │   ├── 正常系: 特別ケースに該当する場合
    │   └── 正常系: 通常のチェックで該当する場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 特別ケースチェックがTrueを返す場合
    │   ├── 正常系: 部店チェックがTrueを返す場合
    │   ├── 正常系: 課チェックがTrueを返す場合
    │   └── 正常系: エリアチェックがTrueを返す場合
    └── C2: 条件カバレッジ
        ├── 正常系: target_orgが"部店"の場合
        ├── 正常系: target_orgが"課"の場合
        └── 正常系: target_orgが"エリア"の場合

    # C1のディシジョンテーブル
    | 条件                      | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 |
    |---------------------------|--------|--------|--------|--------|--------|
    | matching_df_requests が空でない | Y      | N      | Y      | Y      | Y      |
    | 特別ケースに該当           | Y      | -      | N      | N      | N      |
    | target_org が "部店"       | -      | -      | Y      | N      | N      |
    | target_org が "課"         | -      | -      | N      | Y      | N      |
    | target_org が "エリア"     | -      | -      | N      | N      | Y      |
    | 出力                      | True   | False  | True   | True   | True   |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def sample_df_reference(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '9012'],
            'branch_code_jinji': ['1234', '5678', '3456'],
            'section_gr_code_jinji': ['0', 'B002', 'C003'],
            'section_group_code_bpr': ['A001', 'B002', 'C003']
        })

    @pytest.fixture
    def mock_checker(self):
        df_requests = pd.DataFrame({
            'branch_code': ['1234', '5678'],
            'target_org': ['部店', '課'],
            'section_gr_code': ['A001', 'B002']
        })
        return CheckExistsReferenceRecord('1234', df_requests)

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    @patch.object(CheckExistsReferenceRecord, '_check_ka')
    @patch.object(CheckExistsReferenceRecord, '_check_area')
    def test_check_ref_find_C0_non_empty_matching(self, mock_area, mock_ka, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: matching_df_requestsが空でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = True
        
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    def test_check_ref_find_C0_empty_matching(self, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: matching_df_requestsが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_checker.matching_df_requests = pd.DataFrame()
        result = mock_checker._check_ref_find(sample_df_reference)
        assert not result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    def test_check_ref_find_C0_special_case(self, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 特別ケースに該当する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = True
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    def test_check_ref_find_C0_normal_check(self, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 通常のチェックで該当する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = True
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    def test_check_ref_find_C1_special_case_true(self, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 特別ケースチェックがTrueを返す場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = True
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    def test_check_ref_find_C1_buten_true(self, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 部店チェックがTrueを返す場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = True
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    @patch.object(CheckExistsReferenceRecord, '_check_ka')
    def test_check_ref_find_C1_ka_true(self, mock_ka, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 課チェックがTrueを返す場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = False
        mock_ka.return_value = True
        mock_checker.matching_df_requests.loc[0, 'target_org'] = '課'
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    @patch.object(CheckExistsReferenceRecord, '_check_ka')
    @patch.object(CheckExistsReferenceRecord, '_check_area')
    def test_check_ref_find_C1_area_true(self, mock_area, mock_ka, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: エリアチェックがTrueを返す場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = False
        mock_ka.return_value = False
        mock_area.return_value = True
        mock_checker.matching_df_requests.loc[0, 'target_org'] = 'エリア'
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    def test_check_ref_find_C2_target_org_buten(self, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: target_orgが"部店"の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = True
        mock_checker.matching_df_requests.loc[0, 'target_org'] = '部店'
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    @patch.object(CheckExistsReferenceRecord, '_check_ka')
    def test_check_ref_find_C2_target_org_ka(self, mock_ka, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: target_orgが"課"の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = False
        mock_ka.return_value = True
        mock_checker.matching_df_requests.loc[0, 'target_org'] = '課'
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result

    @patch.object(CheckExistsReferenceRecord, '_check_special_cases')
    @patch.object(CheckExistsReferenceRecord, '_check_buten')
    @patch.object(CheckExistsReferenceRecord, '_check_ka')
    @patch.object(CheckExistsReferenceRecord, '_check_area')
    def test_check_ref_find_C2_target_org_area(self, mock_area, mock_ka, mock_buten, mock_special, mock_checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: target_orgが"エリア"の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_special.return_value = False
        mock_buten.return_value = False
        mock_ka.return_value = False
        mock_area.return_value = True
        mock_checker.matching_df_requests.loc[0, 'target_org'] = 'エリア'
        result = mock_checker._check_ref_find(sample_df_reference)
        assert result


class TestCheckExistsReferenceRecordCheckButen:
    """CheckExistsReferenceRecordの_check_butenメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: branch_codeが4桁で、対応するレコードのsection_gr_code_jinjiが"0"の場合
    │   ├── 正常系: branch_codeが5桁で、対応するレコードのsection_gr_codeが一致する場合
    │   └── 正常系: 条件を満たさない場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: branch_codeが4桁の場合
    │   ├── 正常系: branch_codeが5桁の場合
    │   └── 正常系: branch_codeが4桁でも5桁でもない場合
    └── C2: 条件カバレッジ
        ├── 正常系: branch_codeが4桁で、対応するレコードのsection_gr_code_jinjiが"0"の場合
        ├── 正常系: branch_codeが4桁で、対応するレコードのsection_gr_code_jinjiが"0"でない場合
        ├── 正常系: branch_codeが4桁で、対応するレコードがない場合
        ├── 正常系: branch_codeが5桁で、対応するレコードのsection_gr_codeが一致する場合
        ├── 正常系: branch_codeが5桁で、対応するレコードのsection_gr_codeが一致しない場合
        └── 正常系: branch_codeが5桁で、対応するレコードがない場合

    # C1のディシジョンテーブル
    | 条件                           | ケース1 | ケース2 | ケース3 |
    |--------------------------------|--------|--------|--------|
    | branch_codeが4桁               | Y      | N      | N      |
    | branch_codeが5桁               | N      | Y      | N      |
    | 対応するレコードが存在する     | Y      | Y      | -      |
    | section_gr_code_jinjiが"0"     | Y      | -      | -      |
    | section_gr_codeが一致する      | -      | Y      | -      |
    | 出力                           | True   | True   | False  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def sample_df_reference(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '56789', '90123'],
            'branch_code_jinji': ['1234', '5678', '56789', '90123'],
            'section_gr_code_jinji': ['A009', 'A001', 'B002', 'C003'],
            'section_gr_code_bpr': ['0', 'B002', 'B002', 'C003']
        })

    @pytest.fixture
    def checker(self):
        df_requests = pd.DataFrame({
            'branch_code': ['1234', '56789'],
            'target_org': ['部店', '課'],
            'section_gr_code': ['A001', 'B002']
        })
        return CheckExistsReferenceRecord('1234', df_requests)

    def test_check_buten_C0_4digit_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードのsection_gr_code_jinjiが"0"の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert result

    def test_check_buten_C0_5digit_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードのsection_gr_codeが一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'B002'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert result

    def test_check_buten_C0_no_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たさない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '9999', 'section_gr_code': 'X999'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert not result

    def test_check_buten_C1_4digit(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert result

    def test_check_buten_C1_5digit(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'B002'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert result

    def test_check_buten_C1_invalid_length(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁でも5桁でもない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '123', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert not result

    def test_check_buten_C2_4digit_section_gr_0(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードのsection_gr_code_jinjiが"0"の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert result

    def test_check_buten_C2_4digit_section_gr_non_0(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードのsection_gr_code_jinjiが"0"でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '5678', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert not result

    def test_check_buten_C2_4digit_no_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '9999', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert not result

    def test_check_buten_C2_5digit_section_gr_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードのsection_gr_codeが一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'B002'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert result

    def test_check_buten_C2_5digit_section_gr_mismatch(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードのsection_gr_codeが一致しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'X999'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert not result

    def test_check_buten_C2_5digit_no_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '99999', 'section_gr_code': 'A001'})
        result = checker._check_buten(sample_df_reference, df_requests_row)
        assert not result

class TestCheckExistsReferenceRecordCheckKa:
    """CheckExistsReferenceRecordの_check_kaメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: branch_codeが4桁で、対応するレコードのsection_group_code_bprが一致する場合
    │   ├── 正常系: branch_codeが5桁で、対応するレコードのsection_gr_code_jinjiが一致する場合
    │   └── 正常系: 条件を満たさない場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: branch_codeが4桁の場合
    │   ├── 正常系: branch_codeが5桁の場合
    │   └── 正常系: branch_codeが4桁でも5桁でもない場合
    └── C2: 条件カバレッジ
        ├── 正常系: branch_codeが4桁で、対応するレコードのsection_group_code_bprが一致する場合
        ├── 正常系: branch_codeが4桁で、対応するレコードのsection_group_code_bprが一致しない場合
        ├── 正常系: branch_codeが4桁で、対応するレコードがない場合
        ├── 正常系: branch_codeが5桁で、対応するレコードのsection_gr_code_jinjiが一致する場合
        ├── 正常系: branch_codeが5桁で、対応するレコードのsection_gr_code_jinjiが一致しない場合
        └── 正常系: branch_codeが5桁で、対応するレコードがない場合

    # C1のディシジョンテーブル
    | 条件                           | ケース1 | ケース2 | ケース3 |
    |--------------------------------|--------|--------|--------|
    | branch_codeが4桁               | Y      | N      | N      |
    | branch_codeが5桁               | N      | Y      | N      |
    | 対応するレコードが存在する     | Y      | Y      | -      |
    | section_group_code_bprが一致   | Y      | -      | -      |
    | section_gr_code_jinjiが一致    | -      | Y      | -      |
    | 出力                           | True   | True   | False  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def sample_df_reference(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '56789', '90123'],
            'branch_code_jinji': ['1234', '5678', '56789', '90123'],
            'section_gr_code_jinji': ['A001', 'B002', 'C003', 'D004'],
            'section_gr_code_bpr': ['A001', 'B002', 'C003', 'D004']
        })

    @pytest.fixture
    def checker(self):
        df_requests = pd.DataFrame({
            'branch_code': ['1234', '56789'],
            'target_org': ['部店', '課'],
            'section_gr_code': ['A001', 'C003']
        })
        return CheckExistsReferenceRecord('1234', df_requests)

    def test_check_ka_C0_4digit_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードのsection_group_code_bprが一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert result

    def test_check_ka_C0_5digit_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードのsection_gr_code_jinjiが一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'C003'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert result

    def test_check_ka_C0_no_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たさない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '9999', 'section_gr_code': 'X999'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert not result

    def test_check_ka_C1_4digit(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert result

    def test_check_ka_C1_5digit(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'C003'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert result

    def test_check_ka_C1_invalid_length(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁でも5桁でもない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '123', 'section_gr_code': 'A001'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert not result

    def test_check_ka_C2_4digit_section_group_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードのsection_group_code_bprが一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert result

    def test_check_ka_C2_4digit_section_group_mismatch(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードのsection_group_code_bprが一致しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'X999'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert not result

    def test_check_ka_C2_4digit_no_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが4桁で、対応するレコードがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '9999', 'section_gr_code': 'A001'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert not result

    def test_check_ka_C2_5digit_section_gr_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードのsection_gr_code_jinjiが一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'C003'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert result

    def test_check_ka_C2_5digit_section_gr_mismatch(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードのsection_gr_code_jinjiが一致しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '56789', 'section_gr_code': 'X999'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert not result

    def test_check_ka_C2_5digit_no_match(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: branch_codeが5桁で、対応するレコードがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df_requests_row = pd.Series({'branch_code': '99999', 'section_gr_code': 'A001'})
        result = checker._check_ka(sample_df_reference, df_requests_row)
        assert not result


class TestCheckExistsReferenceRecordCheckSpecialCases:
    """CheckExistsReferenceRecordの_check_special_casesメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 全てのチェッカーが呼び出されることを確認
    │   └── 正常系: チェッカーリストが空の場合
    ├── C1: 分岐カバレッジ
    │   └── 正常系: 複数のチェッカーがある場合、全て呼び出されることを確認
    └── C2: 条件カバレッジ
        ├── 正常系: 実際のCase7818Checkerを含む場合
        └── 正常系: 異なる種類のチェッカーが混在する場合

    # C1のディシジョンテーブル
    | 条件                      | ケース1 | ケース2 |
    |---------------------------|--------|--------|
    | チェッカーリストが空でない | Y      | N      |
    | 複数のチェッカーがある     | Y      | -      |
    | 全てのチェッカーが呼ばれる | Y      | -      |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def sample_df_reference(self):
        return pd.DataFrame({
            'branch_code_bpr': ['1234', '5678', '78180', '90123'],
            'branch_code_jinji': ['1234', '5678', '78180', '90123'],
            'section_gr_code_jinji': ['A001', 'B002', '7818C', 'D004'],
            'section_gr_code_bpr': ['A001', 'B002', '7818C', 'D004']
        })

    @pytest.fixture
    def checker(self):
        df_requests = pd.DataFrame({
            'branch_code': ['1234', '78180'],
            'target_org': ['部店', '課'],
            'section_gr_code': ['A001', '7818C']
        })
        return CheckExistsReferenceRecord('1234', df_requests)

    def test_check_special_cases_C0_all_checkers_called(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 全てのチェッカーが呼び出されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_checker1 = Mock()
        mock_checker2 = Mock()
        checker.special_case_checkers = [mock_checker1, mock_checker2]

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        checker._check_special_cases(sample_df_reference, df_requests_row)

        mock_checker1.check.assert_called_once_with(sample_df_reference, df_requests_row)
        mock_checker2.check.assert_called_once_with(sample_df_reference, df_requests_row)

    def test_check_special_cases_C0_empty_checkers(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: チェッカーリストが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker.special_case_checkers = []
        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        
        # 例外が発生しないことを確認
        checker._check_special_cases(sample_df_reference, df_requests_row)

    def test_check_special_cases_C1_multiple_checkers(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複数のチェッカーがある場合、全て呼び出されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_checker1 = Mock()
        mock_checker2 = Mock()
        mock_checker3 = Mock()
        checker.special_case_checkers = [mock_checker1, mock_checker2, mock_checker3]

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        checker._check_special_cases(sample_df_reference, df_requests_row)

        mock_checker1.check.assert_called_once_with(sample_df_reference, df_requests_row)
        mock_checker2.check.assert_called_once_with(sample_df_reference, df_requests_row)
        mock_checker3.check.assert_called_once_with(sample_df_reference, df_requests_row)

    def test_check_special_cases_C2_real_case7818(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 実際のCase7818Checkerを含む場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        real_checker = Case7818Checker()
        mock_checker = Mock()
        checker.special_case_checkers = [real_checker, mock_checker]

        df_requests_row = pd.Series({'branch_code': '78180', 'section_gr_code': '7818C'})
        checker._check_special_cases(sample_df_reference, df_requests_row)

        mock_checker.check.assert_called_once_with(sample_df_reference, df_requests_row)

    def test_check_special_cases_C2_mixed_checkers(self, checker, sample_df_reference):
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 異なる種類のチェッカーが混在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class DummyChecker:
            def check(self, df_reference, df_requests_row):
                pass

        real_checker = Case7818Checker()
        dummy_checker = DummyChecker()
        mock_checker = Mock()
        checker.special_case_checkers = [real_checker, dummy_checker, mock_checker]

        df_requests_row = pd.Series({'branch_code': '1234', 'section_gr_code': 'A001'})
        checker._check_special_cases(sample_df_reference, df_requests_row)

        mock_checker.check.assert_called_once_with(sample_df_reference, df_requests_row)
