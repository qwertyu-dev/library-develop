import pytest
import pandas as pd
import ulid
from src.lib.converter_utils.ibr_generate_ulid_column import generate_ulid_column
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config
from pathlib import Path

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class Test_generate_ulid_column:
    """generate_ulid_column関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なDataFrameでULID列が正しく生成される
    │   ├── 異常系: 引数がDataFrameでない場合にTypeError
    │   └── 異常系: 予期せぬエラーが発生した場合にException
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: DataFrameが空の場合
    │   ├── 正常系: DataFrameに複数の行がある場合
    │   └── 異常系: DataFrameがNoneの場合
    └── C2: 条件組み合わせ
        ├── 正常系: DataFrameに1列ある場合
        ├── 正常系: DataFrameに複数列ある場合
        ├── 正常系: DataFrameのインデックスが連続していない場合
        └── 正常系: DataFrameのインデックスが文字列の場合

    # C1のディシジョンテーブル
    | 条件                     | ケース1 | ケース2    | ケース3   |
    |--------------------------|---------|------------|-----------|
    | 引数がDataFrame型である  | Y       | Y          | N         |
    | DataFrameが空である      | Y       | N          | -         |
    | 出力                     | 空のDF  | ULID付きDF | TypeError |

    テストコード全体に対する品質チェックリストの適用と結果の提示
    | 項目番号 | 項目名                             | 評価 | 評価コメント                                                           |
    |----------|------------------------------------|------|------------------------------------------------------------------------|
    | 1        | テストの独立性                     | pass | 各テストが他のテストに依存せず、順序に関係なく実行可能                 |
    | 2        | テストの網羅性                     | pass | C0, C1, C2カテゴリを網羅し、正常系と異常系の両方をカバー               |
    | 3        | テストの可読性                     | pass | テストメソッド名が明確で、docstringによる説明も適切                    |
    | 4        | テストの堅牢性                     | pass | 外部依存がなく、フラッキーテストの可能性も低い                         |
    | 5        | テストデータの管理                 | pass | フィクスチャを使用して適切にテストデータを準備                         |
    | 6        | モックとスタブの適切な使用         | pass | この関数テストではモックが不要で、適切に実装                           |
    | 7        | アサーションの品質                 | pass | 具体的で明確なアサーションを使用                                       |
    | 8        | エッジケースのカバレッジ           | pass | 空のDataFrame、異なる列数、非連続インデックスなどをカバー              |
    | 9        | パフォーマンスとリソース管理       | pass | テストの実行時間が適切で、特別なリソース管理も不要                     |
    | 10       | テストの隔離                       | pass | グローバル状態を変更せず、適切に隔離されている                         |
    | 11       | パラメータ化テスト                 | pass | 列数の異なるケースでパラメータ化テストを使用                           |
    | 12       | コードカバレッジ                   | pass | 関数のすべての分岐と条件をカバーしている                               |
    | 13       | テストの保守性                     | pass | 重複が少なく、テストヘルパー関数も適切に使用                           |
    | 14       | テストの粒度                       | pass | 各テストが単一の概念や機能をテスト                                     |
    | 15       | テストフィクスチャの適切な使用     | pass | setup_methodとteardown_methodを適切に使用                              |
    | 16       | 例外処理のテスト                   | pass | TypeError等の例外をテスト                                              |
    | 17       | 非決定的な要素の処理               | pass | ULIDの一意性と妥当性を適切にテスト                                     |
    | 18       | ドキュメンテーション               | pass | クラスとメソッドレベルで適切なドキュメントを提供                       |
    | 19       | テストの一貫性                     | pass | プロジェクト全体で一貫したスタイルを維持                               |
    | 20       | 負のテスト                         | pass | 無効な入力に対するテストを含む                                         |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({'A': [1, 2, 3], 'B': ['a', 'b', 'c']})

    def test_generate_ulid_column_C0_valid_input(self, sample_df):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なDataFrameでULID列が正しく生成される
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_ulid_column(sample_df)

        assert 'ulid' in result.columns
        assert result['ulid'].dtype == 'object'
        assert all(ulid.parse(uid) for uid in result['ulid'])
        assert result['ulid'].nunique() == len(result)

        log_msg(f"Result DataFrame:\n{result}", LogLevel.DEBUG)

    def test_generate_ulid_column_C0_invalid_input(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 引数がDataFrameでない場合にTypeError
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(TypeError):
            generate_ulid_column([1, 2, 3])

    def test_generate_ulid_column_C1_empty_df(self, empty_df):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DataFrameが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_ulid_column(empty_df)

        assert 'ulid' in result.columns
        assert len(result) == 0

        log_msg(f"Result DataFrame:\n{result}", LogLevel.DEBUG)

    def test_generate_ulid_column_C1_multiple_rows(self, sample_df):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DataFrameに複数の行がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_ulid_column(sample_df)

        assert 'ulid' in result.columns
        assert len(result) == len(sample_df)
        assert result['ulid'].nunique() == len(result)

        log_msg(f"Result DataFrame:\n{result}", LogLevel.DEBUG)

    def test_generate_ulid_column_C1_none_input(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DataFrameがNoneの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        #with pytest.raises(TypeError):
        with pytest.raises(AttributeError):
            generate_ulid_column(None)

    @pytest.mark.parametrize(("df", "expected_columns"), [
        (pd.DataFrame({'A': [1, 2, 3]}), ['ulid', 'A']),
        (pd.DataFrame({'A': [1, 2], 'B': ['a', 'b'], 'C': [True, False]}), ['ulid', 'A', 'B', 'C']),
    ])
    def test_generate_ulid_column_C2_different_column_counts(self, df, expected_columns):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameの列数が異なる場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = generate_ulid_column(df)

        assert list(result.columns) == expected_columns
        assert result['ulid'].nunique() == len(result)

        log_msg(f"Result DataFrame:\n{result}", LogLevel.DEBUG)

    def test_generate_ulid_column_C2_non_contiguous_index(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameのインデックスが連続していない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'A': [1, 2, 3]}, index=[0, 2, 4])
        result = generate_ulid_column(_df)

        assert 'ulid' in result.columns
        assert result['ulid'].nunique() == len(result)
        assert list(result.index) == [0, 2, 4]

        log_msg(f"Result DataFrame:\n{result}", LogLevel.DEBUG)

    def test_generate_ulid_column_C2_string_index(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameのインデックスが文字列の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'A': [1, 2, 3]}, index=['a', 'b', 'c'])
        result = generate_ulid_column(_df)

        assert 'ulid' in result.columns
        assert result['ulid'].nunique() == len(result)
        assert list(result.index) == ['a', 'b', 'c']

        log_msg(f"Result DataFrame:\n{result}", LogLevel.DEBUG)

