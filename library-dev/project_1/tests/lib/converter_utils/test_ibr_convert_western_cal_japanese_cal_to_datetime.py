import pytest
from datetime import datetime
import pytz
from pathlib import Path

from src.lib.converter_utils.ibr_convert_western_cal_japanese_cal_to_datetime import Era, DateParseError
from src.lib.converter_utils.ibr_convert_western_cal_japanese_cal_to_datetime import DateFormat, DateConstants, determine_date_format
from src.lib.converter_utils.ibr_convert_western_cal_japanese_cal_to_datetime import parse_str_to_datetime

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

# Tokyo/Azia timezone
jst = pytz.timezone('Asia/Tokyo')

class TestEraEnum:
    """Era Enumのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 各元号(REIWA, HEISEI, SHOWA)の属性(name, code, start_year, max_year)の正確性確認
    ├── C1: from_code メソッドのテスト
    │   ├── 正常系: 有効なコードでの Era オブジェクト取得
    │   └── 異常系: 無効なコードでの ValueError 発生
    └── C2: convert_japanese_year_to_western メソッドのテスト
        ├── 正常系: 各元号の様々な年での変換
        └── 異常系: 無効な元号コードや和暦年での ValueError 発生

    | 条件                   | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 |
    |------------------------|---------|---------|---------|---------|---------|
    | 元号コードが有効       | Y       | Y       | Y       | N       | Y       |
    | 和暦年が有効           | Y       | Y       | N       | -       | Y       |
    | 和暦年が最大年以下     | Y       | N       | -       | -       | Y       |
    | 現在進行中の元号       | N       | -       | -       | -       | Y       |
    | 出力                   | 正常    | エラー  | エラー  | エラー  | 正常    |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.jst = pytz.timezone('Asia/Tokyo')

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_era_attributes_C0_basic(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 各元号の属性(name, code, start_year, max_year)の正確性確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert Era.REIWA.value.name == "令和" and Era.REIWA.value.code == 5 and Era.REIWA.value.start_year == 2019 and Era.REIWA.value.max_year is None
        assert Era.HEISEI.value.name == "平成" and Era.HEISEI.value.code == 4 and Era.HEISEI.value.start_year == 1989 and Era.HEISEI.value.max_year == 31
        assert Era.SHOWA.value.name == "昭和" and Era.SHOWA.value.code == 3 and Era.SHOWA.value.start_year == 1926 and Era.SHOWA.value.max_year == 64

    @pytest.mark.parametrize(("code", "expected_era"), [
        (5, Era.REIWA),
        (4, Era.HEISEI),
        (3, Era.SHOWA),
    ])
    def test_from_code_C1_valid(self, code, expected_era):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効なコードでの Era オブジェクト取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert Era.from_code(code) == expected_era

    def test_from_code_C1_invalid(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効なコードでの ValueError 発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            Era.from_code(99)

    @pytest.mark.parametrize(("era_code", "era_year", "expected_western_year"), [
        (5, 1, 2019),  # 令和元年
        (5, 5, 2023),  # 令和5年
        (4, 1, 1989),  # 平成元年
        (4, 31, 2019),  # 平成31年(最大年)
        (3, 1, 1926),  # 昭和元年
        (3, 64, 1989),  # 昭和64年(最大年)
    ])
    def test_convert_japanese_year_to_western_C2_valid(self, era_code, era_year, expected_western_year):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 各元号の様々な年での変換
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert Era.convert_japanese_year_to_western(era_code, era_year) == expected_western_year

    def test_convert_japanese_year_to_western_C2_invalid(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効な元号コードや和暦年での ValueError 発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 無効な元号コード
        with pytest.raises(ValueError, match="Invalid era code"):
            Era.convert_japanese_year_to_western(99, 1)

        # 無効な和暦年(0年)
        with pytest.raises(ValueError, match="Era year must be positive"):
            Era.convert_japanese_year_to_western(5, 0)

        # 無効な和暦年(負の年)
        with pytest.raises(ValueError, match="Era year must be positive"):
            Era.convert_japanese_year_to_western(5, -1)

        # 最大年を超える和暦年(平成の場合)
        with pytest.raises(ValueError, match="Maximum year for 平成 is 31"):
            Era.convert_japanese_year_to_western(4, 32)

        # 現在進行中の元号(令和)の場合の来年以降の年
        current_year = datetime.now().year
        max_allowed_reiwa_year = current_year - 2019 + 3  # 超過設定
        with pytest.raises(ValueError, match="Maximum allowed year for 令和"):
            Era.convert_japanese_year_to_western(5, max_allowed_reiwa_year + 1)

    def test_convert_japanese_year_to_western_C2_current_era(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 現在進行中の元号(令和)の来年までの変換
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        current_year = datetime.now().year
        next_year = current_year + 1
        current_reiwa_year = current_year - 2019 + 1
        next_reiwa_year = next_year - 2019 + 1

        # 今年の変換
        assert Era.convert_japanese_year_to_western(5, current_reiwa_year) == current_year

        # 来年の変換
        assert Era.convert_japanese_year_to_western(5, next_reiwa_year) == next_year


class TestDetermineDateFormat:
    """determine_date_format 関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 西暦形式の判定
    │   ├── 和暦形式の判定
    │   └── 不明な形式の判定
    ├── C1: 境界値テスト
    │   ├── 最小有効西暦(1000/01/01)
    │   ├── 最大有効西暦(9999/12/31)
    │   ├── 最小有効和暦(3000101)
    │   └── 最大有効和暦(5991231)
    └── C2: 異常系テスト
        ├── 無効な区切り文字を含む西暦形式
        ├── 文字を含む和暦形式
        ├── 長さが不正な日付文字列
        └── None や非文字列の入力

    | 条件                     | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 | ケース6 |
    |--------------------------|---------|---------|---------|---------|---------|---------|
    | 入力が文字列             | Y       | Y       | Y       | Y       | Y       | N       |
    | 文字列長が正しい         | Y       | Y       | N       | Y       | Y       | -       |
    | 区切り文字が正しい       | Y       | -       | -       | N       | -       | -       |
    | 数字のみで構成           | -       | Y       | -       | -       | N       | -       |
    | 出力                     | WESTERN | JAPANESE| UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.mark.parametrize(("date_string", "expected_format"), [
        ("2023/08/11", DateFormat.WESTERN),
        ("5050811", DateFormat.JAPANESE),
        ("2023-08-11", DateFormat.UNKNOWN),
    ])
    def test_determine_date_format_C0_basic(self, date_string, expected_format):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 基本的な日付形式の判定
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = determine_date_format(date_string)
        assert result == expected_format, f"Expected {expected_format}, but got {result} for {date_string}"

    @pytest.mark.parametrize(("date_string", "expected_format"), [
        ("1000/01/01", DateFormat.WESTERN),
        ("9999/12/31", DateFormat.WESTERN),
        ("3000101", DateFormat.JAPANESE),
        ("5991231", DateFormat.JAPANESE),
    ])
    def test_determine_date_format_C1_boundary(self, date_string, expected_format):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 境界値
        - テストシナリオ: 日付形式の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = determine_date_format(date_string)
        assert result == expected_format, f"Expected {expected_format}, but got {result} for {date_string}"

    @pytest.mark.parametrize(("date_string", "expected_format"), [
        ("2023.08.11", DateFormat.UNKNOWN),
        ("505081a", DateFormat.UNKNOWN),
        ("2023/8/11", DateFormat.UNKNOWN),
        ("50508111", DateFormat.UNKNOWN),
        (None, DateFormat.UNKNOWN),
        (12345, DateFormat.UNKNOWN),
        ("", DateFormat.UNKNOWN),
    ])
    def test_determine_date_format_C2_invalid(self, date_string, expected_format):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効な日付形式の判定
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = determine_date_format(date_string)
        assert result == expected_format, f"Expected {expected_format}, but got {result} for {date_string}"

    def test_determine_date_format_C2_edge_cases(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: エッジケース
        - テストシナリオ: 特殊な入力値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 極端に長い文字列
        long_string = "2" * 100
        assert determine_date_format(long_string) == DateFormat.UNKNOWN

        # オブジェクト
        assert determine_date_format(object()) == DateFormat.UNKNOWN

        # リスト
        assert determine_date_format([]) == DateFormat.UNKNOWN

    def test_determine_date_format_C2_performance(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: パフォーマンス
        - テストシナリオ: 大量の入力に対する処理時間の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        import time

        start_time = time.time()
        for _ in range(10000):
            determine_date_format("2023/08/11")
            determine_date_format("5050811")
            determine_date_format("invalid_date")
        end_time = time.time()

        execution_time = end_time - start_time
        log_msg(f"Execution time for 30000 calls: {execution_time:.2f} seconds", LogLevel.INFO)

        # 処理時間が1秒未満であることを確認(この閾値は環境に応じて調整可能)
        assert execution_time < 1, f"Performance test failed. Execution time: {execution_time:.2f} seconds"

class TestParseStrToDatetime:
    """parse_str_to_datetime 関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 西暦形式の変換
    │   ├── 和暦形式の変換
    │   └── タイムゾーンの確認 (Asia/Tokyo)
    ├── C1: 境界値テスト
    │   ├── 西暦の最小値と最大値
    │   ├── 和暦の最小値と最大値
    │   └── 各元号の境界日付
    └── C2: 異常系テスト
        ├── 無効な西暦日付
        ├── 無効な和暦日付
        ├── 存在しない元号コード
        └── 完全に無効な形式の日付文字列

    | 条件                   | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 |
    |------------------------|---------|---------|---------|---------|---------|
    | 入力が有効な形式       | Y       | Y       | N       | N       | N       |
    | 西暦形式               | Y       | N       | Y       | N       | -       |
    | 和暦形式               | N       | Y       | N       | Y       | -       |
    | 日付が実在する         | Y       | Y       | N       | N       | -       |
    | 出力                   | 正常    | 正常    | エラー  | エラー  | エラー  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.jst = pytz.timezone('Asia/Tokyo')

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.mark.parametrize(("date_string", "expected_date"), [
        ("2023/08/11", datetime(2023, 8, 11)),
        ("5050811", datetime(2023, 8, 11)),
    ])
    def test_parse_str_to_datetime_C0_basic(self, date_string, expected_date):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 基本的な日付形式の変換
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = parse_str_to_datetime(date_string)
        expected_date = self.jst.localize(expected_date)
        assert result == expected_date, f"Expected {expected_date}, but got {result} for {date_string}"
        assert str(result.tzinfo) == str(self.jst), f"Expected timezone {self.jst}, but got {result.tzinfo}"

    @pytest.mark.parametrize(("date_string", "expected_date"), [
        ("1000/01/01", datetime(1000, 1, 1)),
        ("9999/12/30", datetime(9999, 12, 30)),
        ("3000101", datetime(1926, 1, 1)),  # 昭和元年 本来は昭和01年01月01日の認識
        ("3010101", datetime(1926, 1, 1)),  # 昭和1年 本来は昭和01年01月01日の認識
        ("3020101", datetime(1927, 1, 1)),  # 昭和2年 昭和02年01月01日での認識
        ("4000101", datetime(1989, 1, 1)),  # 平成元年
        ("4010101", datetime(1989, 1, 1)),  # 平成1年
        ("5000101", datetime(2019, 1, 1)),  # 令和元年
        ("5010101", datetime(2019, 1, 1)),  # 令和1年
        ("5060101", datetime(2024, 1, 1)),  # 令和6年 2024年
#        ("5991231", datetime(2047, 12, 31)),  # 令和29年(仮定)
        (pytest.param("5991231", None, marks=pytest.mark.xfail(raises=DateParseError))),  # 令和99年(エラーを期待)
    ])
    def test_parse_str_to_datetime_C1_boundary(self, date_string, expected_date):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 境界値
        - テストシナリオ: 日付形式の境界値テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = parse_str_to_datetime(date_string)
        expected_date = self.jst.localize(expected_date)
        assert result == expected_date, f"Expected {expected_date}, but got {result} for {date_string}"
        assert str(result.tzinfo) == str(self.jst), f"Expected timezone {self.jst}, but got {result.tzinfo}"


    def test_parse_str_to_datetime_C1_max_date(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 境界値
        - テストシナリオ: 最大日付のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        max_date_string = "9999/12/31"

        # OverflowError または DateParseError が発生することを期待
        with pytest.raises((OverflowError, DateParseError)) as excinfo:
            parse_str_to_datetime(max_date_string)

        log_msg(f"Expected error occurred: {str(excinfo.value)}", LogLevel.INFO)

        # 9999/12/30 のテストを追加(これは必ず成功するはず)
        near_max_date_string = "9999/12/30"
        result = parse_str_to_datetime(near_max_date_string)
        expected_near_max_date = self.jst.localize(datetime(9999, 12, 30))
        assert result == expected_near_max_date, f"Expected {expected_near_max_date}, but got {result} for {near_max_date_string}"
        assert str(result.tzinfo) == str(self.jst), f"Expected timezone {self.jst}, but got {result.tzinfo}"

    def test_parse_str_to_datetime_C1_era_boundaries(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 境界値
        - テストシナリオ: 元号の境界日付テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 昭和から平成への変更
        assert parse_str_to_datetime("3640107") == self.jst.localize(datetime(1989, 1, 7))
        assert parse_str_to_datetime("4010108") == self.jst.localize(datetime(1989, 1, 8))

        # 平成から令和への変更
        assert parse_str_to_datetime("4310430") == self.jst.localize(datetime(2019, 4, 30))
        assert parse_str_to_datetime("5010501") == self.jst.localize(datetime(2019, 5, 1))

    @pytest.mark.parametrize(("date_string", "error_patterns"), [
        ("2023/02/29", ["無効な西暦日付"]),
        ("5130230", ["無効な和暦年", "Maximum allowed year"]),
        ("6010101", ["無効な和暦年", "Invalid era code"]),
        ("invalid_date", ["無効な日付形式"]),
        (None, ["無効な日付形式"]),
        (12345, ["無効な日付形式"]),
    ])
    def test_parse_str_to_datetime_C2_invalid(self, date_string, error_patterns):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効な日付形式の処理

        - エラーMSGいずれかが含まれていれば合致の判断をしています
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(DateParseError) as excinfo:
            parse_str_to_datetime(date_string)

        error_message = str(excinfo.value)
        log_msg(f"Received error message: {error_message}", LogLevel.INFO)

        assert any(pattern in error_message for pattern in error_patterns), \
            f"Expected error message containing any of {error_patterns}, but got '{error_message}'"

    def test_parse_str_to_datetime_C2_performance(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: パフォーマンス
        - テストシナリオ: 大量の入力に対する処理時間の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        import time

        start_time = time.time()
        for _ in range(1000):
            parse_str_to_datetime("2023/08/11")
            parse_str_to_datetime("5050811")
        end_time = time.time()

        execution_time = end_time - start_time
        log_msg(f"Execution time for 2000 calls: {execution_time:.2f} seconds", LogLevel.INFO)

        # 処理時間が1秒未満であることを確認(この閾値は環境に応じて調整可能)
        assert execution_time < 1, f"Performance test failed. Execution time: {execution_time:.2f} seconds"
