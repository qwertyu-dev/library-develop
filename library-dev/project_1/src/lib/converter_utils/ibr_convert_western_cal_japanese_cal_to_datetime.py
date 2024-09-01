"""和暦であっても西暦であってもdatetimeに変換する"""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import NamedTuple
import pytz

class DateFormat(Enum):
    """日付フォーマットの分類を定義するEnum

    Class Overview:
        日付文字列のフォーマットを西暦、和暦、不明の3種類に分類します。

    Attributes:
        WESTERN (auto): 西暦形式
        JAPANESE (auto): 和暦形式
        UNKNOWN (auto): 不明な形式

    Usage Example:
        >>> format = DateFormat.WESTERN
        >>> format
        <DateFormat.WESTERN: 1>

    Notes:
        - このEnumは日付文字列の形式を判別する際に使用されます。

    ResourceLocation:
        - [本体]
            - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
        - [テストコード]
            - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当            |
    |------|--------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |
    """
    WESTERN = auto()
    JAPANESE = auto()
    UNKNOWN = auto()

class DateParseError(Exception):
    """日付解析時のカスタムエラー

    Class Overview:
        日付文字列の解析中に発生するエラーを表現するための例外クラスです。

    Usage Example:
        >>> raise DateParseError("無効な日付形式です")
        DateParseError: 無効な日付形式です

    """

class JapaneseEra(NamedTuple):
    """日本の元号情報を表現するNamedTuple

    Class Overview:
        日本の元号に関する情報(名前、コード、開始年)を保持します。

    Attributes:
        name (str): 元号の名前
        code (int): 元号のコード
        start_year (int): 元号の開始年(西暦)
        max_year (Optional[int]): 元号の最大年(Noneの場合は現在進行中)

    Usage Example:
        >>> reiwa = JapaneseEra("令和", 5, 2018)
        >>> reiwa.name
        '令和'

    ResourceLocation:
        - [本体]
            - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
        - [テストコード]
            - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当            |
    |------|--------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |
    """
    name: str
    code: int
    start_year: int
    max_year: int | None

class Era(Enum):
    """日本の元号を管理するEnum

    Class Overview:
        日本の主要な元号(令和、平成、昭和)を定義し、和暦と西暦の変換機能を提供します。

    Attributes:
        REIWA (JapaneseEra): 令和の情報
        HEISEI (JapaneseEra): 平成の情報
        SHOWA (JapaneseEra): 昭和の情報

    Methods:
        from_code(code: int): 元号コードからEraオブジェクトを取得
        convert_japanese_year_to_western(era_code: int, era_year: int): 和暦年を西暦年に変換

    Usage Example:
        >>> Era.REIWA.value.name
        '令和'
        >>> Era.convert_japanese_year_to_western(5, 1)
        2019

    Notes:
        - 新しい元号を追加する場合は、このEnumに新しい要素を追加してください。

    ResourceLocation:
        - [本体]
            - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
        - [テストコード]
            - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当            |
    |------|--------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |
    """
    REIWA = JapaneseEra("令和", 5, 2019, max_year=None)
    HEISEI = JapaneseEra("平成", 4, 1989, max_year=31)
    SHOWA = JapaneseEra("昭和", 3, 1926, max_year=64)

    @classmethod
    def from_code(cls, code: int) -> 'Era':
        """元号コードからEraオブジェクトを取得する

        Arguments:
            code (int): 元号コード

        Return Value:
            Era: 対応するEraオブジェクト

        Exceptions:
            ValueError: 不明な元号コードの場合

        Usage Example:
            >>> Era.from_code(5)
            <Era.REIWA: JapaneseEra(name='令和', code=5, start_year=2018)>

        Algorithm:
            1. 全てのEra要素を走査
            2. 指定されたコードと一致する要素を返す
            3. 一致する要素がない場合はValueErrorを発生

        Notes:
            - この方法は、新しい元号が追加されても自動的に対応します。

        ResourceLocation:
            - [本体]
                - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
            - [テストコード]
                - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

        Chage History:
        | No   | 修正理由     | 修正点   | 対応日     | 担当            |
        |------|--------------|----------|------------|-----------------|
        | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |
        """
        for era in cls:
            if era.value.code == code:
                return era
        err_msg = f"Invalid era code: {code}"
        raise ValueError(err_msg) from None

    @classmethod
    def convert_japanese_year_to_western(cls, era_code: int, era_year: int) -> int:
        """和暦年を西暦年に変換する

        Arguments:
            era_code (int): 元号コード
            era_year (int): 和暦年

        Return Value:
            int: 変換後の西暦年

        Exceptions:
            ValueError: 不明な元号コードの場合

        Usage Example:
            >>> Era.convert_japanese_year_to_western(5, 1)
            2019

        Algorithm:
            1. from_code メソッドを使用して元号を特定
            2. 元号の開始年に、和暦年から1を引いた値を加算

        Notes:
            - 元年は1として扱われるため、計算時に1を引いています。

        ResourceLocation:
            - [本体]
                - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
            - [テストコード]
                - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

        Chage History:
        | No   | 修正理由     | 修正点   | 対応日     | 担当            |
        |------|--------------|----------|------------|-----------------|
        | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |
        """
        if era_year <= 0:
            err_msg = f"Invalid era year: {era_year}. Era year must be positive."
            raise ValueError(err_msg) from None

        era = cls.from_code(era_code)

        # 元号ごとの最大年チェック
        if era.value.max_year is not None and era_year > era.value.max_year:
            err_msg = f"Invalid era year: {era_year}. Maximum year for {era.value.name} is {era.value.max_year}."
            raise ValueError(err_msg) from None

        # 現在進行中の元号の場合、来年までを許容
        if era.value.max_year is None:
            current_year = datetime.now().year
            max_allowed_year = current_year - era.value.start_year + 2  # +2 for  year from now
            if era_year > max_allowed_year:
                err_msg = f"Invalid era year: {era_year}. Maximum allowed year for {era.value.name} is {max_allowed_year} (next year)."
                raise ValueError(err_msg) from None

        return era.value.start_year + era_year - 1


@dataclass(frozen=True)
class DateConstants:
    """日付処理に関する定数を定義するクラス

    Class Overview:
        日付文字列の解析に必要な各種定数を提供します。

    Attributes:
        WESTERN_DATE_LENGTH (int): 西暦形式の日付文字列の長さ
        JAPANESE_DATE_LENGTH (int): 和暦形式の日付文字列の長さ
        WESTERN_DATE_SEPARATOR (str): 西暦形式の日付区切り文字
        WESTERN_YEAR_INDEX (int): 西暦形式の年の区切り位置
        WESTERN_MONTH_INDEX (int): 西暦形式の月の区切り位置
        ERA_INDEX (int): 和暦形式の元号コードの位置
        YEAR_START_INDEX (int): 和暦形式の年の開始位置
        YEAR_END_INDEX (int): 和暦形式の年の終了位置
        MONTH_START_INDEX (int): 和暦形式の月の開始位置
        MONTH_END_INDEX (int): 和暦形式の月の終了位置
        DAY_START_INDEX (int): 和暦形式の日の開始位置
        DAY_END_INDEX (int): 和暦形式の日の終了位置

    Usage Example:
        >>> DateConstants.WESTERN_DATE_LENGTH
        10

    Notes:
        - これらの定数は日付文字列の解析時に使用されます。

    ResourceLocation:
        - [本体]
            - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
        - [テストコード]
            - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当            |
    |------|--------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |

    """
    WESTERN_DATE_LENGTH: int = 10
    JAPANESE_DATE_LENGTH: int = 7
    WESTERN_DATE_SEPARATOR: str = '/'
    WESTERN_YEAR_INDEX: int = 4
    WESTERN_MONTH_INDEX: int = 7
    ERA_INDEX: int = 0
    YEAR_START_INDEX: int = 1
    YEAR_END_INDEX: int = 3
    MONTH_START_INDEX: int = 3
    MONTH_END_INDEX: int = 5
    DAY_START_INDEX: int = 5
    DAY_END_INDEX: int = 7

def determine_date_format(date_string: str) -> DateFormat:
    """日付文字列のフォーマットを判定する

    Function Overview:
        与えられた日付文字列が西暦形式、和暦形式、または不明な形式のいずれかであるかを判定します。

    Arguments:
        date_string (str): 判定対象の日付文字列

    Return Value:
        DateFormat: 判定されたDateFormatオブジェクト

    Usage Example:
        >>> determine_date_format("2023/05/01")
        <DateFormat.WESTERN: 1>
        >>> determine_date_format("5050501")
        <DateFormat.JAPANESE: 2>

    Algorithm:
        1. 文字列の長さと区切り文字を確認して西暦形式かどうかを判定
        2. 文字列の長さと数字のみかどうかを確認して和暦形式かどうかを判定
        3. 上記のいずれにも該当しない場合は不明な形式と判定

    Notes:
        - この関数は日付文字列の形式のみを判定し、日付としての妥当性は確認しません。

    ResourceLocation:
        - [本体]
            - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
        - [テストコード]
            - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当            |
    |------|--------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |

    """
    if date_string is None or not isinstance(date_string, str):
        return DateFormat.UNKNOWN

    western_conditions = (
        len(date_string) == DateConstants.WESTERN_DATE_LENGTH
        and date_string[DateConstants.WESTERN_YEAR_INDEX] == DateConstants.WESTERN_DATE_SEPARATOR
        and date_string[DateConstants.WESTERN_MONTH_INDEX] == DateConstants.WESTERN_DATE_SEPARATOR
    )

    if western_conditions:
        return DateFormat.WESTERN

    japanese_conditions = (
        len(date_string) == DateConstants.JAPANESE_DATE_LENGTH
        and date_string.isdigit()
    )

    if japanese_conditions:
        return DateFormat.JAPANESE

    return DateFormat.UNKNOWN


def parse_str_to_datetime(date_string: str) -> datetime:
    """文字列形式の日付をdatetimeオブジェクトに変換する

    Function Overview:
        西暦形式(YYYY/MM/DD)または和暦形式(GYYMMDD)の日付文字列をdatetimeオブジェクトに変換します。

    Arguments:
        date_string (str): 'YYYY/MM/DD' または 'GYYMMDD' 形式の日付文字列

    Return Value:
        datetime.datetime: 変換されたdatetimeオブジェクト

    Usage Example:
        >>> parse_str_to_datetime("2023/05/01")
        datetime.datetime(2023, 5, 1, 0, 0)
        >>> parse_str_to_datetime("5050501")
        datetime.datetime(2023, 5, 1, 0, 0)

    Algorithm:
        1. 日付文字列のフォーマットを判定
        2. 西暦形式の場合、strptimeを使用して直接変換
        3. 和暦形式の場合、元号、年、月、日を抽出し、西暦に変換してからdatetimeオブジェクトを生成
        4. 不明な形式の場合、エラーを発生

    Exception:
        DateParseError: 無効な日付形式や存在しない日付の場合

    Notes:
        - 和暦形式の場合、元号コードは1桁、年は2桁、月と日はそれぞれ2桁である必要があります。

    ResourceLocation:
        - [本体]
            - src/lib/converter/ibr_convert_western_cal_japanese_cal_to_datetime.py
        - [テストコード]
            - tests/lib/converter/test_ibr_convert_western_cal_japanese_cal_to_datetime.py

    Chage History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当            |
    |------|--------------|----------|------------|-----------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/08/11 |                 |

    """
    date_string = str(date_string)
    date_format = determine_date_format(date_string)

    # Tokyo/Azia timezone
    jst = pytz.timezone('Asia/Tokyo')

    if date_format == DateFormat.WESTERN:
        try:
            return jst.localize(datetime.strptime(date_string, '%Y/%m/%d'))  # noqa: DTZ007
        except ValueError as e:
            err_msg = f"無効な西暦日付: {e}"
            raise DateParseError(err_msg) from None

    if date_format == DateFormat.JAPANESE:
        try:
            era_code = int(date_string[DateConstants.ERA_INDEX])
            year = int(date_string[DateConstants.YEAR_START_INDEX:DateConstants.YEAR_END_INDEX])
            month = int(date_string[DateConstants.MONTH_START_INDEX:DateConstants.MONTH_END_INDEX])
            day = int(date_string[DateConstants.DAY_START_INDEX:DateConstants.DAY_END_INDEX])

            # 年が00の場合(正しくないが元年を00と認識されるケース)は1年として扱う
            year = max(year, 1)

        except ValueError as e:
            err_msg = f"和暦日付の解析エラー: {e}"
            raise DateParseError(err_msg) from None

        try:
            western_year = Era.convert_japanese_year_to_western(era_code, year)
        except ValueError as e:
            err_msg = f"無効な和暦年: {str(e)}"
            raise DateParseError(err_msg) from None

        try:
            return jst.localize(datetime(western_year, month, day))  # noqa: DTZ001
        except ValueError as e:
            err_msg = f"無効な和暦日付: {e}"
            raise DateParseError(err_msg) from None

    err_msg = "無効な日付形式です"
    raise DateParseError(err_msg) from None
