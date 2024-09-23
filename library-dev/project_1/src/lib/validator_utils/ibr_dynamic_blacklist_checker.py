"""動的BlackList"""
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from typing import Callable
import pandas as pd

class BlacklistCheckerError(Exception):
    """BlacklistCheckerに関する例外のベースクラス"""

class RuleApplicationError(BlacklistCheckerError):
    """ルール適用時のエラーを表す例外クラス"""

class BlacklistChecker:
    r"""動的ブラックリストチェックを実行するクラス

    Class Overview:
        このクラスは、リファレンステーブルと申請テーブルを使用して、
        定義されたルールに基づいて動的にブラックリストチェックを実行します。
        複数のルールを追加し、それらを適用して結果を取得することができます。

    Attributes:
        reference_searcher (TableSearcher): リファレンステーブルを検索するためのTableSearcherインスタンス
        application_searcher (TableSearcher): 申請テーブルを検索するためのTableSearcherインスタンス
        rules (list[dict]): 適用するルールのリスト。各ルールは名前と条件関数を含む辞書として保存される

    Condition Information:
        - Condition:1
            - ID: RULE_CONDITION
            - Type: 動的ルール条件
            - Applicable Scenarios: 各ルールの条件関数による判定

    Pattern Information:
        - Pattern:1
            - ID: BLACKLIST_CHECK
            - Type: ブラックリストチェックパターン
            - Applicable Scenarios: 全てのルールを順次適用し、結果を集約する

    Methods:
        __init__(reference_searcher: TableSearcher, application_searcher: TableSearcher): コンストラクタ
        add_rule(name: str, condition: Callable[[pd.DataFrame, pd.DataFrame], pd.Series]): ルールを追加する
        check_blacklist() -> pd.DataFrame: ブラックリストチェックを実行する
        refresh_data(): データを更新する

    Usage Example:
        # ルール定義の例
        def rule_executive_change(ref_df: pd.DataFrame, app_df: pd.DataFrame) -> pd.Series:
            ref_condition = ref_df["BPR部店名称"].str.contains("役員") & ref_df["職位コード"].isin(["001", "002", "003"])
            app_condition = (app_df["種類"] == "変更")
            return app_df["部店コード"].isin(ref_df[ref_condition]["部店コード"]) & app_condition

        def rule_specific_department_change(ref_df: pd.DataFrame, app_df: pd.DataFrame) -> pd.Series:
            ref_condition = (
                ref_df["BPR部店コード"].astype(str).str.startswith("1") &
                ref_df["BPR課Grコード"].astype(str).str.endswith("00") &
                (ref_df["重要度"] > 5)
            )
            app_condition = (app_df["種類"] == "変更")
            return app_df["部店コード"].isin(ref_df[ref_condition]["部店コード"]) & app_condition

        # BlacklistCheckerの使用例
        >>> from src.common_lib.ibr_pickled_table_searcher import TableSearcher
        >>> from src.lib.blacklist.ibr_dynamic_blacklist_checker import BlacklistChecker, RuleApplicationError
        >>>
        >>> reference_searcher = TableSearcher.create_for_production("reference_table.pkl")
        >>> application_searcher = TableSearcher.create_for_production("application_table.pkl")
        >>>
        >>> checker = BlacklistChecker(reference_searcher, application_searcher)
        >>>
        >>> checker.add_rule("役員変更制限", rule_executive_change)
        >>> checker.add_rule("特定部署変更制限", rule_specific_department_change)
        >>>
        >>> try:
        ...     results = checker.check_blacklist()
        ...     print("ブラックリストチェック結果:")
        ...     print(results)
        ...
        ...     if not results.empty:
        ...         print("\n各ルールの該当件数:")
        ...         print(results['rule_name'].value_counts())
        ...     else:
        ...         print("ブラックリストに該当する申請はありませんでした。")
        ...
        ... except RuleApplicationError as e:
        ...     print(f"ルール適用中にエラーが発生しました: {e}")
        >>>
        >>> # データの更新(必要に応じて)
        >>> checker.refresh_data()
        >>>
        >>> # 更新後の再チェック
        >>> try:
        ...     updated_results = checker.check_blacklist()
        ...     print("\n更新後のブラックリストチェック結果:")
        ...     print(updated_results)
        ... except RuleApplicationError as e:
        ...     print(f"更新後のチェック中にエラーが発生しました: {e}")

    Notes:
        - ルールの条件関数は、リファレンスDataFrameと申請DataFrameを引数に取り、ブールのSeriesを返す必要があります
        - エラーが発生した場合、RuleApplicationErrorが発生します

    Dependency:
        - pandas
        - src.common_lib.ibr_pickled_table_searcher

    ResourceLocation:
        - [本体]
            - src/lib/validator_utils/ibr_dynamic_blacklist_checker.py
        - [テストコード]
            - tests/lib/validator_utils/test_ibr_dynamic_blacklist_checker.py

    Todo:
        - 必要あれば追記する

    Change History:
    | No   | 修正理由     | 修正点                           | 対応日     | 担当         |
    |------|--------------|----------------------------------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成                         | 2024/08/25 | xxxx aaa.bbb |
    """

    def __init__(self, reference_searcher: TableSearcher, application_searcher: TableSearcher):
        """BlacklistCheckerクラスのコンストラクタ

        Arguments:
        reference_searcher (TableSearcher): リファレンステーブルを検索するためのTableSearcherインスタンス
        application_searcher (TableSearcher): 申請テーブルを検索するためのTableSearcherインスタンス
        """
        if not isinstance(reference_searcher, TableSearcher):
            error_msg = "Invalid reference_searcher. Must be an instance of TableSearcher."
            raise BlacklistCheckerError(error_msg) from None
        if not isinstance(application_searcher, TableSearcher):
            error_msg = "Invalid application_searcher. Must be an instance of TableSearcher."
            raise BlacklistCheckerError(error_msg) from None

        self.reference_searcher = reference_searcher
        self.application_searcher = application_searcher

        self.rules = []


    def add_rule(self, name: str, condition: Callable[[pd.DataFrame, pd.DataFrame], pd.Series]) -> list:
        """ブラックリストチェックのルールを追加する

        Arguments:
        name (str): ルールの名前
        condition (Callable[[pd.DataFrame, pd.DataFrame], pd.Series]): ルールの条件関数

        Return Value:
        None

        Algorithm:
            1. 新しいルールを辞書形式で作成
            2. ルールをrulesリストに追加

        Usage Example:
        >>> checker.add_rule("役員変更制限", rule_executive_change)
        """
        if not name or not name.strip():
            err_msg = "Rule name cannot be empty or only whitespace."
            raise ValueError(err_msg) from None
        if not callable(condition):
            err_msg = "Condition must be a callable function."
            raise TypeError(err_msg) from None
        self.rules.append({"name": name, "condition": condition})

    def check_blacklist(self) -> pd.DataFrame:
        """ブラックリストチェックを実行する

        Return Value:
        pd.DataFrame: ブラックリストに該当する申請データ

        Exceptions:
        RuleApplicationError: ルールの適用中にエラーが発生した場合

        Algorithm:
            1. リファレンスと申請のDataFrameを取得
            2. 各ルールを順に適用
            3. ルールに該当するデータを抽出し、結果を集約
            4. 全ての結果を結合して返す

        Usage Example:
        >>> results = checker.check_blacklist()
        >>> print(results)
        """
        reference_df = self.reference_searcher.df
        application_df = self.application_searcher.df

        results = []
        for rule in self.rules:
            mask = rule["condition"](reference_df, application_df)
            if not isinstance(mask, pd.Series) or mask.dtype != bool:
                error_msg = f"Rule '{rule['name']}' did not return a valid boolean mask."
                raise RuleApplicationError(error_msg) from None

            result = application_df[mask].copy()
            result["rule_name"] = rule["name"]
            results.append(result)

        return pd.concat(results, ignore_index=True) if results else pd.DataFrame()

    def refresh_data(self) -> None:
        """リファレンステーブルと申請テーブルのデータを更新する

        Return Value:
        None

        Algorithm:
            1. reference_searcherのデータを更新
            2. application_searcherのデータを更新

        Usage Example:
        >>> checker.refresh_data()
        """
        try:
            self.reference_searcher.refresh_data()
            self.application_searcher.refresh_data()
        except Exception as e:
            error_msg = f"Error refreshing data: {str(e)}"
            raise BlacklistCheckerError(error_msg) from e
