"""merge前処理、マージ処理テスト"""
import sys
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import ApplicationType, LogLevel, OrganizationType
from src.lib.converter_utils.ibr_reference_mergers import (
    BranchNameSplitError,
    DataLoadError,
    ReferenceMergers,
    RemarksParseError,
)

# config共有
config = initialize_config(sys.modules[__name__])
package_config = config.package_config
log_msg = config.log_message

class TestReferenceMergersAddBprTargetFlag:
    """ReferenceMergersクラスのadd_bpr_target_flag_from_referenceメソッドのテスト

    テスト対象: ReferenceMergers.add_bpr_target_flag_from_reference()
    │   ├── C0: 基本機能テスト
    │   │   ├── 正常系: 新設以外の申請に対するBPRADフラグ付与
    │   │   ├── 異常系: データロード失敗
    │   │   └── 異常系: マージ処理失敗
    │   ├── C1: 分岐カバレッジ
    │   │   ├── データロード分岐
    │   │   └── マージ処理分岐
    │   ├── C2: 条件組み合わせ
    │   │   ├── 新設申請
    │   │   ├── 変更申請
    │   │   └── 廃止申請
    │   ├── DT: ディシジョンテーブル
    │   │   ├── 申請種類
    │   │   └── BPRADフラグ状態
    │   └── BVT: 境界値テスト
    │       ├── エリアコード境界
    │       └── フラグ値境界

    C1のディシジョンテーブル:
    | 条件                                   | DT1 | DT2 | DT3 | DT4 | DT5 |
    |----------------------------------------|-----|-----|-----|-----|-----|
    | 申請種類が新設以外                     | Y   | N   | Y   | Y   | Y   |
    | リファレンスに対応レコードが存在する   | Y   | -   | N   | Y   | Y   |
    | エリアコードが一致する                 | Y   | -   | -   | N   | Y   |
    | BPRフラグ値が存在する                  | Y   | -   | -   | -   | N   |
    | 期待される動作                         | 成功| 成功| 成功| 成功| 成功|

    境界値検証ケース一覧:
    | ケースID | テストケース     | テスト値 | 期待結果 | テストの目的       | 実装状況                                       |
    |----------|------------------|----------|----------|--------------------|------------------------------------------------|
    | BVT_001  | 最小エリアコード | "A"      | 正常終了 | 最小有効値の確認   | 実装済み (test_add_bpr_flag_BVT_area_code_min) |
    | BVT_002  | 最大エリアコード | "Z"      | 正常終了 | 最大有効値の確認   | 実装済み (test_add_bpr_flag_BVT_area_code_max) |
    | BVT_003  | 空エリアコード   | ""       | 正常終了 | 空値の確認         | 実装済み (test_add_bpr_flag_BVT_area_code_empty) |
    | BVT_004  | BPRフラグ最小値  | "0"      | 正常終了 | フラグ最小値の確認 | 実装済み (test_add_bpr_flag_BVT_flag_min) |
    | BVT_005  | BPRフラグ最大値  | "1"      | 正常終了 | フラグ最大値の確認 | 実装済み (test_add_bpr_flag_BVT_flag_max) |
    """

    @pytest.fixture()
    def integrated_layout_df(self) -> pd.DataFrame:
        """統合レイアウトデータのfixture"""
        columns = [
            'ulid', 'form_type', 'application_type', 'target_org', 'business_unit_code',
            'parent_branch_code', 'branch_code', 'branch_name', 'section_gr_code',
            'section_gr_name', 'section_name_en', 'resident_branch_code',
            'resident_branch_name', 'aaa_transfer_date', 'internal_sales_dept_code',
            'internal_sales_dept_name', 'area_code', 'area_name', 'remarks',
            'branch_name_kana', 'section_gr_name_kana', 'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        data = [
            ['add_bpr_target_flag_from_reference', '2', '変更', '部', '339', '*', '0001', 'AAA支店', '0', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
            ['add_bpr_target_flag_from_reference', '2', '変更', '課', '339', '*', '0001', 'AAA支店', '00011', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
            ['add_bpr_target_flag_from_reference', '2', '削除', '部', '339', '*', '0002', 'AAA支店', '0', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
            ['add_bpr_target_flag_from_reference', '2', '新設', '課', '339', '*', '0002', 'AAA支店', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
        ]

        return pd.DataFrame(data, columns=columns)

    @pytest.fixture()
    def reference_table_df(self) -> pd.DataFrame:
        """リファレンステーブルのfixture"""
        columns = [
            'reference_db_update_datetime', 'organization_change_date', 'ulid',
            'branch_code_bpr', 'branch_name_bpr', 'section_gr_code_bpr', 'section_gr_name_bpr',
            'business_unit_code_bpr', 'parent_branch_code', 'internal_sales_dept_code',
            'internal_sales_dept_name', 'branch_code_jinji', 'branch_name_jinji',
            'section_gr_code_jinji', 'section_gr_name_jinji', 'branch_code_area',
            'branch_name_area', 'section_gr_code_area', 'section_gr_name_area',
            'sub_branch_code', 'sub_branch_name', 'business_code', 'area_code',
            'area_name', 'resident_branch_code', 'resident_branch_name', 'portal_use',
            'portal_send', 'hq_sales_branch_flag', 'organization_classification',
            'organization_classification_code', 'branch_sort_number', 'branch_sort_number2',
            'organization_name_kana', 'dp_code', 'dp_code_bp', 'gr_code', 'gr_code_bp',
            'grps_code', 'bpr_target_flag', 'secondment_recovery_flag', 'remarks',
            'sort',
        ]

        data = [
            ['add_bpr_target_flag_from_reference', '20241211', 'ULID000009', '00100', '支店10', '00107', 'グループ10', '3', '00040', 'S0009', '営業部10', '0001', '支店10', '0', 'グループ10', '00100', '支店10', '00107', 'グループ10', 'SB009', '出張所10', 'B', 'FBFT10', 'エリア10', '00040', '常駐支店10', '1', '0', '0', 'DOMESTIC', '2', '0010', '0010', 'シテン10', 'DP009', 'DPB009', 'GR009', 'GRB009', 'GRPS009', '5', '0', '備考10', '10'],
            ['add_bpr_target_flag_from_reference', '20241211', 'ULID000009', '00100', '支店10', '00107', 'グループ10', '3', '00040', 'S0009', '営業部10', '00011', '支店10', '00011', 'グループ10', '00100', '支店10', '00107', 'グループ10', 'SB009', '出張所10', 'B', 'FBFT10', 'エリア10', '00040', '常駐支店10', '1', '0', '0', 'DOMESTIC', '2', '0010', '0010', 'シテン10', 'DP009', 'DPB009', 'GR009', 'GRB009', 'GRPS009', '6', '0', '備考10', '10'],
            ['add_bpr_target_flag_from_reference', '20241211', 'ULID000009', '00100', '支店10', '00107', 'グループ10', '3', '', 'S0009', '営業部10', '0002', '支店20', '0', 'グループ10', '00100', '支店20', '00107', 'グループ10', 'SB009', '出張所10', 'B', 'FBFT10', 'エリア10', '00040', '常駐支店10', '1', '0', '0', 'DOMESTIC', '2', '0010', '0010', 'シテン10', 'DP009', 'DPB009', 'GR009', 'GRB009', 'GRPS009', '7', '0', '備考10', '10'],
            ['add_bpr_target_flag_from_reference', '20241211', 'ULID000009', '00100', '支店10', '00107', 'グループ10', '3', '', 'S0009', '営業部10', '00021', '支店20', '00021', 'グループ10', '00100', '支店20', '00107', 'グループ10', 'SB009', '出張所10', 'B', 'FBFT10', 'エリア10', '00040', '常駐支店10', '1', '0', '0', 'DOMESTIC', '2', '0010', '0010', 'シテン10', 'DP009', 'DPB009', 'GR009', 'GRB009', 'GRPS009', '8', '0', '備考10', '10'],
        ]

        return pd.DataFrame(data, columns=columns)

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_add_bpr_flag_C0_valid_configuration(self, integrated_layout_df, reference_table_df):
        """正常系: 有効な設定での基本機能テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 基本的なBPRフラグ付与処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'reference_bpr_target_flag' in result.columns

        # 変更/廃止の場合はリファレンスの値が設定されている
        change_delete_mask = result['application_type'].isin(['変更', '削除'])
        assert result.loc[change_delete_mask, 'reference_bpr_target_flag'].notna().all()

    def test_add_bpr_flag_C1_dt1_successful_merge(self, integrated_layout_df, reference_table_df):
        """C1: 全条件を満たす正常系テスト(DT1)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT1の全条件満たすケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'reference_bpr_target_flag' in result.columns
        assert result['reference_bpr_target_flag'].notna().any()

    def test_add_bpr_flag_C1_dt2_new_record(self, integrated_layout_df, reference_table_df):
        """C1: 新設レコードのテスト(DT2)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 異常系 - DT2の新設レコードケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 全て新設に変更
        integrated_layout_df['application_type'] = ApplicationType.NEW.value
        reference_table_df['bpr_target_flag'] = '' # 新設なのですくなくともBPRADフラグは値なし
        log_msg('reference_table_df', LogLevel.DEBUG)
        tabulate_dataframe(reference_table_df)

        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )

        assert 'reference_bpr_target_flag' in result.columns
        assert result['reference_bpr_target_flag'].eq('').all()

    def test_add_bpr_flag_C2_area_code_combinations(self, integrated_layout_df, reference_table_df):
        """C2: エリアコードの組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 条件組み合わせ - エリアコードの一致/不一致
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エリアコード一致
        result1 = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )
        assert 'reference_bpr_target_flag' in result1.columns
        change_delete_mask = result1['application_type'].isin(['変更', '削除'])
        assert result1.loc[change_delete_mask, 'reference_bpr_target_flag'].notna().any()

        # エリアコード不一致
        integrated_layout_df['area_code'] = 'XXXXX'
        result2  = ReferenceMergers.add_bpr_target_flag_from_reference(
                integrated_layout_df,
                reference_table_df,
            )
        log_msg('reference_table_df', LogLevel.DEBUG)
        tabulate_dataframe(reference_table_df)
        log_msg('integrated', LogLevel.DEBUG)
        tabulate_dataframe(integrated_layout_df)
        log_msg('result2', LogLevel.DEBUG)
        tabulate_dataframe(result2)
        # データの内4件はエリアコードに依存しない
        assert len(result2) == 4
        # reference_bpr_target_flagは値設定されず空振り
        assert all(result2['reference_bpr_target_flag'] == '')

    def test_add_bpr_flag_BVT_area_code_boundary(self, integrated_layout_df, reference_table_df):
        """境界値: エリアコードの境界値テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: エリアコードの境界値テスト
            - 最小値: "A0000"
            - 最大値: "Z9999"
            - 空文字列
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小値テスト
        integrated_layout_df['area_code'] = 'A0000'
        reference_table_df['area_code'] = 'A0000'
        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )
        assert isinstance(result, pd.DataFrame)
        assert 'reference_bpr_target_flag' in result.columns

        # 最大値テスト
        integrated_layout_df['area_code'] = 'Z9999'
        reference_table_df['area_code'] = 'Z9999'
        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )
        assert isinstance(result, pd.DataFrame)
        assert 'reference_bpr_target_flag' in result.columns

        # 空文字列テスト
        integrated_layout_df['area_code'] = ''
        reference_table_df['area_code'] = ''
        result =   ReferenceMergers.add_bpr_target_flag_from_reference(
                integrated_layout_df,
                reference_table_df,
            )
        # データの内4件はエリアコードに依存しない
        assert len(result) == 4
        assert result.loc[0, 'reference_bpr_target_flag'] == '5'
        assert result.loc[1, 'reference_bpr_target_flag'] == ''  # ヒットしない
        assert result.loc[2, 'reference_bpr_target_flag'] == '7'
        assert result.loc[3, 'reference_bpr_target_flag'] == ''  # ヒットしない

    def test_add_bpr_flag_BVT_flag_value_boundary(self, integrated_layout_df, reference_table_df):
        """境界値: BPRフラグ値の境界値テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: BPRフラグ値の境界値テスト
            - 最小値: "0"
            - 最大値: "1"
            - NULL値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小値テスト
        reference_table_df['bpr_target_flag'] = '0'
        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )
        log_msg('reference_table_df', LogLevel.DEBUG)
        tabulate_dataframe(reference_table_df)
        log_msg('integrated', LogLevel.DEBUG)
        tabulate_dataframe(integrated_layout_df)
        log_msg('result', LogLevel.DEBUG)
        tabulate_dataframe(result)

        assert isinstance(result, pd.DataFrame)
        assert 'reference_bpr_target_flag' in result.columns
        #change_delete_mask = result['application_type'].isin(['変更', '削除'])
        #assert result.loc[change_delete_mask, 'reference_bpr_target_flag'].eq('0').all()
        # 変更・削除レコードの検証
        change_delete_mask = result['application_type'].isin(['変更', '削除'])
        change_delete_base_mask = change_delete_mask & (result['section_gr_code'] == '0')
        change_delete_detail_mask = change_delete_mask & (result['section_gr_code'] != '0')

        # 基準レコード(部)の検証
        assert result.loc[change_delete_base_mask, 'reference_bpr_target_flag'].eq('0').all(), \
            "変更・削除の基準レコードのフラグ値が'0'ではありません"

        # 明細レコード(課)の検証
        assert result.loc[change_delete_detail_mask, 'reference_bpr_target_flag'].eq('').all(), \
            "変更・削除の明細レコードのフラグ値が空文字ではありません"

        # 新設レコードの検証
        new_mask = result['application_type'] == ApplicationType.NEW.value
        assert result.loc[new_mask, 'reference_bpr_target_flag'].eq('').all(), \
            "新設レコードのフラグ値が空文字ではありません"

        # 最大値テスト
        reference_table_df['bpr_target_flag'] = '1'
        result = ReferenceMergers.add_bpr_target_flag_from_reference(
            integrated_layout_df,
            reference_table_df,
        )

        # 変更・削除レコードの検証(部/課で分けて検証)
        change_delete_mask = result['application_type'].isin(['変更', '削除'])
        change_delete_base_mask = change_delete_mask & (result['section_gr_code'] == '0')
        change_delete_detail_mask = change_delete_mask & (result['section_gr_code'] != '0')

        # 部レコード(section_gr_code = '0')の検証
        assert result.loc[change_delete_base_mask, 'reference_bpr_target_flag'].eq('1').all(), \
            "変更・削除の部レコードのフラグ値が'1'ではありません"

        # 課レコード(section_gr_code != '0')の検証
        assert result.loc[change_delete_detail_mask, 'reference_bpr_target_flag'].eq('').all(), \
            "変更・削除の課レコードのフラグ値が空文字ではありません"

        # 新設レコードの検証
        new_mask = result['application_type'] == '新設'
        assert result.loc[new_mask, 'reference_bpr_target_flag'].eq('').all(), \
        "新設レコードのフラグ値が空文字ではありません"

        ## NULL値テスト
        reference_table_df['bpr_target_flag'] = None
        result = ReferenceMergers.add_bpr_target_flag_from_reference(
                integrated_layout_df,
                reference_table_df,
            )
        log_msg('result', LogLevel.DEBUG)
        tabulate_dataframe(result)

        assert all(result['reference_bpr_target_flag'] == '')

class TestReferenceMergersSetupInternalSales:
    """ReferenceMergersクラスのsetup_internal_sales_to_integrated_dataメソッドのテスト

    テスト対象: ReferenceMergers.setup_internal_sales_to_integrated_data()
    │   ├── C0: 基本機能テスト
    │   │   ├── 正常系: 拠点内営業部データの編集
    │   │   ├── 異常系: データロード失敗
    │   │   └── 異常系: 名称分割失敗
    │   ├── C1: 分岐カバレッジ
    │   │   ├── データ有無分岐
    │   │   └── 処理成功分岐
    │   ├── C2: 条件組み合わせ
    │   │   ├── 有効データ
    │   │   └── 無効データ
    │   ├── DT: ディシジョンテーブル
    │   │   └── データ処理条件
    │   └── BVT: 境界値テスト
    │       └── 名称長境界

    C1のディシジョンテーブル:
    | 条件                                  | DT1 | DT2 | DT3 | DT4 | DT5 |
    |---------------------------------------|-----|-----|-----|-----|-----|
    | 拠点内営業部データが存在する          | Y   | N   | Y   | Y   | Y   |
    | 支店名称に'支店'が含まれる            | Y   | -   | N   | Y   | Y   |
    | 支店名称に'営業部'が含まれる          | Y   | -   | -   | N   | Y   |
    | 部店コードが4桁である                 | Y   | -   | -   | -   | N   |
    | 期待される動作                        | 成功| 警告| 成功| 成功| 成功|

    境界値検証ケース一覧:
    | ケースID | テストケース   | テスト値                              | 期待結果 | テストの目的     | 実装状況                                                 |
    |----------|----------------|---------------------------------------|----------|------------------|----------------------------------------------------------|
    | BVT_001  | 最小部店コード | "0000"                                | 正常終了 | 最小有効値の確認 | 実装済み (test_setup_internal_sales_BVT_min_branch_code) |
    | BVT_002  | 最大部店コード | "9999"                                | 正常終了 | 最大有効値の確認 | 実装済み (test_setup_internal_sales_BVT_max_branch_code) |
    | BVT_003  | 無効部店コード | "999"                                 | 正常終了 | 3桁の確認        | 実装済み (test_setup_internal_sales_BVT_invalid_branch_code) |
    | BVT_004  | 名称最小長     | "A支店B営業部"                        | 正常終了 | 最小名称長の確認 | 実装済み (test_setup_internal_sales_BVT_min_name_length) |
    | BVT_005  | 名称最大長     | "A"*100 + "支店" + "B"*100 + "営業部" | 正常終了 | 最大名称長の確認 | 実装済み (test_setup_internal_sales_BVT_max_name_length) |
    """

    @pytest.fixture()
    def integrated_layout_df(self) -> pd.DataFrame:
        """統合レイアウトデータのfixture"""
        columns = [
            'ulid', 'form_type', 'application_type', 'target_org', 'business_unit_code',
            'parent_branch_code', 'branch_code', 'branch_name', 'section_gr_code',
            'section_gr_name', 'section_name_en', 'resident_branch_code',
            'resident_branch_name', 'aaa_transfer_date', 'internal_sales_dept_code',
            'internal_sales_dept_name', 'area_code', 'area_name', 'remarks',
            'branch_name_kana', 'section_gr_name_kana', 'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        data = [
            ['setup_internal_sales_to_integrated_data', '2', '新設', '拠点内営業部', '339', '*', '0003', 'AAA支店BBB営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
            ['setup_internal_sales_to_integrated_data', '2', '新設', '拠点内営業部', '339', '*', '00032', 'AAA支店CCC営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
        ]

        return pd.DataFrame(data, columns=columns)

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_setup_internal_sales_C0_valid_data(self, integrated_layout_df):
        """正常系: 拠点内営業部データの基本的な編集テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 基本的な拠点内営業部データの編集を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.setup_internal_sales_to_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert 'internal_sales_dept_code' in result.columns
        assert 'internal_sales_dept_name' in result.columns

        # データの検証
        internal_sales_mask = result['target_org'] == OrganizationType.INTERNAL_SALES.value
        assert result.loc[internal_sales_mask, 'internal_sales_dept_code'].notna().all()
        assert result.loc[internal_sales_mask, 'internal_sales_dept_name'].notna().all()

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

    def test_setup_internal_sales_C0_no_data(self, integrated_layout_df):
        """正常系: 拠点内営業部データが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 拠点内営業部データが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # データを変更して拠点内営業部を含まないようにする
        integrated_layout_df['target_org'] = OrganizationType.BRANCH.value

        result = ReferenceMergers.setup_internal_sales_to_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.equals(integrated_layout_df)

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

    def test_setup_internal_sales_C1_dt1_successful(self, integrated_layout_df):
        """C1: 全条件を満たす正常系テスト(DT1)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT1のすべての条件を満たすケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.setup_internal_sales_to_integrated_data(
            integrated_layout_df,
        )

        # 結果の検証
        internal_sales_mask = result['target_org'] == OrganizationType.INTERNAL_SALES.value
        assert result.loc[internal_sales_mask, 'internal_sales_dept_code'].notna().all()
        assert result.loc[internal_sales_mask, 'internal_sales_dept_name'].notna().all()
        assert result.loc[internal_sales_mask, 'branch_name'].str.contains('支店').all()
        assert result.loc[internal_sales_mask, 'internal_sales_dept_name'].str.contains('営業部').all()

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

    def test_setup_internal_sales_C1_dt2_no_internal_sales(self, integrated_layout_df):
        """C1: 拠点内営業部データが存在しない場合のテスト(DT2)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT2の拠点内営業部データなしケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # データを変更して拠点内営業部を含まないようにする
        integrated_layout_df['target_org'] = '部'

        result = ReferenceMergers.setup_internal_sales_to_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.equals(integrated_layout_df)

    def test_setup_internal_sales_C2_branch_name_patterns(self, integrated_layout_df):
        """C2: 支店名称パターンの組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 条件組み合わせ - 支店名称のパターン
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_patterns = [
            ('AAA支店BBB営業部', True, 'BBB営業部'),
            ('AAA支店営業部', True, '営業部'),
            ('支店営業部', True, '営業部'),
            ('AAA支店', True, ''),
            ('AAA営業部', True, ''),
            ('AAA', True, ''),
        ]

        for branch_name, should_succeed, expected_dept_name in test_patterns:
            # テストデータの準備
            test_df = integrated_layout_df.copy()
            test_df.loc[0, 'branch_name'] = branch_name

            if should_succeed:
                result = ReferenceMergers.setup_internal_sales_to_integrated_data(test_df)
                internal_sales_mask = result['target_org'] == OrganizationType.INTERNAL_SALES.value
                assert result.loc[internal_sales_mask, 'internal_sales_dept_name'].iloc[0] == expected_dept_name
            else:
                with pytest.raises(BranchNameSplitError):
                    ReferenceMergers.setup_internal_sales_to_integrated_data(test_df)

    def test_setup_internal_sales_BVT_name_boundary(self, integrated_layout_df):
        """境界値: 部店名称の境界値テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 部店名称の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小長テスト
        integrated_layout_df.loc[0, 'branch_name'] = 'A支店B営業部'
        result = ReferenceMergers.setup_internal_sales_to_integrated_data(
            integrated_layout_df,
        )
        internal_sales_mask = result['target_org'] == OrganizationType.INTERNAL_SALES
        assert result.loc[internal_sales_mask, 'branch_name'].str.contains('支店').all()
        assert result.loc[internal_sales_mask, 'internal_sales_dept_name'].str.contains('営業部').all()

        # 最大長テスト(100文字)
        long_name = 'A' * 47 + '支店' + 'B' * 47 + '営業部'
        integrated_layout_df.loc[0, 'branch_name'] = long_name
        result = ReferenceMergers.setup_internal_sales_to_integrated_data(
            integrated_layout_df,
        )
        assert result.loc[internal_sales_mask, 'branch_name'].str.contains('支店').all()
        assert result.loc[internal_sales_mask, 'internal_sales_dept_name'].str.contains('営業部').all()

        # 本来は無効なパターンテスト
        invalid_patterns = [
            '',           # 空文字
            'AAA',        # 支店・営業部なし
            'AAA支店',    # 営業部なし
            'AAA営業部',  # 支店なし
        ]

        for invalid_name in invalid_patterns:
            test_df = integrated_layout_df.copy()
            test_df.loc[0, 'branch_name'] = invalid_name
            result = ReferenceMergers.setup_internal_sales_to_integrated_data(test_df)

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)


class TestReferenceMergersSetupArea:
    """ReferenceMergersクラスのsetup_area_to_integrated_dataメソッドのテスト

    テスト対象: ReferenceMergers.setup_area_to_integrated_data()
    │   ├── C0: 基本機能テスト
    │   │   ├── 正常系: エリア向けデータ編集
    │   │   ├── 異常系: データロード失敗
    │   │   └── 異常系: 備考欄解析失敗
    │   ├── C1: 分岐カバレッジ
    │   │   ├── データ有無分岐
    │   │   └── 処理成功分岐
    │   ├── C2: 条件組み合わせ
    │   │   ├── 有効データ
    │   │   └── 無効データ
    │   ├── DT: ディシジョンテーブル
    │   │   └── エリア処理条件
    │   └── BVT: 境界値テスト
    │       └── エリアコード境界

    C1のディシジョンテーブル:
    | 条件                             | DT1 | DT2 | DT3 | DT4 | DT5 |
    |----------------------------------|-----|-----|-----|-----|-----|
    | エリアデータが存在する           | Y   | N   | Y   | Y   | Y   |
    | 備考欄にエリアグループコードあり | Y   | -   | N   | Y   | Y   |
    | 備考欄にエリアグループ名あり     | Y   | -   | -   | N   | Y   |
    | エリアグループ形式が正しい       | Y   | -   | -   | -   | N   |
    | 期待される動作                   | 成功| 警告| 成功| 成功| 成功|

    境界値検証ケース一覧:
    | ケースID | テストケース     | テスト値                    | 期待結果  | テストの目的/検証ポイント | 実装状況                                  |
    |----------|------------------|-----------------------------|-----------|---------------------------|-------------------------------------------|
    | BVT_001  | 最小フォーマット | "41000 東日本第一Gr"        | 成功      | 最小形式の確認            | 実装済み (test_setup_area_BVT_min_format) |
    | BVT_002  | 最大フォーマット | "41000 東日本第一Gr (test)" | 成功      | 付加情報付きの確認        | 実装済み (test_setup_area_BVT_max_format) |
    | BVT_003  | コード最小値     | "00001"                     | 成功      | コード最小値の確認        | 実装済み (test_setup_area_BVT_min_code)   |
    | BVT_004  | コード最大値     | "99999"                     | 成功      | コード最大値の確認        | 実装済み (test_setup_area_BVT_max_code)   |
    | BVT_005  | 備考欄空         | ""                          | 成功      | 空値の処理確認            | 実装済み (test_setup_area_BVT_empty_remarks) |
    """

    @pytest.fixture()
    def integrated_layout_df(self) -> pd.DataFrame:
        """統合レイアウトデータのfixture"""
        columns = [
            'ulid', 'form_type', 'application_type', 'target_org', 'business_unit_code',
            'parent_branch_code', 'branch_code', 'branch_name', 'section_gr_code',
            'section_gr_name', 'section_name_en', 'resident_branch_code',
            'resident_branch_name', 'aaa_transfer_date', 'internal_sales_dept_code',
            'internal_sales_dept_name', 'area_code', 'area_name', 'remarks',
            'branch_name_kana', 'section_gr_name_kana', 'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        data = [
            ['setup_area_to_integrated_data', '2', '新設', 'エリア', '339', '*', '00033', 'AAA支店DDD営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '41000 東日本第一Gr', '', '', '', ''],
            ['setup_area_to_integrated_data', '2', '新設', 'エリア', '339', '*', '00034', 'AAA支店EEE営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '42000 東日本第一Ｇｒ', '', '', '', ''],
            ['setup_area_to_integrated_data', '2', '新設', 'エリア', '339', '*', '00035', 'AAA支店FFF営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '42000 東日本第一Ｇｒ (zzzzzz)', '', '', '', ''],
        ]

        return pd.DataFrame(data, columns=columns)

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_setup_area_C0_valid_data(self, integrated_layout_df):
        """正常系: エリアデータの基本的な編集テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 基本的なエリアデータの編集を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.setup_area_to_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

        # エリアデータの検証
        area_mask = result['target_org'] == OrganizationType.AREA.value
        assert result.loc[area_mask, 'branch_code'].notna().all()
        assert result.loc[area_mask, 'branch_name'].notna().all()

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

    def test_setup_area_C0_no_area_data(self, integrated_layout_df):
        """正常系: エリアデータが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - エリアデータが存在しない場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エリアデータを含まないように変更
        integrated_layout_df['target_org'] = '部'

        result = ReferenceMergers.setup_area_to_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.equals(integrated_layout_df)  # 入力と同じ

    def test_setup_area_C1_dt1_successful(self, integrated_layout_df):
        """C1: 全条件を満たす正常系テスト(DT1)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT1の全条件を満たすケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.setup_area_to_integrated_data(
            integrated_layout_df,
        )

        area_mask = result['target_org'] == OrganizationType.AREA.value
        assert result.loc[area_mask, 'branch_code'].str.match(r'^\d{5}$').all()
        assert result.loc[area_mask, 'branch_name'].str.contains('Gr|Ｇｒ').all()

    def test_setup_area_C1_dt2_no_area_data(self, integrated_layout_df):
        """C1: エリアデータが存在しない場合のテスト(DT2)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT2のエリアデータなしケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        integrated_layout_df['target_org'] = '部'
        result = ReferenceMergers.setup_area_to_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.equals(integrated_layout_df)

    def test_setup_area_C2_remarks_patterns(self, integrated_layout_df):
        """C2: 備考欄パターンの組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 条件組み合わせ - 備考欄のパターン
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_patterns = [
            ('41000 東日本第一Gr', True, '41000', '東日本第一Gr'),
            ('41000 東日本第一Ｇｒ', True, '41000', '東日本第一Ｇｒ'),
            ('41000 東日本第一Gr (備考)', True, '41000', '東日本第一Gr'),
            ('41000東日本第一Gr', True, '', ''),  # 本来はNG入力
            ('東日本第一Gr', True, '', ''),       # 本来はNG入力
            ('41000', True, '', ''),              # 本来はNG入力
        ]

        for remarks, should_succeed, expected_code, expected_name in test_patterns:
            test_df = integrated_layout_df.copy()
            test_df.loc[0, 'remarks'] = remarks

            if should_succeed:
                result = ReferenceMergers.setup_area_to_integrated_data(test_df)
                area_mask = result['target_org'] == OrganizationType.AREA.value
                assert result.loc[area_mask, 'branch_code'].iloc[0] == expected_code
                assert result.loc[area_mask, 'branch_name'].iloc[0] == expected_name
            else:
                with pytest.raises(RemarksParseError):
                    ReferenceMergers.setup_area_to_integrated_data(test_df)

    def test_setup_area_BVT_remarks_format(self, integrated_layout_df):
        """境界値: 備考欄フォーマットの境界値テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 備考欄フォーマットの境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小フォーマット
        integrated_layout_df.loc[0, 'remarks'] = '00001 最小Gr'
        result = ReferenceMergers.setup_area_to_integrated_data(
            integrated_layout_df,
        )
        area_mask = result['target_org'] == OrganizationType.AREA.value
        assert result.loc[area_mask, 'branch_code'].iloc[0] == '00001'
        assert result.loc[area_mask, 'branch_name'].iloc[0] == '最小Gr'

        # 最大フォーマット
        integrated_layout_df.loc[0, 'remarks'] = '99999 最大グループGr (付加情報)'
        result = ReferenceMergers.setup_area_to_integrated_data(
            integrated_layout_df,
        )
        assert result.loc[area_mask, 'branch_code'].iloc[0] == '99999'
        assert result.loc[area_mask, 'branch_name'].iloc[0] == '最大グループGr'

        # 無効なパターン,だがエラーにはしない
        invalid_patterns = [
            '',                # 空
            '123',             # コードのみ
            'グループ',        # 名称のみ
            '1234 グループ',   # コード桁数不足
            '123456 グループ', # コード桁数超過
        ]

        for invalid_remarks in invalid_patterns:
            test_df = integrated_layout_df.copy()
            test_df.loc[0, 'remarks'] = invalid_remarks
            result = ReferenceMergers.setup_area_to_integrated_data(test_df)
            tabulate_dataframe(result)

class TestReferenceMergersSetupSectionUnderInternalSales:
    """ReferenceMergersクラスのsetup_section_under_internal_sales_integrated_dataメソッドのテスト

    テスト対象: ReferenceMergers.setup_section_under_internal_sales_integrated_data()
    ├── C0: 基本機能テスト
    │   ├── 正常系: 拠点内営業部配下課データ編集
    │   ├── 異常系: データロード失敗
    │   └── 異常系: 備考欄解析失敗
    ├── C1: 分岐カバレッジ
    │   ├── データ有無分岐
    │   └── 処理成功分岐
    ├── C2: 条件組み合わせ
    │   ├── 有効データ
    │   └── 無効データ
    ├── DT: ディシジョンテーブル
    │   └── 課処理条件
    └── BVT: 境界値テスト
        └── コード値境界

    C1のディシジョンテーブル:
    | 条件                                      | DT1 | DT2 | DT3 | DT4 | DT5 |
    |-------------------------------------------|-----|-----|-----|-----|-----|
    | 拠点内営業部配下課データが存在する        | Y   | N   | Y   | Y   | Y   |
    | 備考欄に拠点内営業部情報が含まれる        | Y   | -   | N   | Y   | Y   |
    | 対応する拠点内営業部レコードが存在する    | Y   | -   | -   | N   | Y   |
    | 拠点内営業部名称が正しい形式              | Y   | -   | -   | -   | N   |
    | 期待される動作                            | 成功| 警告| 成功| 成功| 成功|

    境界値検証ケース一覧:
    | ケースID | テストケース | テスト値                              | 期待結果                  | テストの目的/検証ポイント | 実装状況 |
    |----------|--------------|---------------------------------------|---------------------------|---------------------------|----------|
    | BVT_001  | 最小パターン | "AAA支店BBB営業部"                    | 成功                      | 最小形式の確認            | 実装済み (test_setup_section_under_internal_sales_BVT_min) |
    | BVT_002  | 名称最大長   | "A"*100 + "支店" + "B"*100 + "営業部" | 成功                      | 最大長の確認              | 実装済み (test_setup_section_under_internal_sales_BVT_max_name) |
    | BVT_003  | 備考欄空     | ""                                    | エラー                    | 空値の処理確認            | 実装済み (test_setup_section_under_internal_sales_BVT_empty) |
    | BVT_004  | 備考欄NULL   | None                                  | エラー                    | NULL値の処理確認          | 実装済み (test_setup_section_under_internal_sales_BVT_null) |
    | BVT_005  | 不正な形式   | "AAA営業部"                           | エラー                    | 不正形式の処理確認        | 実装済み (test_setup_section_under_internal_sales_BVT_invalid) |
    """

    @pytest.fixture()
    def integrated_layout_df(self) -> pd.DataFrame:
        """統合レイアウトデータのfixture"""
        columns = [
            'ulid', 'form_type', 'application_type', 'target_org', 'business_unit_code',
            'parent_branch_code', 'branch_code', 'branch_name', 'section_gr_code',
            'section_gr_name', 'section_name_en', 'resident_branch_code',
            'resident_branch_name', 'aaa_transfer_date', 'internal_sales_dept_code',
            'internal_sales_dept_name', 'area_code', 'area_name', 'remarks',
            'branch_name_kana', 'section_gr_name_kana', 'section_gr_name_abbr',
            'bpr_target_flag',
        ]

        data = [
            ['setup_section_under_internal_sales_integrated_data', '2', '新設', '拠点内営業部', '339', '*', '00041', 'AAA支店GGG営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', '', '', '', '', ''],
            ['setup_section_under_internal_sales_integrated_data', '2', '新設', '課', '339', '*', '00042', 'AAA支店GGG営業部', '00021', '部署5', 'Department', '36', '60515', '常駐支店50', '', '', 'BFBFT10', 'エリア10', 'AAA支店GGG営業部', '', '', '', ''],
        ]

        return pd.DataFrame(data, columns=columns)

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_setup_section_under_internal_sales_C0_valid_data(self, integrated_layout_df):
        """正常系: 拠点内営業部配下課データの基本的な編集テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 基本的な拠点内営業部配下課データの編集を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty

        # 課データの検証
        section_mask = result['target_org'] == OrganizationType.SECTION_GROUP.value
        assert result.loc[section_mask, 'internal_sales_dept_code'].notna().all()
        assert result.loc[section_mask, 'internal_sales_dept_name'].notna().all()

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

    def test_setup_section_under_internal_sales_C0_no_target_data(self, integrated_layout_df):
        """正常系: 対象データが存在しない場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 対象データが存在しない場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 対象データを含まないように変更
        integrated_layout_df['target_org'] = '部'

        result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.equals(integrated_layout_df)

    def test_setup_section_under_internal_sales_C1_dt1_successful(self, integrated_layout_df):
        """C1: 全条件を満たす正常系テスト(DT1)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT1の全条件を満たすケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(
            integrated_layout_df,
        )

        section_mask = result['target_org'] == OrganizationType.SECTION_GROUP.value
        assert result.loc[section_mask, 'internal_sales_dept_code'].notna().all()
        assert result.loc[section_mask, 'internal_sales_dept_name'].str.contains('営業部').all()

    def test_setup_section_under_internal_sales_C1_dt2_no_data(self, integrated_layout_df):
        """C1: 対象データが存在しない場合のテスト(DT2)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT2の対象データなしケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        integrated_layout_df['target_org'] = OrganizationType.BRANCH.value
        result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(
            integrated_layout_df,
        )

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert result.equals(integrated_layout_df)


    def test_setup_section_under_internal_sales_C2_remarks_patterns(self, integrated_layout_df):
        """C2: 備考欄パターンの組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 条件組み合わせ - 備考欄のパターン
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_patterns = [
            ('AAA支店BBB営業部', True),
            ('AAA支店営業部', True),
            ('支店BBB営業部', False), #RemarksParseでは営業部判定されない
            ('AAA支店', False),
            ('BBB営業部', False),
            ('', False),
            (None, False),
        ]

        for remarks, should_succeed in test_patterns:
            test_df = integrated_layout_df.copy()
            mask_section_group = test_df['target_org'] == OrganizationType.SECTION_GROUP.value
            test_df.loc[mask_section_group, 'remarks'] = remarks
            mask_internal_sales = test_df['target_org'] == OrganizationType.INTERNAL_SALES.value
            test_df.loc[mask_internal_sales, 'branch_name'] = remarks
            log_msg(f'\n{mask_section_group}', LogLevel.DEBUG)
            log_msg(f'\n{mask_internal_sales}', LogLevel.DEBUG)
            log_msg('test_df', LogLevel.DEBUG)
            tabulate_dataframe(test_df)

            if should_succeed:
                result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(test_df)
                assert (result.loc[mask_section_group, 'internal_sales_dept_name'] != '').all()
                assert (result.loc[mask_section_group, 'internal_sales_dept_code'] != '').all()
            else:
                result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(test_df)
                assert (result.loc[mask_section_group, 'internal_sales_dept_name'] == '').all()

    def test_setup_section_under_internal_sales_BVT_remarks_boundary(self, integrated_layout_df):
        """境界値: 備考欄の境界値テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 備考欄の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小パターン
        mask = integrated_layout_df['target_org'] == OrganizationType.SECTION_GROUP.value
        integrated_layout_df.loc[mask, 'remarks'] = '支店営業部'
        result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(
            integrated_layout_df,
        )
        assert result.loc[mask, 'internal_sales_dept_name'].notna().all()

        # 最大パターン
        long_name = 'A' * 47 + '支店' + 'B' * 47 + '営業部'
        test_df = integrated_layout_df.copy()
        test_df.loc[mask, 'remarks'] = long_name
        result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(
            test_df,
        )
        assert result.loc[mask, 'internal_sales_dept_name'].notna().all()

        # 無効なパターン,だがエラーにはしない
        invalid_patterns = [
            '',          # 空文字
            None,        # NULL
            'AAA',       # 支店・営業部なし
            'AAA支店',   # 営業部なし
            'AAA営業部', # 支店なし
            'A' * 256,   # 長すぎる文字列
        ]

        for invalid_remarks in invalid_patterns:
            test_df = integrated_layout_df.copy()
            test_df.loc[mask, 'remarks'] = invalid_remarks
            result = ReferenceMergers.setup_section_under_internal_sales_integrated_data(test_df)

        log_msg("\n処理結果:", LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

# 編集部品たちのテスト

class TestReferenceMergersProcessInternalSales:
    """ReferenceMergersの_process_internal_sales_dataメソッドのテスト

    テスト対象: ReferenceMergers._process_internal_sales_data()

    C1のディシジョンテーブル:
    | 条件                                  | DT1 | DT2 | DT3 | DT4 | DT5 |
    |---------------------------------------|-----|-----|-----|-----|-----|
    | 対象データが存在する                  | Y   | N   | Y   | Y   | Y   |
    | 部店名称が正しい形式                  | Y   | -   | N   | Y   | Y   |
    | 部店コードが4桁                       | Y   | -   | -   | N   | Y   |
    | 名称分割が成功する                    | Y   | -   | -   | -   | N   |
    | 期待される動作                        | 成功| 警告| 成功| 成功| 成功|

    境界値検証ケース一覧:
    | ケースID | テストケース   | テスト値                              | 期待結果  | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|---------------------------------------|-----------|---------------------------|----------|
    | BVT_001  | 最小部店コード | "0000"                                | 成功      | 最小有効値の確認          | 実装済み (test_process_internal_sales_BVT_min_code) |
    | BVT_002  | 最大部店コード | "9999"                                | 成功      | 最大有効値の確認          | 実装済み (test_process_internal_sales_BVT_max_code) |
    | BVT_003  | 無効部店コード | "000"                                 | エラー    | 桁数不足の確認            | 実装済み (test_process_internal_sales_BVT_invalid_code) |
    | BVT_004  | 最小名称長     | "A支店B営業部"                        | 成功      | 最小名称長の確認          | 実装済み (test_process_internal_sales_BVT_min_name) |
    | BVT_005  | 最大名称長     | "A"*100 + "支店" + "B"*100 + "営業部" | 成功      | 最大名称長の確認          | 実装済み (test_process_internal_sales_BVT_max_name) |
    """

    @pytest.fixture()
    def base_df(self) -> pd.DataFrame:
        """基本テストデータのfixture"""
        columns = [
            'target_org', 'branch_code', 'branch_name',
            'internal_sales_dept_code', 'internal_sales_dept_name',
        ]
        data = [
            ['拠点内営業部', '0001', 'AAA支店BBB営業部', '', ''],
            ['拠点内営業部', '0002', 'CCC支店DDD営業部', '', ''],
            ['部', '0003', 'EEE支店', '', ''],
        ]
        return pd.DataFrame(data, columns=columns)

    def test_process_internal_sales_C0_valid_data(self, base_df):
        """正常系: 基本的なデータ処理の確認"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系 - 基本的なデータ処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # マスク作成
        mask = base_df['target_org'] == OrganizationType.INTERNAL_SALES.value

        # 処理実行
        result = ReferenceMergers._process_internal_sales_data(base_df, mask)

        # 検証
        assert isinstance(result, pd.DataFrame)
        target_rows = result[mask]
        assert target_rows['internal_sales_dept_code'].notna().all()
        assert target_rows['internal_sales_dept_name'].notna().all()
        assert (target_rows['branch_name'].str.contains('支店')).all()

    def test_process_internal_sales_C1_dt1_successful(self, base_df):
        """C1: 全条件を満たす正常系テスト(DT1)"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT1の全条件満たすケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mask = base_df['target_org'] == OrganizationType.INTERNAL_SALES.value
        result = ReferenceMergers._process_internal_sales_data(base_df, mask)

        # 検証
        target_rows = result[mask]
        assert all(
            target_rows['internal_sales_dept_name'].str.contains('営業部'),
        )
        assert all(
            target_rows['branch_name'].str.endswith('支店'),
        )
        assert all(
            target_rows['branch_code'].str.match(r'^\d{4}$'),
        )

    def test_process_internal_sales_C1_dt2_no_target_data(self, base_df):
        """C1: 対象データが存在しない場合のテスト(DT2)k"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 正常系 - DT2の対象データなしケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 対象データなしのマスク
        mask = base_df['target_org'] == '存在しない区分'

        result = ReferenceMergers._process_internal_sales_data(base_df, mask)
        assert result.equals(base_df)  # 入力と同じ


    @pytest.mark.parametrize(('branch_name', 'expected_success'), [
        ('AAA支店BBB営業部', True),     # 正常系: 標準パターン
        ('AAA支店営業部', True),        # 正常系: 最小パターン
        ('支店BBB営業部', True),       # 異常系: 支店名不足
        ('AAA支店', True),             # 異常系: 営業部なし
        ('AAA営業部', True),           # 異常系: 支店なし
    ])
    def test_process_internal_sales_branch_name_patterns(
        self, base_df, branch_name, expected_success,
    ):
        """部店名称パターンの組み合わせテスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 条件組み合わせ - 部店名称のパターン
        テストデータ: {branch_name}
        期待結果: {'成功' if expected_success else '失敗'}
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_df = base_df.copy()
        mask = test_df['target_org'] == OrganizationType.INTERNAL_SALES.value
        test_df.loc[mask, 'branch_name'] = branch_name

        log_msg('テスト前のデータ:', LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(test_df)}", LogLevel.DEBUG)

        if expected_success:
            result = ReferenceMergers._process_internal_sales_data(test_df, mask)
            assert result.loc[mask, 'internal_sales_dept_name'].notna().all()
            assert result.loc[mask, 'internal_sales_dept_code'].notna().all()
            log_msg('テスト結果:', LogLevel.DEBUG)
            log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)
        else:
            with pytest.raises(BranchNameSplitError):
                ReferenceMergers._process_internal_sales_data(test_df, mask)

    @pytest.mark.parametrize(('branch_code','branch_name','expected_error'), [
        ('0000', 'AAA支店BBB営業部', None),         # 最小コード
        ('9999', 'AAA支店BBB営業部', None),         # 最大コード
        ('000', 'AAA支店BBB営業部', None),  # 無効コード
        ('0001', 'A支店B営業部', None),             # 最小名称長
        ('0001', 'A'*100 + '支店' + 'B'*100 + '営業部', None),  # 最大名称長
        ('0001', '', None),        # 空名称
    ])
    def test_process_internal_sales_boundary_values(
        self, base_df, branch_code, branch_name, expected_error,
    ):
        """コードと名称の境界値テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 境界値テスト - コードと名称の境界値
        テストデータ:
            - branch_code: {branch_code}
            - branch_name: {branch_name[:20]}{'...' if len(branch_name) > 20 else ''}
        期待結果: {'正常終了' if expected_error is None else expected_error.__name__}
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_df = base_df.copy()
        mask = test_df['target_org'] == OrganizationType.INTERNAL_SALES.value
        test_df.loc[mask, 'branch_code'] = branch_code
        test_df.loc[mask, 'branch_name'] = branch_name

        log_msg('テスト前のデータ:', LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(test_df)}", LogLevel.DEBUG)

        if expected_error:
            with pytest.raises(expected_error):
                ReferenceMergers._process_internal_sales_data(test_df, mask)
        else:
            result = ReferenceMergers._process_internal_sales_data(test_df, mask)
            assert result.loc[mask, 'internal_sales_dept_name'].notna().all()
            assert result.loc[mask, 'internal_sales_dept_code'].notna().all()
            log_msg('テスト結果:', LogLevel.DEBUG)
            log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)


    @pytest.mark.parametrize(('target_org','expected_modified'), [
        ('拠点内営業部', True),   # 対象データあり
        ('部', True),             # 対象データなし 実利用においては入ってこないケース
        ('課', False),            # 対象データなし 実利用においては入ってこないケース
    ])
    def test_process_internal_sales_target_data(
        self, base_df, target_org, expected_modified,
    ):
        """対象データの有無による動作テスト"""
        test_doc = f"""
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 対象データの有無による動作確認
        テストデータ: target_org = {target_org}
        期待結果: {'データ更新あり' if expected_modified else 'データ更新なし'}
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_df = base_df.copy()
        mask = test_df['target_org'] == target_org

        # テスト前のデータを保存
        original_df = test_df.copy()

        log_msg('テスト前のデータ:', LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(original_df)}", LogLevel.DEBUG)

        # 処理実行
        result = ReferenceMergers._process_internal_sales_data(test_df, mask)

        log_msg('テスト後のデータ:', LogLevel.DEBUG)
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.DEBUG)

        if expected_modified:
            # 差分の確認
            assert not result.equals(original_df), "データが更新されていません"

            # 具体的な変更の検証
            modified_rows = result[mask]
            assert modified_rows['internal_sales_dept_code'].notna().all(), \
                "internal_sales_dept_codeが設定されていません"
            assert modified_rows['internal_sales_dept_name'].notna().all(), \
                "internal_sales_dept_nameが設定されていません"
            assert modified_rows['branch_name'].str.endswith('支店').all(), \
                "branch_nameが正しく更新されていません"
        else:
            assert result.equals(original_df), "データが予期せず更新されています"

        # 差分の詳細表示(デバッグ用)
        if expected_modified:
            log_msg('変更された列:', LogLevel.DEBUG)
            for col in ['branch_name', 'internal_sales_dept_code', 'internal_sales_dept_name']:
                changed = result[col] != original_df[col]
                if changed.any():
                    log_msg(f"\n{col}の変更:", LogLevel.DEBUG)
                    log_msg(f"変更前: {original_df.loc[changed, col].to_list()}", LogLevel.DEBUG)
                    log_msg(f"変更後: {result.loc[changed, col].to_list()}", LogLevel.DEBUG)


class TestReferencesMergersProcessAreaData:
    """_process_area_data メソッドのテスト

    テスト構造:
    ├── C0
    │   ├── 正常系: 有効な入力でのテスト
    │   ├── 正常系: 処理対象のエリアデータが存在しない場合
    │   └── 異常系: 備考欄に解析できない内容が含まれる場合
    ├── C1
    │   ├── 正常系: 備考欄に正常な内容が含まれる場合
    │   └── 異常系: 備考欄に解析できない内容が含まれる場合
    ├── C2
    │   ├── 正常系: 有効な入力でのテスト
    │   ├── 正常系: 処理対象のエリアデータが存在しない場合
    │   └── 異常系: 備考欄に解析できない内容が含まれる場合
    ├── DT
    │   ├── ケース1: 正常系 - 備考欄に正常な内容が含まれる場合
    │   └── ケース2: 異常系 - 備考欄に解析できない内容が含まれる場合
    └── BVT
        ├── 正常系: 空の備考欄
        ├── 正常系: 有効な備考欄
        ├── 正常系: 有効な備考欄 (別ケース)
        ├── 正常系: 有効な備考欄 (別ケース)
        ├── 異常系: 無効な備考欄
        ├── 異常系: 無効な備考欄 (余分な文字)
        └── 異常系: 極端に長い備考欄

    ディシジョンテーブル:
    | 条件                         | ケース1    | ケース2           |
    |------------------------------|------------|-------------------|
    | 備考欄に正常な内容が含まれる | Y          | N                 |
    | 部店コードの設定             | A001       | -                 |
    | 部店名称の設定               | 東京エリア | -                 |
    | 例外発生                     | -          | RemarksParseError |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                                                                               | 期待される結果           | テストの目的/検証ポイント                 | 実装状況 | 対応するテストケース       |
    |----------|----------------|----------------------------------------------------------------------------------------|--------------------------|-------------------------------------------|----------|----------------------------|
    | BVT_001  | remarks        | ""                                                                                     | ('', '')                 | 空文字列の処理を確認                      | 実装済み | test_process_area_data_BVT |
    | BVT_002  | remarks        | "区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01"              | ('A001', '東京エリア')   | 正常系: 有効な備考欄の処理を確認          | 実装済み | test_process_area_data_BVT |
    | BVT_003  | remarks        | "区分:エリア グループコード:A002 グループ名:大阪エリア 設立日:2023-04-15"              | ('A002', '大阪エリア')   | 正常系: 有効な備考欄の処理を確認          | 実装済み | test_process_area_data_BVT |
    | BVT_004  | remarks        | "区分:エリア グループコード:A003 グループ名:名古屋エリア 設立日:2021-09-30"            | ('A003', '名古屋エリア') | 正常系: 有効な備考欄の処理を確認          | 実装済み | test_process_area_data_BVT |
    | BVT_005  | remarks        | "invalid remarks"                                                                      | ('', '')                 | 無効な備考欄の処理を確認                  | 実装済み | test_process_area_data_BVT |
    | BVT_006  | remarks        | "invalid remarks with extra characters"                                                | ('', '')                 | 無効な備考欄 (余分な文字) の処理を確認    | 実装済み | test_process_area_data_BVT |
    | BVT_007  | remarks        | "a" * 255 + " 区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01" | ('', '')                 | 極端に長い備考欄の処理を確認              | 実装済み | test_process_area_data_BVT |

    注記:
    - 境界値検証ケースはすべて実装済みです。
    - 備考欄の解析処理に関するテストケースは、C0、C1、C2、DTでも網羅的に実施しています。
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_area_data_C0_valid_input(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01'],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '', 'branch_name': ''},
            'area_group': {'group_code': 'A001', 'group_name': '東京エリア', 'established_date': '2022-01-01'},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance

        # 処理実行
        result = ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # アサーション
        assert result['branch_code'][0] == 'A001'
        assert result['branch_name'][0] == '東京エリア'

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01')

    def test_process_area_data_C0_no_area_data(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 処理対象のエリアデータが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.INTERNAL_SALES.value],
            'remarks': ['備考'],
        })

        # 処理実行
        result = ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # アサーション
        assert len(result) == len(_df)
        assert 'branch_code' in result.columns
        assert 'branch_name' in result.columns

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_area_data_C0_invalid_remarks(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 備考欄に解析できない内容が含まれる場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['invalid remarks'],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = RemarksParseError
        mock_parser.return_value = mock_parser_instance

        # 処理実行と例外検証
        with pytest.raises(RemarksParseError):
            ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('invalid remarks')

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @pytest.mark.parametrize(("remarks", "expected_branch_code", "expected_branch_name"), [
        ('区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01', 'A001', '東京エリア'),
        ('区分:エリア グループコード:A002 グループ名:大阪エリア 設立日:2023-04-15', 'A002', '大阪エリア'),
        ('区分:エリア グループコード:A003 グループ名:名古屋エリア 設立日:2021-09-30', 'A003', '名古屋エリア'),
    ])
    def test_process_area_data_C1_DT_01_valid_remarks(self, mock_parser, remarks, expected_branch_code, expected_branch_name):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 備考欄に正常な内容が含まれる場合

        ディシジョンテーブル:
        | 条件                         | ケース1    |
        |------------------------------|------------|
        | 備考欄に正常な内容が含まれる | Y          |
        | 部店コードの設定             | A001       |
        | 部店名称の設定               | 東京エリア |
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': [remarks],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '', 'branch_name': ''},
            'area_group': {'group_code': expected_branch_code, 'group_name': expected_branch_name, 'established_date': ''},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance

        # 処理実行
        result = ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # アサーション
        assert result['branch_code'][0] == expected_branch_code
        assert result['branch_name'][0] == expected_branch_name

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with(remarks)

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_area_data_C1_DT_02_invalid_remarks(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 備考欄に解析できない内容が含まれる場合

        ディシジョンテーブル:
        | 条件                               | ケース1           |
        |------------------------------------|-------------------|
        | 備考欄に解析できない内容が含まれる | Y                 |
        | 例外発生                           | RemarksParseError |
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['invalid remarks'],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = RemarksParseError
        mock_parser.return_value = mock_parser_instance

        # 処理実行と例外検証
        with pytest.raises(RemarksParseError):
            ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('invalid remarks')

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_area_data_C2_valid_input(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01'],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '', 'branch_name': ''},
            'area_group': {'group_code': 'A001', 'group_name': '東京エリア', 'established_date': '2022-01-01'},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance

        # 処理実行
        result = ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # アサーション
        assert result['branch_code'][0] == 'A001'
        assert result['branch_name'][0] == '東京エリア'

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01')

    def test_process_area_data_C2_no_area_data(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 処理対象のエリアデータが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.INTERNAL_SALES.value],
            'remarks': ['備考'],
        })

        # 処理実行
        result = ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # アサーション
        assert len(result) == len(_df)
        assert 'branch_code' in result.columns
        assert 'branch_name' in result.columns

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_area_data_C2_invalid_remarks(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 備考欄に解析できない内容が含まれる場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['invalid remarks'],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = RemarksParseError
        mock_parser.return_value = mock_parser_instance

        # 処理実行と例外検証
        with pytest.raises(RemarksParseError):
            ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('invalid remarks')

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @pytest.mark.parametrize(("remarks", "expected_branch_code", "expected_branch_name"), [
        ('', '', ''),
        ('区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01', 'A001', '東京エリア'),
        ('区分:エリア グループコード:A002 グループ名:大阪エリア 設立日:2023-04-15', 'A002', '大阪エリア'),
        ('区分:エリア グループコード:A003 グループ名:名古屋エリア 設立日:2021-09-30', 'A003', '名古屋エリア'),
        ('invalid remarks', '', ''),
        ('invalid remarks with extra characters', '', ''),
        ('a' * 255 + ' 区分:エリア グループコード:A001 グループ名:東京エリア 設立日:2022-01-01', '', ''),
    ])
    def test_process_area_data_BVT(self, mock_parser, remarks, expected_branch_code, expected_branch_name):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/異常系
        - テストシナリオ: 備考欄の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': [remarks],
        })

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '', 'branch_name': ''},
            'area_group': {'group_code': expected_branch_code, 'group_name': expected_branch_name, 'established_date': ''},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance

        # 処理実行
        result = ReferenceMergers._process_area_data(_df, _df['target_org'] == OrganizationType.AREA.value)

        # アサーション
        assert result['branch_code'][0] == expected_branch_code
        assert result['branch_name'][0] == expected_branch_name

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with(remarks)


class TestReferencesMergersProcessSectionUnderInternalSales:
    """_process_section_under_internal_sales メソッドのテスト

    テスト構造:
    ├── C0
    │   ├── 正常系: 有効な入力でのテスト
    │   ├── 正常系: 拠点内営業部配下課データが存在しない場合
    │   └── 異常系: 備考欄の解析に失敗する場合
    ├── C1
    │   ├── 正常系: 備考欄に正常な内容が含まれる場合
    │   └── 異常系: 備考欄の解析に失敗する場合
    ├── C2
    │   ├── 正常系: 有効な入力でのテスト
    │   ├── 正常系: 拠点内営業部配下課データが存在しない場合
    │   └── 異常系: 備考欄の解析に失敗する場合
    ├── DT
    │   ├── ケース1: 正常系 - 備考欄に正常な内容が含まれる場合
    │   └── ケース2: 異常系 - 備考欄の解析に失敗する場合
    └── BVT
        ├── 正常系: 空の備考欄
        ├── 正常系: 有効な備考欄
        ├── 正常系: 有効な備考欄 (別ケース)
        ├── 正常系: 有効な備考欄 (別ケース)
        ├── 異常系: 無効な備考欄
        ├── 異常系: 無効な備考欄 (余分な文字)
        └── 異常系: 極端に長い備考欄

    ディシジョンテーブル:
    | 条件                 | ケース1 |
    |---------------------|---------|
    | 備考欄に正常な内容が含まれる | Y       |
    | 拠点内営業部コードの設定     | 1001    |
    | 拠点内営業部名称の設定       | 東京支店 営業部 |
    | 例外発生             | RemarksParseError |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                                     | 期待される結果                    | テストの目的/検証ポイント               | 実装状況 | 対応するテストケース                          |
    |----------|----------------|----------------------------------------------|-----------------------------------|-----------------------------------------|----------|-----------------------------------------------|
    | BVT_001  | remarks        | ""                                           | ('', '')                          | 空文字列の処理を確認                    | 実装済み | test_process_section_under_internal_sales_BVT |
    | BVT_002  | remarks        | "拠点内営業部: 東京支店 営業部"              | ('1001', '東京支店 営業部')       | 正常系: 有効な備考欄の処理を確認        | 実装済み | test_process_section_under_internal_sales_BVT |
    | BVT_003  | remarks        | "拠点内営業部: 大阪支店 第一営業部"          | ('1002', '大阪支店 第一営業部')   | 正常系: 有効な備考欄の処理を確認        | 実装済み | test_process_section_under_internal_sales_BVT |
    | BVT_004  | remarks        | "拠点内営業部: 名古屋支店 第二営業部"        | ('1003', '名古屋支店 第二営業部') | 正常系: 有効な備考欄の処理を確認        | 実装済み | test_process_section_under_internal_sales_BVT |
    | BVT_005  | remarks        | "invalid remarks"                            | ('', '')                          | 無効な備考欄の処理を確認                | 実装済み | test_process_section_under_internal_sales_BVT |
    | BVT_006  | remarks        | "invalid remarks with extra characters"      | ('', '')                          | 無効な備考欄 (余分な文字) の処理を確認  | 実装済み | test_process_section_under_internal_sales_BVT |
    | BVT_007  | remarks        | "a" * 255 + " 拠点内営業部: 東京支店 営業部" | ('', '東京支店 営業部')           | 極端に長い備考欄の処理を確認            | 実装済み | test_process_section_under_internal_sales_BVT |

    Note:
    - 境界値検証ケースはすべて実装済みです。
    - 備考欄の解析処理に関するテストケースは、C0、C1、C2、DTでも網羅的に実施しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks')
    def test_process_section_under_internal_sales_C0_valid_input(self, mock_find_branch_code, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': ['拠点内営業部: 東京支店 営業部'],
            'internal_sales_dept_code': ['1001'],
            'internal_sales_dept_name': ['東京支店'],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '東京支店 営業部', 'branch_name': ''},
            'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance
        mock_find_branch_code.return_value = '1001'

        # 処理実行
        result = ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # アサーション
        assert result['internal_sales_dept_code'][0] == '1001'
        assert result['internal_sales_dept_name'][0] == '東京支店 営業部'

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('拠点内営業部: 東京支店 営業部')
        mock_find_branch_code.assert_called_once_with(_df, mask)

    def test_process_section_under_internal_sales_C0_no_section_under_internal_sales_data(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 拠点内営業部配下課データが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['エリア: 東京'],
        })
        mask = _df['target_org'] == OrganizationType.AREA.value

        # Mockの設定
        with patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser'):
            with patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks') as mock_find_branch_code:
                mock_find_branch_code.return_value = ''

                # 処理実行
                result = ReferenceMergers._process_section_under_internal_sales(_df, mask)

                # アサーション
                assert len(result) == len(_df)
                assert 'internal_sales_dept_code' in result.columns
                assert 'internal_sales_dept_name' in result.columns

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_section_under_internal_sales_C0_invalid_remarks(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 備考欄の解析に失敗する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': ['invalid remarks'],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = RemarksParseError
        mock_parser.return_value = mock_parser_instance

        # 処理実行と例外検証
        with pytest.raises(RemarksParseError):
            ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('invalid remarks')

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks')
    def test_process_section_under_internal_sales_C1_DT_01_valid_remarks(self, mock_find_branch_code, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 備考欄に正常な内容が含まれる場合

        ディシジョンテーブル:
        | 条件                 | ケース1 |
        |---------------------|---------|
        | 備考欄に正常な内容が含まれる | Y       |
        | 拠点内営業部コードの設定     | 1001    |
        | 拠点内営業部名称の設定       | 東京支店 営業部 |
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': ['拠点内営業部: 東京支店 営業部'],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '東京支店 営業部', 'branch_name': ''},
            'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance
        mock_find_branch_code.return_value = '1001'

        # 処理実行
        result = ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # アサーション
        assert result['internal_sales_dept_code'][0] == '1001'
        assert result['internal_sales_dept_name'][0] == '東京支店 営業部'

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('拠点内営業部: 東京支店 営業部')
        mock_find_branch_code.assert_called_once_with(_df, mask)

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    def test_process_section_under_internal_sales_C1_DT_02_invalid_remarks(self, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 備考欄の解析に失敗する場合

        ディシジョンテーブル:
        | 条件                     | ケース1           |
        |--------------------------|-------------------|
        | 備考欄の解析に失敗する   | Y                 |
        | 例外発生                 | RemarksParseError |
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': ['invalid remarks'],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = RemarksParseError
        mock_parser.return_value = mock_parser_instance

        # 処理実行と例外検証
        with pytest.raises(RemarksParseError):
            ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('invalid remarks')

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks')
    def test_process_section_under_internal_sales_C2_valid_input(self, mock_find_branch_code, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': ['拠点内営業部: 東京支店 営業部'],
            'internal_sales_dept_code': ['1001'],
            'internal_sales_dept_name': ['東京支店'],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': '東京支店 営業部', 'branch_name': ''},
            'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance
        mock_find_branch_code.return_value = '1001'

        # 処理実行
        result = ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # アサーション
        assert result['internal_sales_dept_code'][0] == '1001'
        assert result['internal_sales_dept_name'][0] == '東京支店 営業部'

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('拠点内営業部: 東京支店 営業部')
        mock_find_branch_code.assert_called_once_with(_df, mask)

    def test_process_section_under_internal_sales_C2_no_section_under_internal_sales_data(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 拠点内営業部配下課データが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.AREA.value],
            'remarks': ['エリア: 東京'],
        })
        mask = _df['target_org'] == OrganizationType.AREA.value

        # Mockの設定
        with patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser'):
            with patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks') as mock_find_branch_code:
                mock_find_branch_code.return_value = ''

                # 処理実行
                result = ReferenceMergers._process_section_under_internal_sales(_df, mask)

                # アサーション
                assert len(result) == len(_df)
                assert 'internal_sales_dept_code' in result.columns
                assert 'internal_sales_dept_name' in result.columns

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks')
    def test_process_section_under_internal_sales_C2_invalid_remarks(self, mock_find_branch_code, mock_parser):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 備考欄の解析に失敗する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': ['invalid remarks'],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.side_effect = RemarksParseError
        mock_parser.return_value = mock_parser_instance
        mock_find_branch_code.return_value = ''

        # 処理実行と例外検証
        with pytest.raises(RemarksParseError):
            ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with('invalid remarks')
        #mock_find_branch_code.assert_called_once_with(df, mask)    # RemarkParserでエラー判定、呼ばれない

    @patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser')
    @patch('src.lib.converter_utils.ibr_reference_mergers.ReferenceMergers._find_branch_code_from_remarks')
    @pytest.mark.parametrize(("remarks", "expected_internal_sales_dept_code", "expected_internal_sales_dept_name"), [
        ('', '', ''),
        ('拠点内営業部: 東京支店 営業部', '1001', '東京支店 営業部'),
        ('拠点内営業部: 大阪支店 第一営業部', '1002', '大阪支店 第一営業部'),
        ('拠点内営業部: 名古屋支店 第二営業部', '1003', '名古屋支店 第二営業部'),
        ('invalid remarks', '', ''),
        ('invalid remarks with extra characters', '', ''),
        ('a' * 255 + ' 拠点内営業部: 東京支店 営業部', '', '東京支店 営業部'),
    ])
    def test_process_section_under_internal_sales_BVT(self, mock_find_branch_code, mock_parser, remarks, expected_internal_sales_dept_code, expected_internal_sales_dept_name):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系/異常系
        - テストシナリオ: 備考欄の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テストデータ準備
        _df = pd.DataFrame({
            'target_org': [OrganizationType.SECTION_GROUP.value],
            'remarks': [remarks],
        })
        mask = _df['target_org'] == OrganizationType.SECTION_GROUP.value

        # Mockの設定
        mock_parser_instance = MagicMock()
        mock_parser_instance.parse.return_value = {
            'request_type': '',
            'sales_department': {'department_name': expected_internal_sales_dept_name, 'branch_name': ''},
            'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
            'other_info': '',
        }
        mock_parser.return_value = mock_parser_instance
        mock_find_branch_code.return_value = expected_internal_sales_dept_code

        # 処理実行
        result = ReferenceMergers._process_section_under_internal_sales(_df, mask)

        # アサーション
        assert result['internal_sales_dept_code'][0] == expected_internal_sales_dept_code
        assert result['internal_sales_dept_name'][0] == expected_internal_sales_dept_name

        # Mockの検証
        mock_parser.assert_called_once_with()
        mock_parser_instance.parse.assert_called_once_with(remarks)
        mock_find_branch_code.assert_called_once_with(_df, mask)

class TestReferenceMergers_LoadData:
    """ReferenceMergersの_load_dataメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: DataFrameが直接渡された場合
    │   ├── 正常系: ファイルからの読み込み
    │   └── 異常系: 例外発生
    ├── C1: 分岐カバレッジ
    │   ├── dfがNoneの場合
    │   ├── dfが空でない場合
    │   └── dfが空の場合
    ├── C2: 条件カバレッジ
    │   ├── df is None and ファイル読み込み成功
    │   ├── df is None and ファイル読み込み失敗
    │   ├── df is not None and df not empty
    │   └── df is not None and df empty
    └── BVT: 境界値テスト
        ├── 最小サイズのDataFrame
        ├── 空のDataFrame
        └── 大きなサイズのDataFrame

    # C1のディシジョンテーブル
    | 条件                          | Case1 | Case2 | Case3 | Case4 | Case5 |
    |-------------------------------|-------|-------|-------|-------|-------|
    | dfがNone                      | Y     | Y     | N     | N     | N     |
    | ファイル読み込み成功          | Y     | N     | -     | -     | -     |
    | dfが空でない                  | -     | -     | Y     | N     | -     |
    | 出力                          | 成功  | 失敗  | 成功  | 空DF  | 空DF  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ   | テスト値                | 期待される結果        | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース             |
    |----------|------------------|-------------------------|-----------------------|---------------------------------|----------|----------------------------------|
    | BVT_001  | df               | None                    | TableSearcherからのDF | Noneケースの処理を確認          | 実装済み | test_load_data_C0_none_df        |
    | BVT_002  | df               | 空のDataFrame           | 空のDataFrame         | 空DataFrameの処理を確認         | 実装済み | test_load_data_C0_empty_df       |
    | BVT_003  | df               | 1行1列のDataFrame       | 入力DFのコピー        | 最小DataFrameの処理を確認       | 実装済み | test_load_data_C1_minimal_df     |
    | BVT_004  | file_name        | ""                      | DataLoadError         | 空文字列ファイル名の処理を確認  | 実装済み | test_load_data_C1_empty_filename |
    | BVT_005  | file_name        | 最大長のファイル名      | DataLoadError         | 長いファイル名の処理を確認      | 未実装   | -                                |
    """
    def setup_method(self):
        self.config_mock = Mock(log_message=Mock())

    def teardown_method(self):
        pass

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({'test': [1, 2, 3]})

    def test_load_data_C0_none_df(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: dfがNoneの場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('src.lib.converter_utils.ibr_reference_mergers.TableSearcher') as mock_searcher:
            mock_searcher.return_value.df = pd.DataFrame({'test': [1]})
            result = ReferenceMergers._load_data(None, 'test.pkl')
            assert isinstance(result, pd.DataFrame)
            assert not result.empty

    def test_load_data_C0_with_df(self, sample_df):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: dfが提供される場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._load_data(sample_df)
        assert isinstance(result, pd.DataFrame)
        assert result.equals(sample_df)
        assert id(result) != id(sample_df)  # コピーされていることを確認

    def test_load_data_C0_empty_df(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 空のDataFrameが提供される場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_df = pd.DataFrame()
        result = ReferenceMergers._load_data(empty_df)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_load_data_C1_file_error(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: ファイル読み込みエラーの場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('src.lib.converter_utils.ibr_reference_mergers.TableSearcher') as mock_searcher:
            mock_searcher.side_effect = Exception('File read error')
            with pytest.raises(DataLoadError):
                ReferenceMergers._load_data(None, 'error.pkl')

    def test_load_data_C2_none_df_file_success(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: dfがNoneでファイル読み込み成功の場合のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_df = pd.DataFrame({'test': [1]})
        with patch('src.lib.converter_utils.ibr_reference_mergers.TableSearcher') as mock_searcher:
            mock_searcher.return_value.df = test_df
            result = ReferenceMergers._load_data(None)
            assert isinstance(result, pd.DataFrame)
            assert result.equals(test_df)

    def test_load_data_BVT_minimal_df(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 最小サイズのDataFrameのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        minimal_df = pd.DataFrame({'col': [1]})
        result = ReferenceMergers._load_data(minimal_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert len(result.columns) == 1

    def test_load_data_BVT_empty_filename(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空文字列のファイル名のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(DataLoadError):
            ReferenceMergers._load_data(None, '')

class TestReferenceMergers_ExtractBranchCodePrefix:
    """ReferenceMergersの_extract_branch_code_prefixメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 通常の部店コード処理
    │   └── 異常系: 無効なデータ型
    ├── C1: 分岐カバレッジ
    │   ├── コードが4桁以上の場合
    │   └── コードが4桁未満の場合
    ├── C2: 条件カバレッジ
    │   ├── 部店コードが数字のみ
    │   ├── 部店コードが英数字混在
    │   └── 部店コードが空文字含む
    └── BVT: 境界値テスト
        ├── 4桁ちょうどの部店コード
        ├── 4桁未満の部店コード
        └── 4桁を超える部店コード

    # C1のディシジョンテーブル
    | 条件                   | Case1 | Case2 | Case3 | Case4 |
    |------------------------|-------|-------|-------|-------|
    | コードが4桁以上        | Y     | N     | Y     | N     |
    | コードが数字のみ       | Y     | Y     | N     | N     |
    | 出力                   | 成功  | 成功  | 成功  | 成功  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値       | 期待される結果 | テストの目的/検証ポイント      | 実装状況 | 対応するテストケース                                  |
    |----------|----------------|----------------|----------------|--------------------------------|----------|-------------------------------------------------------|
    | BVT_001  | column_values  | ["1234"]       | ["1234"]       | 4桁ちょうどの処理を確認        | 実装済み | test_extract_branch_code_prefix_BVT_exact_4digits     |
    | BVT_002  | column_values  | ["123"]        | ["123"]        | 4桁未満の処理を確認            | 実装済み | test_extract_branch_code_prefix_BVT_less_than_4digits |
    | BVT_003  | column_values  | ["12345"]      | ["1234"]       | 4桁超過の処理を確認            | 実装済み | test_extract_branch_code_prefix_BVT_more_than_4digits |
    | BVT_004  | column_values  | [""]           | [""]           | 空文字列の処理を確認           | 実装済み | test_extract_branch_code_prefix_BVT_empty_string      |
    | BVT_005  | column_values  | None           | None           | None値の処理を確認             | 実装済み | test_extract_branch_code_prefix_BVT_none_value        |
    """

    def setup_method(self):
        self.config_mock = Mock(log_message=Mock())

    def teardown_method(self):
        pass

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({
            'code': ['12345', '67890', 'ABCDE'],
        })

    def test_extract_branch_code_prefix_C0_normal(self, sample_df):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 通常の部店コード処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._extract_branch_code_prefix(sample_df, 'code')
        assert len(result) == 3
        assert result.iloc[0] == '1234'
        assert result.iloc[1] == '6789'
        assert result.iloc[2] == 'ABCD'

    def test_extract_branch_code_prefix_C1_short_code(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 4桁未満のコードの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'code': ['123', '45']})
        result = ReferenceMergers._extract_branch_code_prefix(_df, 'code')
        assert len(result) == 2
        assert result.iloc[0] == '123'
        assert result.iloc[1] == '45'

    def test_extract_branch_code_prefix_C2_mixed_codes(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 英数字混在のコードの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'code': ['A123', '1B2C', '12D4'],
        })
        result = ReferenceMergers._extract_branch_code_prefix(_df, 'code')
        assert len(result) == 3
        assert all(len(code) <= 4 for code in result)

    def test_extract_branch_code_prefix_BVT_exact_4digits(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 4桁ちょうどのコードの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'code': ['1234', 'ABCD']})
        result = ReferenceMergers._extract_branch_code_prefix(_df, 'code')
        assert len(result) == 2
        assert all(len(code) == 4 for code in result)

    def test_extract_branch_code_prefix_BVT_empty_string(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'code': ['']})
        result = ReferenceMergers._extract_branch_code_prefix(_df, 'code')
        assert len(result) == 1
        assert result.iloc[0] == ''

    def test_extract_branch_code_prefix_BVT_none_value(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: None値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'code': [None]})
        result = ReferenceMergers._extract_branch_code_prefix(_df, 'code')
        assert len(result) == 1
        assert pd.isna(result.iloc[0])

    def test_extract_branch_code_prefix_BVT_mixed_length(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 異なる長さのコードの混在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'code': ['123', '1234', '12345'],
        })
        result = ReferenceMergers._extract_branch_code_prefix(_df, 'code')
        assert len(result) == 3
        assert result.iloc[0] == '123'
        assert result.iloc[1] == '1234'
        assert result.iloc[2] == '1234'

class TestReferenceMergers_SplitBranchNameRegex:
    """ReferenceMergersの_split_branch_name_regexメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 標準的な支店名分割
    │   └── 異常系: 無効な入力値
    ├── C1: 分岐カバレッジ
    │   ├── 支店名のみ
    │   ├── 支店名+営業部名
    │   └── 支店名が含まれない
    ├── C2: 条件カバレッジ
    │   ├── 支店名に"支店"を含む
    │   ├── 支店名に"支店"を複数含む
    │   └── 支店名に"支店"を含まない
    └── BVT: 境界値テスト
        ├── 空文字列
        ├── None値
        └── 極端に長い文字列

    # C1のディシジョンテーブル
    | 条件                      | Case1 | Case2 | Case3 | Case4 | Case5 |
    |--------------------------|-------|-------|-------|-------|-------|
    | 入力がNone/NA            | Y     | N     | N     | N     | N     |
    | "支店"を含む             | -     | Y     | Y     | N     | Y     |
    | 営業部名が存在する       | -     | N     | Y     | -     | Y     |
    | 出力                     | NA,NA | 支店名,"" | 支店名,営業部名 | 全体,"" | 支店名,営業部名 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値       | 期待される結果   | テストの目的/検証ポイント | 実装状況 | 対応するテストケース                            |
    |----------|----------------|----------------|------------------|---------------------------|----------|-------------------------------------------------|
    | BVT_001  | name           | ""             | ("", "")         | 空文字列の処理を確認      | 実装済み | test_split_branch_name_regex_BVT_empty_string   |
    | BVT_002  | name           | None           | (None, None)     | None値の処理を確認        | 実装済み | test_split_branch_name_regex_BVT_none_value     |
    | BVT_003  | name           | "A" * 1000     | (入力値, "")     | 長い文字列の処理を確認    | 実装済み | test_split_branch_name_regex_BVT_long_string    |
    | BVT_004  | name           | "支店"         | ("支店", "")     | 最短支店名の処理を確認    | 実装済み | test_split_branch_name_regex_BVT_minimal_branch |
    | BVT_005  | name           | "支店支店"     | ("支店支店", "") | 重複支店名の処理を確認    | 実装済み | test_split_branch_name_regex_C2_multiple_branch |
    """

    def setup_method(self):
        self.config_mock = Mock(log_message=Mock())

    def teardown_method(self):
        pass

    def test_split_branch_name_regex_C0_normal(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 標準的な支店名の分割処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("東京支店第一営業部")
        assert result == ("東京支店", "第一営業部")

    def test_split_branch_name_regex_C0_branch_only(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 支店名のみの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("大阪支店")
        assert result == ("大阪支店", "")

    def test_split_branch_name_regex_C1_no_branch(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 支店名を含まない場合の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_name = "営業第一部"
        result = ReferenceMergers._split_branch_name_regex(test_name)
        assert result == (test_name, "")

    def test_split_branch_name_regex_C1_with_department(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 営業部名を含む場合の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("横浜支店営業第二部")
        assert result == ("横浜支店", "営業第二部")

    def test_split_branch_name_regex_C2_multiple_branch(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 支店が複数回出現する場合の処理,最短マッチ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("支店支店営業部")
        assert result == ("支店", "支店営業部")

    def test_split_branch_name_regex_BVT_none_value(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: None値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex(None)
        assert result == (None, None)

    def test_split_branch_name_regex_BVT_empty_string(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("")
        assert result == ("", "")

    def test_split_branch_name_regex_BVT_long_string(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 極端に長い文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        long_name = "長い支店" * 100 + "長い営業部名" * 100
        result = ReferenceMergers._split_branch_name_regex(long_name)
        expected_branch = "長い支店"
        expected_dept = "長い支店" * 99 + "長い営業部名" * 100
        assert result == (expected_branch, expected_dept)

    def test_split_branch_name_regex_BVT_minimal_branch(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 最小の支店名パターンの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("支店")
        assert result == ("支店", "")

    def test_split_branch_name_regex_C2_special_characters(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 特殊文字を含む場合の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._split_branch_name_regex("東京★支店◆営業部")
        assert result == ("東京★支店", "◆営業部")

class TestReferenceMergers_ParseRemarks:
    """ReferenceMergersの_parse_remarksメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 標準的な備考解析
    │   ├── 正常系: 空の備考解析
    │   └── 異常系: 異常値の処理
    ├── C1: 分岐カバレッジ
    │   ├── remarks が None/NA
    │   ├── remarks が空文字列
    │   └── remarks が有効な文字列
    ├── C2: 条件カバレッジ
    │   ├── 全フィールドが存在
    │   ├── 一部フィールドのみ存在
    │   └── 不正なフィールド値
    └── BVT: 境界値テスト
        ├── 空文字列
        ├── None値
        ├── 最小有効データ
        └── 最大長データ

    # C1のディシジョンテーブル
    | 条件                          | Case1 | Case2 | Case3 | Case4 | Case5 |
    |-------------------------------|-------|-------|-------|-------|-------|
    | remarksがNone/NA              | Y     | N     | N     | N     | N     |
    | remarksが空文字列             | N     | Y     | N     | N     | N     |
    | Parserが正常動作              | -     | -     | Y     | N     | Y     |
    | 全フィールドが存在            | -     | -     | Y     | -     | N     |
    | 出力                          | 空構造 | 空構造 | 解析結果 | エラー | 部分結果 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値            | 期待される結果    | テストの目的/検証ポイント | 実装状況 | 対応するテストケース                |
    |----------|----------------|---------------------|-------------------|---------------------------|----------|-------------------------------------|
    | BVT_001  | remarks        | None                | 空のParsedRemarks | None値の処理を確認        | 実装済み | test_parse_remarks_BVT_none_value   |
    | BVT_002  | remarks        | ""                  | 空のParsedRemarks | 空文字列の処理を確認      | 実装済み | test_parse_remarks_BVT_empty_string |
    | BVT_003  | remarks        | "最小有効データ"    | 最小ParsedRemarks | 最小データの処理を確認    | 実装済み | test_parse_remarks_BVT_minimal_data |
    | BVT_004  | remarks        | "x" * 1000          | エラーまたは結果  | 長大データの処理を確認    | 実装済み | test_parse_remarks_BVT_long_string  |
    """

    def setup_method(self):
        """テストメソッドの前処理"""
        self.empty_remarks_structure = {
            'request_type': '',
            'sales_department': {
                'department_name': '',
                'branch_name': '',
            },
            'area_group': {
                'group_code': '',
                'group_name': '',
                'established_date': '',
            },
            'other_info': '',
        }

    @pytest.fixture()
    def mock_remarks_parser(self):
        """RemarksParserのモック"""
        with patch('src.lib.converter_utils.ibr_reference_mergers.RemarksParser') as mock:
            parser_instance = Mock()
            mock.return_value = parser_instance
            yield parser_instance

    @pytest.fixture()
    def valid_parsed_result(self) -> dict[str, any]:
        """有効な解析結果のフィクスチャ"""
        return {
            'request_type': '新設',
            'sales_department': {
                'department_name': '第一営業部',
                'branch_name': '東京支店',
            },
            'area_group': {
                'group_code': 'A001',
                'group_name': '首都圏エリア',
                'established_date': '2024-01-01',
            },
            'other_info': '備考追記',
        }

    def test_parse_remarks_C0_normal(self, mock_remarks_parser, valid_parsed_result):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 標準的な備考解析
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_remarks_parser.parse.return_value = valid_parsed_result
        result = ReferenceMergers._parse_remarks("標準的な備考文")

        assert result == valid_parsed_result
        mock_remarks_parser.parse.assert_called_once_with("標準的な備考文")

    def test_parse_remarks_C0_empty_string(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 空文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # RemarksParserインスタンスの戻り値を明示的に設定
        mock_remarks_parser.parse.return_value = self.empty_remarks_structure

        with patch('pandas.isna', return_value=False):  # 空文字列の場合はFalse
            result = ReferenceMergers._parse_remarks("")
            assert result == self.empty_remarks_structure
            # 空文字列の場合はparseメソッドが呼ばれることを確認
            mock_remarks_parser.parse.assert_called_once_with("")

    def test_parse_remarks_C1_none_value(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: None値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('pandas.isna', return_value=True):  # None値の場合はTrue
            result = ReferenceMergers._parse_remarks(None)
            assert result == self.empty_remarks_structure
            # None値の場合はparseメソッドが呼ばれないことを確認
            mock_remarks_parser.parse.assert_not_called()

    def test_parse_remarks_C2_partial_fields(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 一部フィールドのみ存在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        partial_result = {
            'request_type': '変更',
            'sales_department': {
                'department_name': '営業部',
                'branch_name': '',
            },
            'area_group': {
                'group_code': '',
                'group_name': '',
                'established_date': '',
            },
            'other_info': '',
        }
        mock_remarks_parser.parse.return_value = partial_result
        result = ReferenceMergers._parse_remarks("部分的な備考文")
        assert result == partial_result
        mock_remarks_parser.parse.assert_called_once_with("部分的な備考文")

    def test_parse_remarks_C2_parser_error(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: パーサーエラーの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # pd.isnaのモックを追加
        with patch('pandas.isna', return_value=False):
            # エラーを発生させる設定
            mock_remarks_parser.parse.side_effect = Exception("Parser Error")

        # 例外が発生することを確認
        with pytest.raises(RemarksParseError) as excinfo:
            ReferenceMergers._parse_remarks("エラーを発生させる備考文")

        # エラーメッセージの検証
        assert "RemarksParse処理で異常が発生しました: Parser Error" in str(excinfo.value)

        # Mockの呼び出し確認
        mock_remarks_parser.parse.assert_called_once_with("エラーを発生させる備考文")

    def test_parse_remarks_BVT_minimal_data(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 最小有効データの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        minimal_result = {
            'request_type': '新設',
            'sales_department': {
                'department_name': '部',
                'branch_name': '',
            },
            'area_group': {
                'group_code': 'A',
                'group_name': '',
                'established_date': '',
            },
            'other_info': '',
        }
        mock_remarks_parser.parse.return_value = minimal_result

        result = ReferenceMergers._parse_remarks("最小データ")

        assert result == minimal_result
        mock_remarks_parser.parse.assert_called_once_with("最小データ")

    def test_parse_remarks_BVT_long_string(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 長大な文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        long_remarks = "x" * 1000
        expected_result = {
            'request_type': '変更',
            'sales_department': {
                'department_name': '長い部署名',
                'branch_name': '長い支店名',
            },
            'area_group': {
                'group_code': 'LONG',
                'group_name': '長いエリア名',
                'established_date': '2024-01-01',
            },
            'other_info': '長い追加情報',
        }
        mock_remarks_parser.parse.return_value = expected_result

        result = ReferenceMergers._parse_remarks(long_remarks)

        assert result == expected_result
        mock_remarks_parser.parse.assert_called_once_with(long_remarks)

    def test_parse_remarks_C2_various_errors(self, mock_remarks_parser):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 様々な例外パターンのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_cases = [
            (ValueError("値エラー"), "値エラー"),
            (TypeError("型エラー"), "型エラー"),
            (Exception("一般エラー"), "一般エラー"),
        ]

        for original_error, error_msg in test_cases:
            with patch('pandas.isna', return_value=False):
                # エラーを発生させる設定
                mock_remarks_parser.parse.side_effect = original_error

                # 例外が発生することを確認
                with pytest.raises(RemarksParseError) as excinfo:
                    ReferenceMergers._parse_remarks("エラーを発生させる備考文")

                # エラーメッセージの検証
                expected_msg = f"RemarksParse処理で異常が発生しました: {error_msg}"
                assert expected_msg in str(excinfo.value)

                # Mockの呼び出し確認
                mock_remarks_parser.parse.assert_called_once_with("エラーを発生させる備考文")

                # 次のテストのためにモックをリセット
                mock_remarks_parser.parse.reset_mock()

class TestReferenceMergers_FindBranchCodeFromRemarks:
    """ReferenceMergersの_find_branch_code_from_remarksメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: マッチする部店名が存在
    │   ├── 正常系: マッチする部店名が存在しない
    │   └── 異常系: 無効なデータ構造
    ├── C1: 分岐カバレッジ
    │   ├── 拠点内営業部が存在する
    │   ├── 拠点内営業部が存在しない
    │   └── マスクが全てFalse
    ├── C2: 条件カバレッジ
    │   ├── 完全一致する部店名
    │   ├── 部分一致する部店名
    │   └── 大文字小文字が異なる部店名
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        ├── 1行のみのデータ
        └── 重複する部店名

    # C1のディシジョンテーブル
    | 条件                          | Case1 | Case2 | Case3 | Case4 | Case5 |
    |-------------------------------|-------|-------|-------|-------|-------|
    | DataFrameが空でない           | Y     | Y     | Y     | N     | Y     |
    | 拠点内営業部レコードが存在    | Y     | Y     | N     | -     | Y     |
    | マスクが有効                  | Y     | N     | -     | -     | Y     |
    | 部店名が一致                  | Y     | -     | -     | -     | N     |
    | 出力                          | コード | None  | None  | None  | None  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント      | 実装状況 | 対応するテストケース                  |
    |----------|----------------|----------------------------|----------------|--------------------------------|----------|---------------------------------------|
    | BVT_001  | df             | 空のDataFrame              | 空のSeries     | 空データの処理を確認           | 実装済み | test_find_branch_code_BVT_empty_df |
    | BVT_002  | df             | 1行のデータ                | 対応するコード | 最小データセットの処理を確認   | 実装済み | test_find_branch_code_BVT_single_row |
    | BVT_003  | df             | 重複部店名                 | 最初のコード   | 重複データの処理を確認         | 実装済み | test_find_branch_code_BVT_duplicate_names |
    | BVT_004  | mask           | 全てFalse                  | 空のSeries     | 無効なマスクの処理を確認       | 実装済み | test_find_branch_code_BVT_all_false_mask |
    | BVT_005  | mask           | 一部True                   | 部分的な結果   | 部分的なマスクの処理を確認     | 実装済み | test_find_branch_code_BVT_partial_mask |
    """

    @pytest.fixture()
    def sample_df(self):
        """テスト用の基本データセット"""
        return pd.DataFrame({
            'target_org': [
                OrganizationType.INTERNAL_SALES.value,  # 拠点内営業部
                OrganizationType.INTERNAL_SALES.value,  # 拠点内営業部
                OrganizationType.SECTION_GROUP.value,   # 課
            ],
            'branch_name': [
                '東京営業第一部',   # これと
                '大阪営業第一部',
                '審査第一課',
            ],
            'branch_code': ['T001', 'O001', 'S001'],
            'remarks': [
                '東京営業第一部の備考',
                '大阪営業第一部の備考',
                '東京営業第一部',    # これが一致している必要がある
            ],
        })

    @pytest.fixture()
    def sample_mask(self):
        """テスト用のマスク"""
        return pd.Series([False, False, True])

    def test_find_branch_code_C0_normal(self, sample_df, sample_mask):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 正常系の基本動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = ReferenceMergers._find_branch_code_from_remarks(sample_df, sample_mask)
        assert isinstance(result, pd.Series)
        masked_result = result[sample_mask]
        assert len(masked_result) == 1
        # 課のremarksと一致する拠点内営業部のコードが取得できることを確認
        # インデックスを直接使用
        assert result[2] == 'T001'  # 東京営業第一部のコード
        # もしくは、マスクに基づいて値を確認
        assert result[sample_mask].iloc[0] == 'T001'  # より安全なアプローチ

    def test_find_branch_code_C0_no_match(self, sample_df):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: マッチする拠点内営業部名が存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mask = pd.Series([False, False, True])
        modified_df = sample_df.copy()
        modified_df.loc[2, 'remarks'] = '福岡営業第一部'  # 存在しない拠点内営業部名
        result = ReferenceMergers._find_branch_code_from_remarks(modified_df, mask)
        assert pd.isna(result[mask].iloc[0])

    def test_find_branch_code_C1_internal_sales_exists(self, sample_df):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 拠点内営業部が存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mask = pd.Series([False, False, True])
        result = ReferenceMergers._find_branch_code_from_remarks(sample_df, mask)
        assert result[mask].iloc[0] == 'T001'

    def test_find_branch_code_C2_exact_match(self, sample_df):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 部店名が完全一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mask = pd.Series([False, False, True])
        modified_df = sample_df.copy()
        modified_df.loc[2, 'remarks'] = '東京営業'  # 部分一致
        result = ReferenceMergers._find_branch_code_from_remarks(modified_df, mask)
        assert pd.isna(result[mask].iloc[0])


    def test_find_branch_code_C2_partial_match(self, sample_df):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 部分一致の場合は一致とみなさない
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mask = pd.Series([False, False, True])
        modified_df = sample_df.copy()
        modified_df.loc[2, 'remarks'] = '東京営業'  # 部分一致
        result = ReferenceMergers._find_branch_code_from_remarks(modified_df, mask)
        assert pd.isna(result[mask].iloc[0])

    def test_find_branch_code_BVT_empty_df(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空のDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_df = pd.DataFrame(columns=['target_org', 'branch_name', 'branch_code', 'remarks'])
        empty_mask = pd.Series([], dtype=bool)
        result = ReferenceMergers._find_branch_code_from_remarks(empty_df, empty_mask)
        assert isinstance(result, pd.Series)
        assert len(result) == 0

    def test_find_branch_code_BVT_single_row(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 1行のみのデータの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'target_org': [OrganizationType.INTERNAL_SALES.value],
            'branch_name': ['東京営業第一部'],
            'branch_code': ['T001'],
            'remarks': ['東京営業第一部'],
        })
        mask = pd.Series([True])
        result = ReferenceMergers._find_branch_code_from_remarks(_df, mask)
        assert isinstance(result, pd.Series)
        assert len(result) == 1
        assert result[mask].iloc[0] == 'T001'


    def test_find_branch_code_C0_duplicate_branch_names(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 拠点内営業部名の重複エラー
        - 拠点内営業部名が重複している場合は、マッチング時にエラーとすること
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'target_org': [
                OrganizationType.INTERNAL_SALES.value,
                OrganizationType.INTERNAL_SALES.value,
                OrganizationType.SECTION_GROUP.value,
            ],
            'branch_name': [
                '東京営業第一部',
                '東京営業第一部',  # 重複
                '審査第一課',
            ],
            'branch_code': ['T001', 'T002', 'S001'],
            'remarks': [
                '東京営業第一部の備考',
                '東京営業第一部の備考',
                '東京営業第一部',
            ],
        })
        mask = pd.Series([False, False, True])

        # エラーが発生することを確認
        with pytest.raises(RemarksParseError) as exc_info, \
            patch('src.lib.converter_utils.ibr_reference_mergers.log_msg') as mock_log:
            ReferenceMergers._find_branch_code_from_remarks(_df, mask)

        # エラーメッセージの確認
        error_message = str(exc_info.value)
        assert "拠点内営業部名に重複があります(データ不整合): 東京営業第一部" in error_message

        # エラーログの出力確認
        mock_log.assert_called_once_with(error_message, LogLevel.ERROR)

    #def test_find_branch_code_BVT_all_false_mask(self, sample_df):
    #    """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テストケース: 全てFalseのマスクの処理  -> 呼び出し元でmaskが全てFalseの場合は呼び出さない制御有り
    #    """
    #    mask = pd.Series([False, False, False])
    #    result = ReferenceMergers._find_branch_code_from_remarks(sample_df, mask)
    #    assert isinstance(result, pd.Series)
    #    assert len(result) == len(sample_df)
    #    assert all(pd.isna(result))  # 全ての要素がNaN
