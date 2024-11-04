
import re
from pathlib import Path
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from src.lib.common_utils.ibr_eventlog_handler import WindowsEventLogger
#from typing import FrozenSet
#from typing import FrozenDict
from enum import Enum, StrEnum
from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe

from src.lib.common_utils.ibr_enums import (
    BprADFlagResults,
    ApplicationType,
    BranchCodeType,
    RelatedCompanyType,
)

# config共有
import sys
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher

config = initialize_config(sys.modules[__name__])
package_config = config.package_config
log_msg = config.log_message

# Enum定義へ移植
#@dataclass
#class BprADFlagResults(frozen=True):
#    AD_ONLY: str =  'ADのみ'
#    BPR_TARGET: str =  'BPR対象'
#    NOT_BPR_TARGET: str = 'BPR対象外'

#class APPLICATION_TYPE(frozen=True):
#    NEW: str = '新設'
#    MODIFY: str = '変更'
#    DISCONTINUE: str = '廃止'

#@dataclass
#class ConditionCode(frozen=True):
#    ZERO_CODE: str = '0'
#    FORM_TYPE_KOKUKI: str = '1'

class BprFragDeterminerError(Exception):
    pass

class BprTargetConfig:
    """BPR対象設定を表すデータクラス"""
    SINGLE_DIGIT_RULES = {
        BranchCodeType.DOMESTIC_BRANCH.value: BprADFlagResults.BPR_TARGET.value,
        BranchCodeType.CORPORATE_SALES.value: BprADFlagResults.BPR_TARGET.value,
        BranchCodeType.LOAN_PROMOTION.value: BprADFlagResults.BPR_TARGET.value,
        BranchCodeType.OVERSEAS_BRANCH.value: BprADFlagResults.AD_ONLY.value,
        BranchCodeType.BANK_HEAD_OFFICE.value: BprADFlagResults.BPR_TARGET.value,
        BranchCodeType.DORMITORY.value: BprADFlagResults.NOT_BPR_TARGET.value,
    }

    TWO_DIGIT_RULES = {
        RelatedCompanyType.MUFG_HOLDINGS_71.value: BprADFlagResults.BPR_TARGET.value,
        RelatedCompanyType.MUFG_HOLDINGS_72.value: BprADFlagResults.BPR_TARGET.value,
    }

    NOT_BPR_TARGET_PREFIXES = {
        '70', '73', '74', '75', '76', '77', '78', '79',
    }

class AlertCode(Enum):
    """アラートコードを表す列挙型"""
    HQ_SPECIFIC_WORD = 1001
    BPR_FLAG_CHECK = 1002
    BRANCH_CODE_ERROR = 1003

class ValidationConfig:
    """バリデーション設定を表すデータクラス"""
    ZERO_CODE: str = '0'

    # form_type定義
    FORM_TYPE_JINJI: str = '1'
    FORM_TYPE_KOKUKI: str = '2'
    FORM_TYPE_KANREN_WITH_DUMMMY: str = '3'
    FORM_TYPE_KANREN_WITHOUT_DUMMMY: str = '4'

    #ALERT_MESSAGES: FrozenDict[AlertCode, str] = field(default_factory=lambda: FrozenDict({
    ALERT_MESSAGES: dict[AlertCode, str] =  {
        AlertCode.HQ_SPECIFIC_WORD: "部店コード6系,名称に特定キーワードあり: {name}",
        AlertCode.BPR_FLAG_CHECK: "BPR-ADフラグ判定アラート: {message}",
        AlertCode.BRANCH_CODE_ERROR: "部店コードエラー: {code}",
    }

    #ALERT_DETAILS: FrozenDict[AlertCode, tuple[str, list[str]]] = field(default_factory=lambda: FrozenDict({
    ALERT_DETAILS: dict[AlertCode, tuple[str, list[str]]] = {
        AlertCode.HQ_SPECIFIC_WORD: (
            '要確認アラート: リファレンス BPR-ADフラグ初期値設定',
            ['部店コード6始まり', '課Gr名称、エリア名称に特定キーワードあり'],
        ),
        AlertCode.BPR_FLAG_CHECK: (
            '要確認アラート: リファレンス BPR-ADフラグ初期値設定',
            ['課Grコード0レコードなく、BPR対象外'],
        ),
    }

class BprAdFlagDeterminer:
    """BPR・AD対象フラグを決定するクラス

    Class Overview:
        このクラスは、銀行の部署情報に基づいてBPR・AD対象フラグを決定するロジックを実装します。
        新設、変更、廃止の各処理タイプに対応し、部店コードや課Gコードなどの条件に基づいて
        適切なフラグを設定します。また、特定の条件下でアラートを生成します。

    """
    def __init__(self, file_path: str|None=None):
        """コンストラクタ

        Arguments:
            file_path(str): pickleファイルをデフォルトPath以外から読み取る際に設定
        """
        # 設定情報取得
        self.SPECIFIC_WORDS = package_config.get('ibr_bpr_flag_determiner',{}).get('SpecificWords','')
        file_path = file_path if file_path else None
        log_msg(f'init file_path: {file_path}', LogLevel.INFO)
        reference_data = package_config.get('ibr_bpr_flag_determiner',{}).get('reference_data','')
        request_data = package_config.get('ibr_bpr_flag_determiner',{}).get('request_data','')

        # リファレンスデータ.pickle及び申請明細.pickleを取得する,読み取り専用で利用
        reference = TableSearcher(reference_data, file_path)
        request = TableSearcher(request_data, file_path)
        self.reference_df = reference.df
        self.request_df = request.df
        log_msg(f'init self.reference_df: \n\n{tabulate_dataframe(self.reference_df.head(5))}', LogLevel.DEBUG)
        log_msg(f'init self.request_df: \n\n{tabulate_dataframe(self.request_df)}', LogLevel.DEBUG)

    def determine_bpr_ad_flag(self, series: pd.Series) -> str:
        """申請データからBPR/ADフラグ標準設定値を決定する

        Arguments:
            series(pd.Series): 編集対象series,outputレイアウト構造と初期値設定状態
        """
        # 種類 | application_type により分岐する / 新設 or 変更 or 削除
        log_msg(f"series.application_type: {series['application_type']}", LogLevel.INFO)
        match series['application_type']:
            case ApplicationType.NEW.value: # 新設
                # Case.1: 申請元が国企かつ部店コード先頭1桁が6
                if ((series['form_type'] == ValidationConfig.FORM_TYPE_KOKUKI) and (series['branch_code'].startswith('6'))):
                    return BprADFlagResults.AD_ONLY

                # 課Grコード0部店の存在チェック
                result_df = (self._exists_branch_code_with_zero_group_code(series))
                log_msg(f'\n課Grコード"0"部店の存在チェック 探索結果: \n{tabulate_dataframe(result_df)}', LogLevel.INFO)

                # Case.2 課Grコード0部店有り,探索結果のBPR_ADフラグをセットする
                if len(result_df):
                    # アラート判定
                    self._alert_case_hq(series['branch_code'], series['section_gr_name'])
                    alert_msg = "部店コード6系,名称に特定キーワード有り {series['section_gr_name']}"
                    log_msg(f'BPR-ADフラグ判定アラート: {alert_msg}', LogLevel.ERROR)
                    # 結果還元 存在するDataから値取得する,値取得なので[0]で取り出し
                    log_msg(f"BPR AD Flag: {result_df['bpr_target_flag'].to_numpy()[0]}",LogLevel.DEBUG)
                    return result_df['bpr_target_flag'].to_numpy()[0]

                # Case.3: 課Grコード0部店が存在しない, branch_codeで分岐制御
                return self._ensure_new_division_bprad_flag_config(series)

            case ApplicationType.MODIFY.value: # 変更
                # self.reference_dfに対して探索実施
                # TODO():edited_seriesの探索キー
                # TODO():referenceテーブルの対となる探索キー
                return 'リファレンステーブルからの情報取得'

            case ApplicationType.DISCONTINUE.value: # 廃止
                # TODO(): 変更でも廃止でも同じ処理、どう実装するか
                return 'リファレンステーブルからの情報取得'

            case _:
                # 想定外の値の場合の処理
                err_msg = f"Unexpected application_type: {series['application_type']}"
                raise ValueError(err_msg) from None

    def _ensure_new_division_bprad_flag_config(self, series: pd.Series) -> str:
        # 判定
        if not series['branch_code']:
            # Enum保有値を返す,enum自体を返すのではない
            return BprADFlagResults.NOT_BPR_TARGET.value

        # 1桁判定
        if flag := BprTargetConfig.SINGLE_DIGIT_RULES.get(series['branch_code'][0]):
            self._alert_case_hq(series['branch_code'], series['branch_name'])
            return flag

        # 2桁判定
        prefix = series['branch_code'][:2]
        if flag := BprTargetConfig.TWO_DIGIT_RULES.get(prefix):
            return flag

        # 対象外判定
        if prefix in BprTargetConfig.NOT_BPR_TARGET_PREFIXES:
            # アラート判定
            self._alert_case_any()
            alert_msg = f"部店コード{series['branch_code']}"
            log_msg(f'BPR-ADフラグ判定アラート: {alert_msg}', LogLevel.ERROR)
            # Enum保有値を返す,enum自体を返すのではない
            return BprADFlagResults.NOT_BPR_TARGET.value

        # ヒット無し,Enum保有値を返す,enum自体を返すのではない
        return BprADFlagResults.NOT_BPR_TARGET.value

    def _exists_branch_code_with_zero_group_code(self, series: pd.Series) -> pd.DataFrame:
        """指定された部店コードを持つレコードの中で、

        課Grコードまたはエリアコードがゼロのレコードが存在するかチェックする

        Args:
            series (pd.Series): チェック対象の行

        Returns:
            bool: 条件に合致するレコードが存在すればTrue、存在しなければFalse

        Note:
            - 部店コードが一致するレコードを抽出
            - 抽出したレコードの中から課Grコード=='0'またはエリアコード=='0'を持つものを検索
        """
        try:
            # 処理中series部店コードに対し、申請明細から部店コード一致抽出
            cond_branch_df = self._filter_by_branch_code(series)
            log_msg(f'debug---\n\n{tabulate_dataframe(cond_branch_df)}', LogLevel.DEBUG)
            if cond_branch_df.empty:
                return pd.DataFrame()

            # 申請明細から抽出したレコードに対して条件抽出
            return self._filter_zero_group_codes(cond_branch_df)

        except KeyError as e:
            # 必要なカラムが存在しない場合のエラーハンドリング
            error_msg = f"Required column {str(e)} not found in DataFrame"
            log_msg(f'{error_msg}', LogLevel.INFO)
            return pd.DataFrame()
        except Exception as e:
            raise BprFragDeterminerError from e

    def _filter_by_branch_code(self, series: pd.Series) -> pd.DataFrame:
        """部店コードでフィルタリング"""
        mask = (self.request_df['branch_code'] == series['branch_code'])
        log_msg(f'debug---mask\n\n{mask}', LogLevel.DEBUG)
        return self.request_df[mask]

    #def _filter_zero_group_codes(self, df: pd.DataFrame) -> pd.DataFrame:
    #    """課Grコードまたはエリアコードがゼロのレコードをフィルタリング"""
    #    return df[
    #        (df['section_gr_code'] == ValidationConfig.ZERO_CODE) |
    #        (df['business_and_area_code'] == ValidationConfig.ZERO_CODE)
    #    ]
    def _filter_zero_group_codes(self, df: pd.DataFrame) -> pd.DataFrame:
        """課Grコードまたはエリアコードがゼロのレコードをフィルタリング"""
        mask = pd.Series(False, index=df.index)
        if 'section_gr_code' in df.columns:
            mask |= (df['section_gr_code'] == ValidationConfig.ZERO_CODE)
        if 'business_and_area_code' in df.columns:
            mask |= (df['business_and_area_code'] == ValidationConfig.ZERO_CODE)
        return df[mask]

    def _is_specific_word_in_name(self, name: str) -> bool:
        """(内部関数)部名/課G名(name: str)に特定の単語が含まれているかをチェックする

        Args:
            name (str): チェック対象の課G名/部名称 # 引数名をnameに統一

        Returns:
            bool: 特定の単語が文字列に部分的にも含まれている場合はTrue、そうでない場合はFalse

        Examples:
            >>> checker = DepartmentChecker()
            >>> checker.is_specific_word_in_name("米州")
            True
            >>> checker.is_specific_word_in_name("営業")
            False
        """
        # 空文字チェック
        if not name:
            return False

        # 各特定ワードについてチェック
        return any(specific_word in name for specific_word in self.SPECIFIC_WORDS)

    def _alert_case_hq(self, branch_code: str, name: str) -> None:
        if (branch_code.startswith(BranchCodeType.BANK_HEAD_OFFICE) and
            any(word in name for word in self.SPECIFIC_WORDS)):

            title, details = ValidationConfig.ALERT_DETAILS[AlertCode.HQ_SPECIFIC_WORD]
            WindowsEventLogger.write_error_log(title, AlertCode.HQ_SPECIFIC_WORD.value, details)

    def _alert_case_any(self) -> None:
        title, details = ValidationConfig.ALERT_DETAILS[AlertCode.BPR_FLAG_CHECK]
        WindowsEventLogger.write_error_log(title, AlertCode.BPR_FLAG_CHECK.value, details)

    #def _alert_case_hq(self, branch_code: str, name: str) -> None:
    #    if (branch_code.startswith('6') & (any(specific_word in name for specific_word in self.SPECIFIC_WORDS))):
    #        # WindowsSyslogへ出力
    #        WindowsEventLogger.write_error_log(
    #            '要確認アラート: リファレンス BPR-ADフラグ初期値設定',
    #            1002,
    #            ['部店コード6始まり','課Gr名称、エリア名称に特定キーワードあり'],
    #        )

    #def _alert_case_any(self) -> None:
    #    # WindowsSyslogへ出力
    #        WindowsEventLogger.write_error_log(
    #            '要確認アラート: リファレンス BPR-ADフラグ初期値設定',
    #            1002,
    #            ['課Grコード0レコードなく、BPR対象外'],
    #        )

