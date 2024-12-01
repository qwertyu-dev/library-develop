# config共有
import sys
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto

import pytz

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel

config = initialize_config(sys.modules[__name__])
package_config = config.package_config
log_msg = config.log_message

class DateParseError(Exception):
    """日付解析時のカスタムエラー"""

class OutputFormat(Enum):
    """日付文字列の出力形式を定義する列挙型

    Attributes:
        WESTERN: YYYY/MM/DD形式
        YYYYMMDD: YYYYMMDD形式
        JAPANESE: GYYMMDD形式(G:元号コード)
    """
    WESTERN = 'western'
    YYYYMMDD = 'yyyymmdd'
    JAPANESE = 'japanese'

class DateConverter:
    """日付文字列をdatetime型に変換するユーティリティクラス

    このクラスは以下の形式日付文字列を処理できます
    YYYY/MM/DD(西暦形式)
    YYYYMMDD(8桁数字形式)
    GYYMMDD(和暦形式、G: 元号コード)

    全てのメソッドはstaticメソッドと定義する

    Usage:
        dt = DateConverter.parse('2024/11/30')
        dt = DateConverter.parse('20241130')
        dt = DateConverter.parse('5061130')
        dt = DateConverter.parse('5061130', 'UTC')
    """
    class _DateFormat(Enum):
        """日付フォーマットの内部分類"""
        WESTERN = auto()
        JAPANESE = auto()
        YYYYMMDD = auto()
        UNKNOWN = auto()

    @dataclass(frozen=True)
    class _DateConstants:
        """日付処理に関する内部定数"""
        WESTERN_DATE_LENGTH: int = 10
        JAPANESE_DATE_LENGTH: int = 7
        YYYYMMDD_DATE_LENGTH: int = 8
        #
        WESTERN_DATE_SEPARATOR: str = '/'
        WESTERN_YEAR_INDEX: int = 4
        WESTERN_MONTH_INDEX: int = 7
        #
        YYYYMMDD_YEAR_END: int = 4
        YYYYMMDD_MONTH_END: int = 6
        #
        ERA_INDEX: int = 0
        YEAR_START_INDEX: int = 1
        YEAR_END_INDEX: int = 3
        MONTH_START_INDEX: int = 3
        MONTH_END_INDEX: int = 5
        DAY_START_INDEX: int = 5
        DAY_END_INDEX: int = 7
        #
        YEAR_REIWA: int = 2019
        MIN_YEAR: int = 1926  # 昭和元年
        MAX_YEAR: int = 2100  # システム上限


    _CONSTANTS = _DateConstants()

    @staticmethod
    def parse(date_string: str, timezone_name: str='Asia/Tokyo') -> datetime:
        """日付文字列をdatetimeオブジェクトに変換します

        Args:
            date_string: 変換対象の日付文字列
            timezone_name: タイムゾーン名(デフォルト: 'Asia/Tokyo')

        Returns:
            datetime: 変換後のdatetimeオブジェクト

        Raises:
            DateParseError: 日付文字列の解析に失敗した場合
        """
        date_format = DateConverter._determine_format(str(date_string))
        timezone = pytz.timezone(timezone_name)
        try:
            year, month, day = DateConverter._parse_components(date_string, date_format)
            return DateConverter._create_datetime(year, month, day, timezone)
        except DateParseError:
            raise
        except Exception as e:
            err_msg = f"AAA提供日解析に失敗しました: {str(e)}"
            raise DateParseError(err_msg) from None

    @staticmethod
    def is_valid_date(date_string: str) -> bool:
        """日付文字列が有効な形式かどうかを判定する

        一括申請Validationでの使用を想定して提供

        Args:
            date_string: 検証対象の日付文字列

        Returns:
            bool: 有効な日付形式の場合True
        """
        try:
            DateConverter.parse(date_string)
        except DateParseError:
            return False
        else:
            return True

    @staticmethod
    def to_string(dt: datetime, output_format: OutputFormat = OutputFormat.WESTERN) -> str:
        """datetimeオブジェクトを指定された形式の文字列に変換する

        Args:
            dt: 変換対象のdatetimeオブジェクト
            output_format: 出力形式(OutputFormat列挙型の値)

        Returns:
            str: 変換後の日付文字列

        Raises:
            ValueError: 未対応の出力形式が指定された場合
        """
        const = DateConverter._CONSTANTS

        if output_format == OutputFormat.WESTERN:
            return dt.strftime('%Y/%m/%d')

        if output_format == OutputFormat.YYYYMMDD:
            return dt.strftime('%Y%m%d')

        if output_format == OutputFormat.JAPANESE:
            year = dt.year
            if year >= const.YEAR_REIWA:
                era_code = 5  # 令和
                era_year = year - const.YEAR_REIWA + 1
            else:
                err_msg = "Date is too old for Japanese era conversion"
                raise ValueError(err_msg) from None

            return f"{era_code}{era_year:02d}{dt.month:02d}{dt.day:02d}"

        err_msg = f"Unsupported output format: {output_format}"
        raise ValueError(err_msg) from None

    @staticmethod
    def _determine_format(date_string: str) -> _DateFormat:
        """日付文字列のフォーマットを判定"""
        if not isinstance(date_string, str):
            return DateConverter._DateFormat.UNKNOWN

        const = DateConverter._CONSTANTS

        if (len(date_string) == const.WESTERN_DATE_LENGTH and
            date_string[const.WESTERN_YEAR_INDEX] == const.WESTERN_DATE_SEPARATOR and
            date_string[const.WESTERN_MONTH_INDEX] == const.WESTERN_DATE_SEPARATOR
            ):
            return DateConverter._DateFormat.WESTERN

        if (len(date_string) == const.YYYYMMDD_DATE_LENGTH and
            date_string.isdigit()
            ):
            return DateConverter._DateFormat.YYYYMMDD

        if (len(date_string) == const.JAPANESE_DATE_LENGTH and
            date_string.isdigit()
        ):
            return DateConverter._DateFormat.JAPANESE

        err_msg = "Unsupported date format"
        return DateParseError(err_msg)

    @staticmethod
    def _parse_components(date_string: str, format_date: _DateFormat) -> tuple[int, int, int]:
        """日付文字列から年月日の要素を抽出"""
        if format_date == DateConverter._DateFormat.WESTERN:
            return DateConverter._parse_western(date_string)
        if format_date == DateConverter._DateFormat.YYYYMMDD:
            return DateConverter._parse_yyyymmdd(date_string)
        if format_date == DateConverter._DateFormat.JAPANESE:
            return DateConverter._parse_japanese(date_string)

        err_msg = "Unsupported date_format"
        raise DateParseError(err_msg) from None

    @staticmethod
    def _parse_western(date_string: str) -> tuple[int, int, int]:
        """YYYY/MM/DD形式を解析"""
        try:
            year_str, month_str, day_str = date_string.split(DateConverter._CONSTANTS.WESTERN_DATE_SEPARATOR)
            return int(year_str), int(month_str), int(day_str)
        except (ValueError, IndentationError) as e:
            err_msg = f'Invalid western date format: {str(e)}'
            raise DateParseError(err_msg) from e

    @staticmethod
    def _parse_yyyymmdd(date_string: str) -> tuple[int, int, int]:
        """YYYYMMDD形式を解析"""
        const = DateConverter._CONSTANTS
        try:
            year_str = date_string[:const.YYYYMMDD_YEAR_END]
            month_str = date_string[const.YYYYMMDD_YEAR_END:const.YYYYMMDD_MONTH_END]
            day_str = date_string[const.YYYYMMDD_MONTH_END:]
            return int(year_str), int(month_str), int(day_str)
        except (ValueError, IndentationError) as e:
            err_msg = f'Invalid YYYYMMDD date format: {str(e)}'
            raise DateParseError(err_msg) from e

    @staticmethod
    def _parse_japanese(date_string: str) -> tuple[int, int, int]:
        """和暦形式を解析"""
        const = DateConverter._CONSTANTS
        try:
            era_code_str = date_string[const.ERA_INDEX]
            year_str = date_string[const.YEAR_START_INDEX:const.YEAR_END_INDEX]
            month_str = date_string[const.MONTH_START_INDEX:const.MONTH_END_INDEX]
            day_str = date_string[const.DAY_START_INDEX:const.DAY_END_INDEX]

            year = max(int(year_str), 1)  # 年が00の場合は1年としてあつかう
            western_year = DateConverter._convert_japanese_to_western(int(era_code_str), year)
            return western_year, int(month_str), int(day_str)
        except (ValueError, IndexError) as e:
            err_msg = f"Invalid Japanese date format: {str(e)}"
            raise DateParseError(err_msg) from None

    @staticmethod
    def _convert_japanese_to_western(era_code: int, year: int) -> int:
        """和暦年を西暦年に変換"""
        era_start_years = {
            5: 2019,  # 令和
            4: 1989,  # 平成
            3: 1926,  # 昭和
        }

        if era_code not in era_start_years:
            err_msg = f'Unknown era code: {era_code}'
            raise DateParseError(err_msg) from None

        # 年号元年のケースは入力ルールに留意が必要
        # 担当部署と意思確認すること
        if year < 1:
            err_msg = f'無効な年 "{year}" (年号コード {era_code})'
            raise ValueError(err_msg) from None

        return era_start_years[era_code] + year - 1

    @staticmethod
    def _create_datetime(year: int, month: int, day: int, timezone: pytz.timezone) -> datetime:
        """年月日からdatetimeオブジェクトを生成"""
        try:
            const = DateConverter._CONSTANTS
            if not (const.MIN_YEAR <= year <= const.MAX_YEAR):
                err_msg = f"Year {year} is out of valid range"
                raise DateParseError(err_msg) from None
            #dt = timezone.localize(datetime(year, month, day, tzinfo=timezone))
            dt = timezone.localize(datetime(year, month, day))
        except ValueError as e:
            err_msg = f"Invalid date components: {str(e)}"
            raise DateParseError(err_msg) from None
        else:
            return dt
