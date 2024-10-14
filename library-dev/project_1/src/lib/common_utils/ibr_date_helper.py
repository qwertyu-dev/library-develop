"""日付処理サポートライブラリ"""

import sys
import traceback
from datetime import datetime
from pathlib import Path

from dateutil import tz

from src.lib.common_utils.ibr_decorator_config import (
    initialize_config,
)
from src.lib.common_utils.ibr_enums import (
    DigitsNumberforUnixtime,
    LogLevel,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

################################
# tz生成
################################
UTC = tz.tzutc()
JST = tz.gettz('Aaia/Tokyo')

################################
# 関数定義
################################

class ConvertWithTimezoneError(Exception):
    """date_helperに関する独自例外定義"""

def convert_with_no_timezone_to_jst(
    date_str: str,
    date_format: str='%Y/%m/%d %H:%M:%S',
    ) -> datetime|None:
    """timezoneを持たないUTC日付文字列をdatatime-JSTに変換する

    - プロダクトによってはUTCでしか日付還元がないものがある
    - 利便性向上の為UTCをJSTに変換したdatatimeを生成する

    Copy right:
        (あとで書く)

    Args:
        date_str (str): UTC基準の日付文字列、tzを持たない
        date_format (str): default='%Y/%m/%d %H:%M:%S' 取り込みデータ日付フォーマット

    Returns:
        (datetime|None): JST変換後のdatetime

    Raises:
        Exception: datetime変換処理中のエラー

    Example:
        >>> _date_time = convert_with_no_timezone_to_jst('2024/01/01 00:00:00')

    Notes:
        UTC基準のデータが対象となります

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    try:
        return datetime.strptime(date_str, date_format).replace(tzinfo=UTC).astimezone(JST)
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        return None


def convert_with_timezone_to_jst(
    date_str: str,
    date_format: str='%Y/%m/%d %H:%M:%S%z',
    ) -> datetime|None:
    """timezoneを持つUTC日付文字列をdatatime-JSTに変換する

    - プロダクトによってはUTCでしか日付還元がないものがある
    - 利便性向上の為UTCをJSTに変換したdatatimeを生成する

    Copy right:
        (あとで書く)

    Args:
        date_str (str): UTC基準の日付文字列、tzを持つ
        date_format (str): default='%Y/%m/%d %H:%M:%S' 取り込みデータ日付フォーマット

    Returns:
        (datetime|None): JST変換後のdatetime

    Raises:
        Exception: datetime変換処理中のエラー

    Example:
        >>> _date_time = convert_with_timezone_to_jst('2024/01/01 00:00:00+0000')

    Notes:
        UTC基準のデータが対象となります

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    try:
        return datetime.strptime(date_str, date_format).astimezone(JST)
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        return None


def _fromtimestamp_wrapper(unixtime, tz) -> datetime:
    """UNIXTIME変換ヘルパー"""
    return datetime.fromtimestamp(unixtime, tz)


def convert_unixtime_to_jst(unixtime_str: str) -> datetime|None:
    """UNIXTIMEをdatatime-JSTへ変換する

    - プロダクトによってはUNIXTIMEでしか日付還元がないものがある
    - 利便性向上の為UTCをJSTに変換したdatatimeを生成する

    Copy right:
        (あとで書く)

    Args:
        unixtime_str (str): UNIXITMEを保有する文字列,10,13,16桁

    Returns:
        (datetime|None): JST変換後のdatetime

    Raises:
        Exception: datetime変換処理中のエラー

    Example:
        >>> target_string = '1615860122'
        >>> result = convert_unixtime_to_jst(target_string)

    Notes:
        ...

    Changelog:
        - v1.0.0 (2024/01/01): Initial release
        -
    """
    if unixtime_str is None:
        return None
    if len(unixtime_str) == int(DigitsNumberforUnixtime.DIGITS_10.value):
        unixtime = int(unixtime_str)
    elif len(unixtime_str) == int(DigitsNumberforUnixtime.DIGITS_13.value):
        unixtime = int(unixtime_str) // 1000
    elif len(unixtime_str) == int(DigitsNumberforUnixtime.DIGITS_16.value):
        unixtime = int(unixtime_str) // 1000000
    else:
        log_msg(f'unixtime_strは10/13/16桁のいずれかでなければなりません: {len(unixtime_str)}桁', LogLevel.ERROR)
        return None

    try:
        log_msg(f'unixtime: {unixtime}', LogLevel.INFO)
        return _fromtimestamp_wrapper(unixtime, tz=UTC).astimezone(JST)
    except Exception as e:
        tb = traceback.TracebackException.from_exception(e)
        log_msg(''.join(tb.format()), LogLevel.ERROR)
        return None

# add 2024/05/04
def load_calendar_file(calendar_file_path: str | Path) -> tuple[set[str], set[str]]:
    """銀行カレンダーファイルを読み込み、休業日と営業日のセットを返す

    Args:
        calendar_file_path (str | Path): 銀行カレンダーファイルのパス

    Returns:
        tuple[set[str], set[str]]: 休業日と営業日のセット

    Raises:
        FileNotFoundError: 銀行カレンダーファイルが存在しない場合
        ValueError: 無効なフォーマットの行がある場合
    """
    calendar_file_path = Path(calendar_file_path)
    if not calendar_file_path.exists():
        log_msg = f"銀行カレンダーファイルが見つかりません: {calendar_file_path}"
        raise FileNotFoundError(log_msg)

    closed_days = set()
    operation_days = set()
    with calendar_file_path.open('r') as file:
        for line in file:
            striped_line = line.strip()
            key, value = striped_line.split('=', maxsplit=1)
            if key == 'cl':
                closed_days.add(value)
            elif key == 'op':
                operation_days.add(value)
            else:
                msg = f"無効なフォーマット: {line}"
                raise ValueError(msg)
    return closed_days, operation_days


def _convert_date_to_string(date: str | datetime) -> str:
    """日付をYYYY/MM/DD形式の文字列に変換する

    Args:
        date (str | datetime): 変換する日付

    Returns:
        str: YYYY/MM/DD形式の日付文字列

    Raises:
        ValueError: 日付のフォーマットが正しくない場合
        TypeError: 引数の型が正しくない場合
    """
    if isinstance(date, datetime):
        return date.strftime('%Y/%m/%d')
    if isinstance(date, str):
        datetime.strptime(date, '%Y/%m/%d').replace(tzinfo=UTC).astimezone(JST)
        return date
    msg = f"日付は文字列もしくはdatetime型でなければなりません: {type(date)}"
    raise TypeError(msg)


def is_bank_business_day(date: str | datetime, calendar_file_path: str | Path) -> bool | None:
    """銀行営業日判定関数

    JP1提供銀行カレンダーに基づき、指定日付が銀行営業日であるかの判定を行う

    Args:
        date (str | datetime): 判定対象の日付(文字列またはdatetime型)
        calendar_file_path (str): 銀行カレンダーファイルのパス

    Returns:
        bool: 銀行営業日の場合はTrue、銀行休業日の場合はFalse
        None: 判定不能の場合

    Raises:
        FileNotFoundError: 銀行カレンダーファイルが存在しない場合
        ValueError: 日付のフォーマットが正しくない場合
        TypeError: 引数の型が正しくない場合
    """
    try:
        closed_days, operation_days = load_calendar_file(calendar_file_path)
    except (FileNotFoundError, ValueError) as e:
        log_msg(str(e))
        raise

    try:
        date_string = _convert_date_to_string(date)
    except (ValueError, TypeError) as e:
        log_msg(str(e))
        raise

    if date_string in closed_days:
        return False
    if date_string in operation_days:
        return True
    return None
