import pickle
from pathlib import Path
from unittest.mock import Mock, patch

import numpy as np
import pandas as pd
import pytest
import sys

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.converter_utils.ibr_reference_mergers import ReferenceMergers

# config共有
config = initialize_config(sys.modules[__name__])
package_config = config.package_config
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
    def test_merge_reference_data(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        # リファレンスデータ,申請玉
        integrated = TableSearcher('integrated_layout.pkl','tests/table')
        reference = TableSearcher('reference_table.pkl','tests/table')
        
        result_df = ReferenceMergers.merge_zero_group_parent_branch_with_reference(integrated.df, reference.df)

        tabulate_dataframe(integrated.df)
        tabulate_dataframe(reference.df)
        tabulate_dataframe(result_df)

    def test_merge_reference_data2(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        # リファレンスデータ,申請玉
        integrated = TableSearcher('integrated_layout.pkl','tests/table')
        reference = TableSearcher('reference_table.pkl','tests/table')
        
        result_df = ReferenceMergers.merge_zero_group_parent_branch_with_self(integrated.df)

        tabulate_dataframe(integrated.df)
        tabulate_dataframe(reference.df)
        tabulate_dataframe(result_df)

    def test_merge_reference_data3(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameで処理
        """
        # リファレンスデータ,申請玉
        integrated = TableSearcher('integrated_layout.pkl','tests/table')
        reference = TableSearcher('reference_table.pkl','tests/table')
        
        result_df = ReferenceMergers.match_unique_reference(integrated.df, reference.df)

        tabulate_dataframe(integrated.df)
        tabulate_dataframe(reference.df)
        tabulate_dataframe(result_df)
