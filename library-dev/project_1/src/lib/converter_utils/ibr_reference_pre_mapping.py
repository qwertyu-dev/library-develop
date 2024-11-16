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
    #REFERENCE_COLUMNS_MAPPING_BPR: ClassVar[dict[str, str]] = {
    #    'branch_code_bpr': f'{REFERENCE_PREFIX}branch_code_bpr',
    #    'branch_name_bpr': f'{REFERENCE_PREFIX}branch_name_bpr',
    #    'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
    #}

    REFERENCE_COLUMNS_MAPPING_JINJI: ClassVar[dict[str, str]] = {
        'branch_code_jinji': f'{REFERENCE_PREFIX}branch_code_jinji',
        'branch_name_jinji': f'{REFERENCE_PREFIX}branch_name_jinji',
        'parent_branch_code': f'{REFERENCE_PREFIX}parent_branch_code',
        'organization_name_kana': f'{REFERENCE_PREFIX}organization_name_kana',
    }

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

    @staticmethod
    def add_bpr_target_flag_from_reference( integrated_df: pd.DataFrame | None = None, reference_df: pd.DataFrame | None = None) -> pd.DataFrame:
        """申請明細データに対して、リファレンス.BPRADフラグColumnを付与する

        * 一意Key: 部店コード,課Grコード,エリアコード(4桁, 申請データは2桁目-/リファンレンスはエリアコード)
        * 対象レコード: 種類: 新設以外

        Args:
            integrated_df: 申請データ DataFrame
            reference_df: リファレンスデータ DataFrame

        Returns:
            pd.DataFrame: BPRADフラグが付与された申請データ

        Raises:
            DataMergeError: マージ処理に失敗した場合

        Notes:
            BPRフラグ初期値設定部品で利用される想定,新設以外はリファレンスからBPRADフラグ取得要件
        """
        try:
            # データ読み込み
            result_df = ReferenceMergers._load_data(
                integrated_df, MergerConfig.DEFAULT_LAYOUT_FILE,
            )
            reference_df = ReferenceMergers._load_data(
                reference_df, MergerConfig.REFERENCE_TABLE_FILE,
            )

            # マージ設定
            merge_config = {
                'columns': {
                    'integrated': [
                        'application_type', 'branch_code', 'section_gr_code',
                        'area_code', 'area_code_sep', 'bpr_target_flag',
                    ],
                    'reference': [
                        'branch_code_jinji', 'section_gr_code_jinji',
                        'area_code', 'bpr_target_flag',
                    ],
                },
                'keys': {
                    'left': ['branch_code', 'section_gr_code', 'area_code_sep'],
                    'right': ['branch_code_jinji', 'section_gr_code_jinji', 'area_code'],
                },
            }

            # マージ前処理
            # エリアコード処理
            # 一括申請.area_code分割, area_codeにはNaNが入っていない前提 ブランクを含むstr
            # 一括申請.エリアコード２桁目〜 = リファレンス.エリアコード
            result_df['area_code_sep'] = result_df['area_code'].str[1:]

            # 新設しかない場合はColumnが落ちるケースを考慮
            result_df['reference_bpr_target_flag'] = ''

            # マージデータの準備
            filtered_df = result_df[merge_config['columns']['integrated']]
            filtered_ref = reference_df[merge_config['columns']['reference']]

            # 新設以外(変更/廃止)明細を対象に処理
            non_new_mask = (filtered_df['application_type'] != ApplicationType.NEW.value)

            # マージ処理
            if non_new_mask.any():
                merged_df = filtered_df[non_new_mask].merge(
                    filtered_ref,
                    left_on=merge_config['keys']['left'],
                    right_on=merge_config['keys']['right'],
                    how='left',
                )

                # 対象となる申請明細(種類: 変更/廃止)に対となるレコードがリファレンスにない
                if merged_df.empty:
                    err_msg = '変更/廃止申請にも関わらず対となる明細がリファレンス上にありません'
                    log_msg(err_msg, LogLevel.ERROR)
                    ReferenceMergers._handle_merge_error(err_msg)

                # BPR/ADフラグ: column付与処理
                result_df.loc[non_new_mask, 'reference_bpr_target_flag'] = (
                    merged_df['bpr_target_flag_y']
                )
                result_df['reference_bpr_target_flag'] =  result_df['reference_bpr_target_flag'].fillna('')

                log_msg('bprad col added:\n')
                tabulate_dataframe(result_df)

            ReferenceMergers._log_bpr_flag_results(result_df)

        except Exception as e:
            err_msg = f"BPRADフラグ付与処理でエラーが発生しました: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

    #######################################################
    # Merge前のColumn編集 統合レイアウトのColumn加工
    #######################################################
    @staticmethod
    def setup_internal_sales_to_integrated_data(integrated_df: pd.DataFrame | None = None) -> pd.DataFrame:
        """拠点内営業部向けのデータ編集を行う

        * 部店コードを拠点内営業部コードへセットする
        * 部店名称を分割し部店名称/営業部名称に分割する
        * 部店名称に分割した部店名称をセットする
        * 拠点内営業部名称に分割した営業部名称をセットする
        * 部店コードを上位4桁に切り落とす

        Args:
            integrated_df: 申請データ DataFrame

        Returns:
            pd.DataFrame: 拠点内営業部処理済のDataFrame

        Raises:
            DataLoadError: データ読み込みに失敗した場合
            BranchNameSplitError: 部店名称の分割処理に失敗した場合
        """
        try:
            # データ読み込み
            result_df = ReferenceMergers._load_data(integrated_df)

            # 対象データの抽出
            mask = (result_df['target_org'] == OrganizationType.INTERNAL_SALES.value)
            if not mask.any():
                err_msg = "処理対象の拠点内営業部データが存在しません"
                log_msg(f'{err_msg}', LogLevel.WARNING)
                return result_df

            # 拠点内営業部の処理
            result_df = ReferenceMergers._process_internal_sales_data(result_df, mask)
            log_msg("処理結果:\n", LogLevel.INFO)
            tabulate_dataframe(result_df)
            return result_df

        except Exception as e:
            err_msg = f"拠点内営業部向けデータ編集処理でエラーが発生しました: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

    @staticmethod
    def setup_area_to_integrated_data(integrated_df: pd.DataFrame | None = None) -> pd.DataFrame:
        """エリア向けのデータ編集を行う

        * 備考欄からエリアグループコードを取得して部店コードに設定する
        * 備考欄からエリアグループ名を取得して部店名称にセットする

        Args:
            integrated_df: 申請データ DataFrame

        Returns:
            pd.DataFrame: エリア区分処理済のDataFrame

        Raises:
            DataLoadError: データ読み込みに失敗した場合
            RemarksParseError: 備考欄の解析に失敗した場合
        """
        try:
            # データ読み込み
            result_df = ReferenceMergers._load_data(integrated_df)

            # 対象データの抽出
            mask = (result_df['target_org'] == OrganizationType.AREA.value)
            if not mask.any():
                err_msg = "処理対象のエリアデータが存在しません"
                log_msg(err_msg, LogLevel.WARNING)
                return result_df

            # エリアデータの処理
            result_df = ReferenceMergers._process_area_data(result_df, mask)

            log_msg("処理結果:\n")
            tabulate_dataframe(result_df)

        except Exception as e:
            err_msg = f"エリア向けデータ編集処理でエラーが発生しました: {e}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

    @staticmethod
    def setup_section_under_internal_sales_integrated_data(integrated_df: pd.DataFrame | None = None) -> pd.DataFrame:
        """拠点内営業部配下の課向けのデータ編集を行う

        * 備考欄から取得した拠点内営業部に関する記述に対して
            自身の備考欄から取得した拠点内営業部名に一致する,拠点内営業部申請レコードを申請レコードから探索する
            探索対象は対象: '拠点内営業部'
            探索したレコードの拠点内営業部.部店コードを課.拠点内営業部コードとしてセットする
        * 備考欄を解析した結果から,取得した拠点内営業部名を課.拠点内営業部名としてセットする

        Args:
            integrated_df: 申請データ DataFrame

        Returns:
            pd.DataFrame: 処理済みのDataFrame

        Raises:
            DataLoadError: データ読み込みに失敗した場合
            RemarksParseError: 備考欄の解析に失敗した場合
        """
        try:
            # データ読み込み
            result_df = ReferenceMergers._load_data(integrated_df)

            # 対象データの抽出
            mask = ((result_df['target_org'] == OrganizationType.SECTION_GROUP.value) & (result_df['remarks'].notna()))
            if not mask.any():
                err_msg = "処理対象の拠点内営業部配下課データが存在しません"
                log_msg(err_msg, LogLevel.WARNING)
                return result_df

            # データの処理
            result_df = ReferenceMergers._process_section_under_internal_sales(result_df, mask)

            log_msg("処理結果:\n")
            tabulate_dataframe(result_df)

        except Exception as e:
            err_msg = f"拠点内営業部配下課向けデータ編集処理でエラーが発生しました: {str(e)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise DataMergeError(err_msg) from e
        else:
            return result_df

    #######################################################
    # マージ/データ加工のための部品群
    #######################################################
    @staticmethod
    def _load_data( df: pd.DataFrame | None = None, file_name: str = MergerConfig.DEFAULT_LAYOUT_FILE) -> pd.DataFrame:
        """データ読み込み処理

        Args:
            df: 入力DataFrame
            file_name: 読み込むファイル名

        Returns:
            pd.DataFrame: 処理用にコピーしたDataFrame

        Raises:
            DataLoadError: データ読み込みに失敗した場合
        """
        try:
            result_df = (df if df is not None else TableSearcher(file_name).df)
            return result_df.copy() if not result_df.empty else pd.DataFrame()
        except Exception as e:
            err_msg = f'データの取得に失敗しました: {str(e)}'
            log_msg(f'{err_msg}', LogLevel.ERROR)
            raise DataLoadError(err_msg) from e

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

    @staticmethod
    def _parse_remarks(remarks: str) -> ParsedRemarks:
        """備考欄の解析処理

        RemarksParser()共通部品を仕様視制御する
        共通部品のラッパー編集部品の立ち位置

        Args:
            remarks: 解析対象の備考文字列

        Returns:
            ParsedRemarks: 解析結果

        Notes:
            共通部品を使用して制御するラッパーの立ち位置

        See:
            RemarksParser()
        """
        if pd.isna(remarks):
            return {
                'request_type': '',
                'sales_department': {'department_name': '', 'branch_name': ''},
                'area_group': {'group_code': '', 'group_name': '', 'established_date': ''},
                'other_info': '',
            }
        try:
            parser = RemarksParser()
            return parser.parse(str(remarks))
        except Exception as e:
            err_msg = f"RemarksParse処理で異常が発生しました: {str(e)}"
            raise RemarksParseError(err_msg) from e

    @staticmethod
    def _process_internal_sales_data(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
        """拠点内営業部データの処理

        setup_internal_sales_to_integrated_data()での編集加工実体

        Args:
            df: 処理対象DataFrame
            mask: 処理対象行のマスク

        Returns:
            pd.DataFrame: 処理後のDataFrame

        Raises:
            BranchNameSplitError: 部店名称の分割処理に失敗した場合
        """
        try:
            # 部店コードの処理
            df.loc[mask, 'internal_sales_dept_code'] = df.loc[mask, 'branch_code']

            # 部店名称の分割処理
            split_names = df.loc[mask, 'branch_name'].apply(ReferenceMergers._split_branch_name_regex)
            df.loc[mask, 'branch_name'] = split_names.apply(lambda x: x[0])
            df.loc[mask, 'internal_sales_dept_name'] = split_names.apply(lambda x: x[1])

            # 部店コードの切り詰め
            df.loc[mask, 'branch_code'] = ReferenceMergers._extract_branch_code_prefix(
                df.loc[mask], 'branch_code',
            )

        except Exception as e:
            err_msg = '拠点内営業部向け: 部店名称分割処理でエラーが発生しました'
            log_msg(err_msg, LogLevel.ERROR)
            raise BranchNameSplitError(err_msg) from e
        else:
            return df


    @staticmethod
    def _process_area_data(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
        """エリアデータの処理

        setup_area_to_integrated_data()加工処理実体

        Args:
            df: 処理対象DataFrame
            mask: 処理対象行のマスク

        Returns:
            pd.DataFrame: 処理後のDataFrame

        Raises:
            RemarksParseError: 備考欄の解析に失敗した場合
        """
        try:
            # 結果を格納するDataFrameをコピー
            result_df = df.copy()

            # 備考欄の解析
            parsed_series = df.loc[mask, 'remarks'].apply(ReferenceMergers._parse_remarks)

            # エリアグループ情報の設定
            result_df.loc[mask, 'branch_code'] = parsed_series.apply(lambda x: x['area_group']['group_code'])
            result_df.loc[mask, 'branch_name'] = parsed_series.apply(lambda x: x['area_group']['group_name'])

            # デバッグ情報の出力
            ReferenceMergers._log_parsed_remarks_results(parsed_series)

        except Exception as e:
            err_msg = f'エリア向け: 備考欄の解析処理でエラーが発生しました: {e}'
            log_msg(err_msg, LogLevel.ERROR)
            raise RemarksParseError(err_msg) from e
        else:
            return result_df

    @staticmethod
    def _process_section_under_internal_sales(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
        """拠点内営業部配下課データの処理

        setup_section_under_internal_sales_integrated_data()加工処理実体

        Args:
            df: 処理対象DataFrame
            mask: 処理対象行のマスク

        Returns:
            pd.DataFrame: 処理後のDataFrame

        Raises:
            RemarksParseError: 備考欄の解析に失敗した場合
        """
        try:
            # 備考欄の解析と情報の設定
            parsed_series = df.loc[mask, 'remarks'].apply(ReferenceMergers._parse_remarks)

            # 拠点内営業部コードの設定
            df.loc[mask, 'internal_sales_dept_code'] = ReferenceMergers._find_branch_code_from_remarks(df, mask)

            # 拠点内営業部名称の設定
            df.loc[mask, 'internal_sales_dept_name'] = parsed_series.apply(
                lambda x: x['sales_department']['department_name'],
            )

            # デバッグ情報の出力
            ReferenceMergers._log_parsed_remarks_results(parsed_series)

        except Exception as e:
            err_msg = f'拠点内営業部配下課向け: 備考欄の解析処理でエラーが発生しました: {str(e)}'
            log_msg(err_msg, LogLevel.ERROR)
            raise RemarksParseError(err_msg) from e
        else:
            return df

    @staticmethod
    def _find_branch_code_from_remarks(df: pd.DataFrame, mask: pd.Series) -> pd.Series:
        """備考欄に基づく部店コードの検索

        setup_section_under_internal_sales_integrated_data()データ探索処理の実体
        '名称'で探索している点に留意が必要

        Args:
            df: 処理対象DataFrame
            mask: 処理対象行のマスク

        Returns:
            pd.Series: 検索された部店コード
        """
        # 拠点内営業部の申請レコードのみ抽出
        internal_sales_df = df[
            df['target_org'] == OrganizationType.INTERNAL_SALES.value
        ][['branch_name', 'branch_code']]

        # branch_nameの重複チェック - データ不整合確認を最優先
        duplicated_names = internal_sales_df['branch_name'].duplicated()
        if duplicated_names.any():
            duplicated_list = internal_sales_df.loc[duplicated_names, 'branch_name'].tolist()
            err_msg = f"拠点内営業部名に重複があります(データ不整合): {', '.join(duplicated_list)}"
            log_msg(err_msg, LogLevel.ERROR)
            raise RemarksParseError(err_msg)

        try:
            # 備考欄から取得した拠点内営業部名でマッチング
            return df.loc[mask, 'remarks'].map(internal_sales_df.set_index('branch_name')['branch_code'])

        except Exception as e:
            err_msg = f"部店コードの検索でエラーが発生しました: {str(e)}"
            raise RemarksParseError(err_msg) from e

    #######################################################
    # Helper
    #######################################################
    @staticmethod
    def _handle_merge_error(err_msg: str) -> None:
        log_msg(err_msg, LogLevel.ERROR)
        raise DataMergeError(err_msg) from None

    #######################################################
    # Debugger
    #######################################################
    @staticmethod
    def _get_nested_dict_value(data: dict, field_path: str) -> dict:
        """ネストされた辞書から値を取得

        Args:
            data: 対象の辞書
            field_path: ドット区切りのフィールドパス

        Returns:
            Any: 取得した値
        """
        current = data
        for key in field_path.split('.'):
            current = current[key]
        return current

    @staticmethod
    def _log_bpr_flag_results(df: pd.DataFrame) -> None:
        """BPRADフラグ付与結果のログ出力

        Args:
            df: 処理結果のDataFrame
        """
        display_columns = [
            'branch_code', 'section_gr_code', 'area_code',
            'application_type', 'bpr_target_flag', 'reference_bpr_target_flag',
        ]

        # 全体結果
        log_msg("処理結果全体:\n")
        tabulate_dataframe(df[display_columns])

        # 新設/新設以外の内訳
        new_data = df[df['application_type'] == ApplicationType.NEW.value]
        non_new_data = df[df['application_type'] != ApplicationType.NEW.value]

        log_msg(f"新設データ ({len(new_data)}件):\n", LogLevel.DEBUG)
        tabulate_dataframe(new_data[display_columns])
        log_msg(f"新設以外データ ({len(non_new_data)}件):\n", LogLevel.DEBUG)
        tabulate_dataframe(non_new_data[display_columns])


    @staticmethod
    def _log_parsed_remarks_results(parsed_series: pd.Series) -> None:
        """備考欄解析結果のログ出力

        Args:
            parsed_series: 解析済みのSeries
        """
        debug_fields = [
            'request_type',
            'sales_department.department_name',
            'sales_department.branch_name',
            'area_group.group_code',
            'area_group.group_name',
            'area_group.established_date',
            'other_info',
        ]

        for field in debug_fields:
            try:
                value = parsed_series.apply(lambda x, f=field: ReferenceMergers._get_nested_dict_value(x, f))
                log_msg(f"{field}: {value}", LogLevel.DEBUG)
            except Exception as e:
                err_msg = f"デバッグ情報の出力でエラーが発生しました - {field}: {str(e)}"
                log_msg(err_msg, LogLevel.ERROR)
