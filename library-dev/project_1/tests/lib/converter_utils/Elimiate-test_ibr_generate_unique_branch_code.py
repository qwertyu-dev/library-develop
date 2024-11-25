import pytest
import pandas as pd
from pathlib import Path
from src.lib.converter_utils.ibr_generate_unique_branch_code import BranchCodeProcessor
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config


package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message

class Test_BranchCodeProcessor_preprocess_branch_code:
    """BranchCodeProcessorの_preprocess_branch_codeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 有効な4桁コードの処理
    │   ├── 有効な5桁コード(7820で始まる)の処理
    │   ├── 有効な5桁コード(7746で始まる)の処理
    │   ├── その他の有効な5桁コードの処理
    │   ├── 空文字列の処理
    │   ├── NaNの処理
    │   └── 無効な長さのコードの処理(ValueError)
    ├── C1: 分岐網羅
    │   ├── 入力値の検証
    │   │   ├── 空文字列を入力
    │   │   └── 非空の有効な文字列を入力
    │   ├── コードの長さチェック
    │   │   ├── 4桁のコードを入力
    │   │   └── 4桁以外のコードを入力
    │   ├── 5桁コードの処理
    │   │   ├── 5桁のコードを入力
    │   │   └── 5桁以外のコードを入力
    │   └── 特殊5桁コードの処理
    │       ├── '7820'で始まる5桁コードを入力
    │       ├── '7746'で始まる5桁コードを入力
    │       └── その他の5桁コードを入力
    └── C2: 条件網羅
        ├── 入力値の検証組み合わせ
        │   ├── NaN値を入力
        │   ├── 空文字列を入力
        │   └── 非空の有効な文字列を入力
        ├── コードの長さの組み合わせ
        │   ├── 4桁のコードを入力
        │   ├── 5桁のコードを入力
        │   └── 4桁でも5桁でもないコードを入力
        └── 特殊5桁コードの組み合わせ
            ├── '7820'で始まる5桁コードを入力
            ├── '7746'で始まる5桁コードを入力
            └── '7820'や'7746'で始まらない5桁コードを入力

    C1のディシジョンテーブル:
    | 条件                            | Case 1 | Case 2 | Case 3 | Case 4 | Case 5 | Case 6 |
    |---------------------------------|--------|--------|--------|--------|--------|--------|
    | 入力が空文字列またはNaN         | Y      | N      | N      | N      | N      | N      |
    | 入力が4桁                       | -      | Y      | N      | N      | N      | N      |
    | 入力が5桁                       | -      | -      | Y      | Y      | Y      | N      |
    | 入力が'7820'で始まる            | -      | -      | Y      | N      | N      | -      |
    | 入力が'7746'で始まる            | -      | -      | N      | Y      | N      | -      |
    | 入力が有効な長さ(4桁または5桁)  | -      | Y      | Y      | Y      | Y      | N      |
    | 出力                            | None   | そのまま | そのまま | そのまま | 先頭4桁 | Error  |
    """

    @pytest.fixture()
    def processor(self):
        return BranchCodeProcessor()

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0テスト
    def test_preprocess_branch_code_C0_valid_4digit(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な4桁コードの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("1234")
        assert result == "1234"

    def test_preprocess_branch_code_C0_valid_5digit_7820(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な5桁コード(7820で始まる)の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("78201")
        assert result == "78201"

    def test_preprocess_branch_code_C0_valid_5digit_7746(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な5桁コード(7746で始まる)の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("77465")
        assert result == "77465"

    def test_preprocess_branch_code_C0_valid_5digit_other(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: その他の有効な5桁コードの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("12345")
        assert result == "1234"

    def test_preprocess_branch_code_C0_empty_string(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 空文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("")
        assert result is None

    def test_preprocess_branch_code_C0_nan(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: NaNの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code(pd.NA)
        assert result is None


    def test_preprocess_branch_code_C0_invalid_length(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 無効な長さのコードの処理(ValueError)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            processor._preprocess_branch_code("123")

    # C1テスト
    def test_preprocess_branch_code_C1_empty_input(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 空文字列を入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("")
        assert result is None

    def test_preprocess_branch_code_C1_valid_input(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 非空の有効な文字列を入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("1234")
        assert result == "1234"

    def test_preprocess_branch_code_C1_4digit_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 4桁のコードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("1234")
        assert result == "1234"

    def test_preprocess_branch_code_C1_non_4digit_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 4桁以外のコードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("12345")
        assert result == "1234"

    def test_preprocess_branch_code_C1_5digit_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 5桁のコードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("12345")
        assert result == "1234"

    def test_preprocess_branch_code_C1_non_5digit_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 5桁以外のコードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            processor._preprocess_branch_code("123456")

    def test_preprocess_branch_code_C1_7820_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: '7820'で始まる5桁コードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("78201")
        assert result == "78201"

    def test_preprocess_branch_code_C1_7746_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: '7746'で始まる5桁コードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("77465")
        assert result == "77465"

    def test_preprocess_branch_code_C1_other_5digit_code(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: その他の5桁コードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code("12345")
        assert result == "1234"

    # C2テスト
    @pytest.mark.parametrize(("input_value", "expected_output"), [
        (pd.NA, None),
        ("", None),
        ("1234", "1234"),
        ("12345", "1234"),
        ("78201", "78201"),
        ("77465", "77465"),
        ("56789", "5678"),
    ])
    def test_preprocess_branch_code_C2_input_variations(self, processor, input_value, expected_output):
        test_doc = f"""テスト内容:
        - テストカテゴリ: C2
        - テスト区分: {'正常系' if expected_output is not None else '異常系'}
        - テストシナリオ: 入力値 '{input_value}' に対する処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = processor._preprocess_branch_code(input_value)
        assert result == expected_output

    def test_preprocess_branch_code_C2_invalid_length(self, processor):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効な長さのコードを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            processor._preprocess_branch_code("123")

        with pytest.raises(ValueError):
            processor._preprocess_branch_code("123456")

class Test_BranchCodeProcessor_generate_unique_branch_code:
    """BranchCodeProcessorのgenerate_unique_branch_codeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 有効なDataFrameの処理
    │   ├── 重複を含むDataFrameの処理
    │   ├── 無効なコードを含むDataFrameの処理
    │   └── 'branch_code'カラムが存在しないDataFrameの処理(ValueError)
    ├── C1: 分岐網羅
    │   ├── 'branch_code'カラムの存在チェック
    │   │   ├── 'branch_code'カラムを含むDataFrameを入力
    │   │   └── 'branch_code'カラムを含まないDataFrameを入力
    │   └── 処理済みコードの有効性チェック
    │       ├── 有効なコードのみを含むDataFrameを入力
    │       └── 無効なコード(None)を含むDataFrameを入力
    └── C2: 条件網羅
        ├── 入力DataFrameの変動
        │   ├── 空のDataFrame
        │   ├── 単一の有効なコードを含むDataFrame
        │   ├── 複数の有効なコードを含むDataFrame
        │   ├── 重複コードを含むDataFrame
        │   └── 無効なコードを含むDataFrame
        └── 特殊コードの処理
            ├── '7820'で始まる5桁コードを含むDataFrame
            ├── '7746'で始まる5桁コードを含むDataFrame
            └── 通常の5桁コードを含むDataFrame

    C1のディシジョンテーブル:
    | 条件                            | Case 1 | Case 2 | Case 3 | Case 4 |
    |---------------------------------|--------|--------|--------|--------|
    | 'branch_code'カラムが存在する   | Y      | N      | Y      | Y      |
    | 全てのコードが有効              | Y      | -      | N      | Y      |
    | 重複コードが存在する            | N      | -      | -      | Y      |
    | 出力                            | 正常   | Error  | 一部除外 | 重複除去 |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # C0テスト
    def test_generate_unique_branch_code_C0_valid_dataframe(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'branch_code': ['1234', '5678', '7820']})
        result = BranchCodeProcessor.generate_unique_branch_code(_df)
        assert len(result) == 3
        assert list(result['processed_branch_code']) == ['1234', '5678', '7820']

    def test_generate_unique_branch_code_C0_duplicates(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 重複を含むDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'branch_code': ['1234', '1234', '5678']})
        result = BranchCodeProcessor.generate_unique_branch_code(_df)
        assert len(result) == 2
        assert list(result['processed_branch_code']) == ['1234', '5678']

    def test_generate_unique_branch_code_C0_invalid_codes(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 無効なコードを含むDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'branch_code': ['1234', '', '5678']})
        result = BranchCodeProcessor.generate_unique_branch_code(_df)
        assert len(result) == 2
        assert list(result['processed_branch_code']) == ['1234', '5678']

    def test_generate_unique_branch_code_C0_missing_column(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 'branch_code'カラムが存在しないDataFrameの処理(ValueError)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'wrong_column': ['1234', '5678']})
        with pytest.raises(ValueError):
            BranchCodeProcessor.generate_unique_branch_code(_df)

    # C1テスト
    def test_generate_unique_branch_code_C1_column_exists(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 'branch_code'カラムを含むDataFrameを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'branch_code': ['1234', '5678']})
        result = BranchCodeProcessor.generate_unique_branch_code(_df)
        assert 'processed_branch_code' in result.columns

    def test_generate_unique_branch_code_C1_column_missing(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 'branch_code'カラムを含まないDataFrameを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'wrong_column': ['1234', '5678']})
        with pytest.raises(ValueError):
            BranchCodeProcessor.generate_unique_branch_code(_df)

    def test_generate_unique_branch_code_C1_valid_codes(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効なコードのみを含むDataFrameを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'branch_code': ['1234', '5678']})
        result = BranchCodeProcessor.generate_unique_branch_code(_df)
        assert len(result) == 2

    def test_generate_unique_branch_code_C1_invalid_codes(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 無効なコード(None)を含むDataFrameを入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'branch_code': ['1234', None, '5678']})
        result = BranchCodeProcessor.generate_unique_branch_code(_df)
        assert len(result) == 2

    # C2テスト
    @pytest.mark.parametrize(("input_df", "expected_codes"), [
        (pd.DataFrame({'branch_code': []}), []),
        (pd.DataFrame({'branch_code': ['1234']}), ['1234']),
        (pd.DataFrame({'branch_code': ['1234', '5678']}), ['1234', '5678']),
        (pd.DataFrame({'branch_code': ['1234', '1234', '5678']}), ['1234', '5678']),
        (pd.DataFrame({'branch_code': ['1234', '', '5678']}), ['1234', '5678']),
        (pd.DataFrame({'branch_code': ['78201', '77465', '12345']}), ['1234', '77465', '78201']),
    ])
    def test_generate_unique_branch_code_C2_variations(self, input_df, expected_codes):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 入力DataFrameの変動と特殊コードの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = BranchCodeProcessor.generate_unique_branch_code(input_df)
        log_msg(f"\n入力 DataFrame:\n{input_df}", LogLevel.INFO)
        log_msg(f"\n結果 DataFrame:\n{result}", LogLevel.INFO)

        assert len(result) == len(expected_codes)
        assert list(result['processed_branch_code']) == expected_codes
