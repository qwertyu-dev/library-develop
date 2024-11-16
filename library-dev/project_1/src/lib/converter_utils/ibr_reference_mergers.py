import re
import sys
from dataclasses import dataclass
from typing import ClassVar, TypedDict

import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import ApplicationType, LogLevel, OrganizationType

#from src.lib.common_utils.ibr_logger_helper import format_dict
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.converter_utils.ibr_excel_field_analyzer import RemarksParser

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

# 備考欄解析: 構造定義
class AreaGroupInfo(TypedDict):
    """エリアグループ情報"""
    group_code: str
    group_name: str
    established_date: str

class SalesDepartmentInfo(TypedDict):
    """営業部門情報"""
    department_name: str
    branch_name: str

class ParsedRemarks(TypedDict):
    """備考欄解析結果"""
    request_type: str
    sales_department: SalesDepartmentInfo
    area_group: AreaGroupInfo
    other_info: str

# データ探索: 固定値定義
@dataclass(frozen=True)
class MergerConfig:
    """ReferenceMergersの設定値"""
    DEFAULT_LAYOUT_FILE: ClassVar[str] = 'integrated_layout.pkl'
    REFERENCE_TABLE_FILE: ClassVar[str] = 'reference_table.pkl'
    BRANCH_CODE_LENGTH: ClassVar[int] = 4
    #BRANCH_NAME_PATTERN: ClassVar[str] = r'^(.+?支店)(.*)$'
    BRANCH_NAME_PATTERN: ClassVar[str] = r'^(.*?支店)(.*)$'
    REFERENCE_PREFIX: ClassVar[str] = 'branch_reference_'

    # リファレンステーブルのカラム名マッピング
    REFERENCE_COLUMNS_MAPPING_BPR: ClassVar[dict[str, str]] = {
        'branch_code_bpr': f'{REFERENCE_PREFIX}branch_code_bpr',
        'branch_name_bpr': f'{REFERENCE_PREFIX}branch_name_bpr',
        'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
        'organization_name_kana': f'{REFERENCE_PREFIX}organization_name_kana',
    }

    #REFERENCE_COLUMNS_MAPPING_JINJI: ClassVar[dict[str, str]] = {
    #    'branch_code_jinji': f'{REFERENCE_PREFIX}branch_code_jinji',
    #    'branch_name_jinji': f'{REFERENCE_PREFIX}branch_name_jinji',
    #    'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
    #    'organization_name_kana': f'{REFERENCE_PREFIX}organization_name_kana',
    #}

class ReferenceMergersError(Exception):
    """ReferenceMergerの基底例外クラス"""

class DataLoadError(ReferenceMergersError):
    """データ読み込みエラー"""

class DataMergeError(ReferenceMergersError):
    """データマージエラー"""

class BranchNameSplitError(ReferenceMergersError):
    """部店名称分割処理エラー"""

class RemarksParseError(ReferenceMergersError):
    """備考欄解析エラー"""

class ReferenceMergers:
    """統合レイアウトデータとリファレンステーブルのマージを行うクラス"""

    #######################################################
    # データ編集 提供メソッド群
    #######################################################
    @staticmethod
    def merge_zero_group_parent_branch(integrated_layout: pd.DataFrame, reference_table: pd.DataFrame) -> pd.DataFrame:
        """統合レイアウトデータにリファレンステーブルの情報をマージする

        * 部店グループ: 課Grコード'0'を保有する明細の情報を取得する
        * 該当するリファレンスレコードの部店コードColumnを申請レコードに付与する
        * 該当するリファレンスレコードの部名称Columnを申請レコードに付与する
        * 該当するリファレンスレコードの親部店コード値があれば申請レコードをColumn付与する、なければブランク
        * 申請レコードに追加するColumnには一律reference_接頭辞を付与する
        * reference_parent_branch_codeとreference_parent_branch_codeが無い場合は空文字で列生成する

        Args:
            integrated_layout: 統合レイアウトデータ
            reference_table: リファレンステーブル

        Returns:
            pd.DataFrame: マージされたデータフレーム

        Raises:
            DataMergeError: マージ処理に失敗した場合
        """
        try:
            # データの検証
            required_columns = {
                'left': ['branch_code'],
                'right': ['branch_code_bpr', 'section_gr_code_bpr'],
            }
            ReferenceMergers._validate_merge_data(integrated_layout, reference_table, required_columns)

            # 部店コードの上位4桁を取得
            result_df = integrated_layout.copy()
            result_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(result_df, 'branch_code')
            reference_table['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(reference_table, 'branch_code_bpr')

            # リファレンステーブルのフィルタリングとリネーム
            filtered_reference = (
                reference_table[reference_table['section_gr_code_bpr'] == '0']
                .rename(columns=MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR)
            )
            log_msg('リファンレンス.課Grコード=="0"抽出\n')
            log_msg(f'{tabulate_dataframe(filtered_reference)}', LogLevel.DEBUG)

            # マージ処理
            merge_columns = [
                'branch_code_prefix',
                *MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values(),
            ]
            merged_df = result_df.merge(
                filtered_reference[merge_columns],
                on='branch_code_prefix',
                how='left',
            ).fillna('')

            # reference_parent_branch_codeとreference_parent_branch_codeが無い場合は空文字で列生成
            if 'branch_reference_parent_branch_code' not in merged_df.columns:
                merged_df['branch_reference_parent_branch_code'] = ''

            # 不要カラムの削除
            result_df = merged_df.drop(columns=['branch_code_prefix'])

            log_msg("マージ結果:\n", LogLevel.DEBUG)
            tabulate_dataframe(result_df)

        except Exception as e:
            err_msg = f"課Grコード=='0'レコードからの付与/親部店情報のマージ処理でエラーが発生しました: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e

        else:
            return result_df


    @staticmethod
    def _extract_branch_code_prefix(df: pd.DataFrame, column: str) -> pd.Series:
        """部店コードの上位4桁を取得する"""
        return df[column].str[:MergerConfig.BRANCH_CODE_LENGTH]

    @staticmethod
    def _split_branch_name_regex(name: str) -> tuple[str, str]:
        """支店名と営業部名の分割処理

        '支店'で支店名と営業部名を分割する

        Args:
            name: 分割対象の部店名称

        Returns:
            tuple[str, str]: (支店名, 営業部名)のtuple
        """
        if pd.isna(name):
            return (name, name)

        match = re.match(MergerConfig.BRANCH_NAME_PATTERN, name)
        if match:
            return (match.group(1), match.group(2).strip())
        return (name, '')

    #######################################################
    # Debugger
    #######################################################
    @staticmethod
    def _validate_merge_data(
        left_df: pd.DataFrame,
        right_df: pd.DataFrame,
        required_columns: dict[str, list[str]],
    ) -> None:
        """マージデータのバリデーション

        Args:
            left_df: 左側DataFrame
            right_df: 右側DataFrame
            required_columns: 必要なカラム名の辞書

        Raises:
            ValueError: 入力チェックエラー
        """
        if left_df.empty or right_df.empty:
            err_msg = "Empty DataFrame provided"
            raise ValueError(err_msg) from None

        missing_left = set(required_columns['left']) - set(left_df.columns)
        missing_right = set(required_columns['right']) - set(right_df.columns)

        if missing_left or missing_right:
            err_msg = f"Missing columns: left={missing_left}, right={missing_right}"
            raise ValueError(err_msg) from None

#    @staticmethod
#    def _get_nested_dict_value(data: dict, field_path: str) -> dict:
#        """ネストされた辞書から値を取得
#
#        Args:
#            data: 対象の辞書
#            field_path: ドット区切りのフィールドパス
#
#        Returns:
#            Any: 取得した値
#        """
#        current = data
#        for key in field_path.split('.'):
#            current = current[key]
#        return current
#
#    @staticmethod
#    def _log_bpr_flag_results(df: pd.DataFrame) -> None:
#        """BPRADフラグ付与結果のログ出力
#
#        Args:
#            df: 処理結果のDataFrame
#        """
#        display_columns = [
#            'branch_code', 'section_gr_code', 'area_code',
#            'application_type', 'bpr_target_flag', 'reference_bpr_target_flag',
#        ]
#
#        # 全体結果
#        log_msg("処理結果全体:\n")
#        tabulate_dataframe(df[display_columns])
#
#        # 新設/新設以外の内訳
#        new_data = df[df['application_type'] == ApplicationType.NEW.value]
#        non_new_data = df[df['application_type'] != ApplicationType.NEW.value]
#
#        log_msg(f"新設データ ({len(new_data)}件):\n", LogLevel.DEBUG)
#        tabulate_dataframe(new_data[display_columns])
#        log_msg(f"新設以外データ ({len(non_new_data)}件):\n", LogLevel.DEBUG)
#        tabulate_dataframe(non_new_data[display_columns])
#
#
#    @staticmethod
#    def _log_parsed_remarks_results(parsed_series: pd.Series) -> None:
#        """備考欄解析結果のログ出力
#
#        Args:
#            parsed_series: 解析済みのSeries
#        """
#        debug_fields = [
#            'request_type',
#            'sales_department.department_name',
#            'sales_department.branch_name',
#            'area_group.group_code',
#            'area_group.group_name',
#            'area_group.established_date',
#            'other_info',
#        ]
#
#        for field in debug_fields:
#            try:
#                value = parsed_series.apply(lambda x, f=field: ReferenceMergers._get_nested_dict_value(x, f))
#                log_msg(f"{field}: {value}", LogLevel.DEBUG)
#            except Exception as e:
#                err_msg = f"デバッグ情報の出力でエラーが発生しました - {field}: {str(e)}"
#                log_msg(err_msg, LogLevel.ERROR)
#