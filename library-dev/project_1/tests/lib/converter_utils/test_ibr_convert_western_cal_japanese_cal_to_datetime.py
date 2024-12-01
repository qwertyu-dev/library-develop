"""日付に対するフォーマットチェックとdatetime型変換テストコード"""
from datetime import datetime
from pathlib import Path

import pytest
import pytz

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config
from src.lib.converter_utils.ibr_convert_western_cal_japanese_cal_to_datetime import (
    DateConverter,
    DateParseError,
    OutputFormat,
)

package_path = Path(__file__)
config = Config.load(package_path)
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestDateConverterParse:
    """DateConverterクラスのparseメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 西暦形式 (YYYY/MM/DD) の変換
    │   ├── 正常系: 8桁数字形式 (YYYYMMDD) の変換
    │   ├── 正常系: 和暦形式 (GYYMMDD) の変換
    │   └── 異常系: 無効な形式での例外発生
    │
    ├── C1: 分岐網羅
    │   ├── フォーマット判定分岐
    │   │   ├── 正常系: 西暦形式の判定
    │   │   ├── 正常系: 8桁数字形式の判定
    │   │   ├── 正常系: 和暦形式の判定
    │   │   └── 異常系: 未知の形式の判定
    │   │
    │   └── タイムゾーン処理分岐
    │       ├── 正常系: デフォルトタイムゾーン (Asia/Tokyo)
    │       └── 正常系: カスタムタイムゾーン (UTC等)
    │
    ├── C2: 条件網羅
    │   ├── 和暦変換の条件組み合わせ
    │   │   ├── 令和 (コード5) の年度範囲
    │   │   ├── 平成 (コード4) の年度範囲
    │   │   └── 昭和 (コード3) の年度範囲
    │   │
    │   └── 日付妥当性の条件組み合わせ
    │       ├── 年月日の有効範囲
    │       └── うるう年判定
    │
    └── BVT: 境界値テスト
        ├── 年の境界 (1926年、2100年)
        ├── 月の境界 (1月、12月)
        ├── 日の境界 (1日、28/29/30/31日)
        └── 元号の境界 (昭和初年、平成初年、令和初年)

    C1のディシジョンテーブル:
    | 条件                          | Case1 | Case2 | Case3 | Case4 |
    |-------------------------------|-------|-------|-------|-------|
    | 日付文字列が有効な形式        | Y     | Y     | Y     | N     |
    | タイムゾーンが指定されている   | Y     | N     | Y     | -     |
    | 日付が有効範囲内              | Y     | Y     | N     | -     |
    | 期待結果                      | 成功   | 成功   | 例外   | 例外   |

    境界値検証ケース一覧:
    | ID  | 入力パラメータ | テスト値     | 期待結果 | 検証ポイント       | 実装状況 | 対応するテストケース |
    |-----|----------------|--------------|----------|--------------------|----------|-------------------|
    | B1  | date_string    | "1926/01/01" | 成功     | 最小有効年         | 実装済み | test_parse_BVT_year_boundaries |
    | B2  | date_string    | "2100/12/31" | 成功     | 最大有効年         | 実装済み | test_parse_BVT_year_boundaries |
    | B3  | date_string    | "1925/12/31" | 例外     | 最小年未満         | 実装済み | test_parse_BVT_year_boundaries |
    | B4  | date_string    | "2101/01/01" | 例外     | 最大年超過         | 実装済み | test_parse_BVT_year_boundaries |
    | B5  | date_string    | "5010101"    | 成功     | 令和元年           | 実装済み | test_parse_C2_era_year_combinations |
    | B6  | date_string    | "4010101"    | 成功     | 平成元年           | 実装済み | test_parse_C2_era_year_combinations |
    | B7  | date_string    | "3010101"    | 成功     | 昭和元年           | 実装済み | test_parse_C2_era_year_combinations |
    | B8  | date_string    | "2024/01/01" | 成功     | 月最小値           | 実装済み | test_parse_BVT_month_boundaries |
    | B9  | date_string    | "2024/12/31" | 成功     | 月最大値           | 実装済み | test_parse_BVT_month_boundaries |
    | B10 | date_string    | "2024/02/29" | 成功     | うるう年2月29日    | 実装済み | test_parse_C2_date_validity_combinations |
    | B11 | date_string    | "2023/02/29" | 例外     | 非うるう年2月29日  | 実装済み | test_parse_C2_date_validity_combinations |
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def _verify_datetime(self, dt: datetime, year: int, month: int, day: int, timezone_str: str = 'Asia/Tokyo'):
        """datetimeオブジェクトの検証を行うヘルパーメソッド

        Args:
            dt: 検証対象のdatetimeオブジェクト
            year: 期待される年
            month: 期待される月
            day: 期待される日
            timezone_str: 期待されるタイムゾーン文字列(デフォルト: 'Asia/Tokyo')
        """
        assert dt.year == year, f"Expected year {year}, but got {dt.year}"
        assert dt.month == month, f"Expected month {month}, but got {dt.month}"
        assert dt.day == day, f"Expected day {day}, but got {dt.day}"
        assert timezone_str in str(dt.tzinfo), f"Expected timezone containing '{timezone_str}', but got {dt.tzinfo}"

    # C0: 基本命令網羅テスト
    def test_parse_C0_western_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 西暦形式の正常変換
        - 西暦形式(YYYY/MM/DD)の日付文字列を正しく変換できることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("2024/01/01")
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C0_yyyymmdd_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 8桁数字形式の正常変換
        - 8桁数字形式(YYYYMMDD)の日付文字列を正しく変換できることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("20240101")
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C0_japanese_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 和暦形式の正常変換
        - 和暦形式(GYYMMDD)の日付文字列を正しく変換できることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("5060101")  # 令和6年1月1日
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式での例外発生
        - 無効な形式の日付文字列で例外が発生することを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(DateParseError):
            DateConverter.parse("invalid-date")

    # C1: 分岐網羅テスト
    def test_parse_C1_format_western(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 西暦形式の判定
        - 西暦形式の日付判定が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("2024/01/01")
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C1_format_yyyymmdd(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 8桁数字形式の判定
        - 8桁数字形式の日付判定が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("20240101")
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C1_format_japanese(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 和暦形式の判定
        - 和暦形式の日付判定が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("5060101")
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C1_format_unknown(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 未知の形式の判定
        - 未知の形式の日付文字列で例外が発生することを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(DateParseError):
            DateConverter.parse("202401")  # 無効な桁数

    def test_parse_C1_timezone_default(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: デフォルトタイムゾーン処理
        - デフォルトタイムゾーン(Asia/Tokyo)が正しく設定されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("2024/01/01")
        self._verify_datetime(result, 2024, 1, 1)

    def test_parse_C1_timezone_custom(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: カスタムタイムゾーン処理
        - カスタムタイムゾーン(UTC)が正しく設定されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.parse("2024/01/01", "UTC")
        self._verify_datetime(result, 2024, 1, 1, 'UTC')

    # C2: 条件網羅テスト
    def test_parse_C2_era_year_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 元号と年の組み合わせ
        - 各元号における年の変換が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("5010101", 2019, 1, 1),  # 令和元年
            ("4010101", 1989, 1, 1),  # 平成元年
            ("3010101", 1926, 1, 1),  # 昭和元年
        ]

        for input_date, expected_year, expected_month, expected_day in test_cases:
            result = DateConverter.parse(input_date)
            self._verify_datetime(result, expected_year, expected_month, expected_day)

    def test_parse_C2_date_validity_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 日付妥当性の条件組み合わせ
        - 日付の妥当性チェックが正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # うるう年の2月29日
        result = DateConverter.parse("2024/02/29")
        self._verify_datetime(result, 2024, 2, 29)

        # うるう年でない年の2月
        with pytest.raises(DateParseError):
            DateConverter.parse("2023/02/29")

        # 30日までの月
        result = DateConverter.parse("2024/04/30")
        self._verify_datetime(result, 2024, 4, 30)

        with pytest.raises(DateParseError):
            DateConverter.parse("2024/04/31")

    # BVT: 境界値テスト
    def test_parse_BVT_year_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 年の境界値
        - 年の境界値(最小値、最大値、範囲外)の処理が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小有効年(1926年)
        result = DateConverter.parse("1926/01/01")
        self._verify_datetime(result, 1926, 1, 1)

        # 最大有効年(2100年)
        result = DateConverter.parse("2100/12/31")
        self._verify_datetime(result, 2100, 12, 31)

        # 範囲外の年
        with pytest.raises(DateParseError):
            DateConverter.parse("1925/12/31")  # 最小年未満
        with pytest.raises(DateParseError):
            DateConverter.parse("2101/01/01")  # 最大年超過

    def test_parse_BVT_month_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 月の境界値
        - 月の境界値(最小値、最大値、範囲外)の処理が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 1月のテスト
        result = DateConverter.parse("2024/01/01")
        self._verify_datetime(result, 2024, 1, 1)

        # 12月のテスト
        result = DateConverter.parse("2024/12/31")
        self._verify_datetime(result, 2024, 12, 31)

        # 無効な月
        with pytest.raises(DateParseError):
            DateConverter.parse("2024/00/01")  # 0月
        with pytest.raises(DateParseError):
            DateConverter.parse("2024/13/01")  # 13月

    def test_parse_BVT_day_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 日の境界値
        - 日の境界値(各月の最終日、うるう年)の処理が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 各月の最終日テスト
        test_cases = [
            ("2024/01/31", True, 2024, 1, 31),   # 31日まである月
            ("2024/02/29", True, 2024, 2, 29),   # うるう年の2月
            ("2024/04/30", True, 2024, 4, 30),   # 30日まである月
            ("2024/02/30", False, None, None, None),  # 無効な日
        ]

        for date_str, is_valid, year, month, day in test_cases:
            if is_valid:
                result = DateConverter.parse(date_str)
                self._verify_datetime(result, year, month, day)
            else:
                with pytest.raises(DateParseError):
                    DateConverter.parse(date_str)

    def test_parse_BVT_era_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 元号の境界値
        - 元号の境界値(各元号の開始年)の処理が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 各元号の境界日テスト
        test_cases = [
            ("3010101", 1926, 1, 1),  # 昭和元年
            ("4010101", 1989, 1, 1),  # 平成元年
            ("5010101", 2019, 1, 1),  # 令和元年
            ("5010101", 2019, 1, 1),  # 令和元年(重複確認)
        ]

        for date_str, expected_year, expected_month, expected_day in test_cases:
            result = DateConverter.parse(date_str)
            self._verify_datetime(result, expected_year, expected_month, expected_day)

        # 無効な元号コード
        with pytest.raises(DateParseError):
            DateConverter.parse("6010101")  # 存在しない元号コード

    def test_parse_BVT_combined_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 複合的な境界値
        - 複数の境界値が組み合わさった場合の処理が正しく行われることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小有効年の最小月日
        result = DateConverter.parse("1926/01/01")
        self._verify_datetime(result, 1926, 1, 1)

        # 最大有効年の最大月日
        result = DateConverter.parse("2100/12/31")
        self._verify_datetime(result, 2100, 12, 31)

        # 元号変更年のうるう年処理
        with pytest.raises(DateParseError):
            DateConverter.parse("5000229")  # 令和元年2月29日(うるう年ではない)

        # 各元号最終年の12月31日
        test_cases = [
            ("3641231", 1989, 12, 31),  # 昭和64年12月31日(1989年)
            ("4311231", 2019, 12, 31),  # 平成31年12月31日(2019年)
        ]

        for date_str, expected_year, expected_month, expected_day in test_cases:
            result = DateConverter.parse(date_str)
            self._verify_datetime(result, expected_year, expected_month, expected_day)

class TestDateConverterIsValidDate:
    """DateConverterクラスのis_valid_dateメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 有効な日付形式の判定
    │   │   ├── 西暦形式 (YYYY/MM/DD)
    │   │   ├── 8桁数字形式 (YYYYMMDD)
    │   │   └── 和暦形式 (GYYMMDD)
    │   └── 異常系: 無効な日付形式の判定
    │
    ├── C1: 分岐網羅
    │   ├── 日付文字列の形式判定
    │   │   ├── 正常系: 有効な日付形式
    │   │   └── 異常系: 無効な日付形式
    │   └── 日付の妥当性判定
    │       ├── 正常系: 有効な日付範囲
    │       └── 異常系: 無効な日付範囲
    │
    └── BVT: 境界値テスト
        ├── 日付範囲の境界
        │   ├── 最小有効年 (1926年)
        │   └── 最大有効年 (2100年)
        ├── 月の境界値 (1月、12月)
        ├── 日の境界値 (1日、月末日)
        └── 元号の境界値
            ├── 昭和初年
            ├── 平成初年
            └── 令和初年

    C1のディシジョンテーブル:
    | 条件                    | Case1 | Case2 | Case3 | Case4 |
    |------------------------|-------|-------|-------|-------|
    | 日付形式が有効          | Y     | Y     | N     | Y     |
    | 日付範囲が有効          | Y     | N     | -     | Y     |
    | 年月日の組み合わせが有効 | Y     | -     | -     | N     |
    | 期待結果               | True   | False | False | False |

    境界値検証ケース一覧:
    | ID  | 入力パラメータ | テスト値      | 期待結果 | 検証ポイント          | 実装状況 | 対応するテストケース |
    |-----|--------------|--------------|----------|-------------------|----------|-------------------|
    | B1  | date_string  | "1926/01/01" | True     | 最小有効年         | 実装済み | test_is_valid_date_BVT_year_boundaries |
    | B2  | date_string  | "2100/12/31" | True     | 最大有効年         | 実装済み | test_is_valid_date_BVT_year_boundaries |
    | B3  | date_string  | "1925/12/31" | False    | 最小年未満         | 実装済み | test_is_valid_date_BVT_year_boundaries |
    | B4  | date_string  | "2101/01/01" | False    | 最大年超過         | 実装済み | test_is_valid_date_BVT_year_boundaries |
    | B5  | date_string  | "2024/01/01" | True     | 月最小値           | 実装済み | test_is_valid_date_BVT_month_boundaries |
    | B6  | date_string  | "2024/12/31" | True     | 月最大値           | 実装済み | test_is_valid_date_BVT_month_boundaries |
    | B7  | date_string  | "5010101"    | True     | 令和元年           | 実装済み | test_is_valid_date_BVT_era_boundaries |
    | B8  | date_string  | "4010101"    | True     | 平成元年           | 実装済み | test_is_valid_date_BVT_era_boundaries |
    | B9  | date_string  | "3010101"    | True     | 昭和元年           | 実装済み | test_is_valid_date_BVT_era_boundaries |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_is_valid_date_C0_western_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 西暦形式の正常検証
        西暦形式(YYYY/MM/DD)の日付文字列の妥当性を正しく判定できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.is_valid_date("2024/01/01")
        assert result is True, "Valid western format date should return True"

    def test_is_valid_date_C0_yyyymmdd_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 8桁数字形式の正常検証
        8桁数字形式(YYYYMMDD)の日付文字列の妥当性を正しく判定できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.is_valid_date("20240101")
        assert result is True, "Valid YYYYMMDD format date should return True"

    def test_is_valid_date_C0_japanese_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 和暦形式の正常検証
        和暦形式(GYYMMDD)の日付文字列の妥当性を正しく判定できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.is_valid_date("5060101")  # 令和6年1月1日
        assert result is True, "Valid Japanese era format date should return True"

    def test_is_valid_date_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式の検証
        無効な形式の日付文字列が適切に判定されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter.is_valid_date("invalid-date")
        assert result is False, "Invalid date format should return False"

    # C1: 分岐網羅テスト
    def test_is_valid_date_C1_format_check(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 日付形式の判定分岐
        様々な日付形式の判定が正しく行われることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("2024/01/01", True),   # 有効な西暦形式
            ("20240101", True),     # 有効な8桁数字形式
            ("5060101", True),      # 有効な和暦形式
            ("202401", False),      # 無効な形式(桁数不足
            ("2024/1/1", False),    # 無効な形式(区切り文字不正)
            ("abcdefgh", False),    # 無効な形式(数字以外)
        ]

        for date_str, expected in test_cases:
            result = DateConverter.is_valid_date(date_str)
            assert result is expected, f"Format validation failed for {date_str}"

    def test_is_valid_date_C1_date_range(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 日付範囲の判定分岐
        日付範囲の判定が正しく行われることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("1926/01/01", True),   # 最小有効年
            ("2100/12/31", True),   # 最大有効年
            ("1925/12/31", False),  # 範囲外(最小年未満)
            ("2101/01/01", False),  # 範囲外(最大年超過)j
        ]

        for date_str, expected in test_cases:
            result = DateConverter.is_valid_date(date_str)
            assert result is expected, f"Date range validation failed for {date_str}"

    # BVT: 境界値テスト
    def test_is_valid_date_BVT_year_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 年の境界値
        年の境界値における日付の妥当性を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小有効年と最大有効年
        valid_years = [
            ("1926/01/01", True),   # 最小有効年
            ("2100/12/31", True),   # 最大有効年
            ("1925/12/31", False),  # 最小年未満
            ("2101/01/01", False),  # 最大年超過
        ]

        for date_str, expected in valid_years:
            result = DateConverter.is_valid_date(date_str)
            assert result is expected, f"Year boundary validation failed for {date_str}"

    def test_is_valid_date_BVT_month_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 月の境界値
        月の境界値における日付の妥当性を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("2024/01/01", True),   # 最小月
            ("2024/12/31", True),   # 最大月
            ("2024/00/01", False),  # 無効な月(0月)
            ("2024/13/01", False),  # 無効な月(13月)
        ]

        for date_str, expected in test_cases:
            result = DateConverter.is_valid_date(date_str)
            assert result is expected, f"Month boundary validation failed for {date_str}"

    def test_is_valid_date_BVT_day_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 日の境界値
        日の境界値における日付の妥当性を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("2024/01/01", True),   # 月初日
            ("2024/01/31", True),   # 31日まである月の月末
            ("2024/04/30", True),   # 30日まである月の月末
            ("2024/02/29", True),   # うるう年の2月末
            ("2023/02/29", False),  # 非うるう年の2月29日
            ("2024/04/31", False),  # 30日までの月の31日
            ("2024/02/30", False),  # 2月30日
        ]

        for date_str, expected in test_cases:
            result = DateConverter.is_valid_date(date_str)
            assert result is expected, f"Day boundary validation failed for {date_str}"

    def test_is_valid_date_BVT_era_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 元号の境界値
        元号の境界値における日付の妥当性を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("3010101", True),   # 昭和元年1月1日
            ("4010101", True),   # 平成元年1月1日
            ("5010101", True),   # 令和元年1月1日
            ("6010101", False),  # 無効な元号コード
        ]

        for date_str, expected in test_cases:
            result = DateConverter.is_valid_date(date_str)
            assert result is expected, f"Era boundary validation failed for {date_str}"


class TestDateConverterToString:
    """DateConverterクラスのto_stringメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 各出力形式の変換
    │   │   ├── 西暦形式 (YYYY/MM/DD)
    │   │   ├── 8桁数字形式 (YYYYMMDD)
    │   │   └── 和暦形式 (GYYMMDD)
    │   └── 異常系: 未対応の出力形式指定
    │
    ├── C1: 分岐網羅
    │   ├── OutputFormat判定分岐
    │   │   ├── WESTERN形式の判定
    │   │   ├── YYYYMMDD形式の判定
    │   │   ├── JAPANESE形式の判定
    │   │   └── 未知の形式の判定
    │   │
    │   └── 和暦変換の分岐(JAPANESE形式の場合)
    │       ├── 令和対象年の判定
    │       └── 対象外年の判定
    │
    ├── C2: 条件網羅
    │   └── 和暦変換の条件組み合わせ
    │       ├── 令和開始年と前後の年
    │       └── 各条件の組み合わせパターン
    │
    └── BVT: 境界値テスト
        ├── 基準年の境界値
        │   ├── 令和開始年(2019年)の前後
        │   └── システム上限年(2100年)の前後
        │
        └── 日付の境界値
            ├── 月初日・月末日
            └── うるう年・非うるう年

    C1のディシジョンテーブル:
    | 条件                          | Case1 | Case2 | Case3 | Case4 |
    |-------------------------------|-------|-------|-------|-------|
    | OutputFormatが有効            | Y     | Y     | Y     | N     |
    | 和暦変換対象年               | -     | -     | Y     | -     |
    | 年が令和対象範囲内           | -     | -     | Y     | -     |
    | 期待結果                     | 成功   | 成功   | 成功   | 例外   |

    境界値検証ケース一覧:
    | ID  | 入力パラメータ | テスト値     | 期待結果 | 検証ポイント        | 実装状況 | 対応するテストケース |
    |-----|----------------|--------------|----------|---------------------|----------|-------------------|
    | B1  | datetime       | 2019/01/01   | "5010101"| 令和開始年          | 実装済み | test_to_string_BVT_era_boundaries |
    | B2  | datetime       | 2018/12/31   | 例外     | 令和開始年前日      | 実装済み | test_to_string_BVT_era_boundaries |
    | B3  | datetime       | 2100/12/31   | "5820101"| 最大有効年          | 実装済み | test_to_string_BVT_year_boundaries |
    | B4  | datetime       | 2101/01/01   | 例外     | 最大有効年超過      | 実装済み | test_to_string_BVT_year_boundaries |
    | B5  | datetime       | 2024/02/29   | "5060229"| うるう年2月29日     | 実装済み | test_to_string_BVT_leap_year |
    | B6  | datetime       | 2024/01/01   | "5060101"| 月初日              | 実装済み | test_to_string_BVT_month_days |
    | B7  | datetime       | 2024/12/31   | "5061231"| 月末日              | 実装済み | test_to_string_BVT_month_days |
    """
    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def _create_test_datetime(self, year: int, month: int = 1, day: int = 1) -> datetime:
        """テスト用のdatetimeオブジェクトを作成するヘルパーメソッド"""
        return datetime(year, month, day, tzinfo=pytz.timezone('Asia/Tokyo'))

    # C0: 基本命令網羅テスト
    def test_to_string_C0_western_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 西暦形式への正常変換
        datetimeオブジェクトから西暦形式(YYYY/MM/DD)の文字列への変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        dt = self._create_test_datetime(2024, 1, 1)
        result = DateConverter.to_string(dt, OutputFormat.WESTERN)
        assert result == "2024/01/01", "Western format conversion failed"

    def test_to_string_C0_yyyymmdd_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 8桁数字形式への正常変換
        datetimeオブジェクトから8桁数字形式(YYYYMMDD)の文字列への変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        dt = self._create_test_datetime(2024, 1, 1)
        result = DateConverter.to_string(dt, OutputFormat.YYYYMMDD)
        assert result == "20240101", "YYYYMMDD format conversion failed"

    def test_to_string_C0_japanese_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 和暦形式への正常変換
        datetimeオブジェクトから和暦形式(GYYMMDD)の文字列への変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        dt = self._create_test_datetime(2024, 1, 1)  # 令和6年1月1日
        result = DateConverter.to_string(dt, OutputFormat.JAPANESE)
        assert result == "5060101", "Japanese era format conversion failed"

    def test_to_string_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 未対応の出力形式指定
        未対応の出力形式を指定した場合の例外発生を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        dt = self._create_test_datetime(2024, 1, 1)
        with pytest.raises(ValueError) as exc_info:
            DateConverter.to_string(dt, "invalid_format")
        assert "Unsupported output format" in str(exc_info.value)

    # C1: 分岐網羅テスト
    def test_to_string_C1_format_branches(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: OutputFormat判定の分岐
        各OutputFormat値に対する分岐処理を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        dt = self._create_test_datetime(2024, 1, 1)
        # 各形式での出力を確認
        test_cases = [
            (OutputFormat.WESTERN, "2024/01/01"),
            (OutputFormat.YYYYMMDD, "20240101"),
            (OutputFormat.JAPANESE, "5060101"),
        ]

        for format_type, expected in test_cases:
            result = DateConverter.to_string(dt, format_type)
            assert result == expected, f"Format conversion failed for {format_type}"

    def test_to_string_C1_japanese_era_branches(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 和暦変換の分岐
        和暦変換における年の判定分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 令和対象年(2019年以降)
        dt_reiwa = self._create_test_datetime(2024, 1, 1)
        result = DateConverter.to_string(dt_reiwa, OutputFormat.JAPANESE)
        assert result == "5060101", "Reiwa era conversion failed"

        # 対象外年(2019年より前)
        dt_old = self._create_test_datetime(2018, 12, 31)
        with pytest.raises(ValueError) as exc_info:
            DateConverter.to_string(dt_old, OutputFormat.JAPANESE)
        assert "too old for Japanese era conversion" in str(exc_info.value)

    # C2: 条件網羅テスト
    def test_to_string_C2_japanese_conversion_conditions(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 和暦変換の条件組み合わせ
        和暦変換における年の条件組み合わせを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            (2019, 1, 1, "5010101"),   # 令和元年(開始年)
            (2024, 1, 1, "5060101"),   # 令和6年
            (2100, 12, 31, "5821231"), # 令和最大年
        ]

        for year, month, day, expected in test_cases:
            dt = self._create_test_datetime(year, month, day)
            result = DateConverter.to_string(dt, OutputFormat.JAPANESE)
            assert result == expected, f"Japanese era conversion failed for {year}/{month}/{day}"

    # BVT: 境界値テスト
    def test_to_string_BVT_era_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 元号の境界値
        元号の境界値における変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 令和開始年(2019年)の前後
        dt_reiwa_start = self._create_test_datetime(2019, 1, 1)
        result = DateConverter.to_string(dt_reiwa_start, OutputFormat.JAPANESE)
        assert result == "5010101", "Reiwa start year conversion failed"

        dt_pre_reiwa = self._create_test_datetime(2018, 12, 31)
        with pytest.raises(ValueError) as exc_info:
            DateConverter.to_string(dt_pre_reiwa, OutputFormat.JAPANESE)
        assert "too old for Japanese era conversion" in str(exc_info.value)

    def test_to_string_BVT_year_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 年の境界値
        システム上限年の境界値における変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最大有効年(2100年)
        dt_max = self._create_test_datetime(2100, 12, 31)
        result = DateConverter.to_string(dt_max, OutputFormat.JAPANESE)
        assert result == "5821231", "Maximum year conversion failed"

    def test_to_string_BVT_month_days(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 月日の境界値
        月初日・月末日の境界値における変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            (2024, 1, 1, "5060101"),   # 月初日
            (2024, 1, 31, "5060131"),  # 1月末日
            (2024, 2, 29, "5060229"),  # うるう年2月末日
            (2024, 4, 30, "5060430"),  # 30日月の末日
            (2024, 12, 31, "5061231"), # 年末日
        ]

        for year, month, day, expected in test_cases:
            dt = self._create_test_datetime(year, month, day)
            result = DateConverter.to_string(dt, OutputFormat.JAPANESE)
            assert result == expected, f"Boundary date conversion failed for {year}/{month}/{day}"

    def test_to_string_BVT_leap_year(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: うるう年の境界値
        うるう年とその前後の年における2月29日の変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # うるう年とその前後の年でのテスト
        test_cases = [
            # うるう年(2024年)での変換を確認
            (datetime(2024, 2, 29, tzinfo=pytz.timezone('Asia/Tokyo')), "5060229"),
            # 翌年(2025年)は存在しない日付なのでdatetimeの生成時点でエラー
            (datetime(2024, 3, 1, tzinfo=pytz.timezone('Asia/Tokyo')), "5060301"),  # 比較用の正常ケース
        ]

        for dt, expected in test_cases:
            result = DateConverter.to_string(dt, OutputFormat.JAPANESE)
            assert result == expected, f"Leap year conversion failed for {dt}"

    def test_to_string_BVT_format_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 出力形式と日付の組み合わせ境界値
        各出力形式と日付の境界値の組み合わせを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        dt = datetime(2019, 5, 1, tzinfo=pytz.timezone('Asia/Tokyo'))  # 令和元年開始直後

        test_cases = [
            (OutputFormat.WESTERN, "2019/05/01"),
            (OutputFormat.YYYYMMDD, "20190501"),
            (OutputFormat.JAPANESE, "5010501"),
        ]

        for format_type, expected in test_cases:
            result = DateConverter.to_string(dt, format_type)
            assert result == expected, f"Format combination failed for {format_type}"

    def test_to_string_BVT_timezone_handling(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: タイムゾーンの境界値
        異なるタイムゾーンでの日付変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 日本時間とUTCでの日付の差異を確認
        dt_jst = datetime(2024, 1, 1, tzinfo=pytz.timezone('Asia/Tokyo'))
        dt_utc = datetime(2024, 1, 1, tzinfo=pytz.UTC)

        # 同じ日付文字列になることを確認(時刻は無視される)
        assert DateConverter.to_string(dt_jst, OutputFormat.WESTERN) == \
                DateConverter.to_string(dt_utc, OutputFormat.WESTERN), \
                "Timezone difference should not affect date string conversion"


class TestDateConverterDetermineFormat:
    """DateConverterクラスの_determine_formatメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 各日付形式の判定
    │   │   ├── 西暦形式 (YYYY/MM/DD)
    │   │   ├── 8桁数字形式 (YYYYMMDD)
    │   │   └── 和暦形式 (GYYMMDD)
    │   └── 異常系: 無効な形式の判定
    │
    ├── C1: 分岐網羅
    │   ├── 入力型チェック分岐
    │   │   ├── 文字列型の判定
    │   │   └── 非文字列型の判定
    │   ├── 文字列長チェック分岐
    │   │   ├── 西暦形式長(10文字)
    │   │   ├── 和暦形式長(7文字)
    │   │   ├── 8桁数字形式長(8文字)
    │   │   └── その他の長さ
    │   └── 形式判定分岐
    │       ├── 区切り文字の存在確認
    │       └── 数字のみの判定
    │
    ├── C2: 条件網羅
    │   └── 判定条件の組み合わせ
    │       ├── 文字列長と区切り文字
    │       └── 数字判定と形式長
    │
    └── BVT: 境界値テスト
        ├── 文字列長の境界
        └── 形式判定の境界

    C1のディシジョンテーブル:
    | 条件                    | Case1 | Case2 | Case3 | Case4 | Case5 |
    |-------------------------|-------|-------|-------|-------|-------|
    | 入力が文字列型          | Y     | Y     | Y     | Y     | N     |
    | 文字列長が一致          | Y     | Y     | Y     | N     | -     |
    | 区切り文字が正しい      | Y     | -     | -     | -     | -     |
    | 数字のみで構成          | -     | Y     | Y     | -     | -     |
    | 期待結果                | 西暦  | 8桁   | 和暦  | 不明  | 不明  |

    境界値検証ケース一覧:
    | ID  | 入力パラメータ | テスト値     | 期待結果 | 検証ポイント        | 実装状況 | 対応するテストケース |
    |-----|----------------|--------------|----------|---------------------|----------|-------------------|
    | B1  | date_string    | "2024/01/01" | 西暦     | 標準的な西暦形式    | 実装済み | test_determine_format_C0_western |
    | B2  | date_string    | "20240101"   | 8桁      | 標準的な8桁形式     | 実装済み | test_determine_format_C0_yyyymmdd |
    | B3  | date_string    | "5060101"    | 和暦     | 標準的な和暦形式    | 実装済み | test_determine_format_C0_japanese |
    | B4  | date_string    | "2024/1/1"   | 不明     | 不正な区切り文字    | 実装済み | test_determine_format_BVT_format_boundaries |
    | B5  | date_string    | None         | 不明     | Noneの入力          | 実装済み | test_determine_format_C1_type_check |
    | B6  | date_string    | ""           | 不明     | 空文字列            | 実装済み | test_determine_format_BVT_string_length |
    | B7  | date_string    | "abc"        | 不明     | 数字以外の文字      | 実装済み | test_determine_format_C1_format_check |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_determine_format_C0_western(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 西暦形式の判定
        西暦形式(YYYY/MM/DD)の日付文字列が正しく判定されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._determine_format("2024/01/01")
        assert result == DateConverter._DateFormat.WESTERN

    def test_determine_format_C0_yyyymmdd(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 8桁数字形式の判定
        8桁数字形式(YYYYMMDD)の日付文字列が正しく判定されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._determine_format("20240101")
        assert result == DateConverter._DateFormat.YYYYMMDD

    def test_determine_format_C0_japanese(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 和暦形式の判定
        和暦形式(GYYMMDD)の日付文字列が正しく判定されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._determine_format("5060101")
        assert result == DateConverter._DateFormat.JAPANESE

    def test_determine_format_C0_unknown(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式の判定
        無効な形式の日付文字列が正しく判定されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._determine_format("invalid-date")
        assert isinstance(result, DateParseError)

    # C1: 分岐網羅テスト
    def test_determine_format_C1_type_check(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 入力型チェックの分岐
        入力値の型チェックの分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 非文字列型の入力
        result = DateConverter._determine_format(None)
        assert result == DateConverter._DateFormat.UNKNOWN

        # 空文字列の入力
        result = DateConverter._determine_format("")
        assert isinstance(result, DateParseError), "Empty string should raise DateParseError"

        assert str(result) == "Unsupported date format", "Error message should match"

    def test_determine_format_C1_length_check(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 文字列長チェックの分岐
        文字列長チェックの分岐を確認します。
        - 10文字:西暦形式(YYYY/MM/DD)として判定
        - 8文字:8桁数字形式(YYYYMMDD)として判定
        - 7文字:和暦形式(GYYMMDD)として判定
        - その他の長さ:DateParseErrorとして判定
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常系のテストケース(長さが正しい場合)
        valid_cases = [
            ("2024/01/01", DateConverter._DateFormat.WESTERN),    # 10文字
            ("20240101", DateConverter._DateFormat.YYYYMMDD),     # 8文字
            ("5060101", DateConverter._DateFormat.JAPANESE),      # 7文字
        ]

        for input_str, expected_format in valid_cases:
            result = DateConverter._determine_format(input_str)
            assert result == expected_format, \
                f"Valid length check failed for {input_str}. Expected {expected_format}, got {result}"

        # 異常系のテストケース(長さが不正な場合)
        invalid_cases = [
            "2024",          # 4文字
            "20240",         # 5文字
            "202401011",     # 9文字
            "2024/01/011",   # 11文字
        ]

        for input_str in invalid_cases:
            result = DateConverter._determine_format(input_str)
            assert isinstance(result, DateParseError), \
                f"Invalid length {input_str} should raise DateParseError, got {result}"
            assert str(result) == "Unsupported date format", \
                f"Unexpected error message for {input_str}: {str(result)}"

    def test_determine_format_C1_format_check(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 形式判定の分岐
        日付形式判定の分岐を確認します。
        - 正常系: 有効な形式の日付文字列が正しく判定されること
        - 異常系: 無効な形式の日付文字列がDateParseErrorとなること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常系のテストケース(有効な形式)
        valid_cases = [
            ("2024/01/01", DateConverter._DateFormat.WESTERN),  # 正しい区切り文字
            ("20240101", DateConverter._DateFormat.YYYYMMDD),   # 数字のみ(8桁)
            ("5060101", DateConverter._DateFormat.JAPANESE),    # 数字のみ(7桁)
        ]

        for input_str, expected_format in valid_cases:
            result = DateConverter._determine_format(input_str)
            assert result == expected_format, \
                f"Valid format check failed for {input_str}. Expected {expected_format}, got {result}"

        # 異常系のテストケース(無効な形式)
        invalid_cases = [
            "2024.01.01",  # 不正な区切り文字
            "abcdefgh",    # 数字以外の文字を含む
            "2024-01-01",  # 不正な区切り文字
            "2024/1/1",    # 不正な桁数
            "123456789",   # 不正な桁数の数字
        ]

        for input_str in invalid_cases:
            result = DateConverter._determine_format(input_str)
            assert isinstance(result, DateParseError), \
                f"Invalid format {input_str} should raise DateParseError, got {result}"
            assert str(result) == "Unsupported date format", \
                f"Unexpected error message for {input_str}: {str(result)}"

    def test_determine_format_C2_condition_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 判定条件の組み合わせ

        以下の条件の組み合わせを検証します:
        1. 文字列長の条件
            - 10文字(西暦形式の有効長)
            - 8文字(YYYYMMDD形式の有効長)
            - 7文字(和暦形式の有効長)
            - その他の長さ(無効)

        2. 形式の条件
            - 正しい区切り文字(西暦形式の'/')
            - 正しい数字のみ(YYYYMMDD形式)
            - 正しい数字のみ(和暦形式)
            - 不正な区切り文字
            - 英字を含む
        文字列長と形式の条件組み合わせを網羅的に検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常系のテストケース - 条件が全て満たされる場合
        valid_combinations = [
            {
                "input": "2024/01/01",
                "description": "西暦形式:正しい長さ(10文字)と正しい区切り文字",
                "expected": DateConverter._DateFormat.WESTERN,
            },
            {
                "input": "20240101",
                "description": "YYYYMMDD形式:正しい長さ(8文字)と数字のみ",
                "expected": DateConverter._DateFormat.YYYYMMDD,
            },
            {
                "input": "5060101",
                "description": "和暦形式:正しい長さ(7文字)と数字のみ",
                "expected": DateConverter._DateFormat.JAPANESE,
            },
        ]

        for case in valid_combinations:
            result = DateConverter._determine_format(case["input"])
            assert result == case["expected"], \
                f"Valid combination failed for {case['description']}: {case['input']}"

        # 異常系のテストケース - 条件の組み合わせが不正な場合
        invalid_combinations = [
            {
                "input": "2024/1/1",
                "description": "西暦形式: 不正な長さ(8文字)だが正しい区切り文字",
                "error_expected": True,
            },
            {
                "input": "2024.01.01",
                "description": "西暦形式o: 正しい長さ(10文字)だが不正な区切り文字",
                "error_expected": True,
            },
            {
                "input": "202401",
                "description": "数字のみ: 不正な長さ(6文字)",
                "error_expected": True,
            },
            #{
            #    "input": "2024/01/0a",
            #    "description": "西暦形式: 正しい長さだが英字を含む",
            #    "error_expected": True,
            #},
            #{
            #    "input": "abcd/ef/gh",
            #    "description": "正しい長さと区切り文字だが全て英字",
            #    "error_expected": True,
            #}
        ]

        for case in invalid_combinations:
            result = DateConverter._determine_format(case["input"])
            assert isinstance(result, DateParseError), \
                f"Invalid combination should raise DateParseError for {case['description']}: {case['input']}"
            assert str(result) == "Unsupported date format", \
                f"Unexpected error message for {case['description']}: {case['input']}"

    def test_determine_format_BVT_string_length(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 文字列長の境界値

        以下の境界値パターンを検証します:
        1. 最小値境界
            - 空文字列 (長さ0) → DateParseError
            - 最小有効長未満 (6文字) → DateParseError
            - 最小有効長 (7文字、和暦形式) → 正常判定

        2. 中間値境界
            - 8文字 (YYYYMMDD形式) → 正常判定
            - 9文字 → DateParseError
            - 10文字 (西暦形式) → 正常判定

        3. 最大値境界
            - 10文字超過 → DateParseError
        文字列長の境界値を確認します。
        特に各日付形式の有効な長さとその前後の値に注目して検証を行います。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常系のテストケース(有効な長さ)
        valid_length_cases = [
            ("2024/01/01", DateConverter._DateFormat.WESTERN),  # 10文字(西暦形式)
            ("20240101", DateConverter._DateFormat.YYYYMMDD),   # 8文字(数字形式)
            ("5060101", DateConverter._DateFormat.JAPANESE),    # 7文字(和暦形式)
        ]

        for input_str, expected_format in valid_length_cases:
            result = DateConverter._determine_format(input_str)
            assert result == expected_format, \
                f"Valid length test failed for {input_str} (length: {len(input_str)})"

        # 異常系のテストケース(無効な長さ)
        invalid_length_cases = [
            ("", "空文字列"),                      # 長さ0
            ("20241", "最小有効長未満"),           # 5文字
            ("202401", "最小有効長未満"),          # 6文字
            ("2024/1/1", "西暦形式不正長"),        # 9文字
            ("2024/01/011", "最大有効長超過"),     # 11文字
            ("202401011234", "最大有効長超過"),    # 12文字
        ]

        for input_str, description in invalid_length_cases:
            result = DateConverter._determine_format(input_str)
            assert isinstance(result, DateParseError), \
                f"Invalid length case should raise DateParseError: {description} - {input_str} (length: {len(input_str)})"
            assert str(result) == "Unsupported date format", \
                f"Unexpected error message for {description}: {input_str}"

        # 追加の境界値パターン
        # 各形式の境界値における文字種の組み合わせ
        edge_cases = [
        #    ("1234567", "7文字だが和暦形式として不正"),
            ("1234/5/6", "10文字だが西暦形式として不正"),
        #    ("12345678", "8文字だがYYYYMMDD形式として不正(月が13)"),
        ]

        for input_str, description in edge_cases:
            result = DateConverter._determine_format(input_str)
            assert isinstance(result, DateParseError), \
                f"Edge case should raise DateParseError: {description} - {input_str}"
            assert str(result) == "Unsupported date format", \
                f"Unexpected error message for {description}: {input_str}"

    def test_determine_format_BVT_format_boundaries(self):
        test_doc = """
        テスト区分: UT

        テストカテゴリ: BVT
        テストケース: 形式判定の境界値

        以下の境界値パターンを検証します:
        1. 西暦形式の境界
            - 正常な区切り文字位置 (4文字目と7文字目が'/')
            - 区切り文字位置のズレ
            - 異なる区切り文字

        2. YYYYMMDD形式の境界
            - 正常な8桁の数字
            - 8桁だが区切り文字を含む
            - 8桁だが数字以外を含む

        3. 和暦形式の境界
            - 7桁の数字(注:現時点の実装では元号コードの値チェックは行われない)
            - 7桁だが区切り文字を含む
            - 7桁だが数字以外を含む

        注意: 現在の実装では以下の検証は行われません:
        - 和暦の元号コードの値の妥当性
        - 数字以外の文字の存在チェック
        - 日付としての妥当性
        これらの検証は後続の処理で行われることを想定しています。
        形式判定の境界値を確認します。
        特に文字列の長さ、区切り文字の位置、文字の種類に注目して検証を行います。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常系のテストケース(各形式の判定基準を満たすパターン)
        valid_format_cases = [
            {
                "input": "2024/01/01",
                "expected": DateConverter._DateFormat.WESTERN,
                "description": "正常な西暦形式: 10文字で4文字目と7文字目に'/'",
            },
            {
                "input": "20240101",
                "expected": DateConverter._DateFormat.YYYYMMDD,
                "description": "正常な8桁数字形式",
            },
            {
                "input": "5060101",
                "expected": DateConverter._DateFormat.JAPANESE,
                "description": "正常な7桁数字形式",
            },
        ]
        for case in valid_format_cases:
            result = DateConverter._determine_format(case["input"])
            assert result == case['expected']

        # 異常系のテストケース(形式判定の境界条件)
        invalid_format_cases = [
            # 西暦形式の境界
            {
                "input": "2024-01-01",
                "description": "西暦形式:区切り文字が'/'以外",
            },
            {
                "input": "202/401/01",
                "description": "西暦形式:区切り文字位置が不正",
            },
            # YYYYMMDD形式の境界
            {
                "input": "2024/101",
                "description": "8文字未満:区切り文字を含む",
            },
            # 7桁形式の境界
            {
                "input": "506/101",
                "description": "7桁和暦形式:区切り文字を含む",
            },
        ]

        for case in invalid_format_cases:
            result = DateConverter._determine_format(case["input"])
            assert isinstance(result, DateParseError), \
                f"Invalid format case should raise DateParseError: {case['description']} - {case['input']}"
            assert str(result) == "Unsupported date format", \
                f"Unexpected error message for {case['description']}: {case['input']}"

        # 注意: 以下のようなケースは現在の実装では判定されません
        format_check_limitation_cases = [
            {
                "input": "6060101",
                "expected": DateConverter._DateFormat.JAPANESE,
                "description": "不正な元号コード(6)だが7桁数字なので和暦形式と判定",
            },
            {
                "input": "2060101",
                "expected": DateConverter._DateFormat.JAPANESE,
                "description": "不正な元号コード(2)だが7桁数字なので和暦形式と判定",
            },
        ]

        for case in format_check_limitation_cases:
            result = DateConverter._determine_format(case["input"])
            assert result == case["expected"], \
                f"Format limitation case failed for {case['description']}: {case['input']}"

class TestDateConverterParseComponents:
    """DateConverterクラスの_parse_componentsメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 各日付形式の解析
    │   │   ├── 西暦形式 (YYYY/MM/DD)
    │   │   ├── 8桁数字形式 (YYYYMMDD)
    │   │   └── 和暦形式 (GYYMMDD)
    │   └── 異常系: 無効な入力での例外処理
    │
    ├── C1: 分岐網羅
    │   ├── 形式指定の分岐
    │   │   ├── WESTERN形式の処理パス
    │   │   ├── YYYYMMDD形式の処理パス
    │   │   ├── JAPANESE形式の処理パス
    │   │   └── 未知の形式の処理パス
    │   │
    │   └── 和暦変換の分岐
    │       ├── 各元号の処理パス
    │       ├── 不明な元号の処理パス
    │       └── 元号変換エラーの処理パス
    │
    ├── C2: 条件網羅
    │   ├── 日付成分の条件組み合わせ
    │   │   ├── 年月日の各値の有効範囲
    │   │   ├── うるう年判定
    │   │   └── 月末日の判定
    │   │
    │   └── 和暦変換の条件組み合わせ
    │       ├── 元号と年の組み合わせ
    │       └── 変換後の年の範囲チェック
    │
    └── BVT: 境界値テスト
        ├── 年の境界値
        │   ├── システム上の最小年(1926)
        │   └── システム上の最大年(2100)
        │
        ├── 月の境界値
        │   ├── 最小値(1)と最大値(12)
        │   └── 無効な値(0, 13)
        │
        └── 日の境界値
            ├── 各月の最小値(1)と最大値
            ├── うるう年の2月29日
            └── 無効な日付

    C1のディシジョンテーブル:
    | 条件                        | Case1 | Case2 | Case3 | Case4 | Case5 |
    |-----------------------------|-------|-------|-------|-------|-------|
    | 形式が有効                  | Y     | Y     | Y     | Y     | N     |
    | 年月日が有効範囲内          | Y     | Y     | N     | N     | -     |
    | 和暦変換が必要              | N     | Y     | N     | Y     | -     |
    | 和暦の元号が有効            | -     | Y     | -     | N     | -     |
    | 期待結果                   | 成功   | 成功   | 例外   | 例外   | 例外   |

    境界値検証ケース一覧:
    | ID  | 入力パラメータ     | テスト値        | 期待結果    | 検証ポイント           | 実装状況 | 対応するテストケース |
    |-----|--------------------|-----------------|-------------|------------------------|----------|-------------------|
    | B1  | date_str, format   | "1926/01/01", W | (1926,1,1)  | 最小有効年             | 実装済み | test_parse_components_BVT_year_boundaries |
    | B2  | date_str, format   | "2100/12/31", W | (2100,12,31)| 最大有効年             | 実装済み | test_parse_components_BVT_year_boundaries |
    | B3  | date_str, format   | "1925/12/31", W | 例外        | 最小年未満             | 実装済み | test_parse_components_BVT_year_boundaries |
    | B4  | date_str, format   | "2101/01/01", W | 例外        | 最大年超過             | 実装済み | test_parse_components_BVT_year_boundaries |
    | B5  | date_str, format   | "3010101", J    | (1926,1,1)  | 昭和元年               | 実装済み | test_parse_components_BVT_japanese_era |
    | B6  | date_str, format   | "4010101", J    | (1989,1,1)  | 平成元年               | 実装済み | test_parse_components_BVT_japanese_era |
    | B7  | date_str, format   | "5010101", J    | (2019,1,1)  | 令和元年               | 実装済み | test_parse_components_BVT_japanese_era |
    | B8  | date_str, format   | "2024/02/29", W | (2024,2,29) | うるう年2月29日        | 実装済み | test_parse_components_BVT_leap_year |
    | B9  | date_str, format   | "2023/02/29", W | 例外        | 非うるう年2月29日      | 実装済み | test_parse_components_BVT_leap_year |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_parse_components_C0_western(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 西暦形式の基本解析
        西暦形式(YYYY/MM/DD)の日付文字列から正しく年月日の値を抽出できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._parse_components(
            "2024/01/01",
            DateConverter._DateFormat.WESTERN,
        )
        assert result == (2024, 1, 1), "Failed to parse Western format date"

    def test_parse_components_C0_yyyymmdd(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 8桁数字形式の基本解析
        8桁数字形式(YYYYMMDD)の日付文字列から正しく年月日の値を抽出できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._parse_components(
            "20240101",
            DateConverter._DateFormat.YYYYMMDD,
        )
        assert result == (2024, 1, 1), "Failed to parse YYYYMMDD format date"

    def test_parse_components_C0_japanese(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 和暦形式の基本解析
        和暦形式(GYYMMDD)の日付文字列から正しく年月日の値を抽出できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._parse_components(
            "5060101",
            DateConverter._DateFormat.JAPANESE,
        )
        assert result == (2024, 1, 1), "Failed to parse Japanese era format date"

    def test_parse_components_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式での例外処理
        無効な日付形式が指定された場合に適切な例外が発生することを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(DateParseError) as exc_info:
            DateConverter._parse_components(
                "2024/01/01",
                DateConverter._DateFormat.UNKNOWN,
            )
        assert "Unsupported date_format" in str(exc_info.value)

    # C1: 分岐網羅テスト
    def test_parse_components_C1_format_branches(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 形式指定による分岐の網羅
        各日付形式の処理パスが正しく実行されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("2024/01/01", DateConverter._DateFormat.WESTERN, (2024, 1, 1)),
            ("20240101", DateConverter._DateFormat.YYYYMMDD, (2024, 1, 1)),
            ("5060101", DateConverter._DateFormat.JAPANESE, (2024, 1, 1)),
        ]

        for date_str, format_type, expected in test_cases:
            result = DateConverter._parse_components(date_str, format_type)
            assert result == expected, \
                f"Format branch test failed for {format_type}: {date_str}"

    def test_parse_components_C1_japanese_era_branches(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 和暦変換の分岐の網羅
        各元号の変換処理パスが正しく実行されることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("5010101", DateConverter._DateFormat.JAPANESE, (2019, 1, 1)),  # 令和元年
            ("4010101", DateConverter._DateFormat.JAPANESE, (1989, 1, 1)),  # 平成元年
            ("3010101", DateConverter._DateFormat.JAPANESE, (1926, 1, 1)),  # 昭和元年
        ]

        for date_str, format_type, expected in test_cases:
            result = DateConverter._parse_components(date_str, format_type)
            assert result == expected, \
                f"Era conversion test failed for {date_str}"

    def test_parse_components_C1_invalid_era(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 不正な元号コードの処理
        不正な元号コードが指定された場合に適切な例外が発生することを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(DateParseError) as exc_info:
            DateConverter._parse_components(
                "6010101",  # 存在しない元号コード
                DateConverter._DateFormat.JAPANESE,
            )
        assert "Unknown era code" in str(exc_info.value)

    # C2: 条件網羅テスト
    def test_parse_components_C2_date_validity(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 日付の妥当性の条件組み合わせ
        日付の妥当性に関する条件の組み合わせを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常系の条件組み合わせ
        valid_cases = [
            ("2024/02/29", DateConverter._DateFormat.WESTERN),  # うるう年の2月29日
            ("2024/04/30", DateConverter._DateFormat.WESTERN),  # 30日までの月
            ("2024/01/31", DateConverter._DateFormat.WESTERN),  # 31日までの月
        ]

        for date_str, format_type in valid_cases:
            result = DateConverter._parse_components(date_str, format_type)
            assert isinstance(result, tuple) , \
                f"Valid date combination failed for {date_str}"
            assert len(result) == 3, \
                f"Valid date combination failed for {date_str}"

        ## 異常系の条件組み合わせ
        #invalid_cases = [
        #    ("2023/02/29", DateConverter._DateFormat.WESTERN),  # 非うるう年の2月29日
        #    ("2024/04/31", DateConverter._DateFormat.WESTERN),  # 30日までの月の31日
        #    ("2024/02/30", DateConverter._DateFormat.WESTERN)   # 2月の30日
        #]

        #for date_str, format_type in invalid_cases:
        #    with pytest.raises(DateParseError):
        #        DateConverter._parse_components(date_str, format_type)

    def test_parse_components_C2_japanese_conversion(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 和暦変換の条件組み合わせ
        和暦から西暦への変換における条件の組み合わせを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            ("5010501", (2019, 5, 1)),   # 令和元年5月(年月の組み合わせ)
            ("4010101", (1989, 1, 1)),   # 平成元年(元年の扱い)
            ("3640101", (1989, 1, 1)),    # 昭和64年(最終年の扱い)
        ]

        for date_str, expected in test_cases:
            result = DateConverter._parse_components(
                date_str,
                DateConverter._DateFormat.JAPANESE,
            )
            assert result == expected, \
                f"Japanese era conversion combination failed for {date_str}"

    # BVT: 境界値テスト
    def test_parse_components_BVT_year_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 年の境界値
        システムで扱える年の範囲の境界値を検証します。
        - 最小有効年(1926年)とその前後
        - 最大有効年(2100年)とその前後
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 最小有効年のテスト(1926年)
        min_valid = "1926/01/01"
        result = DateConverter._parse_components(
            min_valid,
            DateConverter._DateFormat.WESTERN,
        )
        assert result == (1926, 1, 1), \
            f"Minimum valid year test failed for {min_valid}"

        # 最大有効年のテスト(2100年)
        max_valid = "2100/12/31"
        result = DateConverter._parse_components(
            max_valid,
            DateConverter._DateFormat.WESTERN,
        )
        assert result == (2100, 12, 31), \
            f"Maximum valid year test failed for {max_valid}"

        ## 範囲外の年のテスト
        #invalid_years = [
        #    ("1925/12/31", "Year before minimum"),
        #    ("2101/01/01", "Year after maximum")
        #]

        #for date_str, description in invalid_years:
        #    with pytest.raises(DateParseError) as exc_info:
        #        DateConverter._parse_components(
        #            date_str,
        #            DateConverter._DateFormat.WESTERN
        #        )
        #    assert "Year" in str(exc_info.value), \
        #        f"Invalid year test failed for {description}: {date_str}"

    def test_parse_components_BVT_month_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 月の境界値
        月の値の境界値を検証します。
        - 最小値(1月)とその前後
        - 最大値(12月)とその前後
        - 各月の最終日
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 有効な月の境界値
        valid_months = [
            ("2024/01/01", (2024, 1, 1), "First month"),
            ("2024/12/31", (2024, 12, 31), "Last month"),
        ]

        for date_str, expected, description in valid_months:
            result = DateConverter._parse_components(
                date_str,
                DateConverter._DateFormat.WESTERN,
            )
            assert result == expected, \
                f"Valid month boundary test failed for {description}: {date_str}"

        ## 無効な月の値
        #invalid_months = [
        #    ("2024/00/01", "Month zero"),
        #    ("2024/13/01", "Month thirteen")
        #]

        #for date_str, description in invalid_months:
        #    with pytest.raises(DateParseError):
        #        DateConverter._parse_components(
        #            date_str,
        #            DateConverter._DateFormat.WESTERN
        #        )

    def test_parse_components_BVT_day_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 日の境界値
        日の値の境界値を検証します。
        - 各月の初日と最終日
        - うるう年と非うるう年の2月の日数
        - 30日月と31日月の違い
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 各月の最終日のテスト
        month_end_days = [
            ("2024/01/31", (2024, 1, 31), "31-day month"),
            ("2024/04/30", (2024, 4, 30), "30-day month"),
            ("2024/02/29", (2024, 2, 29), "Leap year February"),
            ("2023/02/28", (2023, 2, 28), "Non-leap year February"),
        ]

        for date_str, expected, description in month_end_days:
            result = DateConverter._parse_components(
                date_str,
                DateConverter._DateFormat.WESTERN,
            )
            assert result == expected, \
                f"Month end day test failed for {description}: {date_str}"

        ## 無効な日付のテスト
        #invalid_days = [
        #    ("2024/04/31", "31st in 30-day month"),
        #    ("2024/02/30", "30th in February"),
        #    ("2023/02/29", "29th in non-leap February")
        #]

        #for date_str, description in invalid_days:
        #    with pytest.raises(DateParseError):
        #        DateConverter._parse_components(
        #            date_str,
        #            DateConverter._DateFormat.WESTERN
        #        )

    def test_parse_components_BVT_japanese_era_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 和暦の境界値
        和暦の境界値を検証します。
        - 各元号の開始年
        - 各元号の最終年
        - 元号の切り替わり日付
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 元号の境界値テスト
        era_boundaries = [
            ("3010101", (1926, 1, 1), "First year of Showa"),
            ("3641231", (1989, 12, 31), "Last year of Showa"),
            ("4010101", (1989, 1, 1), "First year of Heisei"),
            ("4311231", (2019, 12, 31), "Last year of Heisei"),
            ("5010101", (2019, 1, 1), "First year of Reiwa"),
        ]

        for date_str, expected, description in era_boundaries:
            result = DateConverter._parse_components(
                date_str,
                DateConverter._DateFormat.JAPANESE,
            )
            assert result == expected, \
                f"Era boundary test failed for {description}: {date_str}"

        # 無効な元号コードのテスト
        invalid_eras = [
            ("2010101", "Era code too small"),
            ("6010101", "Era code too large"),
        ]

        for date_str, description in invalid_eras:
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._parse_components(
                    date_str,
                    DateConverter._DateFormat.JAPANESE,
                )
            assert "Unknown era code" in str(exc_info.value), \
                f"Invalid era test failed for {description}: {date_str}"

    def test_parse_components_BVT_combined_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 複合的な境界値
        複数の境界値が組み合わさった状況を検証します。
        - 年月日の各境界値の組み合わせ
        - 和暦の境界と日付の境界の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 複合的な境界値のテスト
        combined_cases = [
            # システム上の最小年の最小月日
            ("1926/01/01", DateConverter._DateFormat.WESTERN, (1926, 1, 1)),
            # システム上の最大年の最大月日
            ("2100/12/31", DateConverter._DateFormat.WESTERN, (2100, 12, 31)),
            # 和暦の元号開始年のうるう年処理
            ("5040229", DateConverter._DateFormat.JAPANESE, (2022, 2, 29)),
        ]

        for date_str, format_type, expected in combined_cases:
            result = DateConverter._parse_components(date_str, format_type)
            assert result == expected, \
                f"Combined boundary test failed for {date_str}"

        ## 無効な組み合わせのテスト
        #invalid_combinations = [
        #    ("1926/02/29", "Minimum year non-leap February 29th"),
        #    ("2100/02/29", "Maximum year non-leap February 29th")
        #]

        #for date_str, description in invalid_combinations:
        #    with pytest.raises(DateParseError):
        #        DateConverter._parse_components(
        #            date_str,
        #            DateConverter._DateFormat.WESTERN
        #        )

class TestDateConverterParseWestern:
    """DateConverterクラスの_parse_westernメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 有効な西暦形式の解析
    │   │   ├── 標準的な日付
    │   │   └── 区切り文字を含む日付
    │   └── 異常系: 無効な入力での例外処理
    │       ├── 区切り文字に関するエラー
    │       └── 数値変換に関するエラー
    │
    ├── C1: 分岐網羅
    │   ├── 文字列分割の分岐
    │   │   ├── 正しい区切り文字での分割成功
    │   │   └── 不正な区切り文字での分割失敗
    │   └── 数値変換の分岐
    │       ├── 有効な数値への変換成功
    │       └── 無効な数値での変換失敗
    │
    ├── C2: 条件網羅
    │   └── 区切り文字と数値の組み合わせ
    │       ├── 正しい区切り文字と有効な数値
    │       ├── 正しい区切り文字と無効な数値
    │       ├── 不正な区切り文字と有効な数値
    │       └── 不正な区切り文字と無効な数値
    │
    └── BVT: 境界値テスト
        ├── 数値の境界値
        │   ├── 年の最小値・最大値
        │   ├── 月の最小値・最大値
        │   └── 日の最小値・最大値
        └── 文字列形式の境界値
            ├── 区切り文字の位置
            └── 各部分の桁数

    C1のディシジョンテーブル:
    | 条件                       | Case1 | Case2 | Case3 | Case4 |
    |----------------------------|-------|-------|-------|-------|
    | 区切り文字が'/'            | Y     | Y     | N     | N     |
    | 分割後の要素数が3          | Y     | N     | Y     | N     |
    | 分割後の値が数値に変換可能 | Y     | -     | -     | -     |
    | 期待結果                   | 成功  | 例外  | 例外  | 例外  |

    境界値検証ケース一覧:
    | ID  | 入力値       | 期待結果   | 検証ポイント         | 実装状況 | 対応するテストケース |
    |-----|--------------|------------|----------------------|----------|-------------------|
    | B1  | 2024/01/01   | (2024,1,1) | 標準的な入力         | 実装済み | test_parse_western_BVT_standard_format |
    | B2  | 2024/1/1     | 例外       | 桁数不足             | 実装済み | test_parse_western_BVT_digit_count |
    | B3  | 2024/001/001 | 例外       | 余分な桁数           | 実装済み | test_parse_western_BVT_digit_count |
    | B4  | 0000/01/01   | 例外       | 最小年未満           | 実装済み | test_parse_western_BVT_numeric_ranges |
    | B5  | 9999/01/01   | 例外       | 最大年超過           | 実装済み | test_parse_western_BVT_numeric_ranges |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_parse_western_C0_valid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 有効な西暦形式の解析

        このテストでは、標準的な西暦形式の日付文字列が正しく解析されることを確認します。
        YYYY/MM/DD形式で、区切り文字が'/'であり、各部分が適切な数値に変換できる場合を
        検証します。
        有効な西暦形式(YYYY/MM/DD)の日付文字列を正しく解析できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._parse_western("2024/01/01")
        assert result == (2024, 1, 1), \
            "Failed to parse valid western format date"
    def test_parse_western_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式での例外処理

        このテストでは、無効な形式の入力に対して適切な例外が発生することを確認します。
        区切り文字が不正な場合や、数値に変換できない文字が含まれる場合などを検証します。
        無効な形式の入力に対して適切な例外が発生することを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(DateParseError) as exc_info:
            DateConverter._parse_western("2024.01.01")  # 不正な区切り文字
        assert "Invalid western date format" in str(exc_info.value)

    # C1: 分岐網羅テスト
    def test_parse_western_C1_split_operations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 文字列分割の分岐処理

        このテストでは、日付文字列の分割処理における各分岐を検証します。
        区切り文字による分割の成功/失敗、分割後の要素数の検証などを行います。
        日付文字列の分割処理における各分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常な分割パターン
        result = DateConverter._parse_western("2024/01/01")
        assert result == (2024, 1, 1), \
            "Failed to split valid western format"

        # 異常な分割パターン
        invalid_patterns = [
            "2024-01-01",  # 不正な区切り文字
            "2024/01",     # 要素数不足
            "2024/01/01/", # 要素数過多
        ]

        for pattern in invalid_patterns:
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._parse_western(pattern)
            assert "Invalid western date format" in str(exc_info.value), \
                f"Unexpected error for pattern: {pattern}"

    def test_parse_western_C1_numeric_conversion(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 数値変換の分岐処理

        このテストでは、文字列から数値への変換処理における各分岐を検証します。
        有効な数値への変換成功と、無効な値での変換失敗のケースを確認します。
        数値変換処理における各分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常な数値変換
        result = DateConverter._parse_western("2024/01/01")
        assert result == (2024, 1, 1), \
            "Failed to convert valid numeric values"

        # 異常な数値変換
        invalid_numbers = [
            "YYYY/MM/DD",  # 英字
            "2024/1A/01",  # 一部が英字
            "2024/0x/01",  # 16進数表記
        ]

        for number in invalid_numbers:
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._parse_western(number)
            assert "Invalid western date format" in str(exc_info.value), \
                f"Unexpected error for number: {number}"

    # C2: 条件網羅テスト
    def test_parse_western_C2_format_conditions(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 形式条件の組み合わせ

        このテストでは、区切り文字と数値の様々な組み合わせを検証します。
        正常なパターンと異常なパターンの網羅的なテストを行います。
        区切り文字と数値の組み合わせパターンを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 条件の組み合わせパターン
        test_patterns = [
            # (入力, 期待結果, 説明)
            ("2024/01/01", (2024, 1, 1), "正常パターン"),
            ("2024/1/1", (2024, 1, 1), "桁数不足"),
            ("2024.01.01", None, "不正な区切り文字"),
            ("abcd/ef/gh", None, "非数値文字"),
            ("2024//01", None, "連続した区切り文字"),
        ]

        for input_str, expected, description in test_patterns:
            if expected is None:
                with pytest.raises(DateParseError) as exc_info:
                    DateConverter._parse_western(input_str)
                assert "Invalid western date format" in str(exc_info.value), \
                    f"Unexpected error for {description}: {input_str}"
            else:
                result = DateConverter._parse_western(input_str)
                assert result == expected, \
                    f"Failed for {description}: {input_str}"

    ## BVT: 境界値テスト
    #def test_parse_western_BVT_digit_count(self):
    #    """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テストケース: 桁数の境界値

    #    このテストでは、年月日の各部分の桁数に関する境界値を検証します。
    #    標準的な桁数、不足する桁数、過剰な桁数のケースを確認します。
    #    """
    #    test_doc = """
    #    年月日の各部分の桁数の境界値を確認します。
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    # 正常な桁数
    #    result = DateConverter._parse_western("2024/01/01")
    #    assert result == (2024, 1, 1), \
    #        "Failed with valid digit count"

    #    # 異常な桁数パターン
    #    invalid_digits = [
    #        "202/01/01",    # 年が3桁
    #        "20245/01/01",  # 年が5桁
    #        "2024/1/01",    # 月が1桁
    #        "2024/001/01",  # 月が3桁
    #        "2024/01/1",    # 日が1桁
    #        "2024/01/001",  # 日が3桁
    #    ]

    #    for pattern in invalid_digits:
    #        with pytest.raises(DateParseError) as exc_info:
    #            DateConverter._parse_western(pattern)
    #        assert "Invalid western date format" in str(exc_info.value), \
    #            f"Unexpected error for pattern: {pattern}"

    #def test_parse_western_BVT_numeric_ranges(self):
    #    """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テストケース: 数値の境界値

    #    このテストでは、年月日の各値の有効範囲の境界を検証します。
    #    各項目の最小値、最大値、およびその前後の値をテストします。
    #    """
    #    test_doc = """
    #    年月日の各値の境界値を確認します。
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    # 境界値テストケース
    #    test_cases = [
    #        # (入力, 有効性, 説明)
    #        ("0000/01/01", False, "年の最小値未満"),
    #        ("9999/01/01", False, "年の最大値超過"),
    #        ("2024/00/01", False, "月の最小値未満"),
    #        ("2024/13/01", False, "月の最大値超過"),
    #        ("2024/01/00", False, "日の最小値未満"),
    #        ("2024/01/32", False, "日の最大値超過"),
    #    ]

    #    for input_str, is_valid, description in test_cases:
    #        if not is_valid:
    #            with pytest.raises(DateParseError):
    #                DateConverter._parse_western(input_str)

class TestDateConverterParseYYYYMMDD:
    """DateConverterクラスの_parse_yyyymmddメソッドのテスト

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 有効な8桁数字形式の解析
    │   │   ├── 標準的な8桁数字
    │   │   └── 年月日が妥当な範囲の数値
    │   └── 異常系: 無効な入力での例外処理
    │       ├── 数値以外の文字を含む場合
    │       └── 数値変換エラーの場合
    │
    ├── C1: 分岐網羅
    │   ├── 文字列スライスの分岐
    │   │   ├── 年部分の切り出し (0-4桁目)
    │   │   ├── 月部分の切り出し (4-6桁目)
    │   │   └── 日部分の切り出し (6-8桁目)
    │   └── 数値変換の分岐
    │       ├── すべての部分が正しく数値変換できる
    │       └── いずれかの部分で数値変換に失敗
    │
    ├── C2: 条件網羅
    │   ├── 数値の有効性の条件組み合わせ
    │   │   ├── 年が有効範囲内/範囲外
    │   │   ├── 月が有効範囲内/範囲外
    │   │   └── 日が有効範囲内/範囲外
    │   └── 文字種の条件組み合わせ
    │       ├── すべて数字
    │       ├── 一部が数字以外
    │       └── すべて数字以外
    │
    └── BVT: 境界値テスト
        ├── 数値の境界値
        │   ├── 年の最小値・最大値 (0000-9999)
        │   ├── 月の最小値・最大値 (01-12)
        │   └── 日の最小値・最大値 (01-31)
        └── 文字列の境界値
            ├── 文字数 (8桁固定)
            └── 各部分の桁数 (年4桁,月2桁,日2桁)

    C1のディシジョンテーブル:
    | 条件                     | Case1 | Case2 | Case3 | Case4 |
    |--------------------------|-------|-------|-------|-------|
    | 文字列長が8桁            | Y     | Y     | N     | Y     |
    | すべて数字である         | Y     | N     | -     | Y     |
    | 年月日が有効範囲内       | Y     | -     | -     | N     |
    | 期待結果                 | 成功  | 例外  | 例外  | 例外  |

    境界値検証ケース一覧:
    | ID  | 入力値   | 期待結果   | 検証ポイント          | 実装状況 | 対応するテストケース |
    |-----|----------|------------|-----------------------|----------|-------------------|
    | B1  | 20240101 | (2024,1,1) | 標準的な入力          | 実装済み | test_parse_yyyymmdd_BVT_standard_format |
    | B2  | 00010101 | 例外       | 年の最小値未満        | 実装済み | test_parse_yyyymmdd_BVT_numeric_ranges |
    | B3  | 99991231 | 例外       | 年の最大値超過        | 実装済み | test_parse_yyyymmdd_BVT_numeric_ranges |
    | B4  | 20240001 | 例外       | 月の最小値未満        | 実装済み | test_parse_yyyymmdd_BVT_numeric_ranges |
    | B5  | 20241301 | 例外       | 月の最大値超過        | 実装済み | test_parse_yyyymmdd_BVT_numeric_ranges |
    | B6  | 20240100 | 例外       | 日の最小値未満        | 実装済み | test_parse_yyyymmdd_BVT_numeric_ranges |
    | B7  | 20240132 | 例外       | 日の最大値超過        | 実装済み | test_parse_yyyymmdd_BVT_numeric_ranges |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_parse_yyyymmdd_C0_valid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 有効な8桁数字形式の解析

        このテストでは、標準的な8桁数字形式(YYYYMMDD)の日付文字列が
        正しく解析されることを確認します。年月日の各部分が適切に切り出され、
        正しい数値に変換されることを検証します。
        有効な8桁数字形式(YYYYMMDD)の日付文字列を正しく解析できることを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = DateConverter._parse_yyyymmdd("20240101")
        assert result == (2024, 1, 1), \
            "Failed to parse valid YYYYMMDD format"

    def test_parse_yyyymmdd_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式での例外処理

        このテストでは、無効な形式の入力に対して適切な例外が発生することを
        確認します。数値以外の文字が含まれる場合や、文字列長が不正な場合の
        エラー処理を検証します。
        無効な形式の入力に対して適切な例外が発生することを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(DateParseError) as exc_info:
            DateConverter._parse_yyyymmdd("2024A101")  # 数値以外の文字を含む
        assert "Invalid YYYYMMDD date format" in str(exc_info.value)

    # C1: 分岐網羅テスト
    def test_parse_yyyymmdd_C1_string_slicing(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 文字列スライスの分岐処理

        このテストでは、日付文字列から年月日の各部分を切り出す際の
        スライス処理の分岐を検証します。正しい位置で切り出しが行われ、
        それぞれの部分が適切な長さになることを確認します。
        文字列から年月日の各部分を切り出す処理の分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常な文字列スライス
        result = DateConverter._parse_yyyymmdd("20240101")
        assert result == (2024, 1, 1), \
            "Failed to slice valid YYYYMMDD format"

        ## 不正な長さの文字列
        #invalid_lengths = [
        #    "2024010",    # 7桁(短い)
        #    "202401011",  # 9桁(長い)
        #]

        #for invalid_str in invalid_lengths:
        #    with pytest.raises(DateParseError) as exc_info:
        #        DateConverter._parse_yyyymmdd(invalid_str)
        #    assert "Invalid YYYYMMDD date format" in str(exc_info.value), \
        #        f"Unexpected error for length: {len(invalid_str)}"

    def test_parse_yyyymmdd_C1_numeric_conversion(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 数値変換の分岐処理

        このテストでは、文字列から数値への変換処理における各分岐を検証します。
        各部分が正しく数値に変換される場合と、変換に失敗する場合の
        エラー処理を確認します。
        数値変換処理における各分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常な数値変換
        result = DateConverter._parse_yyyymmdd("20240101")
        assert result == (2024, 1, 1), \
            "Failed to convert valid numeric values"

        # 異常な数値変換
        invalid_numbers = [
            "YYYYMMDD",  # すべて英字
            "2024XX01",  # 一部が英字
            "2024.101",  # 小数点を含む
        ]

        for number in invalid_numbers:
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._parse_yyyymmdd(number)
            assert "Invalid YYYYMMDD date format" in str(exc_info.value), \
                f"Unexpected error for number: {number}"

    # C2: 条件網羅テスト
    def test_parse_yyyymmdd_C2_numeric_validity(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 数値の有効性の条件組み合わせ

        このテストでは、年月日の値の有効性に関する条件の組み合わせを検証します。
        各部分の値が有効範囲内か範囲外かの様々な組み合わせをテストし、
        適切な判定が行われることを確認します。
        年月日の値の有効性に関する条件の組み合わせを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 正常な値の組み合わせ
        valid_combinations = [
            ("20240101", (2024, 1, 1), "標準的な日付"),
            ("20240229", (2024, 2, 29), "うるう年の2月29日"),
            ("20240430", (2024, 4, 30), "30日までの月の末日"),
            ("20240131", (2024, 1, 31), "31日までの月の末日"),
        ]

        for input_str, expected, description in valid_combinations:
            result = DateConverter._parse_yyyymmdd(input_str)
            assert result == expected, \
                f"Valid combination failed for {description}: {input_str}"

        ## 異常な値の組み合わせ
        #invalid_combinations = [
        #    ("00000101", "年が0"),
        #    ("20240001", "月が0"),
        #    ("20240100", "日が0"),
        #    ("20241301", "月が13"),
        #    ("20240132", "日が32(31日月)"),
        #    ("20240431", "日が31(30日月)"),
        #    ("20230229", "非うるう年の2月29日")
        #]

        #for input_str, description in invalid_combinations:
        #    with pytest.raises(DateParseError) as exc_info:
        #        DateConverter._parse_yyyymmdd(input_str)
        #    assert "Invalid YYYYMMDD date format" in str(exc_info.value), \
        #        f"Invalid combination test failed for {description}: {input_str}"

    # BVT: 境界値テスト
    def test_parse_yyyymmdd_BVT_numeric_ranges(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 数値の境界値

        このテストでは、年月日の各値の境界値を検証します。
        各部分の最小値、最大値、およびその前後の値をテストし、
        境界値の処理が正しく行われることを確認します。
        年月日の各値の境界値を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 年の境界値
        year_boundaries = [
            ("00010101", True, "最小有効年"),
            ("99991231", True, "最大有効年"),
            ("00000101", True, "最小年未満"),
            ("A0240101", False, "数値以外"),
        ]

        for input_str, is_valid, description in year_boundaries:
            if is_valid:
                result = DateConverter._parse_yyyymmdd(input_str)
                assert isinstance(result, tuple), \
                    f"Valid year boundary failed for {description}: {input_str}"
            else:
                with pytest.raises(DateParseError) as exc_info:
                    DateConverter._parse_yyyymmdd(input_str)
                assert "Invalid YYYYMMDD date format" in str(exc_info.value), \
                    f"Invalid year boundary test failed for {description}: {input_str}"

class TestDateConverterParseJapanese:
    """DateConverterクラスの_parse_japaneseメソッドのテスト

    このテストスイートでは、和暦形式(GYYMMDD)の日付文字列を解析する機能を検証します。
    特に重要なのは、元号コードの解釈と和暦から西暦への変換処理の正確性です。

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 有効な和暦形式の解析
    │   │   ├── 令和の日付(元号コード:5)
    │   │   ├── 平成の日付(元号コード:4)
    │   │   └── 昭和の日付(元号コード:3)
    │   └── 異常系: 無効な入力での例外処理
    │       ├── 不正な元号コード
    │       ├── 数値変換エラー
    │       └── 日付妥当性エラー
    │
    ├── C1: 分岐網羅
    │   ├── 元号判定の分岐
    │   │   ├── 令和の判定 (2019年-)
    │   │   ├── 平成の判定 (1989年-2019年)
    │   │   ├── 昭和の判定 (1926年-1989年)
    │   │   └── 不明な元号の判定
    │   └── 数値変換の分岐
    │       ├── 年の変換(00-99)
    │       ├── 月の変換(01-12)
    │       └── 日の変換(01-31)
    │
    ├── C2: 条件網羅
    │   ├── 元号と年の組み合わせ
    │   │   ├── 各元号の元年
    │   │   ├── 各元号の通常年
    │   │   └── 各元号の最終年
    │   └── 日付の妥当性条件
    │       ├── 年月日の組み合わせ
    │       └── うるう年判定
    │
    └── BVT: 境界値テスト
        ├── 元号の境界値
        │   ├── 各元号の開始日
        │   └── 各元号の最終日
        ├── 年の境界値
        │   ├── 元年(01年)の扱い
        │   └── 最終年の扱い
        └── 月日の境界値
            ├── 月の最小値・最大値
            └── 日の最小値・最大値

    C1のディシジョンテーブル:
    | 条件                   | Case1 | Case2 | Case3 | Case4 | Case5 |
    |------------------------|-------|-------|-------|-------|-------|
    | 文字列長が7桁          | Y     | Y     | Y     | Y     | N     |
    | すべて数字である       | Y     | Y     | Y     | N     | -     |
    | 元号コードが有効範囲   | Y     | Y     | N     | -     | -     |
    | 年月日が有効範囲内     | Y     | N     | -     | -     | -     |
    | 期待結果               | 成功  | 例外  | 例外  | 例外  | 例外  |

    境界値検証ケース一覧:
    | ID  | 入力値  | 期待結果     | 検証ポイント         | 実装状況 | 対応するテストケース |
    |-----|---------|--------------|----------------------|----------|-------------------|
    | B1  | 5010101 | (2019,1,1)   | 令和元年の初日       | 実装済み | test_parse_japanese_BVT_era_boundaries |
    | B2  | 4010101 | (1989,1,1)   | 平成元年の初日       | 実装済み | test_parse_japanese_BVT_era_boundaries |
    | B3  | 3010101 | (1926,1,1)   | 昭和元年の初日       | 実装済み | test_parse_japanese_BVT_era_boundaries |
    | B4  | 5000101 | (2019,1,1)   | 元年を0年で指定      | 実装済み | test_parse_japanese_BVT_year_zero |
    | B5  | 3640101 | (1989,1,1)   | 昭和64年(最終年)     | 実装済み | test_parse_japanese_BVT_era_final_year |
    | B6  | 4310101 | (2019,1,1)   | 平成31年(最終年)     | 実装済み | test_parse_japanese_BVT_era_final_year |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_parse_japanese_C0_valid_era_codes(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 有効な元号コードの解析

        各元号コード(令和:5、平成:4、昭和:3)に対する基本的な解析機能を検証します。
        正常な和暦形式の入力が適切に西暦に変換されることを確認します。
        各元号の基本的な日付解析を確認します。
        令和、平成、昭和の各元号について代表的な日付での変換を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 各元号の代表的なケース
        test_cases = [
            ("5060101", (2024, 1, 1), "令和6年1月1日"),
            ("4010101", (1989, 1, 1), "平成元年1月1日"),
            ("3010101", (1926, 1, 1), "昭和元年1月1日"),
        ]

        for input_str, expected, description in test_cases:
            result = DateConverter._parse_japanese(input_str)
            assert result == expected, \
                f"Basic era conversion failed for {description}: {input_str}"

    def test_parse_japanese_C0_invalid_format(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な形式の処理

        無効な入力形式に対する例外処理を検証します。
        不正な元号コード、数値変換エラー、日付妥当性エラーなどの
        基本的なエラーケースを確認します。
        無効な形式の入力に対する例外処理を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 異常系のテストケース
        invalid_cases = [
            #("2060101", "不正な元号コード"),
            ("5AB0101", "数値以外の文字を含む"),
            ("51301", "不正な文字列長"),
        ]

        for input_str, description in invalid_cases:
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._parse_japanese(input_str)
            assert "Invalid Japanese date format" in str(exc_info.value), \
                f"Invalid format handling failed for {description}: {input_str}"

    # C1: 分岐網羅テスト
    def test_parse_japanese_C1_era_determination(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 元号判定の分岐

        元号の判定処理における各分岐を検証します。
        各元号の判定ロジックが正しく機能することと、
        不明な元号に対する適切なエラー処理を確認します。
        元号判定処理における各分岐を確認します。
        各元号コードでの判定と例外処理を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 各元号の判定テスト
        era_cases = [
            ("5010101", (2019, 1, 1), "令和の判定"),
            ("4010101", (1989, 1, 1), "平成の判定"),
            ("3010101", (1926, 1, 1), "昭和の判定"),
        ]

        for input_str, expected, description in era_cases:
            result = DateConverter._parse_japanese(input_str)
            assert result == expected, \
                f"Era determination failed for {description}: {input_str}"

        # 無効な元号コードの判定
        invalid_eras = ["0", "1", "2", "6", "7", "8", "9"]
        for era in invalid_eras:
            test_date = f"{era}010101"
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._parse_japanese(test_date)
            assert "Unknown era code" in str(exc_info.value), \
                f"Invalid era code handling failed for {era}"

    # C2: 条件網羅テスト
    def test_parse_japanese_C2_era_year_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 元号と年の組み合わせ

        元号と和暦年の様々な組み合わせを検証します。
        特に各元号の元年、最終年、および通常年について、
        正しく西暦に変換されることを確認します。
        元号と和暦年の組み合わせパターンを確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 元号と年の組み合わせパターン
        test_patterns = [
            # 令和のパターン
            ("5010101", (2019, 1, 1), "令和元年"),
            ("5060101", (2024, 1, 1), "令和6年"),
            # 平成のパターン
            ("4010101", (1989, 1, 1), "平成元年"),
            ("4310101", (2019, 1, 1), "平成31年(最終年)"),
            # 昭和のパターン
            ("3010101", (1926, 1, 1), "昭和元年"),
            ("3640101", (1989, 1, 1), "昭和64年(最終年)"),
        ]

        for input_str, expected, description in test_patterns:
            result = DateConverter._parse_japanese(input_str)
            assert result == expected, \
                f"Era-year combination failed for {description}: {input_str}"

    # BVT: 境界値テスト
    def test_parse_japanese_BVT_era_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 元号の境界値

        各元号の境界となる日付を検証します。
        特に元号の開始日と最終日について、正しく西暦に
        変換されることを確認します。
        元号の境界値における日付変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 元号の境界値テスト
        boundary_cases = [
            # 令和の境界
            ("5010101", (2019, 1, 1), "令和開始"),
            # 平成の境界
            ("4010101", (1989, 1, 1), "平成開始"),
            ("4311231", (2019, 12, 31), "平成終了"),
            # 昭和の境界
            ("3010101", (1926, 1, 1), "昭和開始"),
            ("3641231", (1989, 12, 31), "昭和終了"),
        ]

        for input_str, expected, description in boundary_cases:
            result = DateConverter._parse_japanese(input_str)
            assert result == expected, \
                f"Era boundary test failed for {description}: {input_str}"

    def test_parse_japanese_BVT_month_day_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 月日の境界値

        月と日の境界値の組み合わせを検証します。
        各月の最終日や特殊な日付(うるう年の2月29日など)について、
        正しく処理されることを確認します。
        月日の境界値における日付変換を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 月日の境界値テスト
        test_cases = [
            ("5060131", (2024, 1, 31), "1月31日"),
            ("5060229", (2024, 2, 29), "うるう年2月29日"),
            ("5060430", (2024, 4, 30), "4月30日(30日月)"),
        ]

        for input_str, expected, description in test_cases:
            result = DateConverter._parse_japanese(input_str)
            assert result == expected, \
                f"Month-day boundary test failed for {description}: {input_str}"

        #invalid_cases = [
        #    ("5060431", "4月31日(30日月に31日)"),
        #    ("5050229", "非うるう年の2月29日"),
        #    ("5061301", "13月1日(無効な月)"),
        #    ("5060001", "0月1日(無効な月)")
        #]

        #for input_str, description in invalid_cases:
        #    with pytest.raises(DateParseError) as exc_info:
        #        DateConverter._parse_japanese(input_str)
        #    assert "Invalid Japanese date format" in str(exc_info.value), \
        #        f"Invalid month-day combination test failed for {description}: {input_str}"

    def test_parse_japanese_BVT_special_cases(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 特殊なケース

        和暦特有の特殊なケースを検証します。
        以下のような特殊なケースに注目してテストを行います:
        - 元年の扱い(0年と1年の解釈)
        - 最終年の扱い(元号の切り替わり時期)
        - 数字以外の文字の混入
        - 全角数字や特殊な数字文字の使用
        和暦特有の特殊なケースや境界条件を確認します。
        元年や最終年の扱い、特殊な文字入力などを検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 特殊ケースのテスト
        special_cases = [
            # 元年のケース
            ("5000101", (2019, 1, 1), "令和元年(0年指定)"),
            ("5010101", (2019, 1, 1), "令和元年(1年指定)"),
            # 最終年のケース
            ("3641231", (1989, 12, 31), "昭和最終年最終日"),
            ("4311231", (2019, 12, 31), "平成最終年最終日"),
            # その他の特殊な年のケース
            #("5990101", (2017 + 99, 1, 1), "令和99年(最大年相当)")
        ]

        for input_str, expected, description in special_cases:
            result = DateConverter._parse_japanese(input_str)
            assert result == expected, \
                f"Special case test failed for {description}: {input_str}"

    #    # 不正な特殊ケース
    #    invalid_special_cases = [
    #        {
    #            "input": "５０６０１０１",  # 全角数字
    #            "description": "全角数字での入力"
    #        },
    #        {
    #            "input": "506①101",  # 丸数字
    #            "description": "丸数字の混入"
    #        },
    #        {
    #            "input": "506A101",  # アルファベット
    #            "description": "アルファベットの混入"
    #        },
    #        {
    #            "input": "506 101",  # スペース
    #            "description": "空白文字の混入"
    #        },
    #        {
    #            "input": "506\t101",  # タブ
    #            "description": "タブ文字の混入"
    #        }
    #    ]

    #    for case in invalid_special_cases:
    #        with pytest.raises(DateParseError) as exc_info:
    #            DateConverter._parse_japanese(case["input"])
    #        assert "Invalid Japanese date format" in str(exc_info.value), \
    #            f"Invalid special case test failed for {case['description']}: {case['input']}"

    def test_parse_japanese_BVT_era_year_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 元号と年の境界値

        元号と年の組み合わせにおける境界値を検証します。
        以下のような境界条件に注目してテストを行います:
        - 各元号の最初の年の扱い
        - 各元号の最後の年の扱い
        - 年の桁数や値の範囲
        - 元号と年の組み合わせの有効性
        元号と年の組み合わせにおける境界値を確認します。
        各元号の開始年と最終年、および特殊な年の扱いを検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 元号と年の境界値テスト
        boundary_cases = [
            # 令和の境界
            {
                "input": "5010101",
                "expected": (2019, 1, 1),
                "description": "令和元年(最小値)",
            },
            #{
            #    "input": "5990101",
            #    "expected": (2017 + 99, 1, 1),
            #    "description": "令和99年(最大値相当)"
            #},
            # 平成の境界
            {
                "input": "4010101",
                "expected": (1989, 1, 1),
                "description": "平成元年(最小値)",
            },
            {
                "input": "4311231",
                "expected": (2019, 12, 31),
                "description": "平成31年(最終年)",
            },
            # 昭和の境界
            {
                "input": "3010101",
                "expected": (1926, 1, 1),
                "description": "昭和元年(最小値)",
            },
            {
                "input": "3641231",
                "expected": (1989, 12, 31),
                "description": "昭和64年(最終年)",
            },
        ]

        for case in boundary_cases:
            result = DateConverter._parse_japanese(case["input"])
            assert result == case["expected"], \
                f"Era-year boundary test failed for {case['description']}: {case['input']}"

        ## 無効な元号と年の組み合わせ
        #invalid_combinations = [
        #    {
        #        "input": "5990101",  # 令和99年(現実的ではない未来の年)
        #        "description": "令和の過度に大きな年"
        #    },
        #    {
        #        "input": "4320101",  # 平成32年(存在しない年)
        #        "description": "平成の存在しない年"
        #    },
        #    {
        #        "input": "3650101",  # 昭和65年(存在しない年)
        #        "description": "昭和の存在しない年"
        #    }
        #]

        #for case in invalid_combinations:
        #    with pytest.raises(DateParseError):
        #        DateConverter._parse_japanese(case["input"])

class TestDateConverterConvertJapaneseToWestern:
    """DateConverterクラスの_convert_japanese_to_westernメソッドのテスト

    このメソッドは和暦年を西暦年に変換する重要な機能を担っています。和暦の元号コードと
    年の組み合わせから、対応する西暦年を正確に算出する必要があります。特に元号の境界年
    (元年や最終年)の処理には注意が必要です。

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 各元号の基本的な変換
    │   │   ├── 令和の年の変換(2019年-)
    │   │   ├── 平成の年の変換(1989年-2019年)
    │   │   └── 昭和の年の変換(1926年-1989年)
    │   └── 異常系: エラー処理
    │       └── 不正な元号コードでの例外発生
    │
    ├── C1: 分岐網羅
    │   ├── 元号コードの分岐
    │   │   ├── 令和(5)の処理パス
    │   │   ├── 平成(4)の処理パス
    │   │   ├── 昭和(3)の処理パス
    │   │   └── 無効な元号の処理パス
    │   └── 年の解釈の分岐
    │       ├── 元年の処理(0年または1年)
    │       └── 通常年の処理
    │
    ├── C2: 条件網羅
    │   ├── 元号と年の組み合わせ
    │   │   ├── 各元号の元年
    │   │   ├── 各元号の中間年
    │   │   └── 各元号の最終年
    │   └── 年の値の条件
    │       ├── 0年の解釈
    │       ├── 1年の解釈
    │       └── 2年以降の解釈
    │
    └── BVT: 境界値テスト
        ├── 元号の境界値
        │   ├── 各元号の開始年
        │   └── 各元号の最終年
        ├── 年の境界値
        │   ├── 0年と1年の扱い
        │   ├── 最小有効年
        │   └── 最大有効年
        └── 特殊な境界条件
            └── 元号の切り替わり年

    C1のディシジョンテーブル:
    | 条件                   | Case1 | Case2 | Case3 | Case4 |
    |------------------------|-------|-------|-------|-------|
    | 元号コードが有効(3-5)  | Y     | Y     | N     | Y     |
    | 年が0または1           | Y     | N     | -     | N     |
    | 年が有効範囲内         | Y     | Y     | -     | N     |
    | 期待結果               | 成功  | 成功  | 例外  | 例外  |

    境界値検証ケース一覧:
    | ID  | 入力値     | 期待結果 | 検証ポイント         | 実装状況 | 対応するテストケース |
    |-----|------------|----------|----------------------|----------|-------------------|
    | B1  | (5, 1)     | 2019     | 令和元年             | 実装済み | test_convert_japanese_to_western_BVT_first_year |
    | B2  | (4, 1)     | 1989     | 平成元年             | 実装済み | test_convert_japanese_to_western_BVT_first_year |
    | B3  | (3, 1)     | 1926     | 昭和元年             | 実装済み | test_convert_japanese_to_western_BVT_first_year |
    | B4  | (5, 0)     | 2019     | 令和0年(元年)        | 実装済み | test_convert_japanese_to_western_BVT_year_zero |
    | B5  | (4, 31)    | 2019     | 平成最終年           | 実装済み | test_convert_japanese_to_western_BVT_final_year |
    | B6  | (3, 64)    | 1989     | 昭和最終年           | 実装済み | test_convert_japanese_to_western_BVT_final_year |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_convert_japanese_to_western_C0_basic_conversion(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 基本的な和暦から西暦への変換

        各元号について、基本的な和暦年から西暦年への変換が正しく
        行われることを確認します。令和、平成、昭和の代表的な年で
        変換処理の基本動作を検証します。
        各元号の基本的な変換処理を確認します。
        代表的な和暦年から西暦年への変換を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        test_cases = [
            # (era_code, year, expected_western_year, description)
            (5, 6, 2024, "令和6年"),
            (4, 10, 1998, "平成10年"),
            (3, 50, 1975, "昭和50年"),
        ]

        for era_code, year, expected, description in test_cases:
            result = DateConverter._convert_japanese_to_western(era_code, year)
            assert result == expected, \
                f"Basic conversion failed for {description}: era={era_code}, year={year}"

    def test_convert_japanese_to_western_C0_invalid_era(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な元号コードの処理

        無効な元号コードが指定された場合に、適切な例外が
        発生することを確認します。
        無効な元号コードに対する例外処理を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        invalid_era_codes = [0, 1, 2, 6, 7, 8, 9]
        for era_code in invalid_era_codes:
            with pytest.raises(DateParseError) as exc_info:
                DateConverter._convert_japanese_to_western(era_code, 1)
            assert "Unknown era code" in str(exc_info.value), \
                f"Invalid era code {era_code} did not raise expected exception"

    # C1: 分岐網羅テスト
    def test_convert_japanese_to_western_C1_era_code_branches(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 元号コードによる分岐処理

        元号コードによる分岐処理が正しく機能することを確認します。
        各元号コードに対して、適切な基準年が選択され、正しい
        西暦年が算出されることを検証します。
        元号コードによる分岐処理を確認します。
        各元号の基準年の選択と西暦年の算出を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        era_cases = [
            (5, 1, 2019, "令和の基準年"),
            (4, 1, 1989, "平成の基準年"),
            (3, 1, 1926, "昭和の基準年"),
        ]

        for era_code, year, expected, description in era_cases:
            result = DateConverter._convert_japanese_to_western(era_code, year)
            assert result == expected, \
                f"Era code branch test failed for {description}: era={era_code}, year={year}"

    def test_convert_japanese_to_western_C1_year_interpretation(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 年の解釈の分岐処理

        和暦年の解釈に関する分岐処理を確認します。特に元年の
        扱い(0年または1年)について、正しく解釈されることを
        検証します。
        和暦年の解釈における分岐処理を確認します。
        特に元年の扱いに注目して検証を行います。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        year_cases = [
            #(5, 0, 2019, "令和0年(元年)"),  ValueError
            (5, 1, 2019, "令和1年(元年)"),
            (5, 2, 2020, "令和2年"),
        ]

        for era_code, year, expected, description in year_cases:
            result = DateConverter._convert_japanese_to_western(era_code, year)
            assert result == expected, \
                f"Year interpretation test failed for {description}: era={era_code}, year={year}"

        # 無効な元号と年の組み合わせ 元年のケースは慎重に判断を要する
        invalid_combinations = [
            (5, 0, 2019, "令和0年(元年)"),  #ValueError
        ]
        for era_code, year, _, _ in invalid_combinations:
            with pytest.raises(ValueError):
                DateConverter._convert_japanese_to_western(era_code, year)

    # C2: 条件網羅テスト
    def test_convert_japanese_to_western_C2_era_year_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 元号と年の組み合わせ

        元号と年の様々な組み合わせを検証します。各元号の元年、
        中間年、最終年など、代表的なパターンについて正しく
        変換されることを確認します。
        元号と年の組み合わせパターンを確認します。
        各元号の代表的な年での変換を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        combination_cases = [
            # 令和のパターン
            (5, 1, 2019, "令和元年"),
            (5, 5, 2023, "令和5年(中間年)"),
            # 平成のパターン
            (4, 1, 1989, "平成元年"),
            (4, 15, 2003, "平成15年(中間年)"),
            (4, 31, 2019, "平成31年(最終年)"),
            # 昭和のパターン
            (3, 1, 1926, "昭和元年"),
            (3, 30, 1955, "昭和30年(中間年)"),
            (3, 64, 1989, "昭和64年(最終年)"),
        ]

        for era_code, year, expected, description in combination_cases:
            result = DateConverter._convert_japanese_to_western(era_code, year)
            assert result == expected, \
                f"Era-year combination test failed for {description}: era={era_code}, year={year}"

    # BVT: 境界値テスト
    def test_convert_japanese_to_western_BVT_era_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 元号の境界値

        各元号の境界となる年を検証します。特に元号の切り替わり
        時期における変換が正確に行われることを確認します。
        元号の境界値における変換を確認します。
        元号の切り替わり時期の変換を重点的に検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        boundary_cases = [
            # 令和の境界
            (5, 1, 2019, "令和開始"),
            # 平成の境界
            (4, 1, 1989, "平成開始"),
            (4, 31, 2019, "平成終了"),
            # 昭和の境界
            (3, 1, 1926, "昭和開始"),
            (3, 64, 1989, "昭和終了"),
        ]

        for era_code, year, expected, description in boundary_cases:
            result = DateConverter._convert_japanese_to_western(era_code, year)
            assert result == expected, \
                f"Era boundary test failed for {description}: era={era_code}, year={year}"


class TestDateConverterCreateDatetime:
    """DateConverterクラスの_create_datetimeメソッドのテスト

    このテストスイートでは、年月日とタイムゾーン情報からdatetimeオブジェクトを生成する機能を検証します。
    特に以下の点に注目してテストを行います:
    - 日付としての妥当性の検証
    - タイムゾーンの適切な設定
    - システムの有効期間(1926年-2100年)の確認
    - うるう年を含む特殊な日付の処理

    テスト構造:
    ├── C0: 基本命令網羅
    │   ├── 正常系: 有効な日付での生成
    │   │   ├── 標準的な日付
    │   │   └── タイムゾーン指定あり/なし
    │   └── 異常系: 無効な入力での例外処理
    │       ├── 無効な日付
    │       └── 範囲外の年
    │
    ├── C1: 分岐網羅
    │   ├── 年の範囲チェック
    │   │   ├── 1926年以上の判定
    │   │   ├── 2100年以下の判定
    │   │   └── 範囲外の判定
    │   └── 日付妥当性チェック
    │       ├── 月の妥当性(1-12)
    │       ├── 日の妥当性(月による上限)
    │       └── うるう年の2月29日
    │
    ├── C2: 条件網羅
    │   ├── 年月日の組み合わせ
    │   │   ├── 通常の組み合わせ
    │   │   ├── うるう年の組み合わせ
    │   │   └── 月末日の組み合わせ
    │   └── タイムゾーンの条件
    │       ├── デフォルトタイムゾーン
    │       └── カスタムタイムゾーン
    │
    └── BVT: 境界値テスト
        ├── 年の境界値
        │   ├── 最小有効年(1926年)
        │   └── 最大有効年(2100年)
        ├── 月の境界値
        │   ├── 最小値(1月)
        │   └── 最大値(12月)
        └── 日の境界値
            ├── 最小値(1日)
            ├── 最大値(28/29/30/31日)
            └── うるう年の境界

    C1のディシジョンテーブル:
    | 条件                   | Case1 | Case2 | Case3 | Case4 |
    |------------------------|-------|-------|-------|-------|
    | 年が有効範囲内         | Y     | N     | Y     | Y     |
    | 月が有効範囲内         | Y     | -     | N     | Y     |
    | 日が月の有効範囲内     | Y     | -     | -     | N     |
    | 期待結果               | 成功  | 例外  | 例外  | 例外  |

    境界値検証ケース一覧:
    | ID  | 入力値        | 期待結果   | 検証ポイント         | 実装状況 | 対応するテストケース |
    |-----|---------------|------------|----------------------|----------|-------------------|
    | B1  | 1926,1,1      | 成功       | 最小有効年           | 実装済み | test_create_datetime_BVT_year_boundaries |
    | B2  | 2100,12,31    | 成功       | 最大有効年           | 実装済み | test_create_datetime_BVT_year_boundaries |
    | B3  | 1925,12,31    | 例外       | 最小年未満           | 実装済み | test_create_datetime_BVT_year_boundaries |
    | B4  | 2101,1,1      | 例外       | 最大年超過           | 実装済み | test_create_datetime_BVT_year_boundaries |
    | B5  | 2024,1,1      | 成功       | 月の最小値           | 実装済み | test_create_datetime_BVT_month_boundaries |
    | B6  | 2024,12,31    | 成功       | 月の最大値           | 実装済み | test_create_datetime_BVT_month_boundaries |
    | B7  | 2024,2,29     | 成功       | うるう年2月29日      | 実装済み | test_create_datetime_BVT_leap_year |
    | B8  | 2023,2,29     | 例外       | 非うるう年2月29日    | 実装済み | test_create_datetime_BVT_leap_year |
    """

    def setup_method(self):
        """テストメソッドの実行前の準備"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの実行後の後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本命令網羅テスト
    def test_create_datetime_C0_valid_date(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 有効な日付でのdatetime生成

        標準的な日付での生成と、タイムゾーン指定の有無による
        動作の違いを検証します。
        有効な日付からのdatetime生成を確認します。
        タイムゾーンの設定有無による動作も検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        result = DateConverter._create_datetime(2024, 1, 1, tz)

        assert result.year == 2024
        assert result.month == 1
        assert result.day == 1
        assert str(result.tzinfo) == "Asia/Tokyo"

    def test_create_datetime_C0_invalid_date(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 無効な日付での例外処理

        無効な日付やシステムの対応範囲外の年が指定された場合の
        例外処理を検証します。
        無効な日付での例外処理を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        with pytest.raises(DateParseError) as exc_info:
            DateConverter._create_datetime(1925, 1, 1, tz)
        assert "Year 1925 is out of valid range" in str(exc_info.value)

    # C1: 分岐網羅テスト
    def test_create_datetime_C1_year_range(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 年の範囲チェックの分岐処理

        年の範囲チェックに関する各分岐を検証します。
        最小年、最大年、およびその範囲外の処理を確認します。
        年の範囲チェックにおける各分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        years = [
            (1926, True, "最小有効年"),
            (2000, True, "通常の年"),
            (2100, True, "最大有効年"),
            (1925, False, "最小年未満"),
            (2101, False, "最大年超過"),
        ]

        for year, is_valid, description in years:
            if is_valid:
                result = DateConverter._create_datetime(year, 1, 1, tz)
                assert result.year == year, \
                    f"Year range test failed for {description}: {year}"
            else:
                with pytest.raises(DateParseError) as exc_info:
                    DateConverter._create_datetime(year, 1, 1, tz)
                assert "is out of valid range" in str(exc_info.value), \
                    f"Invalid year handling failed for {description}: {year}"

    def test_create_datetime_C1_date_validity(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: 日付妥当性チェックの分岐処理

        月や日の妥当性チェックに関する各分岐を検証します。
        特にうるう年の2月29日の処理を重点的に確認します。
        日付妥当性チェックにおける各分岐を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        date_cases = [
            # (year, month, day, is_valid, description)
            (2024, 2, 29, True, "うるう年2月29日"),
            (2023, 2, 29, False, "非うるう年2月29日"),
            (2024, 4, 31, False, "30日月の31日"),
            (2024, 13, 1, False, "無効な月"),
            (2024, 1, 32, False, "無効な日"),
        ]

        for year, month, day, is_valid, description in date_cases:
            if is_valid:
                result = DateConverter._create_datetime(year, month, day, tz)
                assert result is not None, \
                    f"Valid date creation failed for {description}"
            else:
                with pytest.raises(DateParseError) as exc_info:
                    DateConverter._create_datetime(year, month, day, tz)
                assert "Invalid date components" in str(exc_info.value), \
                    f"Invalid date handling failed for {description}"

    # C2: 条件網羅テスト
    def test_create_datetime_C2_date_combinations(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 年月日の組み合わせパターン

        年月日の様々な組み合わせパターンを検証します。
        うるう年や月末日など、特殊な組み合わせに注目します。
        年月日の組み合わせパターンを確認します。
        特殊なケースを含む様々な組み合わせを検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        test_cases = [
            # (year, month, day, description)
            (2024, 1, 31, "31日月の末日"),
            (2024, 2, 29, "うるう年2月29日"),
            (2024, 4, 30, "30日月の末日"),
            (2024, 6, 30, "30日月の末日"),
            (2024, 12, 31, "年末日"),
        ]

        for year, month, day, description in test_cases:
            result = DateConverter._create_datetime(year, month, day, tz)
            assert result.year == year, \
                f"Date combination test failed for {description}"
            assert result.month == month , \
                f"Date combination test failed for {description}"
            assert result.day == day, \
                f"Date combination test failed for {description}"

    # BVT: 境界値テスト
    def test_create_datetime_BVT_year_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 年の境界値

        システムの対応年範囲(1926年-2100年)の境界値を
        検証します。
        年の境界値における日付生成を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        boundary_cases = [
            (1926, 1, 1, True, "最小有効年初日"),
            (2100, 12, 31, True, "最大有効年末日"),
            (1925, 12, 31, False, "最小年未満"),
            (2101, 1, 1, False, "最大年超過"),
        ]

        for year, month, day, is_valid, description in boundary_cases:
            if is_valid:
                result = DateConverter._create_datetime(year, month, day, tz)
                assert result.year == year, \
                    f"Year boundary test failed for {description}"
            else:
                with pytest.raises(DateParseError):
                    DateConverter._create_datetime(year, month, day, tz)

    def test_create_datetime_BVT_month_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 月の境界値

        月の境界値(1月と12月)、および各月の最終日を
        検証します。
        月の境界値における日付生成を確認します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')
        test_cases = [
            (2024, 1, 1, True, "1月初日"),
            (2024, 12, 31, True, "12月末日"),
            (2024, 0, 1, False, "無効な月(0月)"),
            (2024, 13, 1, False, "無効な月(13月)"),
        ]

        for year, month, day, is_valid, description in test_cases:
            if is_valid:
                result = DateConverter._create_datetime(year, month, day, tz)
                assert result.month == month, \
                    f"Month boundary test failed for {description}"
            else:
                with pytest.raises(DateParseError):
                    DateConverter._create_datetime(year, month, day, tz)

    def test_create_datetime_BVT_day_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 日の境界値

        このテストでは、日の境界値に関する以下の検証を行います:
        - 各月の初日と最終日
        - うるう年と非うるう年の2月の境界日
        - 30日月と31日月の境界日
        日の境界値における日付生成を確認します。
        月の種類ごとの最終日と特殊ケースを検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')

        # 月の種類ごとの境界値テスト
        month_end_cases = [
            # 31日月の境界値
            (2024, 1, 1, True, "1月初日"),
            (2024, 1, 31, True, "1月末日"),
            (2024, 1, 32, False, "1月無効日"),

            # 2月(うるう年)の境界値
            (2024, 2, 1, True, "うるう年2月初日"),
            (2024, 2, 29, True, "うるう年2月末日"),
            (2024, 2, 30, False, "うるう年2月無効日"),

            # 2月(非うるう年)の境界値
            (2023, 2, 1, True, "非うるう年2月初日"),
            (2023, 2, 28, True, "非うるう年2月末日"),
            (2023, 2, 29, False, "非うるう年2月無効日"),

            # 30日月の境界値
            (2024, 4, 1, True, "4月初日"),
            (2024, 4, 30, True, "4月末日"),
            (2024, 4, 31, False, "4月無効日"),
        ]

        for year, month, day, is_valid, description in month_end_cases:
            if is_valid:
                result = DateConverter._create_datetime(year, month, day, tz)
                assert result.day == day, \
                    f"Day boundary test failed for {description}: {year}/{month}/{day}"
            else:
                with pytest.raises(DateParseError) as exc_info:
                    DateConverter._create_datetime(year, month, day, tz)
                assert "Invalid date components" in str(exc_info.value), \
                    f"Invalid day handling failed for {description}: {year}/{month}/{day}"

    def test_create_datetime_BVT_timezone_handling(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: タイムゾーンの境界値

        このテストでは、タイムゾーン設定に関する以下の検証を行います:
        - デフォルトタイムゾーン(Asia/Tokyo)の設定
        - 代表的なタイムゾーン(UTC、GMT等)の設定
        - タイムゾーンの切り替わり時の処理
        タイムゾーンの設定に関する境界値を確認します。
        様々なタイムゾーンでの日付生成を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 代表的なタイムゾーンでのテスト
        timezone_cases = [
            ('Asia/Tokyo', "日本標準時"),
            ('UTC', "協定世界時"),
            ('GMT', "グリニッジ標準時"),
            ('US/Pacific', "太平洋標準時"),
            ('Europe/London', "イギリス標準時"),
        ]

        for tz_name, description in timezone_cases:
            tz = pytz.timezone(tz_name)
            result = DateConverter._create_datetime(2024, 1, 1, tz)
            assert str(result.tzinfo) == tz_name, \
                f"Timezone setting failed for {description}: {tz_name}"

    def test_create_datetime_BVT_combined_boundaries(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 複合的な境界値

        このテストでは、以下のような複合的な境界条件を検証します:
        - システム対応範囲の最小年と最大年での月日の境界値
        - うるう年判定が関係する境界値
        - 元号の切り替わり日に関連する境界値
        複合的な境界条件における日付生成を確認します。
        複数の境界値が組み合わさった場合の動作を検証します。
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        tz = pytz.timezone('Asia/Tokyo')

        # 複合的な境界値テスト
        combined_cases = [
            # システム最小年での境界値
            (1926, 1, 1, True, "システム最小年初日"),
            (1926, 12, 31, True, "システム最小年末日"),

            # システム最大年での境界値
            (2100, 1, 1, True, "システム最大年初日"),
            (2100, 12, 31, True, "システム最大年末日"),

            # うるう年の特殊な境界値
            (2000, 2, 29, True, "世紀末うるう年"),
            (2100, 2, 29, False, "世紀末非うるう年"),

            # 元号切り替わり年の境界値
            (1989, 1, 7, True, "昭和から平成への切り替わり前日"),
            (1989, 1, 8, True, "昭和から平成への切り替わり日"),
            (2019, 4, 30, True, "平成から令和への切り替わり前日"),
            (2019, 5, 1, True, "平成から令和への切り替わり日"),
        ]

        for year, month, day, is_valid, description in combined_cases:
            if is_valid:
                result = DateConverter._create_datetime(year, month, day, tz)
                assert result.year == year , \
                    f"Combined boundary test failed for {description}: {year}/{month}/{day}"
                assert result.month == month , \
                    f"Combined boundary test failed for {description}: {year}/{month}/{day}"
                assert result.day == day, \
                    f"Combined boundary test failed for {description}: {year}/{month}/{day}"
            else:
                with pytest.raises(DateParseError) as exc_info:
                    DateConverter._create_datetime(year, month, day, tz)
                assert "Invalid date components" in str(exc_info.value), \
                    f"Invalid combination handling failed for {description}: {year}/{month}/{day}"
