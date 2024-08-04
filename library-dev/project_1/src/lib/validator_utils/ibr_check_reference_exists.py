import pandas as pd
from enum import IntEnum

class BranchCodeLength(IntEnum):
    """部店処理,課Gr処理判定定数: 部店コード長を想定"""
    BRANCH = 4
    SECTION_GR = 5

class CheckExistsRefferenceRecord:
    """リファレンスレコードの存在をチェックするクラス

    Class Overview:
        このクラスは、指定された部門コードに基づいて、利用申請明細（df_requests）とリファレンステーブル（df_refference）を
        照合し、対応するリファレンスレコードが存在するかどうかを確認します。部店、課、エリアの各レベルでのチェックと
        特別ケースの処理を行います。

    Attributes:
        special_case_checkers (list[SpecialCaseChecker]): 特別ケースのチェッカーリスト
        branch_code (str): 処理対象の部門コード
        matching_df_requests (pd.DataFrame): branch_codeに一致する利用申請明細

    Methods:
        proces_check_refference_data_exists(df_refference: pd.DataFrame) -> bool: メイン処理を実行
        _check_c_sw(df_refference: pd.DataFrame) -> bool: 初期チェックを実行
        _check_ref_find(df_refference: pd.DataFrame) -> bool: 詳細なリファレンス照合を実行
        _check_buten(df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool: 部店レベルのチェックを実行
        _check_ka(df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool: 課レベルのチェックを実行
        _check_area(df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool: エリアレベルのチェックを実行
        _check_special_cases(df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool: 特別ケースのチェックを実行

    Usage Example:
        >>> df_requests = pd.DataFrame({
        ...     'branch_code': ['1234', '5678'],
        ...     'target_org': ['部店', '課'],
        ...     'section_gr_code': ['A001', 'B002']
        ... })
        >>> df_refference = pd.DataFrame({
        ...     'branch_code_bpr': ['1234', '5678'],
        ...     'branch_code_jinji': ['1234', '5678'],
        ...     'section_gr_code_jinji': ['0', 'B002'],
        ...     'section_group_code_bpr': ['A001', 'B002']
        ... })

        # unique利用申請部店番号テーブル毎に呼び出しを想定
        # unique状態にした処理対象部店番号1つ,一括申請データからインスタンス生成
        >>> checker = CheckExistsRefferenceRecord('1234', df_requests)
        >>> result = checker.proces_check_refference_data_exists(df_refference)
        >>> #print(result)
        True

    Notes:
        - 特別ケースの追加は special_case_checkers リストに新しいチェッカーを追加することで可能です。

    Dependency:
        - pandas

    ResourceLocation:
        - 本体:
            - src/lib/validator_utils/ibr_check_exists_refference_record.py
        - テストコード:
            - tests/lib/validator_utils/test_ibr_check_exists_refference_record.py

    Todo:
        - エリアチェックの実装
        - パフォーマンスの最適化
        - 追加の特別ケースチェッカーの実装

    Change History:
    | No   | 修正理由   | 修正点   | 対応日     | 担当            |
    |------|------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/07/28 | xxxx aaa.bbb    |

    """
    def __init__(self, branch_code: str, df_requests: pd.DataFrame):
        """コンストラクタ

        Arguments:
        branch_code (str): 処理対象の部門コード
        df_requests (pd.DataFrame): 利用申請明細データ
        """
        if not isinstance(branch_code, str):
            raise TypeError("branch_code must be a string")
        if len(branch_code) not in [4, 5]:
            raise ValueError("branch_code must be either 4 or 5 digits")
        if not isinstance(df_requests, pd.DataFrame):
            raise TypeError("df_requests must be a pandas DataFrame")

        self.special_case_checkers: list[SpecialCaseChecker] = [
            Case7818Checker(),
            # 他の特別ケースチェッカーをここに追加
        ]
        self.branch_code: str = branch_code
        self.matching_df_requests: pd.DataFrame = self._set_matching_df_requests(df_requests)

    def _set_matching_df_requests(self, df_requests: pd.DataFrame) -> pd.DataFrame:
        """branch_codeに一致する利用申請明細を抽出

        Arguments:
        df_requests (pd.DataFrame): 全ての利用申請明細データ

        Return Value:
        pd.DataFrame: branch_codeに一致する利用申請明細
        """
        return df_requests[df_requests['branch_code'].apply(lambda x: x[:4] == self.branch_code[:4])]

    def proces_check_refference_data_exists(self, df_refference: pd.DataFrame) -> bool:
        """リファレンスデータの存在チェック処理を実行

        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ

        Return Value:
        bool: 処理結果(True: マッチング成功, False: マッチング失敗)

        Usage Example:
        >>> checker = CheckExistsRefferenceRecord('1234', df_requests)
        >>> result = checker.proces_check_refference_data_exists(df_refference)
        >>> #print(result)
        True
        """
        #if self._check_c_sw(df_refference):
        #    return self._check_ref_find(df_refference)
        #return False
        return self._check_ref_find(df_refference)

    #def _check_c_sw(self, df_refference: pd.DataFrame) -> bool:
    #    """初期チェックを実行

    #    どちらかがTrueであれば、Trueを返す
    #    - リファレンス.部店コード.bpr上位4桁 == 処理対象に合致する利用申請明細.部店コード.上位４桁
    #    - リファレンス.部店コード.jinji上位4桁 == 処理対象に合致する利用申請明細.部店コード.上位４桁

    #    Arguments:
    #    df_refference (pd.DataFrame): リファレンステーブルデータ

    #    Return Value:
    #    bool: チェック結果(True: 成功, False: 失敗)
    #    """
    #    if self.matching_df_requests.empty:
    #        return False

    #    # 前処理: branch_codeの先頭4文字を抽出
    #    ## リファレンステーブル
    #    df_refference_prefix = df_refference[['branch_code_bpr', 'branch_code_jinji']].apply(lambda x: x.str[:4])

    #    # unique指定部店コードに対応する利用申請明細
    #    matching_prefix = self.matching_df_requests['branch_code'].str[:4]

    #    # 一括チェック
    #    bpr_match = df_refference_prefix['branch_code_bpr'].isin(matching_prefix).any()
    #    jinji_match = df_refference_prefix['branch_code_jinji'].isin(matching_prefix).any()

    #    return bpr_match or jinji_match

    def _check_ref_find(self, df_refference: pd.DataFrame) -> bool:
        """詳細なリファレンス照合を実行

        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ

        Return Value:
        bool: 照合結果(True: マッチング成功, False: マッチング失敗)
        """
        check_methods = {
            "部店": self._check_buten,
            "課": self._check_ka,
            "エリア": self._check_area,
    }
        if self.matching_df_requests.empty:
            return False

        for _, df_requests_row in self.matching_df_requests.iterrows():
            # 特別ケース
            if self._check_special_cases(df_refference, df_requests_row):
                return True

            # 申請種類による対応
            check_method = check_methods.get(df_requests_row['target_org'])
            if check_method and check_method(df_refference, df_requests_row):
                    return True

        return False

#    def _check_buten(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool:
#        """部店レベルのチェックを実行
#    
#        Arguments:
#        df_refference (pd.DataFrame): リファレンステーブルデータ
#        df_requests_row (pd.Series): チェック対象の利用申請明細の1行
#    
#        Return Value:
#        bool: チェック結果(True: 成功, False: 失敗)
#        """
#        if len(df_requests_row['branch_code']) == BranchCodeLength.BRANCH:
#            matching_rows = df_refference.loc[df_refference['branch_code_bpr'] == df_requests_row['branch_code']]
#            # 複数の対象明細の内、1つでも0を持つ明細があればTrueを返す
#            return (matching_rows['section_gr_code_bpr'] == "0").any()
#
#        if len(df_requests_row['branch_code']) == BranchCodeLength.SECTION_GR:
#            matching_rows = df_refference.loc[df_refference['branch_code_jinji'] == df_requests_row['branch_code']]
#            return (matching_rows['section_gr_code_jinji'] == df_requests_row['section_gr_code']).any()
#
#        return False

    def _check_buten(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool:
        """部店レベルのチェックを実行
    
        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ
        df_requests_row (pd.Series): チェック対象の利用申請明細の1行
    
        Return Value:
        bool: チェック結果(True: 成功, False: 失敗)
        """
        branch_code_length = len(df_requests_row['branch_code'])
    
        if branch_code_length == BranchCodeLength.BRANCH:
            matching_rows = df_refference.loc[df_refference['branch_code_bpr'] == df_requests_row['branch_code']]
            # 複数の対象明細の内、1つでも0を持つ明細があればTrueを返す
            condition = (matching_rows['section_gr_code_bpr'] == "0")
            return condition.any()
    
        if branch_code_length == BranchCodeLength.SECTION_GR:
            matching_rows = df_refference.loc[df_refference['branch_code_jinji'] == df_requests_row['branch_code']]
            condition = (matching_rows['section_gr_code_jinji'] == df_requests_row['section_gr_code'])
            return condition.any()
    
        return False

#    def _check_ka(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool:
#        """課レベルのチェックを実行
#
#        Arguments:
#        df_refference (pd.DataFrame): リファレンステーブルデータ
#        df_requests_row (pd.Series): チェック対象の利用申請明細の1行
#
#        Return Value:
#        bool: チェック結果(True: 成功, False: 失敗)
#        """
#        if len(df_requests_row['branch_code']) == BranchCodeLength.BRANCH:
#            matching_rows = df_refference.loc[df_refference['branch_code_jinji'] == df_requests_row['branch_code']]
#            return (matching_rows['section_gr_code_jinji'] == df_requests_row['section_gr_code']).any()
#
#        if len(df_requests_row['branch_code']) == BranchCodeLength.SECTION_GR:
#            matching_rows = df_refference.loc[df_refference['branch_code_jinji'] == df_requests_row['branch_code']]
#            return (matching_rows['section_gr_code_jinji'] == df_requests_row['section_gr_code']).any()
#
#        return False
#
    def _check_ka(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool:
        """課レベルのチェックを実行
    
        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ
        df_requests_row (pd.Series): チェック対象の利用申請明細の1行
    
        Return Value:
        bool: チェック結果(True: 成功, False: 失敗)
        """
        branch_code_length = len(df_requests_row['branch_code'])
    
        if branch_code_length in [BranchCodeLength.BRANCH, BranchCodeLength.SECTION_GR]:
            matching_rows = df_refference.loc[df_refference['branch_code_jinji'] == df_requests_row['branch_code']]
            condition = (matching_rows['section_gr_code_jinji'] == df_requests_row['section_gr_code'])
            return condition.any()
    
        return False

    def _check_area(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool:
        """エリアレベルのチェックを実行

        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ
        df_requests_row (pd.Series): チェック対象の利用申請明細の1行

        Return Value:
        bool: チェック結果(True: 成功, False: 失敗)

        Note:
        エリアの場合、評価比較文字列に対して固有の条件設定があります
        - 判定条件: 利用申請.課Grコード(最上位１桁)+利用申請.常駐部店コード
        """
        matching_rows = df_refference.loc[df_refference['branch_code_jinji'] == df_requests_row['branch_code']]
        check_target_str = f"{df_requests_row['section_gr_code'][0]}{df_requests_row['resident_branch_code']}" # 利用申請.課Grコード(最上位１桁)+利用申請.常駐部店コード
        condition = (matching_rows['section_gr_code_jinji'] == check_target_str)
        return condition.any()

        return True

    def _check_special_cases(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> None:
        """特別ケースのチェックを実行

        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ
        df_requests_row (pd.Series): チェック対象の利用申請明細の1行

        Return Value:
        None: このメソッドは結果を返さず、各チェッカーを呼び出すだけです。
        """
        for checker in self.special_case_checkers:
            checker.check(df_refference, df_requests_row)

class SpecialCaseChecker:
    """特別ケースチェッカーのインターフェース

    このクラスは特別ケースのチェックを行うための基底クラスです。
    全ての特別ケースチェッカーはこのクラスを継承し、check メソッドを実装する必要があります。
    """

    def check(self, matching_df_refference: pd.DataFrame, df_requests_row: pd.Series, branch_code: str) -> bool:  # noqa: ARG002 インターフェース定義のため
        """特別ケースのチェックを実行

        Arguments:
        matching_df_refference (pd.DataFrame): リファレンステーブルデータ
        df_requests_row (pd.Series): チェック対象の利用申請明細の1行
        branch_code (str): 処理対象の部門コード

        Return Value:
        bool: チェック結果(True: 成功, False: 失敗)

        Raises:
        NotImplementedError: このメソッドは派生クラスで実装される必要があります
        """
        err_msg = "Subclasses must implement this method"
        raise NotImplementedError(err_msg)

class Case7818Checker(SpecialCaseChecker):
    """7818ケースのチェッカー

    特別ケース7818に対するチェックを実行します。
    """

    def check(self, df_refference: pd.DataFrame, df_requests_row: pd.Series) -> bool:
        """7818ケースのチェックを実行

        Arguments:
        df_refference (pd.DataFrame): リファレンステーブルデータ
        df_requests_row (pd.Series): チェック対象の利用申請明細の1行

        Return Value:
        bool: チェック結果(True: 成功, False: 失敗)
        """
        # 1. 左から4文字が "7818" であるデータを抽出
        filtered_df = df_refference.loc[df_refference['section_gr_code_bpr'].str[:4] == "7818"]

        # 2. 抽出されたデータに対して、section_gr_code_bpr と section_gr_code を比較
        if (filtered_df['section_gr_code_bpr'] == df_requests_row['section_gr_code']).any():
            return True

        return False

#----------------------------------------------------------------
# 以下、消す
#----------------------------------------------------------------

# サンプルデータの作成
def create_sample_data() -> (pd.DataFrame, pd.DataFrame):
    # 利用申請明細(RJ)のサンプルデータ
    rj_data = {
        'branch_code': ['1234', '1235', '1234', '5678', '9012'],
        'target_org': ['部店', '課', 'エリア', '部店', '課'],
        'section_gr_code': ['A001', 'B002', 'C003', 'D004', '7818x'],
    }
    rj_df = pd.DataFrame(rj_data)

    # リファレンステーブル(RT)のサンプルデータ
    rt_data = {
        'branch_code_bpr': ['1234', '5678', '9012', '3456', '7890'],
        'branch_code_jinji': ['1234', '5679', '9012', '3457', '7891'],
        'section_gr_code_bpr': ['0', 'B002', '9012', 'D004', '7818'],
        'section_gr_code_jinji': ['A001', 'B002', '7818x', '7818x', '7818'],
        'area_code': ['X001', 'X002', 'X003', 'X004', 'X005'],
    }
    rt_df = pd.DataFrame(rt_data)
    print(rj_df)
    print(rt_df)

    return rj_df, rt_df

def test_department_processor() -> None:
    rj_df, rt_df = create_sample_data()

    ## テストケース1: hi_dept_code = '1234'
    processor1 = CheckExistsRefferenceRecord('1234', rj_df)
    result1 = processor1.proces_check_refference_data_exists(rt_df)
    print(f"Test case 1 (hi_dept_code='1234'): {result1}")

    # テストケース2: hi_dept_code = '5678'
    processor2 = CheckExistsRefferenceRecord('5678', rj_df)
    result2 = processor2.proces_check_refference_data_exists(rt_df)
    print(f"Test case 2 (hi_dept_code='5678'): {result2}")

    # テストケース3: hi_dept_code = '9012'
    processor3 = CheckExistsRefferenceRecord('9012', rj_df)
    result3 = processor3.proces_check_refference_data_exists(rt_df)
    print(f"Test case 3 (hi_dept_code='9012'): {result3}")

    # テストケース4: hi_dept_code = '3456' (マッチする利用申請明細なし)
    processor4 = CheckExistsRefferenceRecord('3456', rj_df)
    result4 = processor4.proces_check_refference_data_exists(rt_df)
    print(f"Test case 4 (hi_dept_code='3456'): {result4}")

# メイン実行
if __name__ == "__main__":
    test_department_processor()
