"""アプリ個別定義の例外です

カスタム例外定義をここに実装します
"""
class BusinessLogicError(Exception):
    """ビジネスロジックに関連する基本的な例外クラス"""
    def __init__(self, message: str, error_code: str):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


