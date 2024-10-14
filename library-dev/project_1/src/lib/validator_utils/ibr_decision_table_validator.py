# ディシジョンテーブルに書く条件判定関数
# いずれも戻り値はboolである
import pandas as pd
import numpy as np
from typing import Any
from dataclasses import dataclass

@dataclass(frozen=True)
class DTConstants:
    """桁数判定固定値定義"""
    # ４桁
    DIGIT4_LEN: int = 4
    DIGIT4_MIN: int = 1000
    DIGIT4_MAX: int = 9999
    # 5桁
    DIGIT5_LEN: int = 5
    DIGIT5_MIN: int = 10000
    DIGIT5_MAX: int = 99999

class DT:
    """ディシジョンテーブル処理用のクラス

    このクラスは、DataFrameに格納されたディシジョンテーブルを処理するための
    メソッドを提供します。ディシジョンテーブル上では 'DT.method_name' の形式で
    関数を参照します。

    Methods:
        is_4digits(value): 値が4桁の文字列かどうかを判定
        is_5digits(value): 値が5桁の文字列かどうかを判定
        is_empty(value): 値が空かどうかを判定
        is_not_empty(value): 値が空でないかどうかを判定

    Decisionテーブル記述:
        DT.is_4digits のように関数名称を記述する、関数()は記載しない

    """
    constants = DTConstants()

    ############################################
    # preparation editor/pattern editor 共通
    ############################################
    @staticmethod
    def is_4digits(value: str|int) -> bool:
        """値が4桁の文字列/数値かどうかを判定"""
        if isinstance(value, str):
            return len(value) == DT.constants.DIGIT4_LEN and value.isdigit()
        if isinstance(value, int|float):
            return DT.constants.DIGIT4_MIN <= value <= DT.constants.DIGIT4_MAX
        return False

    @staticmethod
    def is_5digits(value: str|int) -> bool:
        """値が5桁の文字列/数値かどうかを判定"""
        if isinstance(value, str):
            return len(value) == DT.constants.DIGIT5_LEN and value.isdigit()
        if isinstance(value, int|float):
            return DT.constants.DIGIT5_MIN <= value <= DT.constants.DIGIT5_MAX
        return False

    @staticmethod
    def is_empty(value) -> bool:
        """値が空かどうかを判定"""
        return pd.isna(value) or (isinstance(value, str) and value.strip() == '')

    @staticmethod
    def is_not_empty(value) -> bool:
        """値が空でないかどうかを判定"""
        return not DT.is_empty(value)

    ############################################
    # for preparation editor
    ############################################
    # preparation: 個別のものはないのです

    ############################################
    # for pattern editor
    ############################################
    # TODO(member): 各判定関数の実装
    @staticmethod
    def has_parent_code_and_matching_first_4_digits(value) -> bool:
        """あり、＝部店コード前方4桁"""
        # valueに対し,親部店判定により存在確認
        # 親部店に対し,value前方4桁が一致する
        return True

    @staticmethod
    def has_parent_code_and_not_matching_first_4_digits(value) -> bool:
        """あり、≠部店コード前方4桁"""
        # valueに対し,親部店判定により存在確認
        # 親部店に対し,value前方4桁が一致しない
        return True

    @staticmethod
    def is_bpr_ad_target(value) -> bool:
        """BPR・AD対象"""
        # valueの値比較
        return True

    @staticmethod
    def is_not_bpr_ad_target(value) -> bool:
        """BPR・AD対象外"""
        # valueの値比較
        return True

    @staticmethod
    def is_not_bpr_ad_target_and_is_ad_only_target(value) -> bool:
        """BPR・AD対象外,ADのみ対象"""
        # valueの値比較
        return True



