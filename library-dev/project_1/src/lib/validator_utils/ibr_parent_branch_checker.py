"""親部店を持っているか判定"""
import pandas as pd
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher


class ParentBranchChecker:
    """親部店情報の検索と判定を行うクラス

    Class Overview:
        このクラスは、指定された部店コードに対して親部店情報を検索し、
        3つの条件に基づいて判定を行います。リファレンステーブルと
        申請明細レコード群の両方を対象に検索を実行し、条件を満たすレコードの
        有無をブール値で返します。

    Attributes:
        application_searcher (TableSearcher): 申請明細レコード群を検索するためのTableSearcherインスタンス
        reference_searcher (TableSearcher): リファレンステーブルを検索するためのTableSearcherインスタンス

    Condition Information:
        - Condition:1
            - ID: GROUP_ZERO_BRANCH
            - Type: 親部店判定条件
            - Applicable Scenarios: 部店コードの前方4桁が一致し、課Grコードが0で、部店名に[グループなし]がついている場合
        - Condition:2
            - ID: SPECIFIC_LOCATION_BRANCH
            - Type: 親部店判定条件
            - Applicable Scenarios: 部店コードの前方4桁が一致し、部店名に(大阪)または(名古屋)がついている場合
        - Condition:3
            - ID: PARENT_CODE_DEFINED_BRANCH
            - Type: 親部店判定条件
            - Applicable Scenarios: 親部店コードで定義されている部店の場合

    Methods:
        check_condition_1(branch_code): 条件1に基づいて親部店の有無を判定
        check_condition_2(branch_code): 条件2に基づいて親部店の有無を判定
        check_condition_3(branch_code): 条件3に基づいて親部店の有無を判定

    Usage Example:
        >>> checker = ParentBranchChecker("application_data.pkl", "reference_data.pkl")
        >>> result = checker.check_condition_1("1234567")
        >>> print(result)
        True

    Notes:
        - 各条件チェックメソッドは、リファレンステーブルと申請明細レコード群の両方を検索します
        - 結果はブール値で返されます。条件を満たすレコードが存在する場合はTrue、存在しない場合はFalseを返します

    Dependency:
        - ibr_pickled_table_searcher.TableSearcher
        - pandas

    ResourceLocation:
        - [本体]
            - src/lib/common_utils/parent_branch_checker.py
        - [テストコード]
            - tests/lib/common_utils/test_parent_branch_checker.py

    Todo:
        - パフォーマンスの最適化(大規模データセットに対する効率的な検索方法の検討)
        - 新たな条件や判定ロジックの追加に対する拡張性の確保
        - エラーハンドリングの強化とロギング機能の追加

    Change History:
    | No   | 修正理由                           | 修正点                                     | 対応日     | 担当         |
    |------|------------------------------------|--------------------------------------------|------------|--------------|
    | v0.1 | 初期定義作成                       | 新規作成                                   | 2024/08/24 | xxxx aaa.bbb |
    """

    def __init__(self, application_data_file: str, reference_data_file: str):
        """ParentBranchCheckerクラスのコンストラクタ

        Arguments:
        application_data_file (str): 申請明細レコード群のpickleファイルパス
        reference_data_file (str): リファレンステーブルのpickleファイルパス
        """
        self.application_searcher = TableSearcher(application_data_file)
        self.reference_searcher = TableSearcher(reference_data_file)

    def check_condition_1(self, branch_code: str) -> bool:
        """条件1に基づいて親部店の有無を判定する

        Arguments:
        branch_code (str): 確認対象の部店コード

        Return Value:
        bool: 条件を満たす親部店が存在する場合はTrue、存在しない場合はFalse

        Algorithm:
            1. BPR部店コードの前方4桁を抽出
            2. 申請明細レコード群を検索
            3. リファレンステーブルを検索
            4. いずれかの検索結果が存在すればTrueを返す

        Usage Example:
        >>> result = checker.check_condition_1("12345")
        >>> print(result)
        True
        """
        # 検索条件設定
        prefix = branch_code[:4]
        conditions = {
            "branch_code_bpr": f"startswith:{prefix}",           # 部店コードBPR
            "section_gr_code_bpr": "0",                          # 課GrコードBPR
            "section_gr_name_bpr": "startswith:[グループなし]",  # 課Gr名称BRP
        }

        # 申請明細探索
        app_result = self.application_searcher.simple_search(conditions, operator='AND')
        if not app_result.empty:
            return True

        # リファレンス探索
        ref_result = self.reference_searcher.simple_search(conditions, operator='AND')
        return not ref_result.empty

    def check_condition_2(self, branch_code: str) -> bool:
        """条件2に基づいて親部店の有無を判定する

        Arguments:
        branch_code (str): 確認対象の部店コード

        Return Value:
        bool: 条件を満たす親部店が存在する場合はTrue、存在しない場合はFalse

        Algorithm:
            1. 部店コードの前方4桁を抽出
            2. 部店名に(大阪)または(名古屋)が含まれるか確認する条件を定義
            3. 申請明細レコード群を検索
            4. リファレンステーブルを検索
            5. いずれかの検索結果が存在すればTrueを返す

        Usage Example:
        >>> result = checker.check_condition_2("12345")
        >>> print(result)
        True
        """
        # 検索条件設定
        prefix = branch_code[:4]
        def condition(df) -> pd.Series:
            # 全角・半角の括弧を考慮した正規表現パターン
            osaka_pattern = r'[（(]大阪[）)]'        # noqa: RUF001 全角カッコが探索条件のため
            nagoya_pattern = r'[（(]名古屋[）)]'     # noqa: RUF001 全角カッコが探索条件のため

            return (
                df['branch_code_bpr'].astype(str).str.startswith(prefix) &
                (
                    df['branch_name_bpr'].str.contains(osaka_pattern, regex=True, na=False) |
                    df['branch_name_bpr'].str.contains(nagoya_pattern, regex=True, na=False)
                )
            )

        app_result = self.application_searcher.advanced_search(condition)
        if not app_result.empty:
            return True

        ref_result = self.reference_searcher.advanced_search(condition)
        return not ref_result.empty

    def check_condition_3(self, branch_code: str) -> bool:
        """条件3に基づいて親部店の有無を判定する

        Arguments:
        branch_code (str): 確認対象の部店コード

        Return Value:
        bool: 条件を満たす親部店が存在する場合はTrue、存在しない場合はFalse

        Algorithm:
            1. 部店コードの前方4桁を抽出
            2. リファレンステーブルの親部店コードカラムを検索
            3. 申請明細レコード群の親部店コードカラムを検索
            4. いずれかの検索結果が存在すればTrueを返す

        Usage Example:
        >>> result = checker.check_condition_3("12347")
        >>> print(result)
        True
        """
        # 検索条件設定
        prefix = branch_code[:4]

        # 親部店検索
        ref_result = self.reference_searcher.simple_search(
            {"parent_branch_code": prefix},
        )
        if not ref_result.empty:
            return True

        app_result = self.application_searcher.simple_search(
            {"parent_branch_code": prefix},
        )
        return not app_result.empty
