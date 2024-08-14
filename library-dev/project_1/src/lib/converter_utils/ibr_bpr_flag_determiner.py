class BprAdFlagDeterminer:
    """BPR・AD対象フラグを決定するクラス

    [前述のDocStringの内容はそのまま保持]
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
