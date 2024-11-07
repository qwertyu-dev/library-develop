import numpy as np
import pandas as pd
import pickle
import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from src.lib.converter_utils.ibr_reference_merger import ReferenceMerger
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe

package_path = Path(__file__)
config = Config.load(package_path)
log_msg = config.log_message

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
    def test_merge_reference_data_BPRADフラグ取得して申請玉Columnへ追加(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # リファレンスデータ
        reference = TableSearcher('reference_table.pkl','tests/table')
        integrated = TableSearcher('integrated_layout.pkl','tests/table')

        log_msg(f"\n{tabulate_dataframe(reference.df[['branch_code_jinji','section_gr_code_jinji','business_code','area_code','bpr_target_flag']])}", LogLevel.INFO)
        #log_msg(f"\n{tabulate_dataframe(integrated.df[['branch_code','section_gr_code','area_code']])}", LogLevel.INFO)

        # マージ前処理
        # area_code分割
        integrated.df['business_code_sep'] = integrated.df['area_code'].str[0]
        integrated.df['area_code_sep'] = integrated.df['area_code'].str[1:]
        log_msg(f"\n{tabulate_dataframe(reference.df[['branch_code_jinji','section_gr_code_jinji','business_code','area_code','bpr_target_flag']])}", LogLevel.INFO)

        filtered_integrated_df = integrated.df[['branch_code','section_gr_code','area_code','business_code_sep','area_code_sep','bpr_target_flag']]
        filterd_reference_df = reference.df[['branch_code_jinji','section_gr_code_jinji','business_code','area_code','bpr_target_flag']]

        # マージ処理
        # 結果に対してすぐさまfillna('')はしない
        result = filtered_integrated_df.merge(
            filterd_reference_df,
            left_on=['branch_code', 'section_gr_code', 'business_code_sep', 'area_code_sep'],
            right_on=['branch_code_jinji', 'section_gr_code_jinji', 'business_code', 'area_code'],
            how='left',
        )
        log_msg(f"\n{tabulate_dataframe(result)}", LogLevel.INFO)

        # マージ後処理
        # ヒットしなかった場合は元の値をセットする 指定Columnに対してnull書き換え
        integrated.df['reference_bpr_target_flag'] = result['bpr_target_flag_y'].fillna(result['bpr_target_flag_x'])

        tabulate_dataframe(integrated.df[['branch_code','section_gr_code','area_code','bpr_target_flag']])
        tabulate_dataframe(integrated.df)

    def test_merge_reference_data_C0_拠点内営業部(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # リファレンスデータ,申請玉
        #reference = TableSearcher('reference_table.pkl','tests/table')
        integrated = TableSearcher('integrated_layout.pkl','tests/table')

        #log_msg(f"\n{tabulate_dataframe(reference.df[['branch_code_jinji','section_gr_code_jinji','business_code','area_code','bpr_target_flag']])}", LogLevel.INFO)
        #log_msg(f"\n{tabulate_dataframe(integrated.df[['branch_code','section_gr_code','area_code']])}", LogLevel.INFO)

        # 編集受け皿を用紙
        result_df = integrated.df.copy()

        # 対象データの絞り込み
        mask = (result_df['target_org'] == '拠点内営業部')

        # 部店コードを拠点内営業部コードへセット
        result_df.loc[mask, 'internal_sales_dept_code'] = result_df.loc[mask, 'branch_code']

        # 部店名称を支店で分割、〜支店を部店名に,支店より後を拠点内営業部名称へセット
        import re

        def split_branch_name_regex(name):
            if pd.isna(name):  # NULL/NaN チェック
                return (name, name)

            # 正規表現パターン:
            # ^(.+?支店)(.*)$ の説明:
            # ^     : 文字列の先頭
            # (.+?) : 1文字以上の任意の文字(最小マッチ)をグループ1として取得
            # 支店   : '支店'という文字列
            # (.*)  : 残りの任意の文字列をグループ2として取得
            # $     : 文字列の末尾
            pattern = r'^(.+?支店)(.*)$'

            match = re.match(pattern, name)
            if match:
                branch_part = match.group(1)  # 支店名部分
                dept_part = match.group(2).strip()  # 営業部名部分
                return (branch_part, dept_part)
            return (name, '')  # マッチしない場合

        # 分割処理の適用
        split_names = result_df.loc[mask, 'branch_name'].apply(split_branch_name_regex)

        # 分割結果を各カラムに格納
        result_df.loc[mask, 'branch_name'] = split_names.apply(lambda x: x[0])
        result_df.loc[mask, 'internal_sales_dept_name'] = split_names.apply(lambda x: x[1])

        # 対象データの部店コードを上位から4桁に切り落とし
        result_df.loc[mask, 'branch_code'] = (
            result_df.loc[mask, 'branch_code']
            .astype(str)
            .str[:4]
        )

        tabulate_dataframe(integrated.df)
        tabulate_dataframe(result_df)

    def test_merge_reference_data_C0_エリア(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        from src.lib.converter_utils.ibr_excel_field_analyzer import RemarksParser
        from typing import Any
        from src.lib.common_utils.ibr_logger_helper import format_dict

        # リファレンスデータ,申請玉
        #reference = TableSearcher('reference_table.pkl','tests/table')
        integrated = TableSearcher('integrated_layout.pkl','tests/table')

        #log_msg(f"\n{tabulate_dataframe(reference.df[['branch_code_jinji','section_gr_code_jinji','business_code','area_code','bpr_target_flag']])}", LogLevel.INFO)
        #log_msg(f"\n{tabulate_dataframe(integrated.df[['branch_code','section_gr_code','area_code']])}", LogLevel.INFO)

        # 編集受け皿を用紙
        result_df = integrated.df.copy()

        # 対象データの絞り込み
        mask = (result_df['target_org'] == 'エリア')

        # 備考欄からの情報判定
        # remarks列をベクトル化処理するための関数
        def apply_parser(remarks: str) -> dict[str, Any]:
            # 備考欄解析インスタンス生成
            parser = RemarksParser()
            if pd.isna(remarks):
                return {
                    'request_type': '',
                    'sales_department': {'department_name': '', 'branch_name': ''},
                    'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
                    'other_info': '',
                }
            return parser.parse(str(remarks))

        # apply関数を使用してremarks列全体を処理
        parsed_series = result_df.loc[mask, 'remarks'].apply(apply_parser)

        tabulate_dataframe(integrated.df)
        tabulate_dataframe(result_df)

        log_msg(f"{parsed_series.apply(lambda x: x['request_type'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['sales_department']['department_name'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['sales_department']['branch_name'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['area_group']['group_code'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['area_group']['group_name'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['area_group']['established_date'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['other_info'])}", LogLevel.INFO)

        # dataframeはこの実装で値還元
        #result_df.loc[mask, 'request_type'] = parsed_series.apply(lambda x: x['request_type'])
        #result_df.loc[mask, 'sales_department_name'] = parsed_series.apply(lambda x: x['sales_department']['department_name'])
        #result_df.loc[mask, 'sales_branch_name'] = parsed_series.apply(lambda x: x['sales_department']['branch_name'])
        result_df.loc[mask, 'area_group_code'] = parsed_series.apply(lambda x: x['area_group']['group_code'])
        result_df.loc[mask, 'area_group_name'] = parsed_series.apply(lambda x: x['area_group']['group_name'])
        #result_df.loc[mask, 'area_established_date'] = parsed_series.apply(lambda x: x['area_group']['established_date'])
        #result_df.loc[mask, 'other_info'] = parsed_series.apply(lambda x: x['other_info'])

        tabulate_dataframe(result_df)


    def test_merge_reference_data_C0_課_支店配下の営業部配下(self):
        # mask条件は考える必要あり
        # 課であることと、備考欄が空欄でないことで対象を絞り込めるかと
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        from src.lib.converter_utils.ibr_excel_field_analyzer import RemarksParser
        from typing import Any
        from src.lib.common_utils.ibr_logger_helper import format_dict

        # リファレンスデータ,申請玉
        #reference = TableSearcher('reference_table.pkl','tests/table')
        integrated = TableSearcher('integrated_layout.pkl','tests/table')

        #log_msg(f"\n{tabulate_dataframe(reference.df[['branch_code_jinji','section_gr_code_jinji','business_code','area_code','bpr_target_flag']])}", LogLevel.INFO)
        #log_msg(f"\n{tabulate_dataframe(integrated.df[['branch_code','section_gr_code','area_code']])}", LogLevel.INFO)
        #tabulate_dataframe(integrated.df)

        # 編集受け皿を用紙
        result_df = integrated.df.copy()
        #tabulate_dataframe(result_df)

        ## 対象データの絞り込み
        mask = ((result_df['target_org'] == '課') & (result_df['remarks'] != ''))
        tabulate_dataframe(result_df.loc[mask,:])

        # 備考欄からの情報判定
        # remarks列をベクトル化処理するための関数
        def apply_parser(remarks: str) -> dict[str, Any]:
            # 備考欄解析インスタンス生成
            parser = RemarksParser()
            if pd.isna(remarks):
                return {
                    'request_type': '',
                    'sales_department': {'department_name': '', 'branch_name': ''},
                    'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
                    'other_info': '',
                }
            return parser.parse(str(remarks))

        # apply関数を使用してremarks列全体を処理
        parsed_series = result_df.loc[mask, 'remarks'].apply(apply_parser)

        log_msg(f"{parsed_series.apply(lambda x: x['request_type'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['sales_department']['department_name'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['sales_department']['branch_name'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['area_group']['group_code'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['area_group']['group_name'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['area_group']['established_date'])}", LogLevel.INFO)
        log_msg(f"{parsed_series.apply(lambda x: x['other_info'])}", LogLevel.INFO)

        # internal_sales_dept_name 拠点内営業部名
        result_df.loc[mask, 'internal_sales_dept_name'] = parsed_series.apply(lambda x: x['sales_department']['department_name'])

        def find_branch_code_from_remarks(df: pd.DataFrame, mask: pd.Series) -> pd.Series:
            """マスクされたデータについて、remarksと一致するbranch_nameを持つ行からbranch_codeを取得する

            Args:
                df (pd.DataFrame): 処理対象のDataFrame
                mask (pd.Series): 処理対象の行を示すブールマスク

            Returns:
                pd.Series: 取得したbranch_code(マスクされた行のインデックスを持つ)
            """
            # branch_nameとbranch_codeのマッピングを作成(重複を除去)
            mapping_df = df[['branch_name', 'branch_code']].drop_duplicates()
            name_to_code = mapping_df.set_index('branch_name')['branch_code']

            # マスクされたデータのremarksに基づいてbranch_codeを取得
            return df.loc[mask, 'remarks'].map(name_to_code)

        # internal_sales_dept_code 拠点内営業部コード
        result_df.loc[mask, 'internal_sales_dept_code'] = find_branch_code_from_remarks(result_df, mask)

        tabulate_dataframe(integrated.df)
        tabulate_dataframe(result_df.fillna(''))
