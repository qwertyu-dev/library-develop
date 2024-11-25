"""受付処理前のマージ処理"""
import sys
from dataclasses import dataclass
from typing import ClassVar

import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel, OrganizationType
from src.lib.converter_utils.ibr_reference_mergers_pattern import MatchingPattern, PatternDefinitions

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

###################################################
# グループ探索向けの定義
###################################################
# データ探索: 固定値定義
@dataclass(frozen=True)
class MergerConfig:
    """ReferenceMergersの設定値"""
    BRANCH_CODE_LENGTH: ClassVar[int] = 4
    REFERENCE_PREFIX: ClassVar[str] = 'branch_reference_'
    INTEGRATED_PREFIX: ClassVar[str] = 'branch_integrated_'

    # リファレンステーブルのカラム名マッピング
    REFERENCE_COLUMNS_MAPPING_BPR: ClassVar[dict[str, str]] = {
        #'branch_code_jinji': f'{REFERENCE_PREFIX}branch_code_jinji',
        'branch_name_jinji': f'{REFERENCE_PREFIX}branch_name_jinji',
        #'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
        'organization_name_kana': f'{REFERENCE_PREFIX}organization_name_kana',
        #'branch_code_bpr': f'{REFERENCE_PREFIX}branch_code_bpr',
        #'branch_name_bpr': f'{REFERENCE_PREFIX}branch_name_bpr',
    }

    INTEGRATED_COLUMNS_MAPPING: ClassVar[dict[str, str]] = {
        #'branch_code': f'{INTEGRATED_PREFIX}branch_code',
        'branch_name': f'{INTEGRATED_PREFIX}branch_name',
        #'parent_branch_code': f'{INTEGRATED_PREFIX}parent_branch_code',
    }

    #REFERENCE_COLUMNS_MAPPING_JINJI: ClassVar[dict[str, str]] = {
    #    'branch_code_jinji': f'{REFERENCE_PREFIX}branch_code_jinji',
    #    'branch_name_jinji': f'{REFERENCE_PREFIX}branch_name_jinji',
    #    'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
    #    'organization_name_kana': f'{REFERENCE_PREFIX}organization_name_kana',
    #}

###################################################
# リファレンス一意特定探索のための定義
###################################################

@dataclass(frozen=True)
class ReferenceColumnConfig:
    """リファレンスデータのカラム設定を管理"""
    TARGET_COLUMNS: set[str] = frozenset({
        'branch_code_bpr',                # 部店コード(BPR)
        'branch_name_bpr',                # 部店名(BPR)
        'section_gr_code_bpr',            # 課Grコード(BPR)
        'section_gr_name_bpr',            # 課Gr名(BPR)
        #'business_unit_code_bpr',         # 部門コード(BPR)
        'parent_branch_code',             # 親部店コード
        'internal_sales_dept_code',       # 拠点内営業部コード
        'internal_sales_dept_name',       # 拠点内営業部名称
        'branch_code_jinji',              # 部店コード(人事)
        'branch_name_jinji',              # 部店名(人事)
        'section_gr_code_jinji',          # 課Grコード(人事)
        'section_gr_name_jinji',          # 課Gr名(人事)
        #'branch_code_area',               # 部店コード(エリア)
        #'branch_name_area',               # 部店名(エリア)
        #'section_gr_code_area',           # 課Grコード(エリア)
        'section_gr_name_area',           # 課Gr名(エリア)
        #'sub_branch_code',                # 出張所コード
        #'sub_branch_name',                # 出張所名称
        'business_code',                  # 業務コード
        'area_code',                      # エリアコード
        'area_name',                      # エリア名称
        #'resident_branch_code',           # 常駐部店コード
        'resident_branch_name',           # 常駐部店名称
        #'organization_name_kana',         # カナ組織名(カナ)
        #TODO(): bpr_target_flagはここで付与すべきなのでは(変更/削除対象)
        'bpr_target_flag',                # BPR対象/対象外フラグ
    })
    REFERENCE_PREFIX: str = 'reference_'

    @staticmethod
    def get_renamed_columns() -> dict[str, str]:
        """リネーム用の辞書を生成"""
        return {col: f"{ReferenceColumnConfig.REFERENCE_PREFIX}{col}"
                for col in ReferenceColumnConfig.TARGET_COLUMNS}

    @staticmethod
    def get_prefixed_column(column: str) -> str:
        """カラム名にプレフィックスを付与"""
        return f"{ReferenceColumnConfig.REFERENCE_PREFIX}{column}"


###################################################
# モジュール内例外定義
###################################################
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
    # 申請明細グループ検索/所属グループ部店情報merge
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

            log_msg("Merger Step1", LogLevel.DEBUG)
            ReferenceMergers._log_merge_result(result_df)

        except Exception as e:
            err_msg = f"Error in merging branch records: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df


    #######################################################
    # リファレンスグループ検索/所属グループ部店情報merge
    #######################################################
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

            # マージキーColumn生成 リファレンスは部店コード.BPR
            result_df['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(result_df, 'branch_code')
            reference_table['branch_code_prefix'] = ReferenceMergers._extract_branch_code_prefix(reference_table, 'branch_code_bpr')

            # リファレンス対象データの絞り込み/columnリネーム
            filtered_reference = ReferenceMergers._filter_reference_data(reference_table)

            # マージ処理
            merged_df = ReferenceMergers._perform_merge_with_reference(result_df, filtered_reference)

            # 欠落Columnの初期値付与/不要Columnの削除
            result_df = ReferenceMergers._clean_up_merged_data_with_reference(merged_df)

            log_msg("Merger Step2", LogLevel.DEBUG)
            ReferenceMergers._log_merge_result(result_df)

        except Exception as e:
            err_msg = f"課Grコード=='0'レコードからの付与/親部店情報のマージ処理でエラーが発生しました:: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

    #######################################################
    # リファレンス一意探索処理
    #######################################################
    @staticmethod
    def match_unique_reference(
        integrated_df: pd.DataFrame,
        reference_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """申請データ自身に対する、一意のリファレンスデータを探索しマージする

        Args:
            integrated_df: 統合レイアウトデータ
            reference_df: リファレンスデータ

        Returns:
            pd.DataFrame: リファレンスデータとマージされた統合レイアウトデータ

        Raises:
            DataMergeError: マージ処理に失敗した場合
        """
        try:
            # 入力データの検証
            ReferenceMergers._validate_unique_reference_data(integrated_df, reference_df)

            # 申請データの前処理
            processed_integrated = ReferenceMergers._prepare_integrated_data(integrated_df)

            # リファレンスデータの前処理
            processed_reference = ReferenceMergers._prepare_unique_reference_data(reference_df)

            # パターンによるマッチング処理
            result_df = ReferenceMergers._process_with_patterns(
                processed_integrated,
                processed_reference,
                PatternDefinitions.get_all_patterns(),
            )

            # 作業用カラムの削除
            result_df = ReferenceMergers._cleanup_integrated_data(result_df)

            log_msg("Merger Step3", LogLevel.DEBUG)
            ReferenceMergers._log_unique_reference_result(result_df)

        except Exception as e:
            err_msg = f"リファレンス一意探索処理でエラーが発生しました: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

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
            df[(df['target_org'] == OrganizationType.BRANCH) & (df['branch_code'].str.len() == MergerConfig.BRANCH_CODE_LENGTH)]
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

    @staticmethod
    def _perform_merge(df: pd.DataFrame, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """マージ処理の実行 df:一括申請 filterd_df:リファレンス"""
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
                err_msg = f"Missing required columns in filtered_df: {missing_cols}"
                ReferenceMergers._handle_merge_error(err_msg)

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

        except Exception as e:
            error_msg = f"Merge operation failed: {str(e)}"
            log_msg(error_msg, LogLevel.ERROR)
            raise DataMergeError(error_msg) from e
        else:
            return result

    @staticmethod
    def _perform_merge_with_reference(df: pd.DataFrame, filtered_df: pd.DataFrame) -> pd.DataFrame:
        """リファレンスデータとのマージ処理

        Args:
            df: マージ元DataFrame
            filtered_df: フィルタリング済みのDataFrame

        Returns:
            pd.DataFrame: マージ結果

        Raises:
            DataMergeError: マージ処理に失敗した場合
        """
        try:
            # デバッグ情報の出力
            log_msg("Merge operation debug info:", LogLevel.DEBUG)
            merge_columns = [
                'branch_code_prefix',
                *MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values(),
            ]
            log_msg(f"Required merge columns: {merge_columns}", LogLevel.DEBUG)
            log_msg(f"Input df columns: {df.columns.tolist()}", LogLevel.DEBUG)
            log_msg(f"Filtered df columns: {filtered_df.columns.tolist()}", LogLevel.DEBUG)

            # カラム選択を試みる前に存在確認
            missing_cols = [col for col in merge_columns if col not in filtered_df.columns]
            if missing_cols:
                err_msg = f"Missing required columns in filtered_df: {missing_cols}"
                ReferenceMergers._handle_merge_error(err_msg)

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

        except Exception as e:
            error_msg = f"Merge with reference operation failed: {str(e)}"
            log_msg(error_msg, LogLevel.ERROR)
            raise DataMergeError(error_msg) from e
        else:
            return result

    @staticmethod
    def _prepare_integrated_data(df: pd.DataFrame) -> pd.DataFrame:
        """申請データの前処理

        Args:
            df: 申請データ

        Returns:
            pd.DataFrame: 前処理済みの申請データ
                - branch_code_digits4: 部店コード4桁
                - area_code_first: エリアコード先頭1桁
                - area_code_rest: エリアコード2桁目以降
        """
        # 複製して処理用データ作成
        processed_df = df.copy()

        # 4桁部店コード付与
        processed_df['branch_code_digits4'] = processed_df['branch_code'].str[:4]

        # エリアコードがある場合のみ分割処理
        if 'business_and_area_code' in processed_df.columns:
            # エリアコード分割(先頭1桁)
            processed_df['business_and_area_code_first'] = processed_df['business_and_area_code'].str[0]
            # エリアコード分割(2桁目以降)
            processed_df['business_and_area_code_rest'] = processed_df['business_and_area_code'].str[1:]

        return processed_df

    @staticmethod
    def _cleanup_integrated_data(df: pd.DataFrame) -> pd.DataFrame:
        """申請データの後処理(作業用カラムの削除)

        Args:
            df: 処理済みの申請データ

        Returns:
            pd.DataFrame: 作業用カラムを削除したデータ
        """
        # 削除対象カラム
        work_columns = [
            'branch_code_digits4',
            'business_and_area_code_first',
            'business_and_area_code_rest',
        ]

        # 存在するカラムのみ削除
        _df = df.copy()
        columns_to_drop = [col for col in work_columns if col in _df.columns]
        if columns_to_drop:
            _df = _df.drop(columns=columns_to_drop)

        return _df

    @staticmethod
    def _clean_up_merged_data(df: pd.DataFrame) -> pd.DataFrame:
        _df = df.copy()
        for column in MergerConfig.INTEGRATED_COLUMNS_MAPPING.values():
            if column not in _df.columns:
                _df[column] = ''
        if 'branch_code_prefix' in _df.columns:
            return _df.drop(columns=['branch_code_prefix'])
        return _df

    @staticmethod
    def _clean_up_merged_data_with_reference(df: pd.DataFrame) -> pd.DataFrame:
        _df = df.copy()
        for column in MergerConfig.REFERENCE_COLUMNS_MAPPING_BPR.values():
            if column not in _df.columns:
                _df[column] = ''
        if 'branch_code_prefix' in _df.columns:
            return _df.drop(columns=['branch_code_prefix'])
        return _df

    @staticmethod
    def _validate_unique_reference_data(
        integrated_df: pd.DataFrame,
        reference_df: pd.DataFrame,
    ) -> None:
        """一意探索用の入力データ検証

        Args:
            integrated_df: 統合レイアウトデータ
            reference_df: リファレンスデータ

        Raises:
            DataMergeError: 検証エラーの場合
        """
        if integrated_df.empty or reference_df.empty:
            err_msg = "Empty DataFrame provided for unique reference matching"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg)

        # 必要なカラムの存在チェック
        required_columns = {
            'integrated': [
                'form_type',
                'target_org',
                'branch_code',
                'section_gr_code',
                ],
            'reference': ReferenceColumnConfig.TARGET_COLUMNS,
        }

        missing_integrated = set(required_columns['integrated']) - set(integrated_df.columns)
        missing_reference = set(required_columns['reference']) - set(reference_df.columns)

        if missing_integrated or missing_reference:
            err_msg = (
                f"Missing required columns: "
                f"integrated={missing_integrated}, reference={missing_reference}"
            )
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg)

    @staticmethod
    def _prepare_unique_reference_data(reference_df: pd.DataFrame) -> pd.DataFrame:
        """リファレンスデータの前処理

        Args:
            reference_df: リファレンスデータ

        Returns:
            pd.DataFrame: 前処理済みのリファレンスデータ
        """
        target_columns = ReferenceColumnConfig.TARGET_COLUMNS
        rename_dict = ReferenceColumnConfig.get_renamed_columns()

        # カラムの選択とリネーム
        processed_df = (
            reference_df[target_columns]
            .rename(columns=rename_dict)
            .copy()
        )
        log_msg("前処理後のリファレンスデータ サンプル:", LogLevel.DEBUG)
        tabulate_dataframe(processed_df.head(5))

        return processed_df

    @staticmethod
    def _process_with_patterns(integrated_df: pd.DataFrame, reference_df: pd.DataFrame, patterns: list[MatchingPattern]) -> pd.DataFrame:
        """パターンに基づいたマッチング処理の実行

        Args:
            integrated_df: 統合レイアウトデータ
            reference_df: 前処理済みリファレンスデータ
            patterns: 適用するパターンのリスト

        Returns:
            pd.DataFrame: マッチング結果
        """
        # 結果の入れ物
        result_dfs = []
        # 既に処理済みの行を示すブール値のマスク
        processed_mask = pd.Series(False, index=integrated_df.index)

        # pattern定義条件毎にループ
        for pattern in patterns:
            try:
                # 「パターンに合致する」かつ「まだ処理されていない」行を抽出
                pattern_mask = pattern.target_condition(integrated_df) & ~processed_mask
                if not pattern_mask.any():
                    log_msg( f"\n=== パターン: {pattern.description}: 処理結果 ===", LogLevel.DEBUG)
                    log_msg( "\n該当レコードなし", LogLevel.DEBUG)
                    continue

                # patternの適用
                target_df = integrated_df[pattern_mask].copy()
                matched_df = ReferenceMergers._apply_pattern(pattern, target_df, reference_df)

                # パターン処理結果のログ出力 for Debug
                ReferenceMergers._log_pattern_result(pattern, target_df, matched_df)

                # 結果を入れ物に積み上げ
                result_dfs.append(matched_df)

                # 処理済レコードフラグ更新,次パターンへ
                processed_mask = processed_mask | pattern_mask

            except Exception as e:
                if not target_df.empty:
                    err_msg = (
                    #f"パターン{pattern.pattern_id}:{pattern.description}の処理でエラー: {str(e)}\n"
                    f"パターン:{pattern.description}の処理でエラー: {str(e)}\n"
                    f"対象データ件数: {len(target_df)}\n"
                    f"パターン情報: {pattern.description}")
                else:
                    err_msg = (
                    f"パターン:{pattern.description}の処理でエラー: {str(e)}\n"
                    f"パターン情報: {pattern.description}")

                log_msg(err_msg, LogLevel.ERROR)

                # エラー時は元のデータを保持
                result_dfs.append(target_df)
                processed_mask = processed_mask | pattern_mask

                # エラーが発生しても処理継続
                continue

        # 未処理データの扱い
        unmatched = integrated_df[~processed_mask].copy()
        if not unmatched.empty:
            log_msg(f"未マッチレコード: {len(unmatched)}件", LogLevel.WARNING)
            log_msg("未マッチデータ サンプル:", LogLevel.DEBUG)
            tabulate_dataframe(unmatched.head())
            result_dfs.append(unmatched)

        if not result_dfs:
            log_msg("マッチング結果なし", LogLevel.WARNING)
            return pd.DataFrame()

        # 各種パターン別結果を1つに積んで返す
        return pd.concat(result_dfs, ignore_index=True)

    @staticmethod
    def _apply_pattern( pattern: MatchingPattern, target_df: pd.DataFrame, reference_df: pd.DataFrame) -> pd.DataFrame:
        """個別パターンの適用処理

        Args:
            pattern: 適用するパターン
            target_df: 対象データ
            reference_df: リファレンスデータ

        Returns:
            pd.DataFrame: パターン適用結果
        """
        try:
            # 固定フィルターがない場合も含めて初期化
            filtered_ref = reference_df.copy()
            # リファレンスに対する固定条件の適用/filter条件から事前抽出
            if pattern.fixed_conditions:
                for ref_col, value in pattern.fixed_conditions.items():
                    # prefix付与状態で対象とするreference columnsを取得
                    col_name = ReferenceColumnConfig.get_prefixed_column(ref_col)
                    # 条件抽出
                    filtered_ref = filtered_ref[filtered_ref[col_name] == value]

                log_msg(f"固定条件適用後のリファレンスデータ件数: {len(filtered_ref)}", LogLevel.DEBUG)

            # マージ条件構築
            merge_key = {
                ReferenceColumnConfig.get_prefixed_column(ref_col) :target_col
                for ref_col, target_col in pattern.reference_keys.items()
                if not callable(target_col)
            }
            log_msg(f"マージキー: {merge_key}", LogLevel.DEBUG)

            # マージ処理
            result = target_df.merge(
                filtered_ref,
                left_on=list(merge_key.values()),
                right_on=list(merge_key.keys()),
                how='left',
            )

            # 関数型の参照キーの処理
            for ref_col, target_col in pattern.reference_keys.items():
                if callable(target_col):
                    col_name = ReferenceColumnConfig.get_prefixed_column(ref_col)
                    result[col_name] = target_col(result)

        except Exception as e:
            err_msg = f"パターン適用処理でエラー: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result

    #######################################################
    # Helper
    #######################################################
    @staticmethod
    def _handle_merge_error(err_msg: str) -> None:
        log_msg(err_msg, LogLevel.ERROR)
        raise DataMergeError(err_msg) from None

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

    @staticmethod
    def _log_unique_reference_result(df: pd.DataFrame) -> None:
        """一意探索の結果ログ出力

        Args:
            df: マッチング結果データ
        """
        log_msg("=== 一意探索結果 ===", LogLevel.INFO)
        log_msg(f"総レコード数: {len(df)}", LogLevel.INFO)

        # リファレンスカラムのマッチング状況確認
        ref_columns = [
            col for col in df.columns
            if col.startswith(ReferenceColumnConfig.REFERENCE_PREFIX)
        ]

        for col in ref_columns:
            null_count = df[col].isna().sum()
            if null_count > 0:
                log_msg(f"カラム {col}: {null_count}件の未マッチ", LogLevel.WARNING)


    @staticmethod
    def _log_pattern_result(
        pattern: MatchingPattern,
        target_df: pd.DataFrame,
        matched_df: pd.DataFrame,
    ) -> None:
        """パターン処理結果のログ出力

        Args:
            pattern: 適用したパターン
            target_df: パターン処理対象データ
            matched_df: マッチング結果データ
        """
        try:
            #log_msg(f"\n=== パターン{pattern.pattern_id} ({pattern.description}) 処理結果 ===", LogLevel.INFO)
            log_msg(f"\n=== パターン: {pattern.description} 処理結果 ===", LogLevel.INFO)

            # 基本情報
            log_msg(f"処理対象件数: {len(target_df)}件", LogLevel.INFO)
            log_msg(f"処理結果件数: {len(matched_df)}件", LogLevel.INFO)

            # マッチング状況の確認
            ref_columns = [
                col for col in matched_df.columns
                if col.startswith(ReferenceColumnConfig.REFERENCE_PREFIX)
            ]

            # パターン固有の条件確認
            if pattern.fixed_conditions:
                log_msg("\n固定条件:", LogLevel.DEBUG)
                for col, value in pattern.fixed_conditions.items():
                    log_msg(f"{col} = {value}", LogLevel.DEBUG)

            if ref_columns:
                log_msg("\nマッチング状況:", LogLevel.DEBUG)

                # 全リファレンスカラムでの未マッチチェック
                unmatched_mask = pd.Series(False, index=matched_df.index)
                key_columns = [
                    ReferenceColumnConfig.get_prefixed_column(ref_col)
                    for ref_col, target_col in pattern.reference_keys.items()
                    if not callable(target_col)  # 関数型は除外
                ]

                # パターンのキーカラムのみで判定
                for col in key_columns:
                    unmatched_mask = unmatched_mask | matched_df[col].isna()

                # 詳細なマッチング状況のログ出力
                for col in ref_columns:
                    matched_count = matched_df[col].notna().sum()
                    unmatched_count = matched_df[col].isna().sum()
                    match_rate = (matched_count / len(matched_df) * 100) if len(matched_df) > 0 else 0

                    log_msg(
                        f"カラム {col}:"
                        f" マッチ {matched_count}件,"
                        f" 未マッチ {unmatched_count}件"
                        f" (マッチ率: {match_rate:.1f}%)",
                        LogLevel.DEBUG,
                    )

                # サンプルデータの表示
                if not matched_df.empty:
                    log_msg("\nマッチング結果サンプル:", LogLevel.DEBUG)
                    display_columns = [
                        'form_type',
                        'target_org',
                        'branch_code',
                        'section_gr_code',
                        *key_columns,  # キーカラムを優先
                        *[col for col in ref_columns if col not in key_columns],  # その他のカラム
                    ]
                    sample_df = matched_df[
                        [col for col in display_columns if col in matched_df.columns]
                    ].head()
                    log_msg(tabulate_dataframe(sample_df), LogLevel.DEBUG)

                # 未マッチデータのサンプル表示
                if unmatched_mask.any():
                    unmatched_count = unmatched_mask.sum()
                    log_msg(f"\n未マッチレコード数: {unmatched_count}件", LogLevel.WARNING)
                    log_msg("\n未マッチデータサンプル(パターンのキーカラムが未マッチ):", LogLevel.DEBUG)

                    unmatched_sample = matched_df[unmatched_mask][
                        [col for col in display_columns if col in matched_df.columns]
                    ].head()
                    log_msg(tabulate_dataframe(unmatched_sample), LogLevel.DEBUG)

        except Exception as e:
            # ログ出力処理の失敗はエラーとして扱わない
            log_msg(f"ログ出力処理で例外が発生しました: {str(e)}", LogLevel.WARNING)
