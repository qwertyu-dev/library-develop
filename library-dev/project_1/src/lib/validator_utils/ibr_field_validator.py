import re

# TODO(me) 消す予定
def name_must_contain_space(v: str)-> str:
    if ' ' not in v:
        raise ValueError('must contai a scpace')
    return v


# TODO(me) 消す予定
def username_alphanumeric(v: str) -> str:
    if not v.isapha():
        raise ValueError('must be alphanumeric')
    return v


class StringValidator:
    """文字列特性判定サポートクラス"""

    def __init__(self, text: str) -> bool:
        self.text = text

        # 定義
        self.halfwidth_range = 128

    def is_all_uppercase(self) -> bool:
        """文字列全てが大文字であるか

        Returns:
            bool : True 全てが大文字, False 条件を満たさない
        """
        return self.text.isupper()

    def is_all_halfwidth(self) -> bool:
        """文字列全てが半角であるか

        Returns:
            bool : True 全てが大文字, False 条件を満たさない
        """
        return all(ord(c) < self.halfwidth_range for c in self.text)

    def is_all_halfwidth_kana(self) -> bool:
        """文字列全てが半角カナであるか

            半角英数字: \uFF61 - \uFF9F
            ひらがな:   \uFF66 - \uFF9D
            カタカナ:   \uFF76 - \uFF9D

        Returns:
            bool : True 全てが大文字, False 条件を満たさない
        """
        return all(
            '\u30A1' <= c <= '\u30F4' or
            '\u30F7' <= c <= '\u30FC' or
            '\uFF66' <= c <= '\uFF9D' for c in self.text)
