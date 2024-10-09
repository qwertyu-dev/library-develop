# config共有
import sys
import re
from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_helper import format_dict

#from src.lib.validator_utils.ibr_decision_table_validator import DT
#from src.model.facade.base_facade import DataFrameEditor
from src.model.factory.condition_evaluator import ConditionEvaluator

#from src.model.factory.editor_factory import EditorFactory

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestConditionEvaluatorInit:
    """ConditionEvaluatorの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── dt_functionsの初期化確認
    ├── C1: 分岐カバレッジ
    │   └── DT クラスに適切なメソッドがある場合とない場合
    ├── C2: 条件網羅
    │   └── DT クラスの様々なメソッド組み合わせ
    └── BVT: 境界値テスト
        └── DT クラスにメソッドがない極端なケース

    C1のディシジョンテーブル:
    | 条件                           | ケース1 | ケース2 |
    |--------------------------------|---------|---------|
    | DT クラスにメソッドが存在する  | Y       | N       |
    | 出力                           | 正常初期化| 空の辞書 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値               | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------|----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | DT クラス       | メソッドなし          | 空の辞書       | DTクラスにメソッドがない場合の処理  | 実装済み | test_init_BVT_no_methods          |
    | BVT_002  | DT クラス       | 1つのメソッドのみ     | 1要素の辞書    | 最小限のメソッド数での初期化        | 実装済み | test_init_BVT_single_method       |
    | BVT_003  | DT クラス       | 多数のメソッド(100個) | 100要素の辞書  | 大量のメソッドがある場合の処理      | 実装済み | test_init_BVT_many_methods        |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、__init__メソッドの動作が様々な条件下で正しく機能することを確認しています。
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        config = MagicMock()
        config.log_message = MagicMock()
        return config

    #def test_init_C0_basic_functionality(self, mock_config):
    def test_init_C0_basic_functionality(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: dt_functionsの初期化確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator = ConditionEvaluator()

        assert hasattr(evaluator, 'dt_functions')
        assert isinstance(evaluator.dt_functions, dict)
        assert all(callable(func) for func in evaluator.dt_functions.values())

    def test_init_C1_with_methods(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DT クラスに少なくとも1つのメソッドがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator = ConditionEvaluator()

        assert len(evaluator.dt_functions) > 0
        assert all(callable(func) for func in evaluator.dt_functions.values())


    def test_init_C1_without_methods(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DT クラスに適切なメソッドがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class EmptyDT:
            pass

        with patch('src.model.factory.condition_evaluator.DT', EmptyDT):
            evaluator = ConditionEvaluator()
            assert len(evaluator.dt_functions) == 0


    def test_init_C2_various_method_combinations(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DT クラスの様々なメソッド組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # DTクラスのモックを作成
        class MockDT:
            @staticmethod
            def method1(x: str) -> str:
                return x

            @staticmethod
            def method2(x: str) -> str:
                return x

            @staticmethod
            def __private_method(x: str) -> str:
                return x

        with patch('src.model.factory.condition_evaluator.DT', MockDT):
            evaluator = ConditionEvaluator()

            log_msg(f"\n{format_dict(evaluator.dt_functions)}", LogLevel)

            assert 'method1' in evaluator.dt_functions
            assert 'method2' in evaluator.dt_functions
            assert '_MockDT__private_method' in evaluator.dt_functions
            assert len(evaluator.dt_functions) == 3  # noqa:PLR2004

        # 追加の検証
        assert all(callable(func) for func in evaluator.dt_functions.values())

        # マングリングされたメソッド名の確認
        mangled_methods = [name for name in evaluator.dt_functions if name.startswith('_MockDT')]
        assert len(mangled_methods) == 1
        assert mangled_methods[0] == '_MockDT__private_method'

        # メソッドの動作検証 オプション
        assert evaluator.dt_functions['method1'](5) == 5                   # noqa:PLR2004
        assert evaluator.dt_functions['method2'](10) == 10                 # noqa:PLR2004
        assert evaluator.dt_functions['_MockDT__private_method'](15) == 15 # noqa:PLR2004

    def test_init_BVT_no_methods(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: DT クラスにメソッドがない極端なケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class EmptyDT:
            pass

        with patch('src.model.factory.condition_evaluator.DT', EmptyDT):
            evaluator = ConditionEvaluator()
            log_msg(f"dt_functions content: {format_dict(evaluator.dt_functions)}", LogLevel.INFO)
            assert len(evaluator.dt_functions) == 0

    def test_init_BVT_single_method(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: DT クラスに1つのメソッドのみある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class SingleMethodDT:
            @staticmethod
            def single_method(x: str) -> str:
                return x

        with patch('src.model.factory.condition_evaluator.DT', SingleMethodDT):
            evaluator = ConditionEvaluator()
            log_msg(f"dt_functions content: {format_dict(evaluator.dt_functions)}", LogLevel.INFO)
            assert len(evaluator.dt_functions) == 1
            assert 'single_method' in evaluator.dt_functions
            assert callable(evaluator.dt_functions['single_method'])

    def test_init_BVT_many_methods(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: DT クラスに多数のメソッド(100個)がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class ManyMethodsDT:
            pass

        for i in range(100):
            setattr(ManyMethodsDT, f'method_{i}', staticmethod(lambda x: x))

        with patch('src.model.factory.condition_evaluator.DT', ManyMethodsDT):
            evaluator = ConditionEvaluator()
            log_msg(f"dt_functions content: {format_dict(evaluator.dt_functions)}", LogLevel.INFO)
            assert len(evaluator.dt_functions) == 100 # noqa:PLR2004
            for i in range(100):
                assert f'method_{i}' in evaluator.dt_functions
                assert callable(evaluator.dt_functions[f'method_{i}'])


class TestConditionEvaluatorEvaluateConditions:
    """ConditionEvaluatorのevaluate_conditions関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 全ての条件が一致する場合
    │   └── 一致する条件がない場合
    ├── C1: 分岐カバレッジ
    │   ├── 決定テーブルが空の場合
    │   ├── 入力行が空の場合
    │   └── 部分的に条件が一致する場合
    ├── C2: 条件網羅
    │   ├── 異なる型の条件組み合わせ
    │   └── 複数の一致可能な条件がある場合
    └── BVT: 境界値テスト
        ├── 決定テーブルが1行のみの場合
        └── 非常に大きな決定テーブルの場合

    C1のディシジョンテーブル:
    | 条件                     | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 |
    |--------------------------|---------|---------|---------|---------|---------|
    | 決定テーブルが空         | Y       | N       | N       | N       | N       |
    | 入力行が空               | -       | Y       | N       | N       | N       |
    | 全ての条件が一致         | -       | -       | Y       | N       | N       |
    | 部分的に条件が一致       | -       | -       | -       | Y       | N       |
    | 出力                     | Default | Default | 結果    | Default | Default |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ     | テスト値                   | 期待される結果        | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|--------------------|-----------------------------|------------------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | 決定テーブル       | 空のDataFrame              | DataFrameEditorDefault | 空の決定テーブルの処理を確認         | 実装済み | test_evaluate_conditions_C1_empty_decision_table |
    | BVT_002  | 入力行             | 空のSeries                 | DataFrameEditorDefault | 空の入力行の処理を確認               | 実装済み | test_evaluate_conditions_C1_empty_input_row |
    | BVT_003  | 決定テーブル       | 1行のDataFrame             | 条件に応じた結果       | 最小の決定テーブルの処理を確認       | 実装済み | test_evaluate_conditions_BVT_single_row_decision_table |
    | BVT_004  | 決定テーブル       | 10000行のDataFrame         | 条件に応じた結果       | 大規模な決定テーブルの処理を確認     | 実装済み | test_evaluate_conditions_BVT_large_decision_table |
    | BVT_005  | 入力行、決定テーブル | 型が一致しないデータ      | 例外発生               | データ型の不一致の処理を確認         | 未実装   | - |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 4
    - 未実装: 1
    - 一部実装: 0

    注記:
    BVT_005は現在未実装です。このケースは入力データの型チェックや例外処理の堅牢性を確認するために重要です。
    将来的な実装が推奨されます。
    """

    @pytest.fixture()
    def evaluator(self):
        return ConditionEvaluator()

    def test_evaluate_conditions_C0_all_conditions_match(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 全ての条件が一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 1, 'B': 'test'})
        decision_table = pd.DataFrame({
            'A': [1, 2],
            'B': ['test', 'other'],
            'DecisionResult': ['Result1', 'Result2'],
        })
        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'Result1'

    def test_evaluate_conditions_C0_no_conditions_match(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 一致する条件がない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 3, 'B': 'none'})
        decision_table = pd.DataFrame({
            'A': [1, 2],
            'B': ['test', 'other'],
            'DecisionResult': ['Result1', 'Result2'],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'DataFrameEditorDefault'

    def test_evaluate_conditions_C1_empty_decision_table(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 決定テーブルが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 1, 'B': 'test'})
        decision_table = pd.DataFrame()

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'DataFrameEditorDefault'

    def test_evaluate_conditions_C1_empty_input_row(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 入力行が空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series()
        decision_table = pd.DataFrame({
            'A': [1, 2],
            'B': ['test', 'other'],
            'DecisionResult': ['Result1', 'Result2'],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'DataFrameEditorDefault'

    def test_evaluate_conditions_C1_partial_match(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 部分的に条件が一致する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 1, 'B': 'other'})
        decision_table = pd.DataFrame({
            'A': [1, 2],
            'B': ['test', 'other'],
            'DecisionResult': ['Result1', 'Result2'],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'DataFrameEditorDefault'

    def test_evaluate_conditions_C2_different_types(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 異なる型の条件組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 1, 'B': 'test', 'C': True})
        decision_table = pd.DataFrame({
            'A': [1, 2],
            'B': ['test', 'other'],
            'C': [True, False],
            'DecisionResult': ['Result1', 'Result2'],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'Result1'

    def test_evaluate_conditions_C2_multiple_matches(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 複数の一致可能な条件がある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 1, 'B': 'test'})
        decision_table = pd.DataFrame({
            'A': [1, 1],
            'B': ['test', 'test'],
            'DecisionResult': ['Result1', 'Result2'],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'Result1'

    def test_evaluate_conditions_BVT_single_row_decision_table(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 決定テーブルが1行のみの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 1, 'B': 'test'})
        decision_table = pd.DataFrame({
            'A': [1],
            'B': ['test'],
            'DecisionResult': ['Result1'],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table)}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'Result1'

    def test_evaluate_conditions_BVT_large_decision_table(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 非常に大きな決定テーブルの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'A': 9999, 'B': 'test9999'})
        decision_table = pd.DataFrame({
            'A': range(10000),
            'B': [f'test{i}' for i in range(10000)],
            'DecisionResult': [f'Result{i}' for i in range(10000)],
        })

        log_msg(f'row: \n{row}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table.head())}', LogLevel.INFO)
        log_msg(f'decison_table: \n{tabulate_dataframe(decision_table.tail())}', LogLevel.INFO)

        result = evaluator.evaluate_conditions(row, decision_table)
        assert result == 'Result9999'

class TestConditionEvaluatorCheckCondition:
    """ConditionEvaluatorの_check_condition関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 通常の等価比較
    │   ├── "any" 条件のチェック
    │   ├── NaN 条件のチェック
    │   └── 正規表現条件のチェック
    ├── C1: 分岐カバレッジ
    │   ├── dt_functions にある関数の呼び出し
    │   ├── カンマを含む OR 条件のチェック
    │   └── 正規表現条件のチェック
    ├── C2: 条件網羅
    │   ├── 異なる型の組み合わせ
    │   └── 複合条件(関数呼び出し + OR条件 + 正規表現)
    └── BVT: 境界値テスト
        ├── 空文字列の処理
        ├── 極端に長い条件文字列の処理
        └── 複雑な正規表現パターンの処理

    C1のディシジョンテーブル:
    | 条件                     | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 | ケース6 | ケース7 | ケース8 |
    |--------------------------|---------|---------|---------|---------|---------|---------|---------|---------|
    | condition is NaN         | Y       | N       | N       | N       | N       | N       | N       | N       |
    | condition is "any"       | N       | Y       | N       | N       | N       | N       | N       | N       |
    | condition in dt_functions| N       | N       | Y       | N       | N       | N       | N       | N       |
    | condition contains ","   | N       | N       | N       | Y       | N       | N       | N       | N       |
    | condition is regex       | N       | N       | N       | N       | Y       | N       | N       | N       |
    | str(value) == str(cond)  | N       | N       | N       | N       | N       | Y       | N       | N       |
    | 出力                     | False   | True    | 関数実行| OR評価  | 正規表現| True    | False   | False   |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | value, condition| "", ""                      | True            | 空文字列の処理を確認                 | 実装済み | test_check_condition_BVT_empty_string |
    | BVT_002  | value, condition| "a" * 1000, "a" * 1000      | True            | 極端に長い文字列の処理を確認         | 実装済み | test_check_condition_BVT_long_string |
    | BVT_003  | value, condition| pd.NA, pd.NA                | True            | NaN同士の比較を確認                  | 実装済み | test_check_condition_BVT_nan_comparison |
    | BVT_004  | value, condition| 0, "0"                      | True            | 異なる型(数値と文字列)の比較を確認   | 実装済み | test_check_condition_BVT_type_conversion |
    | BVT_005  | value, condition| "test", "TEST"              | False           | 大文字小文字の区別を確認             | 実装済み | test_check_condition_BVT_case_sensitivity |
    | BVT_006  | value, condition| "abc", "^a.*c$"             | True            | 基本的な正規表現マッチングを確認     | 実装済み | test_check_condition_BVT_basic_regex |
    | BVT_007  | value, condition| "abc", "^a.{1000}c$"        | False           | 極端に長い正規表現パターンを確認     | 実装済み | test_check_condition_BVT_long_regex |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 7
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、_check_condition関数の動作が様々な条件下で正しく機能することを確認しています。
    """

    @pytest.fixture()
    def evaluator(self):
        return ConditionEvaluator()

    def test_check_condition_C0_normal_comparison(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 通常の等価比較
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_condition("test", "test")
        assert evaluator._check_condition(1, 1)
        assert not evaluator._check_condition("test", "other")
        assert not evaluator._check_condition(1, 2)

    def test_check_condition_C0_any_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: "any" 条件のチェック
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_condition("test", "any")
        assert evaluator._check_condition(1, "any")

    def test_check_condition_C0_nan_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: NaN 条件のチェック
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_condition("test", pd.NA)
        assert not evaluator._check_condition(1, pd.NA)

    def test_check_condition_C0_regex_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 正規表現条件のチェック
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(evaluator, 'is_regex', return_value=True):
            assert evaluator._check_condition("test", "^t.*t$")
            assert not evaluator._check_condition("test", "^a.*b$")

    def test_check_condition_C1_dt_function(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: dt_functions にある関数の呼び出し
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
        assert evaluator._check_condition("123", "is_numeric")
        assert not evaluator._check_condition("abc", "is_numeric")

    def test_check_condition_C1_or_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: カンマを含む OR 条件のチェック
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_condition("test", "test,other")
        assert evaluator._check_condition("other", "test,other")
        assert not evaluator._check_condition("none", "test,other")

    def test_check_condition_C1_regex_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 正規表現条件のチェック
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(evaluator, 'is_regex', return_value=True):
            assert evaluator._check_condition("test123", r"^test\d+$")
            assert not evaluator._check_condition("test", r"^\d+$")

    def test_check_condition_C2_different_types(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 異なる型の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_condition(1, "1")
        assert evaluator._check_condition("1", 1)
        assert evaluator._check_condition(True, "True")

    def test_check_condition_C2_complex_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 複合条件(関数呼び出し + OR条件 + 正規表現)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}

        def side_effect_func(condition):
            if condition == "is_numeric":
                return False
            if condition == "abc":
                return False
            if condition == "^[a-z]+$":
                return True
            return False

        with patch.object(evaluator, 'is_regex', side_effect=side_effect_func):
            assert evaluator._check_condition("123", "is_numeric,abc,^[a-z]+$")
            assert evaluator._check_condition("abc", "is_numeric,abc,^[a-z]+$")
            assert not evaluator._check_condition("ABC", "is_numeric,abc,^[a-z]+$")

    def test_check_condition_BVT_empty_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_condition("", "")
        assert not evaluator._check_condition("", "non_empty")

    def test_check_condition_BVT_long_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 極端に長い条件文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        long_string = "a" * 1000
        assert evaluator._check_condition(long_string, long_string)
        assert not evaluator._check_condition(long_string, long_string + "b")

    def test_check_condition_BVT_nan_comparison(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: NaN同士の比較
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_condition(pd.NA, pd.NA)
        assert evaluator._check_condition(pd.NA, "any")
        assert not evaluator._check_condition("value", pd.NA)

    def test_check_condition_BVT_type_conversion(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 異なる型(数値と文字列)の比較
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_condition(0, "0")
        assert evaluator._check_condition("0", 0)
        assert not evaluator._check_condition(1, "1.0")

    def test_check_condition_BVT_case_sensitivity(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 大文字小文字の区別
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_condition("test", "TEST")
        assert not evaluator._check_condition("TEST", "test")
        assert evaluator._check_condition("Test", "Test")

    def test_check_condition_BVT_basic_regex(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 基本的な正規表現マッチング
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(evaluator, 'is_regex', return_value=True):
            assert evaluator._check_condition("abc", "^a.*c$")
            assert not evaluator._check_condition("abc", "^b.*c$")

    def test_check_condition_BVT_long_regex(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 極端に長い正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(evaluator, 'is_regex', return_value=True):
            long_regex = "^a" + "." * 1000 + "z$"
            assert evaluator._check_condition("a" + "x" * 1000 + "z", long_regex)
            assert not evaluator._check_condition("b" + "x" * 1000 + "z", long_regex)

    @pytest.mark.parametrize(("value", "condition", "expected"), [
        ("test", "test", True),
        ("test", "other", False),
        ("test", "any", True),
        #("test", pd.NA, False),
        ("123", "is_numeric", True),
        ("abc", "is_numeric", False),
        ("test", "test,other", True),
        ("none", "test,other", False),
        ("test123", r"^test\d+$", True),
        ("test", r"^\d+$", False),
        (1, "1", True),
        (True, "True", True),
        ("", "", True),
        ("", "non_empty", False),
        (pd.NA, "any", True),
        (0, "0", True),
        ("test", "TEST", False),
        ("abc", "^a.*c$", True),
    ])
    def test_check_condition_parametrized(self, evaluator, value, condition, expected):
        test_doc = f"""
        テスト内容:
        - テストカテゴリ: 統合テスト
        - テスト区分: 正常系/異常系
        - テストシナリオ: 様々な入力の組み合わせ
        - 入力値: {value}
        - 条件: {condition}
        - 期待結果: {expected}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(evaluator, 'is_regex', return_value=condition.startswith('^') and condition.endswith('$')):
            evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
            result = evaluator._check_condition(value, condition)
            assert result == expected, f"Expected {expected}, but got {result}"


#class TestConditionEvaluatorCheckCondition:
#    """ConditionEvaluatorの_check_condition関数のテスト
#
#    テスト構造:
#    ├── C0: 基本機能テスト
#    │   ├── 通常の等価比較
#    │   ├── "any" 条件のチェック
#    │   └── NaN 条件のチェック
#    ├── C1: 分岐カバレッジ
#    │   ├── dt_functions にある関数の呼び出し
#    │   └── カンマを含む OR 条件のチェック
#    ├── C2: 条件網羅
#    │   ├── 異なる型の組み合わせ
#    │   └── 複合条件(関数呼び出し + OR条件)
#    └── BVT: 境界値テスト
#        ├── 空文字列の処理
#        └── 極端に長い条件文字列の処理
#
#    C1のディシジョンテーブル:
#    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 | ケース6 | ケース7 |
#    |--------------------------------|---------|---------|---------|---------|---------|---------|---------|
#    | condition is NaN or "any"      | Y       | N       | N       | N       | N       | N       | N       |
#    | value is NaN                   | -       | Y       | N       | N       | N       | N       | N       |
#    | condition in dt_functions      | -       | -       | Y       | N       | N       | N       | N       |
#    | condition contains ","         | -       | -       | -       | Y       | N       | N       | N       |
#    | str(value) == str(condition)   | -       | -       | -       | -       | Y       | N       | N       |
#    | 出力                           | True    | False   | func    | OR      | True    | False   | False   |
#
#    境界値検証ケース一覧:
#    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
#    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
#    | BVT_001  | value, condition| "", ""                      | True            | 空文字列の処理を確認                 | 実装済み | test_check_condition_BVT_empty_string |
#    | BVT_002  | value, condition| "a" * 1000, "a" * 1000      | True            | 極端に長い文字列の処理を確認         | 実装済み | test_check_condition_BVT_long_string |
#    | BVT_003  | value, condition| pd.NA, pd.NA                | True            | NaN同士の比較を確認                  | 実装済み | test_check_condition_BVT_nan_comparison |
#    | BVT_004  | value, condition| 0, "0"                      | True            | 異なる型(数値と文字列)の比較を確認 | 実装済み | test_check_condition_BVT_type_conversion |
#    | BVT_005  | value, condition| "test", "TEST"              | False           | 大文字小文字の区別を確認             | 実装済み | test_check_condition_BVT_case_sensitivity |
#
#    境界値検証ケースの実装状況サマリー:
#    - 実装済み: 5
#    - 未実装: 0
#    - 一部実装: 0
#
#    注記:
#    すべての境界値検証ケースが実装されています。これらのテストにより、_check_condition関数の動作が様々な条件下で正しく機能することを確認しています。
#    """
#
#    @pytest.fixture()
#    def evaluator(self):
#        return ConditionEvaluator()
#
#    def test_check_condition_C0_normal_comparison(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: 通常の等価比較
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition("test", "test")
#        assert evaluator._check_condition(1, 1)
#        assert not evaluator._check_condition("test", "other")
#        assert not evaluator._check_condition(1, 2)
#
#    def test_check_condition_C0_any_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: "any" 条件のチェック
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition("test", "any")
#        assert evaluator._check_condition(1, "any")
#
#    def test_check_condition_C0_nan_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: NaN 条件のチェック
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition("test", pd.NA)
#        assert evaluator._check_condition(1, pd.NA)
#
#    def test_check_condition_C1_dt_function(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: dt_functions にある関数の呼び出し
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        evaluator.dt_functions = {"is_numeric": lambda x: x.isdigit()}
#        assert evaluator._check_condition("123", "is_numeric")
#        assert not evaluator._check_condition("abc", "is_numeric")
#
#    def test_check_condition_C1_or_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: カンマを含む OR 条件のチェック
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition("test", "test,other")
#        assert evaluator._check_condition("other", "test,other")
#        assert not evaluator._check_condition("none", "test,other")
#
#    def test_check_condition_C2_different_types(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: 異なる型の組み合わせ
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition(1, "1")
#        assert evaluator._check_condition("1", 1)
#        assert evaluator._check_condition(True, "True")
#
#    def test_check_condition_C2_complex_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: 複合条件(関数呼び出し + OR条件)
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
#        assert evaluator._check_condition("123", "is_numeric,abc")
#        assert evaluator._check_condition("abc", "is_numeric,abc")
#        assert not evaluator._check_condition("xyz", "is_numeric,abc")
#
#    def test_check_condition_BVT_empty_string(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 空文字列の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition("", "")
#        assert not evaluator._check_condition("", "non_empty")
#
#    def test_check_condition_BVT_long_string(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 極端に長い条件文字列の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        long_string = "a" * 1000
#        assert evaluator._check_condition(long_string, long_string)
#        assert not evaluator._check_condition(long_string, long_string + "b")
#
#    def test_check_condition_BVT_nan_comparison(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: NaN同士の比較
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition(pd.NA, pd.NA)
#        assert evaluator._check_condition(pd.NA, "any")
#        assert evaluator._check_condition("value", pd.NA)
#
#    def test_check_condition_BVT_type_conversion(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 異なる型(数値と文字列)の比較
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_condition(0, "0")
#        assert evaluator._check_condition("0", 0)
#        assert not evaluator._check_condition(1, "1.0")
#
#    def test_check_condition_BVT_case_sensitivity(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 大文字小文字の区別
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert not evaluator._check_condition("test", "TEST")
#        assert not evaluator._check_condition("TEST", "test")
#        assert evaluator._check_condition("Test", "Test")

# 正規表現対応機能拡張
class TestConditionEvaluatorIsRegex:
    """ConditionEvaluatorのis_regex関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 有効な正規表現パターン
    │   └── 無効な正規表現パターン
    ├── C1: 分岐カバレッジ
    │   ├── 正規表現として解釈可能な文字列
    │   └── 正規表現として解釈不可能な文字列
    ├── C2: 条件網羅
    │   └── 様々な正規表現パターン
    └── BVT: 境界値テスト
        ├── 空文字列
        └── 複雑な正規表現パターン

    C1のディシジョンテーブル:
    | 条件                               | ケース1 | ケース2 |
    |------------------------------------|---------|---------|
    | re.compile でエラーが発生しない    | Y       | N       |
    | 出力                               | True    | False   |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | condition       | ""                          | False           | 空文字列の処理を確認                 | 実装済み | test_is_regex_BVT_empty_string    |
    | BVT_002  | condition       | "^[a-zA-Z0-9_]{1,50}$"      | True            | 複雑だが有効な正規表現を確認         | 実装済み | test_is_regex_BVT_complex_pattern |
    | BVT_003  | condition       | "("                         | False           | 不完全な正規表現の処理を確認         | 実装済み | test_is_regex_BVT_incomplete_pattern |
    | BVT_004  | condition       | "a" * 1000 + "*"            | True            | 非常に長い正規表現の処理を確認       | 実装済み | test_is_regex_BVT_long_pattern    |
    | BVT_005  | condition       | "[" + "a-z" * 100 + "]"     | True            | 複雑で長い文字クラスの処理を確認     | 実装済み | test_is_regex_BVT_complex_long_pattern |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、is_regex関数の動作が様々な条件下で正しく機能することを確認しています。
    """

    @pytest.fixture
    def evaluator(self):
        return ConditionEvaluator()

    def test_is_regex_C0_valid_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator.is_regex("^[a-z]+$")
        assert evaluator.is_regex(r"\d{3}-\d{4}")

    def test_is_regex_C0_invalid_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 無効な正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator.is_regex("(")
        assert not evaluator.is_regex("[a-z")

    def test_is_regex_C1_valid_regex(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 正規表現として解釈可能な文字列
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('re.compile') as mock_compile:
            mock_compile.return_value = True
            assert evaluator.is_regex("test_pattern")

    def test_is_regex_C1_invalid_regex(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 正規表現として解釈不可能な文字列
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('re.compile') as mock_compile:
            mock_compile.side_effect = re.error("Invalid regex")
            assert not evaluator.is_regex("invalid_pattern")

    def test_is_regex_C2_various_patterns(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 様々な正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        patterns = [
            r"^[a-z]+$",
            r"\d{3}-\d{4}",
            r"[A-Z][a-z]*",
            r"(foo|bar)",
            r"\w+@\w+\.\w+",
            r"(?=.*[A-Z])(?=.*[a-z])(?=.*\d)[A-Za-z\d]{8,}",
        ]
        for pattern in patterns:
            assert evaluator.is_regex(pattern), f"Pattern should be valid: {pattern}"

    def test_is_regex_BVT_empty_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空文字列
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator.is_regex("")

    def test_is_regex_BVT_complex_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 複雑な正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        complex_pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
        assert evaluator.is_regex(complex_pattern)

    def test_is_regex_BVT_incomplete_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 不完全な正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator.is_regex("(")
        assert not evaluator.is_regex("[a-z")

    def test_is_regex_BVT_long_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 非常に長い正規表現パターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        long_pattern = "a" * 1000 + "*"
        assert evaluator.is_regex(long_pattern)

    def test_is_regex_BVT_complex_long_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 複雑で長い文字クラス
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        complex_long_pattern = "[" + "a-z" * 100 + "]"
        assert evaluator.is_regex(complex_long_pattern)


class TestConditionEvaluatorCheckRegex:
    r"""ConditionEvaluatorの_check_regex関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── マッチする正規表現
    │   └── マッチしない正規表現
    ├── C1: 分岐カバレッジ
    │   ├── 文字列入力
    │   ├── 数値入力
    │   └── その他の型の入力
    ├── C2: 条件網羅
    │   └── 様々な正規表現パターンと入力値の組み合わせ
    └── BVT: 境界値テスト
        ├── 空文字列
        ├── 非常に長い入力文字列
        └── 複雑な正規表現パターン

    C1のディシジョンテーブル:
    | 条件                 | ケース1 | ケース2 | ケース3 | ケース4 |
    |----------------------|---------|---------|---------|---------|
    | 入力がstr型          | Y       | N       | N       | N       |
    | 入力がint型          | N       | Y       | N       | N       |
    | 入力が他の型         | N       | N       | Y       | N       |
    | 正規表現にマッチ     | Y       | Y       | -       | N       |
    | 出力                 | True    | True    | False   | False   |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ     | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|--------------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | value, condition   | "", ".*"                    | True            | 空文字列の処理を確認                 | 実装済み | test_check_regex_BVT_empty_string |
    | BVT_002  | value, condition   | "a" * 1000000, "a+"         | True            | 非常に長い入力文字列の処理を確認     | 実装済み | test_check_regex_BVT_long_string  |
    | BVT_003  | value, condition   | "abc", "^$"                 | False           | マッチしない境界ケースを確認         | 実装済み | test_check_regex_BVT_no_match     |
    | BVT_004  | value, condition   | "a", "(a|b)*abb"            | False           | 複雑なパターンでのマッチングを確認   | 実装済み | test_check_regex_BVT_complex_pattern |
    | BVT_005  | value, condition   | 12345, r"\d+"               | True            | 数値入力の処理を確認                 | 実装済み | test_check_regex_C1_numeric_input |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、_check_regex関数の動作が様々な条件下で正しく機能することを確認しています。
    """

    @pytest.fixture
    def evaluator(self):
        return ConditionEvaluator()

    def test_check_regex_C0_matching(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: マッチする正規表現
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_regex("test123", r"^test\d+$")
        assert evaluator._check_regex("abc", r"[a-z]+")

    def test_check_regex_C0_non_matching(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: マッチしない正規表現
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_regex("test123", r"^[a-z]+$")
        assert not evaluator._check_regex("123", r"[a-z]+")

    def test_check_regex_C1_string_input(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 文字列入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_regex("test", r"^test$")
        assert not evaluator._check_regex("test", r"^other$")

    def test_check_regex_C1_numeric_input(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 数値入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_regex(123, r"^\d+$")
        assert not evaluator._check_regex(123, r"^[a-z]+$")

    def test_check_regex_C1_other_input(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: その他の型の入力
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_regex(None, r".*")
        assert not evaluator._check_regex([1, 2, 3], r".*")

    def test_check_regex_C2_various_patterns(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 様々な正規表現パターンと入力値の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_cases = [
            ("abc123", r"^[a-z]+\d+$", True),
            ("ABC123", r"^[A-Z]+\d+$", True),
            ("test@example.com", r"^[\w\.-]+@[\w\.-]+\.\w+$", True),
            ("192.168.0.1", r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", True),
            ("12345", r"^\d+$", True),
            ("abcde", r"^\d+$", False),
            ("Test String", r"^[A-Z][a-z]+ [A-Z][a-z]+$", True),
            ("InvalidString", r"^[A-Z][a-z]+ [A-Z][a-z]+$", False),
        ]

        for value, pattern, expected in test_cases:
            result = evaluator._check_regex(value, pattern)
            assert result == expected, f"Failed for value: {value}, pattern: {pattern}"

    def test_check_regex_BVT_empty_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空文字列
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_regex("", r".*")
        assert not evaluator._check_regex("", r".+")

    def test_check_regex_BVT_long_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 非常に長い入力文字列
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        long_string = "a" * 1000000
        assert evaluator._check_regex(long_string, r"^a+$")
        assert not evaluator._check_regex(long_string, r"^b+$")

    def test_check_regex_BVT_no_match(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: マッチしない境界ケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_regex("abc", r"^$")
        assert not evaluator._check_regex("", r".+")

    def test_check_regex_BVT_complex_pattern(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 複雑なパターン
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_regex("aabbcc", r"(a|b)*abb(a|b|c)*")
        assert not evaluator._check_regex("aabbcc", r"(a|b)*abc(a|b|c)*")



class TestConditionEvaluatorCheckDtFunction:
    """ConditionEvaluatorの_check_dt_function関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 既知のDT関数の呼び出し
    ├── C1: 分岐カバレッジ
    │   ├── 存在する関数の呼び出し
    │   └── 存在しない関数の呼び出し(例外処理)
    ├── C2: 条件網羅
    │   └── 異なるDT関数と入力値の組み合わせ
    └── BVT: 境界値テスト
        ├── 極端な入力値での関数呼び出し
        └── 無効な関数名での呼び出し

    C1のディシジョンテーブル:
    | 条件                     | ケース1 | ケース2 |
    |--------------------------|---------|---------|
    | 関数がdt_functionsに存在 | Y       | N       |
    | 出力                     | 結果    | 例外    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | value, condition| "", "is_empty"              | True            | 空文字列の処理を確認                 | 実装済み | test_check_dt_function_BVT_empty_string |
    | BVT_002  | value, condition| "a" * 1000, "is_long"       | True            | 極端に長い文字列の処理を確認         | 実装済み | test_check_dt_function_BVT_long_string |
    | BVT_003  | value, condition| pd.NA, "is_na"              | True            | NaN値の処理を確認                    | 実装済み | test_check_dt_function_BVT_nan_value |
    | BVT_004  | value, condition| 0, "is_zero"                | True            | ゼロ値の処理を確認                   | 実装済み | test_check_dt_function_BVT_zero_value |
    | BVT_005  | value, condition| "test", "invalid_function"  | 例外発生        | 無効な関数名の処理を確認             | 実装済み | test_check_dt_function_BVT_invalid_function |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、_check_dt_function関数の動作が様々な条件下で正しく機能することを確認しています。
    """

    @pytest.fixture()
    def evaluator(self):
        return ConditionEvaluator()

    def test_check_dt_function_C0_known_function(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 既知のDT関数の呼び出し
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
        assert evaluator._check_dt_function("123", "is_numeric")
        assert not evaluator._check_dt_function("abc", "is_numeric")

    def test_check_dt_function_C1_existing_function(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 存在する関数の呼び出し
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_positive": lambda x: int(x) > 0}
        assert evaluator._check_dt_function("5", "is_positive")
        assert not evaluator._check_dt_function("-1", "is_positive")

    def test_check_dt_function_C1_non_existing_function(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 存在しない関数の呼び出し(例外処理)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(KeyError):
            evaluator._check_dt_function("test", "non_existing_function")

    def test_check_dt_function_C2_various_combinations(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 異なるDT関数と入力値の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {
            "is_numeric": lambda x: str(x).isdigit(),
            "is_alphabetic": lambda x: str(x).isalpha(),
            "is_uppercase": lambda x: str(x).isupper(),
            "is_lowercase": lambda x: str(x).islower(),
        }

        assert evaluator._check_dt_function("123", "is_numeric")
        assert evaluator._check_dt_function("abc", "is_alphabetic")
        assert evaluator._check_dt_function("ABC", "is_uppercase")
        assert evaluator._check_dt_function("abc", "is_lowercase")

        assert not evaluator._check_dt_function("abc", "is_numeric")
        assert not evaluator._check_dt_function("123", "is_alphabetic")
        assert not evaluator._check_dt_function("abc", "is_uppercase")
        assert not evaluator._check_dt_function("ABC", "is_lowercase")

    def test_check_dt_function_BVT_empty_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_empty": lambda x: x == ""}
        assert evaluator._check_dt_function("", "is_empty")
        assert not evaluator._check_dt_function("not_empty", "is_empty")

    def test_check_dt_function_BVT_long_string(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 極端に長い文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_long": lambda x: len(x) > 100}      # noqa:PLR2004
        assert evaluator._check_dt_function("a" * 101, "is_long")
        assert not evaluator._check_dt_function("short", "is_long")

    def test_check_dt_function_BVT_nan_value(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: NaN値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_na": pd.isna}
        assert evaluator._check_dt_function(pd.NA, "is_na")
        assert not evaluator._check_dt_function("not_na", "is_na")

    def test_check_dt_function_BVT_zero_value(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: ゼロ値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_zero": lambda x: float(x) == 0}
        assert evaluator._check_dt_function(0, "is_zero")
        assert evaluator._check_dt_function("0", "is_zero")
        assert not evaluator._check_dt_function(1, "is_zero")

    def test_check_dt_function_BVT_invalid_function(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 無効な関数名の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(KeyError):
            evaluator._check_dt_function("test", "invalid_function")


class TestConditionEvaluatorCheckOrCondition:
    """ConditionEvaluatorの_check_or_condition関数のテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 単一条件のOR評価
    │   └── 複数条件のOR評価
    ├── C1: 分岐カバレッジ
    │   ├── 全ての条件がfalseの場合
    │   ├── 少なくとも1つの条件がtrueの場合
    │   └── 正規表現条件を含むOR評価
    ├── C2: 条件網羅
    │   ├── 異なる型と条件の組み合わせ
    │   └── 正規表現、関数呼び出し、通常の条件の組み合わせ
    └── BVT: 境界値テスト
        ├── 空のOR条件の処理
        └── 多数のOR条件を含む文字列の処理

    C1のディシジョンテーブル:
    | 条件                         | ケース1 | ケース2 | ケース3 | ケース4 |
    |------------------------------|---------|---------|---------|---------|
    | 条件1がtrue                  | N       | Y       | N       | N       |
    | 条件2がtrue                  | N       | N       | Y       | N       |
    | 正規表現条件がマッチ         | N       | N       | N       | Y       |
    | 出力                         | False   | True    | True    | True    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | value, condition| "test", ""                  | False           | 空のOR条件の処理を確認               | 実装済み | test_check_or_condition_BVT_empty_condition |
    | BVT_002  | value, condition| "test", "a,b,c,...,z"       | False           | 多数の条件を含むOR条件の処理を確認   | 実装済み | test_check_or_condition_BVT_many_conditions |
    | BVT_003  | value, condition| "", "a,,b"                  | False           | 空文字を含むOR条件の処理を確認       | 実装済み | test_check_or_condition_BVT_empty_value_in_condition |
    | BVT_004  | value, condition| "test", " a , b "           | False           | 空白を含むOR条件の処理を確認         | 実装済み | test_check_or_condition_BVT_whitespace_in_condition |
    | BVT_005  | value, condition| pd.NA, "a,b,c"              | False           | NaN値のOR条件の処理を確認            | 実装済み | test_check_or_condition_BVT_nan_value |
    | BVT_006  | value, condition| "abc", "^a.*c$,def,ghi"     | True            | 正規表現を含むOR条件の処理を確認     | 実装済み | test_check_or_condition_BVT_regex_in_condition |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 6
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、_check_or_condition関数の動作が様々な条件下で正しく機能することを確認しています。
    正規表現を含むOR条件の処理が新たに追加され、テストされています。
    """

    @pytest.fixture
    def evaluator(self):
        return ConditionEvaluator()

    def test_check_or_condition_C0_single_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 単一条件のOR評価
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_or_condition("test", "test")
        assert not evaluator._check_or_condition("test", "other")

    def test_check_or_condition_C0_multiple_conditions(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 複数条件のOR評価
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_or_condition("test", "test,other")
        assert evaluator._check_or_condition("other", "test,other")
        assert not evaluator._check_or_condition("none", "test,other")

    def test_check_or_condition_C1_all_false(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 全ての条件がfalseの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_or_condition("none", "test,other,another")

    def test_check_or_condition_C1_one_true(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 少なくとも1つの条件がtrueの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_or_condition("test", "test,other,another")
        assert evaluator._check_or_condition("other", "test,other,another")
        assert evaluator._check_or_condition("another", "test,other,another")


    def test_check_or_condition_C1_regex_true(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 正規表現条件を含むOR評価
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(evaluator, 'is_regex', return_value=True):
            assert evaluator._check_or_condition("test", "other,^t.*t$,another")
            assert not evaluator._check_or_condition("test", "other,^a.*b$,another")

    def test_check_or_condition_C2_different_types(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 異なる型と条件の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_or_condition(1, "1,2,3")
        assert evaluator._check_or_condition("1", "1,2,3")
        assert evaluator._check_or_condition(True, "True,False")
        assert evaluator._check_or_condition(False, "True,False")

    def test_check_or_condition_C2_complex_conditions(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 正規表現、関数呼び出し、通常の条件の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
    
        def is_regex_side_effect(condition):
            if condition in ["is_numeric", "abc", "123"]:
                return False
            return condition.startswith('^') and condition.endswith('$')

        with patch.object(evaluator, 'is_regex', side_effect=is_regex_side_effect):
            assert evaluator._check_or_condition("123", "is_numeric,^\\d+$,abc")
            assert evaluator._check_or_condition("abc", "is_numeric,^[a-z]+$,123")
            assert not evaluator._check_condition("ABC", "is_numeric,^[a-z]+$,123")

        #evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
        #with patch.object(evaluator, 'is_regex', side_effect=[False, True, False, True]):
        #    assert evaluator._check_or_condition("123", "is_numeric,^\\d+$,abc")
        #    assert evaluator._check_or_condition("abc", "is_numeric,^[a-z]+$,123")
        #    assert not evaluator._check_or_condition("ABC", "is_numeric,^[a-z]+$,123")

    def test_check_or_condition_BVT_empty_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空のOR条件の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_or_condition("test", "")

    def test_check_or_condition_BVT_many_conditions(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 多数のOR条件を含む文字列の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        many_conditions = ",".join([f"condition{i}" for i in range(100)])
        assert evaluator._check_or_condition("condition50", many_conditions)
        assert not evaluator._check_or_condition("not_in_list", many_conditions)

    def test_check_or_condition_BVT_empty_value_in_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空文字を含むOR条件の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_or_condition("", "a,,b")
        assert not evaluator._check_or_condition("c", "a,,b")

    def test_check_or_condition_BVT_whitespace_in_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 空白を含むOR条件の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert evaluator._check_or_condition("a", " a , b ")
        assert evaluator._check_or_condition("b", " a , b ")
        assert not evaluator._check_or_condition("c", " a , b ")

    def test_check_or_condition_BVT_nan_value(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: NaN値のOR条件の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        assert not evaluator._check_or_condition(pd.NA, "a,b,c")
        assert not evaluator._check_or_condition("a", f"{pd.NA},b,c")
        assert evaluator._check_or_condition(pd.NA, f"{pd.NA},b,c")

    def test_check_or_condition_BVT_regex_in_condition(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 正規表現を含むOR条件の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def is_regex_side_effect(condition):
            return condition.startswith('^') and condition.endswith('$')

        with patch.object(evaluator, 'is_regex', side_effect=is_regex_side_effect):
            assert evaluator._check_or_condition("abc", "^a.*c$,def,ghi")
            assert not evaluator._check_or_condition("def", "^a.*c$,ghi,jkl")

#class TestConditionEvaluatorCheckOrCondition:
#    """ConditionEvaluatorの_check_or_condition関数のテスト
#
#    テスト構造:
#    ├── C0: 基本機能テスト
#    │   ├── 単一条件のOR評価
#    │   └── 複数条件のOR評価
#    ├── C1: 分岐カバレッジ
#    │   ├── 全ての条件がfalseの場合
#    │   └── 少なくとも1つの条件がtrueの場合
#    ├── C2: 条件網羅
#    │   ├── 異なる型と条件の組み合わせ
#    │   └── ネストされたOR条件の評価
#    └── BVT: 境界値テスト
#        ├── 空のOR条件の処理
#        └── 多数のOR条件を含む文字列の処理
#
#    C1のディシジョンテーブル:
#    | 条件                         | ケース1 | ケース2 | ケース3 |
#    |------------------------------|---------|---------|---------|
#    | 条件1がtrue                  | N       | Y       | N       |
#    | 条件2がtrue                  | N       | N       | Y       |
#    | 出力                         | False   | True    | True    |
#
#    境界値検証ケース一覧:
#    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
#    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
#    | BVT_001  | value, condition| "test", ""                  | False           | 空のOR条件の処理を確認               | 実装済み | test_check_or_condition_BVT_empty_condition |
#    | BVT_002  | value, condition| "test", "a,b,c,...,z"       | False           | 多数の条件を含むOR条件の処理を確認   | 実装済み | test_check_or_condition_BVT_many_conditions |
#    | BVT_003  | value, condition| "", "a,,b"                  | False           | 空文字を含むOR条件の処理を確認       | 実装済み | test_check_or_condition_BVT_empty_value_in_condition |
#    | BVT_004  | value, condition| "test", " a , b "           | False           | 空白を含むOR条件の処理を確認         | 実装済み | test_check_or_condition_BVT_whitespace_in_condition |
#    | BVT_005  | value, condition| pd.NA, "a,b,c"              | False           | NaN値のOR条件の処理を確認            | 実装済み | test_check_or_condition_BVT_nan_value |
#
#    境界値検証ケースの実装状況サマリー:
#    - 実装済み: 5
#    - 未実装: 0
#    - 一部実装: 0
#
#    注記:
#    すべての境界値検証ケースが実装されています。これらのテストにより、_check_or_condition関数の動作が様々な条件下で正しく機能することを確認しています。
#    """
#
#    @pytest.fixture()
#    def evaluator(self):
#        return ConditionEvaluator()
#
#    def test_check_or_condition_C0_single_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: 単一条件のOR評価
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_or_condition("test", "test")
#        assert not evaluator._check_or_condition("test", "other")
#
#    def test_check_or_condition_C0_multiple_conditions(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C0
#        - テスト区分: 正常系
#        - テストシナリオ: 複数条件のOR評価
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_or_condition("test", "test,other")
#        assert evaluator._check_or_condition("other", "test,other")
#        assert not evaluator._check_or_condition("none", "test,other")
#
#    def test_check_or_condition_C1_all_false(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: 全ての条件がfalseの場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert not evaluator._check_or_condition("none", "test,other,another")
#
#    def test_check_or_condition_C1_one_true(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C1
#        - テスト区分: 正常系
#        - テストシナリオ: 少なくとも1つの条件がtrueの場合
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_or_condition("test", "test,other,another")
#        assert evaluator._check_or_condition("other", "test,other,another")
#        assert evaluator._check_or_condition("another", "test,other,another")
#
#    def test_check_or_condition_C2_different_types(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: 異なる型と条件の組み合わせ
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_or_condition(1, "1,2,3")
#        assert evaluator._check_or_condition("1", "1,2,3")
#        assert evaluator._check_or_condition(True, "True,False")
#        assert evaluator._check_or_condition(False, "True,False")
#
#    def test_check_or_condition_C2_nested_conditions(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: C2
#        - テスト区分: 正常系
#        - テストシナリオ: ネストされたOR条件の評価
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        # このテストケースは現在の実装では対応していないため、コメントアウトしています
#        # 将来的にネストされたOR条件を実装する場合に使用できます
#        # assert evaluator._check_or_condition("test", "condition1,condition2|condition3,condition4") == False
#        # assert evaluator._check_or_condition("condition2", "condition1,condition2|condition3,condition4") == True
#
#    def test_check_or_condition_BVT_empty_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 空のOR条件の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert not evaluator._check_or_condition("test", "")
#
#    def test_check_or_condition_BVT_many_conditions(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 多数のOR条件を含む文字列の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        many_conditions = ",".join([f"condition{i}" for i in range(100)])
#        assert evaluator._check_or_condition("condition50", many_conditions)
#        assert not evaluator._check_or_condition("not_in_list", many_conditions)
#
#    def test_check_or_condition_BVT_empty_value_in_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 空文字を含むOR条件の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_or_condition("", "a,,b")
#        assert not evaluator._check_or_condition("c", "a,,b")
#
#    def test_check_or_condition_BVT_whitespace_in_condition(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: 空白を含むOR条件の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert evaluator._check_or_condition("a", " a , b ")
#        assert evaluator._check_or_condition("b", " a , b ")
#        assert not evaluator._check_or_condition("c", " a , b ")
#
#    def test_check_or_condition_BVT_nan_value(self, evaluator):
#        test_doc = """
#        テスト内容:
#        - テストカテゴリ: BVT
#        - テスト区分: 境界値
#        - テストシナリオ: NaN値のOR条件の処理
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        assert not evaluator._check_or_condition(pd.NA, "a,b,c")
#        assert not evaluator._check_or_condition("a", f"{pd.NA},b,c")
#        assert not evaluator._check_or_condition("a", f"{pd.NA},b,c")
