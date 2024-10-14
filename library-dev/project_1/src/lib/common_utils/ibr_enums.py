"""Enum定義"""
import logging
from enum import Enum


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
    HOSTNAME_REGRESSION = 'regression'  # HOSTNAME_REGRESSION
    HOSTNAME_DEVELOP = 'develop'        # HOSTNAME_DEVELOP
    HOSTNAME_LOCAL = 'local'

class DigitsNumberforUnixtime(Enum):
    """UNIXTIME桁数定義"""
    DIGITS_10 = 10
    DIGITS_13 = 13
    DIGITS_16 = 16
