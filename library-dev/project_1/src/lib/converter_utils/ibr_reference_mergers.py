import re
import sys
from dataclasses import dataclass
from typing import ClassVar, TypedDict

import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import  LogLevel, OrganizationType

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

# データ探索: 固定値定義
@dataclass(frozen=True)
class MergerConfig:
    """ReferenceMergersの設定値"""
    BRANCH_CODE_LENGTH: ClassVar[int] = 4
    REFERENCE_PREFIX: ClassVar[str] = 'branch_reference_'
    INTEGRATED_PREFIX: ClassVar[str] = 'branch_integrated_'

    # リファレンステーブルのカラム名マッピング
    REFERENCE_COLUMNS_MAPPING_BPR: ClassVar[dict[str, str]] = {
        'branch_code_bpr': f'{REFERENCE_PREFIX}branch_code_bpr',
        'branch_name_bpr': f'{REFERENCE_PREFIX}branch_name_bpr',
        'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
        'organization_name_kana': f'{REFERENCE_PREFIX}organization_name_kana',
    }

    INTEGRATED_COLUMNS_MAPPING: ClassVar[dict[str, str]] = {
        'branch_code': f'{INTEGRATED_PREFIX}branch_code',
        'branch_name': f'{INTEGRATED_PREFIX}branch_name',
        'parent_branch_code': f'{INTEGRATED_PREFIX}parent_branch_code',
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
    def merge_zero_group_parent_branch_with_self(integrated_layout: pd.DataFrame) -> pd.DataFrame:
        """統合レイアウトデータへ,自身の所属部店グループにある部店明細の情報を探索しその情報をColumn付与する

        * 部店グループ: 対象: 部店を保有する明細の情報を取得する
        * 該当するリファレンスレコードの部店コードColumnを申請レコードに付与する
        * 該当するリファレンスレコードの部名称Columnを申請レコードに付与する
        * 該当するリファレンスレコードの親部店コード値があれば申請レコードをColumn付与する、なければブランク
        * 申請レコードに追加するColumnには一律 branch_integrated_ 接頭辞を付与する
        * 付与Columnのデフォルト値は空文字で生成する

        Args:
            integrated_layout: 統合レイアウトデータ

        Returns:
            pd.DataFrame: マージされたデータフレーム

        Raises:
            DataMergeError: マージ処理に失敗した場合
        """
        try:
            integrated_df = integrated_layout.copy()
            integrated_self_df = integrated_layout.copy()

            # マージキーColumn生成
            integrated_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(integrated_df, 'branch_code')
            integrated_self_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(integrated_self_df, 'branch_code')
            # 対象データの絞り込み/columnリネーム
            filtered_integrated_self_df = ReferenceMergers._filter_branch_data(integrated_self_df)
            # マージ処理
            merged_df = ReferenceMergers._perform_merge(integrated_df, filtered_integrated_self_df)
            # 欠落Columnの初期値付与/不要Columnの削除
            result_df = ReferenceMergers._clean_up_merged_data(merged_df)

            ReferenceMergers._log_merge_result(result_df)

        except Exception as e:
            err_msg = f"Error in merging branch records: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

        #try:
        #    # 部店コードの上位4桁を取得
        #    integrated_df = integrated_layout.copy()
        #    integrated_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(integrated_df, 'branch_code')

        #    # 申請明細の抽出
        #    filtered_result = (
        #        integrated_df[integrated_df['target_org'] == OrganizationType.BRANCH ]
        #        #.rename(columns=MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR)
        #        .rename(columns=MergerConfig.INTEGRATED_COLUMNS_MAPPING)
        #    )
        #    log_msg('一括申請.部店明細 抽出\n')
        #    log_msg(f'{tabulate_dataframe(filtered_result)}', LogLevel.DEBUG)

        #    # マージ処理
        #    merge_columns = [
        #        'branch_code_prefix',
        #        #*MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values(),
        #        *MergerConfig.INTEGRATED_COLUMNS_MAPPING.values(),
        #    ]
        #    merged_df = integrated_df.merge(
        #        filtered_result[merge_columns],
        #        on='branch_code_prefix',
        #        how='left',
        #    ).fillna('')

        #    ## reference_parent_branch_codeが無い場合は空文字で列生成
        #    #if 'branch_integrated_parent_branch_code' not in merged_df.columns:
        #    #    merged_df['branch_integrated_parent_branch_code'] = ''

        #    for column in MergerConfig.INTEGRATED_COLUMNS_MAPPING.values():
        #        if column not in merged_df.columns:
        #            merged_df[column] = ''

        #    # 不要カラムの削除
        #    result_df = merged_df.drop(columns=['branch_code_prefix'])

        #    log_msg("マージ結果:\n", LogLevel.DEBUG)
        #    tabulate_dataframe(result_df)

        #except Exception as e:
        #    err_msg = f"所属部店レコードからの付与/親部店情報のマージ処理でエラーが発生しました: {str(e)}"
        #    log_msg(err_msg, LogLevel.ERROR)
        #    raise DataMergeError(err_msg) from e

        #else:
        #    return result_df

    @staticmethod
    def merge_zero_group_parent_branch_with_reference(
        integrated_layout: pd.DataFrame,
        reference_table: pd.DataFrame,
    ) -> pd.DataFrame:
        """統合レイアウトデータにリファレンステーブルの情報をマージする,明細に対する部店レコードを探索しその情報をColumn付与する

        * 部店グループ: 課Grコード'0'を保有する明細の情報を取得する
        * 該当するリファレンスレコードの部店コードColumnを申請レコードに付与する
        * 該当するリファレンスレコードの部名称Columnを申請レコードに付与する
        * 該当するリファレンスレコードの親部店コード値があれば申請レコードをColumn付与する、なければブランク
        * 申請レコードに追加するColumnには一律 branch_reference_ 接頭辞を付与する
        * 付与Columnのデフォルト値は空文字で生成する

        Args:
            integrated_layout: 統合レイアウトデータ
            reference_table: リファレンステーブル

        Returns:
            pd.DataFrame: マージされたデータフレーム

        Raises:
            DataMergeError: マージ処理に失敗した場合
        """
        try:
            ReferenceMergers._validate_merge_data(
                integrated_layout,
                reference_table,
                {
                    'left': ['branch_code'],
                    'right': ['branch_code_bpr', 'section_gr_code_bpr'],
                },
            )

            result_df = integrated_layout.copy()

            # マージキーColumn生成
            result_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(result_df, 'branch_code')
            reference_table['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(reference_table, 'branch_code_bpr')
            # リファレンス対象データの絞り込み/columnリネーム
            filtered_reference = ReferenceMergers._filter_reference_data(reference_table)
            # マージ処理
            merged_df = ReferenceMergers._perform_merge_with_reference(result_df, filtered_reference)
            # 欠落Columnの初期値付与/不要Columnの削除
            result_df = ReferenceMergers._clean_up_merged_data_with_reference(merged_df)

            ReferenceMergers._log_merge_result(result_df)

        except Exception as e:
            err_msg = f"課Grコード=='0'レコードからの付与/親部店情報のマージ処理でエラーが発生しました:: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df


#    @staticmethod
#    def merge_zero_group_parent_branch(integrated_layout: pd.DataFrame, reference_table: pd.DataFrame) -> pd.DataFrame:
#    #def merge_zero_group_parent_branch_with_reference(integrated_layout: pd.DataFrame, reference_table: pd.DataFrame) -> pd.DataFrame:
#        """統合レイアウトデータにリファレンステーブルの情報をマージする,明細に対する部店レコードを探索しその情報をColumn付与する
#
#        * 部店グループ: 課Grコード'0'を保有する明細の情報を取得する
#        * 該当するリファレンスレコードの部店コードColumnを申請レコードに付与する
#        * 該当するリファレンスレコードの部名称Columnを申請レコードに付与する
#        * 該当するリファレンスレコードの親部店コード値があれば申請レコードをColumn付与する、なければブランク
#        * 申請レコードに追加するColumnには一律 branch_reference_ 接頭辞を付与する
#        * 付与Columnのデフォルト値は空文字で生成する
#
#        Args:
#            integrated_layout: 統合レイアウトデータ
#            reference_table: リファレンステーブル
#
#        Returns:
#            pd.DataFrame: マージされたデータフレーム
#
#        Raises:
#            DataMergeError: マージ処理に失敗した場合
#        """
#        try:
#            # データの検証
#            required_columns = {
#                'left': ['branch_code'],
#                'right': ['branch_code_bpr', 'section_gr_code_bpr'],
#            }
#            ReferenceMergers._validate_merge_data(integrated_layout, reference_table, required_columns)
#
#            # 部店コードの上位4桁を取得
#            integrated_df = integrated_layout.copy()
#            integrated_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(integrated_df, 'branch_code')
#            reference_table['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(reference_table, 'branch_code_bpr')
#
#            # リファレンステーブルのフィルタリングとリネーム
#            filtered_reference = (
#                reference_table[reference_table['section_gr_code_bpr'] == '0']
#                .rename(columns=MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR)
#            )
#            log_msg('リファンレンス.課Grコード=="0"抽出\n')
#            log_msg(f'{tabulate_dataframe(filtered_reference)}', LogLevel.DEBUG)
#
#            # マージ処理
#            merge_columns = [
#                'branch_code_prefix',
#                *MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values(),
#            ]
#            merged_df = integrated_df.merge(
#                filtered_reference[merge_columns],
#                on='branch_code_prefix',
#                how='left',
#            ).fillna('')
#
#            ## reference_parent_branch_codeとreference_parent_branch_codeが無い場合は空文字で列生成
#            #if 'branch_reference_parent_branch_code' not in merged_df.columns:
#            #    merged_df['branch_reference_parent_branch_code'] = ''
#
#            for column in MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values():
#                if column not in merged_df.columns:
#                    merged_df[column] = ''
#
#            # 不要カラムの削除
#            result_df = merged_df.drop(columns=['branch_code_prefix'])
#
#            log_msg("マージ結果:\n", LogLevel.DEBUG)
#            tabulate_dataframe(result_df)
#
#        except Exception as e:
#            err_msg = f"課Grコード=='0'レコードからの付与/親部店情報のマージ処理でエラーが発生しました: {str(e)}"
#            log_msg(err_msg, LogLevel.ERROR)
#            raise DataMergeError(err_msg) from e
#
#        else:
#            return result_df

    #######################################################
    # マージ/データ加工のための部品群
    #######################################################
    @staticmethod
    def _extract_branch_code_prefix(df: pd.DataFrame, column: str) -> pd.Series:
        """部店コードの上位4桁を取得する"""
        return df[column].str[:MergerConfig.BRANCH_CODE_LENGTH]

    @staticmethod
    def _filter_branch_data(df: pd.DataFrame) -> pd.DataFrame:
        filtered_result = (
            df[df['target_org'] == OrganizationType.BRANCH]
            .rename(columns=MergerConfig.INTEGRATED_COLUMNS_MAPPING)
            .copy()  # 明示的にコピーを作成
        )
        log_msg('Filtered branch data:\n')
        tabulate_dataframe(filtered_result)
        return filtered_result

    @staticmethod
    def _filter_reference_data(df: pd.DataFrame) -> pd.DataFrame:
        filtered_reference = (
            df[df['section_gr_code_bpr'] == '0']
            .rename(columns=MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR)
            .copy()  # 明示的にコピーを作成
        )
        log_msg('Filtered reference data:\n')
        tabulate_dataframe(filtered_reference)
        return filtered_reference

    #@staticmethod
    #def _perform_merge(df: pd.DataFrame, filtered_df: pd.DataFrame) -> pd.DataFrame:
    #    merge_columns = [
    #        'branch_code_prefix',
    #        *MergerConfig.INTEGRATED_COLUMNS_MAPPING.values(),
    #    ]
    #    result = df.merge(
    #        filtered_df[merge_columns],
    #        on='branch_code_prefix',
    #        how='left',
    #    ).fillna('')

    #    # マージ後の件数チェック - 業務要件から1:1のはず
    #    if len(result) != len(df):
    #        error_msg = (
    #            f"Merge violation: Record count mismatch. "
    #            f"Expected {len(df)}, but got {len(result)}. "
    #            "This violates the business rule of unique branch codes."
    #        )
    #        log_msg(error_msg, LogLevel.ERROR)
    #        raise DataMergeError(error_msg)

    @staticmethod
    def _perform_merge(df: pd.DataFrame, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """マージ処理の実行"""
        merge_columns = [
            'branch_code_prefix',
            *MergerConfig.INTEGRATED_COLUMNS_MAPPING.values(),
        ]
    
        # デバッグ情報の出力
        log_msg("Merge operation debug info:", LogLevel.DEBUG)
        log_msg(f"Required merge columns: {merge_columns}", LogLevel.DEBUG)
        log_msg(f"Input df columns: {df.columns.tolist()}", LogLevel.DEBUG)
        log_msg(f"Filtered df columns: {filtered_df.columns.tolist()}", LogLevel.DEBUG)
    
        # filtered_dfのスライス前の状態を確認
        log_msg("Filtered DataFrame before column selection:", LogLevel.DEBUG)
        tabulate_dataframe(filtered_df)
    
        try:
            # カラム選択を試みる前に存在確認
            missing_cols = [col for col in merge_columns if col not in filtered_df.columns]
            if missing_cols:
                raise DataMergeError(f"Missing required columns in filtered_df: {missing_cols}")
    
            # カラム選択を別ステップで実行
            selected_df = filtered_df[merge_columns]
            log_msg("Selected columns for merge:", LogLevel.DEBUG)
            log_msg(f"{tabulate_dataframe(selected_df)}", LogLevel.DEBUG)
    
            # マージ実行
            result = df.merge(
                selected_df,
                on='branch_code_prefix',
                how='left',
            ).fillna('')
    
            log_msg("Merge result:", LogLevel.DEBUG)
            tabulate_dataframe(result)
    
            return result
    
        except Exception as e:
            error_msg = f"Merge operation failed: {str(e)}"
            log_msg(error_msg, LogLevel.ERROR)
            raise DataMergeError(error_msg) from e

    @staticmethod
    def _perform_merge_with_reference(df: pd.DataFrame, filtered_df: pd.DataFrame) -> pd.DataFrame:
        merge_columns = [
            'branch_code_prefix',
            *MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values(),
        ]
        return df.merge(
            filtered_df[merge_columns],
            on='branch_code_prefix',
            how='left',
        ).fillna('')

    @staticmethod
    def _clean_up_merged_data(df: pd.DataFrame) -> pd.DataFrame:
        #if 'branch_integrated_parent_branch_code' not in df.columns:
        #    df['branch_integrated_parent_branch_code'] = ''
        for column in MergerConfig.INTEGRATED_COLUMNS_MAPPING.values():
            if column not in df.columns:
                df[column] = ''
        return df.drop(columns=['branch_code_prefix'])

    @staticmethod
    def _clean_up_merged_data_with_reference(df: pd.DataFrame) -> pd.DataFrame:
        #if 'branch_reference_parent_branch_code' not in df.columns:
        #    df['branch_reference_parent_branch_code'] = ''
        for column in MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values():
            if column not in df.columns:
                df[column] = ''
        return df.drop(columns=['branch_code_prefix'])

    @staticmethod
    def _log_merge_result(df: pd.DataFrame) -> None:
        log_msg("Merge result:\n", LogLevel.DEBUG)
        tabulate_dataframe(df)

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
