"""一括申請明細にリファレンステーブル情報をマージして情報付与する"""
import pandas as pd
from typing import  Any
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher

class ReferenceMerger:
    """統合レイアウトデータとリファレンステーブルのマージを行うクラス

    Class Overview:
        このクラスはデータ取り込み後の統合レイアウトデータと
        リファレンステーブルの情報をマージする機能を提供します。
        部店コードの上位4桁を使用してリファレンステーブルを検索し、
        条件に合致する一部のColumnデータを統合レイアウトにマージします。

    Attributes:
        table_searcher (TableSearcher): リファレンステーブルの検索を行うオブジェクト

    Condition Information:
        - Condition:1
            - ID: ZERO_SECTION_GR_CODE
            - Type: フィルタリング条件
            - Applicable Scenarios: リファレンステーブルから課グループコードが'0'のレコードを選択する

    Pattern Information:
        - Pattern:1
            - ID: BRANCH_CODE_PREFIX_MATCH
            - Type: 検索パターン
            - Applicable Scenarios: 部店コードの上位4桁を使用してリファレンステーブルを検索する

    Methods:
        merge_reference_data(integrated_layout: pd.DataFrame) -> pd.DataFrame:
            統合レイアウトデータにリファレンス情報をマージする
        _get_reference_info(row: pd.Series) -> dict[str, Any]:
            1行のデータに対応するリファレンス情報を取得する
        _get_branch_code_prefix(row: pd.Series) -> str:
            部店コードの上位4桁を取得する
        _search_reference_table(branch_code_prefix: str) -> pd.DataFrame:
            リファレンステーブルを検索する
        _filter_zero_row(df: pd.DataFrame) -> pd.DataFrame:
            課グループコードが'0'の行をフィルタリングする
        _create_result_dict(row: pd.Series) -> dict[str, Any]:
            リファレンス情報の辞書を作成する
        _get_empty_result() -> dict[str, Any]:
            空のリファレンス情報辞書を返す

    Usage Example:
        >>> from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
        >>> from src.lib.converter_utils.ibr_reference_merger import ReferenceMerger
        >>> table_searcher = TableSearcher("reference_table.pkl")
        >>> merger = ReferenceMerger(table_searcher)
        >>> integrated_layout = pd.read_csv("integrated_layout.csv")
        >>> merged_data = merger.merge_reference_data(integrated_layout)
        >>> print(merged_data.head())

    Notes:
        - リファレンステーブルは事前にpickleファイルとして保存されている必要があります
        - 大量のデータを処理する場合、メモリ使用量に注意してください

    Dependency:
        - pandas
        - src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher

    ResourceLocation:
        - [本体]
            - src/lib/converter_utils/ibr_reference_merger.py
        - [テストコード]
            - tests/lib/converter_utils/test_ibr_reference_merger.py

    Todo:
        - パフォーマンスの最適化
        - 並列処理の導入検討
        - エラーハンドリングの強化

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当         |
    |------|--------------|----------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/18 | xxxx aaa.bbb |

    """

    def __init__(self, table_searcher: TableSearcher):
        """コンストラクタ

        Arguments:
        table_searcher (TableSearcher): リファレンステーブルの検索を行うオブジェクト
        """
        self.table_searcher = table_searcher

    def merge_reference_data(self, integrated_layout: pd.DataFrame) -> pd.DataFrame:
        """統合レイアウトデータにリファレンステーブルの情報をマージする

        Arguments:
        integrated_layout (pd.DataFrame): 統合レイアウトデータ

        Return Value:
        pd.DataFrame: マージされたデータフレーム

        Algorithm:
            1. 統合レイアウトの各行に対して_get_reference_infoメソッドを適用
            2. 得られた結果を元のDataFrameとマージして返す

        Exception:
        ValueError: 入力DataFrameが空の場合

        Usage Example:
        >>> merged_data = merger.merge_reference_data(integrated_layout)
        >>> print(merged_data.columns)
        Index(['branch_code', 'other_data', 'reference_branch_code', 'reference_branch_name', 'reference_parent_branch_code'], dtype='object')
        """
        if integrated_layout.empty:
            err_msg = "入力DataFrameが空です"
            raise ValueError(err_msg) from None

        reference_info = integrated_layout.apply(self._get_reference_info, axis=1, result_type='expand')
        return pd.concat([integrated_layout, reference_info], axis=1)

    def _get_reference_info(self, row: pd.Series) -> dict[str, Any]:
        """1行のデータに対応するリファレンス情報を取得する

        Arguments:
        row (pd.Series): 統合レイアウトの1行のデータ

        Return Value:
        dict[str, Any]: 取得したリファレンス情報

        Algorithm:
            1. 部店コードの上位4桁を取得
            2. リファレンステーブルを検索
            3. 検索結果から条件に合う行を抽出
            4. 結果の辞書を作成して返す

        Exception:
        KeyError: 必要なカラムが存在しない場合
        """
        try:
            branch_code_prefix = self._get_branch_code_prefix(row)
            matching_rows = self._search_reference_table(branch_code_prefix)
            zero_row = self._filter_zero_row(matching_rows)

            if zero_row.empty:
                return self._get_empty_result()
            return self._create_result_dict(zero_row.iloc[0])
        except KeyError:
            #必要なカラムが存在しない
            return self._get_empty_result()

    def _get_branch_code_prefix(self, row: pd.Series) -> str:
        """部店コードの上位4桁を取得する"""
        return str(row['branch_code'])[:4]

    def _search_reference_table(self, branch_code_prefix: str) -> pd.DataFrame:
        """リファレンステーブルを検索する"""
        return self.table_searcher.simple_search({
            "branch_code_bpr": f"startswith:{branch_code_prefix}",
        })

    def _filter_zero_row(self, df: pd.DataFrame) -> pd.DataFrame:
        """課グループコードが'0'の行をフィルタリングする"""
        if df.empty or 'section_gr_code_bpr' not in df.columns:
            return pd.DataFrame(columns=df.columns)
        return df[df['section_gr_code_bpr'] == '0']

    def _create_result_dict(self, row: pd.Series) -> dict[str, Any]:
        """リファレンス情報の辞書を作成する"""
        return {
            "reference_branch_code": row['branch_code_bpr'] if pd.notna(row['branch_code_bpr']) else None,
            "reference_branch_name": row['branch_name_bpr'] if pd.notna(row['branch_name_bpr']) else None,
            "reference_parent_branch_code": row['parent_branch_code'] if pd.notna(row['parent_branch_code']) else None,
        }

    def _get_empty_result(self) -> dict[str, Any]:
        """空のリファレンス情報辞書を返す"""
        return {
            "reference_branch_code": None,
            "reference_branch_name": None,
            "reference_parent_branch_code": None,
        }
