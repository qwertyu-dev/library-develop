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
    AD_ONLY: str =  'ADのみ'
    BPR_TARGET: str =  'BPR対象'
    NOT_BPR_TARGET: str = 'BPR対象外'

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
    BRANCH = "部"                    # 部
    INTERNAL_SALES = "拠点内営業部"  # 拠点内営業部
    SECTION_GROUP = "課"             # 課
    AREA = "エリア"                  # エリア
