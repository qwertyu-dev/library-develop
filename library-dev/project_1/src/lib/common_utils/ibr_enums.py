"""Enum定義"""
import logging
from enum import Enum, StrEnum


class LogLevel(Enum):
    """カスタムロガーのLogLevel定義"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

class ExecEnvironment(Enum):
    """パッケージ実行環境判別ラベル定義"""
    # TODO(me): HOSTNAME_XXXXXは実際のサーバホスト名に書き換える -> upper(_hostname)
    # issue-001
    # ただしHOSTNAME_LOCALはそのまま
    HOSTNAME_PRODUCTION = 'production'  # HOSTNAME_PRODUCTIONを実ホスト名@本番に書き換える
    ASBKIBR0BM001F0= 'regression'       # HOSTNAME_REGRESSION
    ASBKIBR0BM002F0 = 'local'           # HOSTNAME_DEVELOP 開発機でも任意一で稼働させるため'local'指定
    HOSTNAME_LOCAL = 'local'

class DigitsNumberforUnixtime(Enum):
    """UNIXTIME桁数定義"""
    DIGITS_10 = 10
    DIGITS_13 = 13
    DIGITS_16 = 16

class BprADFlagResults(Enum):
    """BPR ADフラグ定義"""
    NOT_BPR_TARGET: str = '0'
    BPR_TARGET: str =  '1'
    AD_ONLY: str =  '2'
    #NOT_BPR_TARGET: str = 'BPR対象外'
    #BPR_TARGET: str =  'BPR対象'
    #AD_ONLY: str =  'ADのみ'

class ApplicationType(Enum):
    """申請区分"""
    NEW: str = '新設'
    MODIFY: str = '変更'
    DISCONTINUE: str = '廃止'

class BranchCodeType(StrEnum):
    """部店コードの種類を表す列挙型"""
    DOMESTIC_BRANCH = "0"     # 国内支店
    CORPORATE_SALES = "1"     # 法人営業
    LOAN_PROMOTION = "2"      # ローン推進部
    OVERSEAS_BRANCH = "3"     # 海外拠点
    BANK_HEAD_OFFICE = "6"    # 銀行本部
    DORMITORY = "9"           # 寮

class RelatedCompanyType(StrEnum):
    """関連会社の種類を表す列挙型"""
    MUFG_HOLDINGS_71 = "71"    # 持株会社(MUFG)
    MUFG_HOLDINGS_72 = "72"    # 持株会社(MUFG)

class OrganizationType(StrEnum):
    """組織区分を表す列挙型"""
    BRANCH = "部店"                  # 部店
    INTERNAL_SALES = "拠点内営業部"  # 拠点内営業部
    SECTION_GROUP = "課"             # 課
    AREA = "エリア"                  # エリア

class FormType(StrEnum):
    """対象組織を表す列挙型"""
    JINJI = '1'                       # 人事
    KOKUKI = '2'                      # 国企
    KANREN_WITH_DUMMY = '3'           # 関連ダミー課あり
    KANREN_WITHOUT_DUMMY = '4'        # 関連ダミー課なし

class PatternID(StrEnum):
    """マッチングパターンIDを表す列挙型"""
    BRANCH_7818 = '1'
    BRANCH_4DIGIT = '2'
    BRANCH_5DIGIT_NON7 = '3'
    BRANCH_5DIGIT_7 = '4'
    INTERNAL_SALES = '5'
    SECTION_GROUP = '6'
    AREA = '7'
    RELATED_DUMMY = '8'

class PatternPriority(StrEnum):
    """パターンの優先順位を表す列挙型"""
    BRANCH_7818 = '1'      # 7818を先に処理
    BRANCH_4DIGIT = '2'
    BRANCH_5DIGIT_NON7 = '3'
    BRANCH_5DIGIT_7 = '4'  # 7始まりを後に処理
    INTERNAL_SALES = '5'
    RELATED_DUMMY = '6'
    SECTION_GROUP = '7'
    AREA = '8'

class BranchCodeLength(StrEnum):
    """部店コード長を表す列挙型"""
    BRANCH_LENGTH_4 = '4'
    BRANCH_LENGTH_5 = '5'
