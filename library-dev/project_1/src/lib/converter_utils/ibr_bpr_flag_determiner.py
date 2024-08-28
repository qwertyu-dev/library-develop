class BprAdFlagDeterminer:
    """BPR・AD対象フラグを決定するクラス

    Class Overview:
        このクラスは、銀行の部署情報に基づいてBPR・AD対象フラグを決定するロジックを実装します。
        新設、変更、廃止の各処理タイプに対応し、部店コードや課Gコードなどの条件に基づいて
        適切なフラグを設定します。また、特定の条件下でアラートを生成します。

    Attributes:
        SPECIFIC_WORDS (list): 特定の単語のリスト（'米州', '欧州', 'アジア'）
        reference_data (dict): リファレンスデータを保持する辞書

    Condition Information:
        - Condition:1
            - ID: NEW_DEPARTMENT
            - Type: 新設判定
            - Applicable Scenarios: 部署の新設時のフラグ決定
        - Condition:2
            - ID: CHANGE_OR_DELETE
            - Type: 変更・廃止判定
            - Applicable Scenarios: 部署の変更または廃止時のフラグ決定
        - Condition:3
            - ID: INTERNATIONAL_DEPARTMENT
            - Type: 国際部署判定
            - Applicable Scenarios: 国際事務企画部からの申請で部店コードが'6'で始まる場合
        - Condition:4
            - ID: DEPARTMENT_CODE_012
            - Type: 国内一般部署判定
            - Applicable Scenarios: 部店コードが'0', '1', '2'で始まる場合
        - Condition:5
            - ID: DEPARTMENT_CODE_3
            - Type: 海外部署判定
            - Applicable Scenarios: 部店コードが'3'で始まる場合
        - Condition:6
            - ID: DEPARTMENT_CODE_7172
            - Type: 特定関連会社判定
            - Applicable Scenarios: 部店コードが'71'または'72'で始まる場合
        - Condition:7
            - ID: DEPARTMENT_CODE_OTHER_7X
            - Type: その他関連会社判定
            - Applicable Scenarios: 部店コードが'70', '73', '74', '75', '76', '77', '78', '79'で始まる場合
        - Condition:8
            - ID: DEPARTMENT_CODE_9
            - Type: 特殊コード判定
            - Applicable Scenarios: 部店コードが'9'で始まる場合

    Pattern Information:
        - Pattern:1
            - ID: WITH_GROUP
            - Type: 課Gコード有りパターン
            - Applicable Scenarios: 課Gコードが存在する部署のフラグ決定
            - Details:
                - 部店コードが'6'で始まり、課G名に特定単語を含む場合: 'ADのみ'（要確認アラート）
                - 部店コードが'0', '1', '2', '6'で始まる場合: '対象'
                - 部店コードが'3'で始まる場合: 'ADのみ'
                - その他: '対象外'
        - Pattern:2
            - ID: WITHOUT_GROUP
            - Type: 課Gコード無しパターン
            - Applicable Scenarios: 課Gコードが存在しない部署のフラグ決定
            - Details:
                - 部店コードが'71', '72'で始まる場合: '対象'
                - 部店コードが'70', '73', '74', '75', '76', '77', '78', '79'で始まる場合: '対象外'（要確認アラート）
                - 部店コードが'9'で始まる場合: '対象外'（要確認アラート）
                - その他: '対象外'

    Methods:
        determine_bpr_ad_flag(application_type, applicant, department_code, group_code, group_name): 
            BPR・AD対象フラグを決定する主要メソッド

    StaticMethods:
        このクラスにはスタティックメソッドは定義されていません。

    Usage Example:
        >>> determiner = BprAdFlagDeterminer()
        >>> result, alert = determiner.determine_bpr_ad_flag('新設', '国企', '600001', '001', '米州営業部')
        >>> print(f"フラグ: {result}, アラート: {alert}")
        フラグ: ADのみ, アラート: 要確認: 課G名に特定の単語を含む

    Notes:
        - リファレンスデータの更新と取得には別途メソッドを使用してください。
        - 特定の条件下では要確認アラートが生成されるため、結果を注意深く確認してください。
        - 部店コードと課Gコードの組み合わせによって、異なるフラグ設定とアラート生成が行われます。

    Dependency:
        - 標準ライブラリのみを使用しています。外部依存はありません。

    ResourceLocation:
        - 本体:
            - src/models/bpr_ad_flag_determiner.py
        - テストコード:
            - tests/models/test_bpr_ad_flag_determiner.py

    Todo:
        - リファレンスデータの永続化機能の追加
        - より詳細なログ出力機能の実装
        - パフォーマンス最適化の検討
        - 新たな部店コードパターンへの対応

    Change History:
    | No   | 修正理由                       | 修正点                                   | 対応日     | 担当     |
    |------|--------------------------------|------------------------------------------|------------|----------|
    | v0.1 | 初期定義作成                   | クラスの基本構造と主要機能の実装         | 2024/07/20 | John Doe |
    | v0.2 | 詳細な判定条件の追加           | DocStringに細かい判定条件の情報を追加    | 2024/07/21 | Jane Doe |
    """

    SPECIFIC_WORDS = ['米州', '欧州', 'アジア']

    def __init__(self):
        """コンストラクタ

        Arguments:
            このコンストラクタは引数を取りません。
        """
        self.reference_data: dict = {}

    def is_specific_word_in_group_name(self, group_name: str) -> bool:
        """課G名に特定の単語が含まれているかをチェックする

        Arguments:
        group_name (str): チェック対象の課G名

        Return Value:
        bool: 特定の単語が含まれている場合はTrue、そうでない場合はFalse
        """
        return any(word in group_name for word in self.SPECIFIC_WORDS)

    def determine_flag_for_new_department_with_group(self, department_code: str, group_name: str) -> tuple[str, str | None]:
        """課Gコードがある場合の新設部署のフラグを決定する

        Arguments:
        department_code (str): 部店コード
        group_name (str): 課G名

        Return Value:
        tuple[str, str|None]: (フラグ値, アラートメッセージ)
        """
        if department_code.startswith('6') and self.is_specific_word_in_group_name(group_name):
            return 'ADのみ', '要確認: 課G名に特定の単語を含む'
        if department_code[0] in '0126':
            return '対象', None
        if department_code.startswith('3'):
            return 'ADのみ', None
        return '対象外', None

    def determine_flag_for_new_department_without_group(self, department_code: str) -> tuple[str, str|None]:
        """課Gコードがない場合の新設部署のフラグを決定する

        Arguments:
        department_code (str): 部店コード

        Return Value:
        tuple[str, str|None]: (フラグ値, アラートメッセージ)
        """
        if department_code.startswith(('71', '72')):
            return '対象', None
        if department_code[:2] in ['70', '73', '74', '75', '76', '77', '78', '79']:
            return '対象外', '要確認: MUFG以外の関連会社の可能性'
        if department_code.startswith('9'):
            return '対象外', '要確認: 特殊なコード'
        return '対象外', None

    def determine_bpr_ad_flag(self, application_type: str, applicant: str, department_code: str,
                            group_code: str|None = None, group_name: str|None = None) -> tuple[str,str|None]:
        """BPR・AD対象フラグを決定する

        Arguments:
        application_type (str): 処理タイプ(g'新設', '変更', '廃止')
        applicant (str): 申請元(g'国企' or その他)
        department_code (str): 部店コード
        group_code (Optional[str]): 課Gコード(gデフォルト: None)
        group_name (Optional[str]): 課G名(gデフォルト: None)

        Return Value:
        tuple[str, str|None]: (フラグ値, アラートメッセージ)

        Raises:
        ValueError: 無効な処理タイプが指定された場合
        """
        if application_type in ['変更', '廃止']:
            return self.get_reference_value(department_code, group_code), None

        if application_type != '新設':
            err_msg = "無効な処理タイプです。'新設', '変更', '廃止'のいずれかを指定してください。"
            raise ValueError(err_msg) from None

        if applicant == '国企' and department_code.startswith('6'):
            return 'ADのみ', None

        if group_code:
            if group_name is None:
                err_msg = "課Gコードが指定されている場合、課G名も必須です。"
                raise ValueError(err_msg) from None
            return self.determine_flag_for_new_department_with_group(department_code, group_name)
        return self.determine_flag_for_new_department_without_group(department_code)

    def get_reference_value(self, department_code: str, group_code: str|None) -> str:
        """リファレンスデータから値を取得する

        Arguments:
        department_code (str): 部店コード
        group_code (str|None): 課Gコード

        Return Value:
        str: リファレンス情報の値
        """
        key = (department_code, group_code)
        return self.reference_data.get(key, 'リファレンス情報なし')

    def update_reference_data(self, department_code: str, group_code: str, value: str) -> None:
        """リファレンスデータを更新する

        Arguments:
        department_code (str): 部店コード
        group_code (str): 課Gコード
        value (str): 設定する値

        Return Value:
        None
        """
        key = (department_code, group_code)
        self.reference_data[key] = value

# 使用例
#if __name__ == "__main__":
#    determiner = BprAdFlagDeterminer()
#
#    # リファレンスデータの更新例
#    determiner.update_reference_data('600001', '001', '対象')
#
#    # フラグ判定例
#    try:
#        result, alert = determiner.determine_bpr_ad_flag('新設', '国企', '600001', '001', '米州営業部')
#        print(f"フラグ: {result}, アラート: {alert}")
#
#        # 変更時のフラグ判定例
#        result, alert = determiner.determine_bpr_ad_flag('変更', '国企', '600001', '001')
#        print(f"フラグ: {result}, アラート: {alert}")
#
#        # エラーケース
#        result, alert = determiner.determine_bpr_ad_flag('無効なタイプ', '国企', '600001')
#    except ValueError as e:
#        print(f"エラー: {str(e)}")
