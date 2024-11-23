"""リファレンス一意探索向けの条件/Key定義"""
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar, TypeAlias

import pandas as pd

from src.lib.common_utils.ibr_enums import (
    BranchCodeLength,
    FormType,
    OrganizationType,
    PatternID,
    PatternPriority,
)

# 型エイリアスの定義
TargetCondition: TypeAlias = Callable[[pd.DataFrame], pd.Series]
ReferenceKeys: TypeAlias = dict[str, str | Callable]  # area_codeの処理で関数も許容

@dataclass(frozen=True)
class MatchingPattern:
    """マッチングパターンの定義"""
    #pattern_id: int
    description: str
    target_condition: TargetCondition
    reference_keys: ReferenceKeys
    fixed_conditions: dict[str, str] | None = None
    priority: int = 999  # デフォルトの優先順定義

@dataclass(frozen=True)
class PatternDefinitions:
    """マッチングパターンの定義を管理"""
    # 共通の条件をクラス変数として定義
    STANDARD_FORM_TYPES: ClassVar[list[int]] = [
        FormType.JINJI.value,
        FormType.KOKUKI.value,
        FormType.KANREN_WITH_DUMMY.value,
    ]

    @staticmethod
    def get_all_patterns() -> list[MatchingPattern]:
        """優先順位付きの全パターンの定義を取得"""
        patterns = [
            PatternDefinitions._pattern_branch_7818(),
            PatternDefinitions._pattern_branch_4digit(),
            PatternDefinitions._pattern_branch_5digit_7(),
            PatternDefinitions._pattern_branch_5digit_non7(),
            PatternDefinitions._pattern_internal_sales(),
            PatternDefinitions._pattern_related_dummy(),
            PatternDefinitions._pattern_section(),
            PatternDefinitions._pattern_area(),
        ]
        # 優先順位でソート
        return sorted(patterns, key=lambda x: x.priority)

    @staticmethod
    def _pattern_branch_4digit() -> MatchingPattern:
        """4桁部店コードのパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.BRANCH_4DIGIT.value),
            description="4桁部店コード処理",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.BRANCH.value) &
                (df['branch_code'].str.len() == int(BranchCodeLength.BRANCH_LENGTH_4.value))
            ),
            reference_keys={'branch_code_jinji': 'branch_code'},
            fixed_conditions={'section_gr_code_bpr': '0'},
            priority=int(PatternPriority.BRANCH_4DIGIT.value),
        )

    @staticmethod
    def _pattern_branch_7818() -> MatchingPattern:
        """7818系部店コードのパターンcase1"""
        return MatchingPattern(
            #pattern_id=int(PatternID.BRANCH_7818.value),
            description="7818系部店コード処理case1",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.BRANCH.value) &
                (df['branch_code'].str.startswith('7818'))
            ),
            reference_keys={'branch_code_jinji': 'branch_code'},
            fixed_conditions={'section_gr_code_jinji': ''},
            priority=int(PatternPriority.BRANCH_7818.value),
        )

    @staticmethod
    def _pattern_branch_5digit_non7() -> MatchingPattern:
        """5桁部店コード(7以外始まり)のパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.BRANCH_5DIGIT_NON7.value),
            description="5桁部店コード(7以外始まり)処理",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.BRANCH.value) &
                (df['branch_code'].str.len() == int(BranchCodeLength.BRANCH_LENGTH_5.value)) &
                (~df['branch_code'].str.startswith('7')) # 7スタート以外、否定判定
            ),
            reference_keys={'branch_code_jinji': 'branch_code'},
            fixed_conditions={'section_gr_code_jinji': ''},
        priority=int(PatternPriority.BRANCH_5DIGIT_NON7.value),
        )

    @staticmethod
    def _pattern_branch_5digit_7() -> MatchingPattern:
        """5桁部店コード(7始まり)のパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.BRANCH_5DIGIT_7.value),
            description="5桁部店コード(7始まり)処理",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.BRANCH.value) &
                (df['branch_code'].str.len() == int(BranchCodeLength.BRANCH_LENGTH_5.value)) &
                (df['branch_code'].str.startswith('7')) # 7スタート
            ),
            reference_keys={
                'branch_code_jinji': 'branch_code',
                'section_gr_code_bpr': 'branch_code',
            },
            priority=int(PatternPriority.BRANCH_5DIGIT_7.value),
        )

    @staticmethod
    def _pattern_internal_sales() -> MatchingPattern:
        """拠点内営業部のパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.INTERNAL_SALES.value),
            description="拠点内営業部処理",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.INTERNAL_SALES.value)
            ),
            reference_keys={
                'branch_code_jinji': 'branch_code_digits4', # 上位4桁部店コードColを生成している,これを使う
                'section_gr_code_jinji': 'branch_code',
            },
            priority=int(PatternPriority.INTERNAL_SALES.value),
        )

    @staticmethod
    def _pattern_related_dummy() -> MatchingPattern:
        """関連ダミー課なし.課処理のパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.RELATED_DUMMY.value),
            description="関連ダミー課なし.課処理",
            target_condition=lambda df: (
                (df['form_type'] == FormType.KANREN_WITHOUT_DUMMY.value) &
                (df['target_org'] == OrganizationType.SECTION_GROUP.value)
            ),
            reference_keys={
                'branch_code_jinji': 'branch_code',
                'section_gr_code_bpr': 'section_gr_code',
            },
            priority=int(PatternPriority.RELATED_DUMMY.value),
        )


    @staticmethod
    def _pattern_section() -> MatchingPattern:
        """課処理のパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.SECTION_GROUP.value),
            description="課処理",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.SECTION_GROUP.value)
            ),
            reference_keys={
                'branch_code_jinji': 'branch_code',
                'section_gr_code_jinji': 'section_gr_code',
            },
            priority=int(PatternPriority.SECTION_GROUP.value),
        )

    @staticmethod
    def _pattern_area() -> MatchingPattern:
        """エリア処理のパターン"""
        return MatchingPattern(
            #pattern_id=int(PatternID.AREA.value),
            description="エリア処理",
            target_condition=lambda df: (
                (df['form_type'].isin(PatternDefinitions.STANDARD_FORM_TYPES)) &
                (df['target_org'] == OrganizationType.AREA.value)
            ),
            reference_keys={
                'branch_code_jinji': 'branch_code',
                'business_code': 'business_and_area_code_first',  # 分割したareaコード1桁目
                'area_code': 'business_and_area_code_rest',       # 分割したareaコード2桁目以降
            },
            priority=int(PatternPriority.AREA.value),
        )


