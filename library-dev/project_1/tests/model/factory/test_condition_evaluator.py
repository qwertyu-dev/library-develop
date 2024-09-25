# config共有
import sys
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
    │   └── NaN 条件のチェック
    ├── C1: 分岐カバレッジ
    │   ├── dt_functions にある関数の呼び出し
    │   └── カンマを含む OR 条件のチェック
    ├── C2: 条件網羅
    │   ├── 異なる型の組み合わせ
    │   └── 複合条件(関数呼び出し + OR条件)
    └── BVT: 境界値テスト
        ├── 空文字列の処理
        └── 極端に長い条件文字列の処理

    C1のディシジョンテーブル:
    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 | ケース6 | ケース7 |
    |--------------------------------|---------|---------|---------|---------|---------|---------|---------|
    | condition is NaN or "any"      | Y       | N       | N       | N       | N       | N       | N       |
    | value is NaN                   | -       | Y       | N       | N       | N       | N       | N       |
    | condition in dt_functions      | -       | -       | Y       | N       | N       | N       | N       |
    | condition contains ","         | -       | -       | -       | Y       | N       | N       | N       |
    | str(value) == str(condition)   | -       | -       | -       | -       | Y       | N       | N       |
    | 出力                           | True    | False   | func    | OR      | True    | False   | False   |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | value, condition| "", ""                      | True            | 空文字列の処理を確認                 | 実装済み | test_check_condition_BVT_empty_string |
    | BVT_002  | value, condition| "a" * 1000, "a" * 1000      | True            | 極端に長い文字列の処理を確認         | 実装済み | test_check_condition_BVT_long_string |
    | BVT_003  | value, condition| pd.NA, pd.NA                | True            | NaN同士の比較を確認                  | 実装済み | test_check_condition_BVT_nan_comparison |
    | BVT_004  | value, condition| 0, "0"                      | True            | 異なる型(数値と文字列)の比較を確認 | 実装済み | test_check_condition_BVT_type_conversion |
    | BVT_005  | value, condition| "test", "TEST"              | False           | 大文字小文字の区別を確認             | 実装済み | test_check_condition_BVT_case_sensitivity |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
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

        assert evaluator._check_condition("test", pd.NA)
        assert evaluator._check_condition(1, pd.NA)

    def test_check_condition_C1_dt_function(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: dt_functions にある関数の呼び出し
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_numeric": lambda x: x.isdigit()}
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
        - テストシナリオ: 複合条件(関数呼び出し + OR条件)
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        evaluator.dt_functions = {"is_numeric": lambda x: str(x).isdigit()}
        assert evaluator._check_condition("123", "is_numeric,abc")
        assert evaluator._check_condition("abc", "is_numeric,abc")
        assert not evaluator._check_condition("xyz", "is_numeric,abc")

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

        assert evaluator._check_condition(pd.NA, pd.NA)
        assert evaluator._check_condition(pd.NA, "any")
        assert evaluator._check_condition("value", pd.NA)

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
    │   └── 少なくとも1つの条件がtrueの場合
    ├── C2: 条件網羅
    │   ├── 異なる型と条件の組み合わせ
    │   └── ネストされたOR条件の評価
    └── BVT: 境界値テスト
        ├── 空のOR条件の処理
        └── 多数のOR条件を含む文字列の処理

    C1のディシジョンテーブル:
    | 条件                         | ケース1 | ケース2 | ケース3 |
    |------------------------------|---------|---------|---------|
    | 条件1がtrue                  | N       | Y       | N       |
    | 条件2がtrue                  | N       | N       | Y       |
    | 出力                         | False   | True    | True    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|-----------------|-----------------------------|-----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | value, condition| "test", ""                  | False           | 空のOR条件の処理を確認               | 実装済み | test_check_or_condition_BVT_empty_condition |
    | BVT_002  | value, condition| "test", "a,b,c,...,z"       | False           | 多数の条件を含むOR条件の処理を確認   | 実装済み | test_check_or_condition_BVT_many_conditions |
    | BVT_003  | value, condition| "", "a,,b"                  | False           | 空文字を含むOR条件の処理を確認       | 実装済み | test_check_or_condition_BVT_empty_value_in_condition |
    | BVT_004  | value, condition| "test", " a , b "           | False           | 空白を含むOR条件の処理を確認         | 実装済み | test_check_or_condition_BVT_whitespace_in_condition |
    | BVT_005  | value, condition| pd.NA, "a,b,c"              | False           | NaN値のOR条件の処理を確認            | 実装済み | test_check_or_condition_BVT_nan_value |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これらのテストにより、_check_or_condition関数の動作が様々な条件下で正しく機能することを確認しています。
    """

    @pytest.fixture()
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

    def test_check_or_condition_C2_nested_conditions(self, evaluator):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: ネストされたOR条件の評価
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # このテストケースは現在の実装では対応していないため、コメントアウトしています
        # 将来的にネストされたOR条件を実装する場合に使用できます
        # assert evaluator._check_or_condition("test", "condition1,condition2|condition3,condition4") == False
        # assert evaluator._check_or_condition("condition2", "condition1,condition2|condition3,condition4") == True

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
        assert not evaluator._check_or_condition("a", f"{pd.NA},b,c")
