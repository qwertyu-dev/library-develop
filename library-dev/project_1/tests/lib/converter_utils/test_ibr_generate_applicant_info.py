import pytest
from pathlib import Path
from src.lib.converter_utils.ibr_generate_applicant_info import generate_applicant_info
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestGenerateApplicantInfo:
    """generate_applicant_info関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 各申請者タイプのファイル名でのテスト
    │   └── 異常系: 不正な入力でのテスト
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: ファイルパスの指定と各キーワードの確認
    │   └── 異常系: ファイルパス未指定と不正なファイル名
    └── C2: 条件組み合わせ
        ├── 正常系: 大文字小文字や括弧の有無の組み合わせ
        └── 異常系: 特殊なファイルパスと部分一致ケース

    # C1のディシジョンテーブル
    | 条件                   | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 | ケース6 | ケース7 |
    |------------------------|--------|--------|--------|--------|--------|--------|--------|
    | ファイルパスが指定されている | Y      | N      | Y      | Y      | Y      | Y      | Y      |
    | "人事"を含む           | Y      | -      | N      | N      | N      | N      | N      |
    | "国企"を含む           | N      | -      | Y      | N      | N      | N      | N      |
    | "関連(ダミー課あり)"を含む | N      | -      | N      | Y      | N      | N      | N      |
    | "関連(ダミー課なし)"を含む | N      | -      | N      | N      | Y      | N      | N      |
    | 不正なキーワード        | N      | -      | N      | N      | N      | N      | Y      |
    | 出力                   | 1      | Error  | 2      | 3      | 4      | Error  | Error  |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.mark.parametrize(("file_name", "expected"), [
        ("人事_申請データ.xlsx", 1),
        ("国企_申請データ.xlsx", 2),
        ("関連(ダミー課あり)_申請データ.xlsx", 3),
        ("関連(ダミー課なし)_申請データ.xlsx", 4),
    ])
    def test_generate_applicant_info_C0_valid_input(self, file_name, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_applicant_info(file_name)
        assert result == expected
        log_msg(f"Result: {result}", LogLevel.DEBUG)

    def test_generate_applicant_info_C0_empty_input(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 空の入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            generate_applicant_info("")
        log_msg("ValueError raised as expected", LogLevel.DEBUG)

    def test_generate_applicant_info_C0_invalid_input(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 不正な入力でのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            generate_applicant_info("invalid_file_name.xlsx")
        log_msg("ValueError raised as expected", LogLevel.DEBUG)

    @pytest.mark.parametrize(("file_name","expected"), [
        ("人事_申請データ.xlsx", 1),
        ("国企_申請データ.xlsx", 2),
        ("関連(ダミー課あり)_申請データ.xlsx", 3),
        ("関連(ダミー課なし)_申請データ.xlsx", 4),
    ])
    def test_generate_applicant_info_C1_valid_input(self, file_name, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効な入力での分岐テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_applicant_info(file_name)
        assert result == expected
        log_msg(f"Result: {result}", LogLevel.DEBUG)

    def test_generate_applicant_info_C1_no_input(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 入力なしでの分岐テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            generate_applicant_info(None)
        log_msg("ValueError raised as expected", LogLevel.DEBUG)

    def test_generate_applicant_info_C1_invalid_input(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 不正な入力での分岐テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            generate_applicant_info("invalid_file_name.xlsx")
        log_msg("ValueError raised as expected", LogLevel.DEBUG)

    @pytest.mark.parametrize(("file_name","expected"), [
        ("人事_申請データ.xlsx", 1),
        ("JINJI_申請データ.xlsx", 1),
        ("国企_申請データ.xlsx", 2),
        ("KOKUKI_申請データ.xlsx", 2),
        ("関連(ダミー課あり)_申請データ.xlsx", 3),
        ("関連(ダミー課なし)_申請データ.xlsx", 4),
        ("関連(ダミー課ありxx)_申請データ.xlsx", 3),
        ("関連(ダミー課なしxx)_申請データ.xlsx", 4),
    ])
    def test_generate_applicant_info_C2_case_and_bracket(self, file_name, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 大文字小文字と括弧の組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        applicant_types = {
            "人事": 1,
            "国企": 2,
            "関連(ダミー課あり)": 3,
            "関連(ダミー課なし)": 4,
        }

        #if not any(key in file_name.lower() for key in applicant_types.keys()):
        if not any(key in file_name.lower() for key in applicant_types):
            with pytest.raises(ValueError) as exc_info:
                generate_applicant_info(file_name)
            error_message = str(exc_info.value)
            log_msg(f"ValueError raised: {error_message}", LogLevel.ERROR)
            assert "不正なファイル名パターン" in error_message
        else:
            result = generate_applicant_info(file_name)
            assert result == expected
            log_msg(f"Result: {result}", LogLevel.DEBUG)


    def test_generate_applicant_info_C2_multiple_keywords(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 複数キーワードを含むファイル名のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_applicant_info("人事_国企_関連_申請データ.xlsx")
        assert result == 1  # 最初に一致した"人事"が優先される
        log_msg(f"Result: {result}", LogLevel.DEBUG)

    @pytest.mark.parametrize("file_name", [
        "jinjidata.xlsx",
        "kokudata.xlsx",
        "kanrenmata.xlsx",
    ])
    def test_generate_applicant_info_C2_partial_match(self, file_name):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: キーワードの部分一致テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            generate_applicant_info(file_name)
        log_msg("ValueError raised as expected", LogLevel.DEBUG)

    @pytest.mark.parametrize("file_path", [
        Path("人事_申請データ.xlsx"),
        "C:\\Users\\申請者\\Documents\\人事_申請データ.xlsx",
        "/home/applicant/人事_申請データ.xlsx",
    ])
    def test_generate_applicant_info_C2_path_types(self, file_path):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 異なる形式のファイルパスのテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_applicant_info(file_path)
        assert result == 1
        log_msg(f"Result: {result}", LogLevel.DEBUG)
