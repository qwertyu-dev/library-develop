import sys

import pandas as pd

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class ReferenceMergerError(Exception):
    pass

class ReferenceMerger:
    """統合レイアウトデータとリファレンステーブルのマージを行うクラス"""

    # リファレンスカラムの接頭辞定義
    REFERENCE_PREFIX = 'reference_'
    BRANCH_CODE_PREFIX = 'branch_code_prefix'  # branch_code_prefixを定数化

    # リファレンステーブルのカラム名マッピング
    REFERENCE_COLUMNS_MAPPING: dict[str, str] = {
            'branch_code_bpr': f'{REFERENCE_PREFIX}branch_code_bpr',
            'branch_name_bpr': f'{REFERENCE_PREFIX}branch_name_bpr',
            'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
        }

    def __init__(self):
        """イニシャライザ"""

    @staticmethod
    def merge_zero_group_parent_branch(integrated_layout: pd.DataFrame, reference_table: pd.DataFrame) -> pd.DataFrame:
        """統合レイアウトデータにリファレンステーブルの情報をマージする

        Merge前処理:
        1. 部店コード上位4桁が、統合レイアウトデータ/リファレンステーブルで生成
        2. リファレンステーブル 課GrコードBPR=='0' を抽出、Merge対象データは絞ってから実行
        3. リファレンステーブルのカラムを事前にリネーム(reference_接頭辞を付与)

        Merge処理:
        - Mergeキーは1.で生成した部店コード上位4桁
        - 統合レイアウトを軸にleft join、2.データを対象
        - 親部店コード保持がないケース-> fillna('')で要件対応

        Merge後処理:
        - 不要Columnを削除 (マージ用に作成した上位4桁部店コード保有Columns)

        Args:
            integrated_layout (pd.DataFrame): 統合レイアウトデータ
            reference_table (pd.DataFrame): リファレンステーブル

        Returns:
            pd.DataFrame: マージされたデータフレーム

        Raises:
            ValueError: 入力チェックエラー、マージパラメータエラー
            KeyError: DataFrameのカラム不足
            pd.errors.MergeError: マージ操作エラー
            ReferenceMergerError: その他の予期せぬエラー
        """
        # 入力チェック
        if integrated_layout.empty or reference_table.empty:
            err_msg = "入力DataFrameが空です: 統合レイアウトデータもしくはリファレンステーブル"
            log_msg(err_msg, LogLevel.ERROR)
            raise ValueError(err_msg)

        try:
            # 部店コードの上位4桁を取得して新しいカラムを追加
            integrated_layout['branch_code_prefix'] = integrated_layout['branch_code'].astype(str).str[:4]
            reference_table['branch_code_prefix'] = reference_table['branch_code_bpr'].astype(str).str[:4]

            # リファレンステーブルから課グループコードが'0'の行をフィルタリング
            filtered_reference_table = reference_table[reference_table['section_gr_code_bpr'] == '0']

            # マージ前にリファレンステーブルのカラムをリネーム
            filtered_reference_table = filtered_reference_table.rename(
                columns=ReferenceMerger.REFERENCE_COLUMNS_MAPPING,
            )

            # マージに使用するリファンレンステーブルのカラムを選定
            merge_columns = [
                'branch_code_prefix',
                ReferenceMerger.REFERENCE_COLUMNS_MAPPING['branch_code_bpr'],
                ReferenceMerger.REFERENCE_COLUMNS_MAPPING['branch_name_bpr'],
                ReferenceMerger.REFERENCE_COLUMNS_MAPPING['parent_branch_code'],
            ]

            # 統合レイアウトデータに対して、リファレンステーブルをマージ
            merged_data = integrated_layout.merge(
                filtered_reference_table[merge_columns],
                on='branch_code_prefix',
                how='left',
            ).fillna('')

            # 不要なカラムを削除
            result_df = merged_data.drop(columns=['branch_code_prefix'])

            # デバッグ用にデータフレームの内容をログ出力
            log_msg(f'\n\n{tabulate_dataframe(result_df)}', LogLevel.DEBUG)

            # 最終的なカラム構成をログ出力(デバッグ用)
            log_msg(f'最終的なカラム一覧: {result_df.columns.to_numpy()}', LogLevel.DEBUG)

        except KeyError as e:
            err_msg = f'DataFrameにカラムが存在しません: {str(e)}'
            log_msg(err_msg, LogLevel.ERROR)
            raise

        except ValueError as e:
            err_msg = f'DataFrameマージエラーが発生しました。マージパラメータ: {str(e)}'
            log_msg(err_msg, LogLevel.ERROR)
            raise

        except pd.errors.MergeError as e:
            err_msg = f'DataFrameマージエラーが発生しました。マージ操作エラー: {str(e)}'
            log_msg(err_msg, LogLevel.ERROR)
            raise

        except Exception as e:
            err_msg = f'DataFrameマージ中に予期せぬエラーが発生しました: {str(e)}'
            log_msg(err_msg, LogLevel.ERROR)
            raise ReferenceMergerError from e
        else:
            return result_df
