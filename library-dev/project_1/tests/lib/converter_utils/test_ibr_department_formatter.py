import pytest
from pathlib import Path
from src.lib.converter_utils.ibr_department_formatter import format_department_name
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestFormatDepartmentName:
    """format_department_name 関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 個別要件リスト処理
    │   ├── 全体マッチ例外処理
    │   ├── 「〜部(拠点名)」パターン処理
    │   ├── 括弧分割処理
    │   ├── 「部」後のスペース挿入
    │   ├── 特定パターンのスペース調整
    │   ├── 部分マッチ例外処理
    │   └── 前後スペース除去
    ├── C1: 分岐カバレッジ
    │   ├── 個別要件リスト含有/非含有
    │   ├── 全体マッチ例外含有/非含有
    │   ├── 「〜部(拠点名)」パターン一致/不一致
    │   ├── 「部」で終わる/終わらない
    │   └── 部分マッチ例外含有/非含有
    └── C2: 条件組み合わせ
        ├── 個別要件リストのみ該当
        ├── 全体マッチ例外のみ該当
        ├── 「〜部(拠点名)」パターンのみ該当
        ├── 「部」で終わる一般ケース
        ├── 「部」を含むが終わらないケース
        ├── 複数の特定パターン含有
        ├── 部分マッチ例外含有
        ├── 全条件非該当
        ├── 複雑な括弧含有
        └── エッジケース(空文字列)

    C1のディシジョンテーブル:
    | 条件                               | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 |
    |------------------------------------|---------|---------|---------|---------|---------|
    | 個別要件リストに含まれる           | Y       | N       | N       | N       | N       |
    | 全体マッチの例外ケースに含まれる   | -       | Y       | N       | N       | N       |
    | 「〜部(拠点名)」パターンに一致する | -       | -       | Y       | N       | N       |
    | 「部」で終わる                     | -       | -       | -       | Y       | N       |
    | 部分マッチの例外を含む             | -       | -       | -       | -       | Y       |
    | 出力                               | そのまま | そのまま | そのまま | 処理なし | 例外処理 |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0: 基本機能テスト
    def test_individual_requirement_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 個別要件リストに含まれる部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業本部業務部") == "営業本部業務部"

    def test_full_match_exception_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 全体マッチの例外ケースに含まれる部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("本部審議役") == "本部審議役"

    def test_department_with_location_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 「〜部(拠点名)」パターンの部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業部(東京)") == "営業部(東京)"

    def test_department_with_brackets_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 括弧を含む部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("システム部(開発)") == "システム部(開発)"

    def test_department_ending_with_bu_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 「部」で終わる部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業部") == "営業部"

    def test_department_with_specific_patterns_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 特定パターンを含む部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業部部門") == "営業部 部門"

    def test_partial_match_exception_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 部分マッチの例外を含む部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("中部営業所") == "中部営業所"

    def test_department_with_spaces_C0(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 前後にスペースがある部署名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name(" 営業部 ") == "営業部"

    # C1: 分岐カバレッジ
    def test_individual_requirement_true_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 個別要件リストに含まれる部署名(True パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業本部業務部") == "営業本部業務部"

    def test_individual_requirement_false_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 個別要件リストに含まれない部署名(False パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("一般の部") == "一般の部"

    def test_full_match_exception_true_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 全体マッチの例外ケースに含まれる部署名(True パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("本部審議役") == "本部審議役"

    def test_full_match_exception_false_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 全体マッチの例外ケースに含まれない部署名(False パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("一般審議役") == "一般審議役"

    def test_department_with_location_true_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 「〜部(拠点名)」パターンに一致する部署名(True パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業部(東京)") == "営業部(東京)"

    def test_department_with_location_false_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 「〜部(拠点名)」パターンに一致しない部署名(False パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業部東京") == "営業部 東京"

    def test_department_ending_with_bu_true_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 「部」で終わる部署名(True パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業部") == "営業部"

    def test_department_not_ending_with_bu_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 「部」で終わらない部署名(False パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("営業課") == "営業課"

    def test_partial_match_exception_true_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 部分マッチの例外を含む部署名(True パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("中部営業所") == "中部営業所"

    def test_partial_match_exception_false_C1(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 部分マッチの例外を含まない部署名(False パス)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        assert format_department_name("北部営業所") == "北部 営業所"

    # C2: 条件組み合わせ(パラメータ化)
    @pytest.mark.parametrize(("input_name", "expected_output", "scenario"), [
        ("さいたま本部春日部部クレヨン課", "さいたま本部 春日部部 クレヨン課", "複数の例外パターンを含む複雑な部署名"),
        ("営業本部業務部", "営業本部業務部", "個別要件リストに該当する部署名"),
        ("内部監査部業務監査グループ第三ユニット", "内部監査部業務監査グループ第三ユニット", "個別要件リストに該当する長い部署名"),
        ("トランザクション監視部門(東京本部)", "トランザクション監視部門(東京本部)", "括弧付きの部門名"),
        ("aaa本部bbbb部xxxx課", "aaa本部 bbbb部 xxxx課", "一般的な部署名の組み合わせ"),
        ("中部春日部東部西部", "中部春日部東部西部", "複数の部分マッチ例外を含む部署名"),
        ("システム統括部システム企画課", "システム統括部 システム企画課", "複数の「部」を含む部署名"),
        ("法人・リテールリスク統括部部門検査室", "法人・リテールリスク統括部 部門検査室", "特殊文字と「部門」を含む部署名"),
        ("園田寮(69101)人事部·大", "園田寮(69101)人事部·大", "括弧と特殊文字を含む部署名"),
        ("天満研修所(69101)人事部·大", "天満研修所(69101)人事部·大", "括弧と特殊文字を含む部署名(研修所)"),
        ("浜甲子園寮(69101)人事部·大", "浜甲子園寮(69101)人事部·大", "括弧と特殊文字を含む部署名(寮)"),
        ("茨木西寮(69101)人事部·大", "茨木西寮(69101)人事部·大", "括弧と特殊文字を含む部署名(西寮)"),
        ("京町堀5(69101)人事部·大", "京町堀5(69101)人事部·大", "数字、括弧、特殊文字を含む部署名"),
        ("総務部総務課", "総務部 総務課", "一般的な部署名"),
        ("本部審議役", "本部審議役", "全体マッチの例外ケースに該当する部署名"),
        ("トランザクション監視部門(天津)", "トランザクション監視部門(天津)", "括弧付きの海外部門名"),
        ("部門検査室", "部門検査室", "「部門」で始まる部署名"),
        ("部門検査室(大阪)", "部門検査室(大阪)", "「部門」で始まり括弧付きの部署名"),
        ("〜部(拠点名)", "〜部(拠点名)", "特殊文字を含む部署名"),
        ("テスト部部テスト課", "テスト部部 テスト課", "「部」が連続する部署名"),
        ("テスト部門", "テスト部門", "「部門」で終わる部署名"),
        ("リテールリスク統括部部門管理部", "リテールリスク統括部 部門管理部", "「部」と「部門」を含む複雑な部署名"),
        ("営業本部ナゴヤ営業第一本部", "営業本部 ナゴヤ営業第一本部", "途中に「部」があり最後に「部」を含む部署名"),
        ("営業本部ナゴヤ営業第一本部第一Gr","営業本部 ナゴヤ営業第一本部 第一Gr", "ナゴヤ部署かつ最後が部で終わらない部署名"),
        ("", "", "空文字列(エッジケース)"),
    ])
    def test_format_department_name_C2(self, input_name, expected_output, scenario):
        test_doc = f"""テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: {scenario}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        log_msg(f"\nテスト: 入力: {input_name}, 期待出力: {expected_output}, シナリオ: {scenario}", LogLevel.INFO)
        assert format_department_name(input_name) == expected_output
