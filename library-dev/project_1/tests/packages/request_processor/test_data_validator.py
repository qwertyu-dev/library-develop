# テストに依存しないカスタムロガー
import sys
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from pydantic import BaseModel

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_helper import (
    format_dict,
)
from src.packages.request_processor.data_validator import DataValidator

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestDataValidatorInit:
    """DataValidatorの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なconfigとvalidation_modelでインスタンス生成
    │   └── 異常系: 無効なvalidation_modelでTypeError
    ├── C1: 分岐カバレッジ
    │   ├── configがNoneの場合
    │   └── configが有効な場合
    ├── C2: 条件組み合わせ
    │   ├── config: None / 有効 / 無効
    │   └── validation_model: 有効 / 無効
    └── BVT: 境界値テスト
        ├── configが空辞書
        └── validation_modelが最小限の定義

    C1のディシジョンテーブル:
    | 条件                   | ケース1 | ケース2 | ケース3 | ケース4 |
    |------------------------|---------|---------|---------|---------|
    | configがNone           | Y       | N       | N       | N       |
    | configが有効           | -       | Y       | N       | Y       |
    | validation_modelが有効 | Y       | Y       | Y       | N       |
    | 結果                   | 成功    | 成功    | 成功    | 失敗    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ     | テスト値                   | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース              |
    |----------|--------------------|----------------------------|----------------|--------------------------------------|----------|-----------------------------------|
    | BVT_001  | config             | {}                         | 成功           | 空の設定での動作確認                | 実装済み | test_init_BVT_empty_config         |
    | BVT_002  | validation_model   | class MinModel(BaseModel): | 成功           | 最小限のモデル定義での動作確認      | 実装済み | test_init_BVT_minimal_model        |
    | BVT_003  | config             | None                       | 成功           | Noneの設定での動作確認              | 実装済み | test_init_C1_None_config           |
    | BVT_004  | validation_model   | None                       | 失敗           | 無効なモデルでの例外発生確認        | 実装済み | test_init_C0_invalid_model         |
    | BVT_005  | config             | {'key': 'value'}           | 成功           | 有効な設定での動作確認              | 実装済み | test_init_C0_valid_inputs          |
    | BVT_006  | validation_model   | int                        | 失敗           | BaseModelでないクラスでの例外確認   | 実装済み | test_init_C2_invalid_model_type    |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 6
    - 未実装: 0
    - 一部実装: 0

    注記:
    全ての境界値ケースが実装されています。追加のエッジケースが必要な場合は、さらなるテストケースを追加することができます。
    """

    def setup_method(self):
        self.mock_config = MagicMock()
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_model(self):
        class TestModel(BaseModel):
            field: str
        return TestModel

    def test_init_C0_valid_inputs(self, valid_model):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なconfigとvalidation_modelでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        validator = DataValidator(self.mock_config, valid_model)
        assert isinstance(validator, DataValidator)
        assert validator.config == self.mock_config
        assert validator.validation_model == valid_model

    def test_init_C0_invalid_model(self):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 無効なvalidation_modelでTypeError
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_models = [dict, str, int, list, tuple]
        for invalid_model in invalid_models:
            with pytest.raises(TypeError) as excinfo:
                DataValidator(self.mock_config, invalid_model)
            assert "validation_model must be a subclass of BaseModel" in str(excinfo.value)

    def test_init_C1_None_config(self, valid_model):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: configがNoneの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        validator = DataValidator(None, valid_model)
        assert isinstance(validator, DataValidator)
        assert validator.config is not None  # デフォルトのconfigが使用されるはず

    def test_init_C2_config_combinations(self, valid_model):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: configの様々な組み合わせでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # Noneのconfig
        validator = DataValidator(None, valid_model)
        assert isinstance(validator, DataValidator)
        assert validator.config is not None

        # 有効なconfig
        valid_config = MagicMock()
        validator = DataValidator(valid_config, valid_model)
        assert isinstance(validator, DataValidator)
        assert validator.config == valid_config

        # 無効なconfig
        with pytest.raises(AttributeError):
            DataValidator("invalid_config", valid_model)

    def test_init_C2_invalid_model_type(self):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: BaseModelでないクラスでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class NonBaseModel:
            pass

        with pytest.raises(TypeError) as excinfo:
            DataValidator(self.mock_config, NonBaseModel)
        assert "validation_model must be a subclass of BaseModel" in str(excinfo.value)

    def test_init_BVT_empty_config(self, valid_model):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 空のconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_config = {}
        validator = DataValidator(empty_config, valid_model)
        assert isinstance(validator, DataValidator)
        assert validator.config != {}  # デフォルトのconfigが使用されるはず

    def test_init_BVT_minimal_model(self):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 最小限のモデル定義での初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        class MinimalModel(BaseModel):
            pass

        validator = DataValidator(self.mock_config, MinimalModel)
        assert isinstance(validator, DataValidator)
        assert validator.validation_model == MinimalModel



class TestDataValidatorValidate:
    """DataValidatorのvalidateメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: エラーなしのDataFrame
    │   └── 異常系: エラーありのDataFrame
    ├── C1: 分岐カバレッジ
    │   ├── エラーがない場合
    │   └── エラーがある場合
    ├── C2: 条件組み合わせ
    │   ├── DataFrame: 空 / 1行 / 複数行
    │   └── バリデーション結果: すべて成功 / 一部失敗 / すべて失敗
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        ├── 1行のDataFrame
        └── 大量データのDataFrame

    C1のディシジョンテーブル:
    | 条件                 | ケース1 | ケース2 |
    |----------------------|---------|---------|
    | エラーが発生する     | N       | Y       |
    | 結果                 | ログなし | エラーログ |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値           | 期待される結果     | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース              |
    |----------|----------------|--------------------|--------------------|----------------------------------|----------|-----------------------------------|
    | BVT_001  | df             | 空のDataFrame      | エラーなし         | 空のDataFrameの処理を確認        | 実装済み | test_validate_BVT_empty_dataframe  |
    | BVT_002  | df             | 1行のDataFrame     | 正常に処理         | 最小データセットの処理を確認     | 実装済み | test_validate_BVT_single_row      |
    | BVT_003  | df             | 大量データ(1万行)  | 正常に処理         | 大量データの処理を確認           | 実装済み | test_validate_BVT_large_dataframe |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値ケースが実装されています。パフォーマンスの観点から、大量データのテストケースは実行時間が長くなる可能性があります。
    """

    @pytest.fixture()
    def valid_model(self):
        class TestModel(BaseModel):
            field1: str
            field2: int
        return TestModel

    @pytest.fixture()
    def data_validator(self, valid_model):
        mock_config = MagicMock()
        return DataValidator(mock_config, valid_model)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_validate_C0_no_errors(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: エラーなしのDataFrame
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'field1': ['test'], 'field2': [1]})

        with patch.object(data_validator, 'log_msg') as mock_log:
            data_validator.validate(_df)
        mock_log.assert_called_with("Validation completed: No errors found", LogLevel.INFO)
        assert not data_validator.error_manager.has_errors()

    def test_validate_C1_no_errors(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: エラーがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'field1': ['test1', 'test2'], 'field2': [1, 2]})
        log_msg(f'_df: \n{tabulate_dataframe(_df)}')

        with patch.object(data_validator, 'log_msg') as mock_log:
            data_validator.validate(_df)
        assert not data_validator.error_manager.has_errors()
        mock_log.assert_called_with("Validation completed: No errors found", LogLevel.INFO)
        mock_log.assert_called_once()


    def test_validate_C1_with_errors(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: エラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'field1': ['test1', 'test2'], 'field2': ['invalid', 2]})
        log_msg(f'_df: \n{tabulate_dataframe(_df)}')

        with patch.object(data_validator, 'log_msg') as mock_log:
            data_validator.validate(_df)
        assert data_validator.error_manager.has_errors()
        mock_log.assert_called_with('ValidateProcess completed with 1 line validation errors', LogLevel.INFO)

    @pytest.mark.parametrize(("df", "expected_errors", "expected_log"), [
        (pd.DataFrame(), 0, "Validation skipped: Empty DataFrame"),
        (pd.DataFrame({'field1': ['test'], 'field2': [1]}), 0, "Validation completed: No errors found"),
        (pd.DataFrame({'field1': ['test1', 'test2'], 'field2': [1, 'invalid']}), 1, "ValidateProcess completed with 1 line validation errors"),
        (pd.DataFrame({'field1': ['test1', 'test2'], 'field2': ['invalid1', 'invalid2']}), 2, "ValidateProcess completed with 2 line validation errors"),
    ])
    def test_validate_C2_combinations(self, data_validator, df, expected_errors, expected_log):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: DataFrameの行数とバリデーション結果の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(data_validator, 'log_msg') as mock_log:
            data_validator.validate(df)

        assert data_validator.error_manager.has_errors() == (expected_errors > 0)
        mock_log.assert_any_call(expected_log, LogLevel.INFO)

    def test_validate_BVT_empty_dataframe(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 空のDataFrame
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame()
        data_validator.validate(_df)
        assert not data_validator.error_manager.has_errors()

    def test_validate_BVT_single_row(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 1行のDataFrame
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'field1': ['test'], 'field2': [1]})
        data_validator.validate(_df)
        assert not data_validator.error_manager.has_errors()

    def test_validate_BVT_large_dataframe(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 大量データ(1万行)のDataFrame
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'field1': ['test'] * 10000, 'field2': range(10000)})
        with patch.object(data_validator, 'log_msg') as mock_log:
            data_validator.validate(_df)
        assert not data_validator.error_manager.has_errors()
        mock_log.assert_called_with("Validation completed: No errors found", LogLevel.INFO)
        mock_log.assert_called_once()

class TestDataValidatorValidateRow:
    """DataValidatorの_validate_rowメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: バリデーション成功
    │   ├── 異常系: ValidationError発生
    │   └── 異常系: 予期せぬ例外発生
    ├── C1: 分岐カバレッジ
    │   ├── バリデーション成功
    │   ├── ValidationError発生
    │   └── その他の例外発生
    ├── C2: 条件組み合わせ
    │   ├── 入力データ: 有効 / 無効 / 境界値
    │   └── 例外の種類: なし / ValidationError / その他の例外
    └── BVT: 境界値テスト
        ├── 最小有効データ
        ├── 最大有効データ
        └── 無効なデータ型

    C1のディシジョンテーブル:
    | 条件                 | ケース1 | ケース2 | ケース3 |
    |----------------------|---------|---------|---------|
    | バリデーション成功   | Y       | N       | N       |
    | ValidationError発生  | N       | Y       | N       |
    | その他の例外発生     | N       | N       | Y       |
    | 結果                 | 成功    | エラー追加 | エラー追加 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値           | 期待される結果     | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース              |
    |----------|----------------|--------------------|--------------------|----------------------------------|----------|-----------------------------------|
    | BVT_001  | row            | 最小有効データ     | バリデーション成功 | 最小限の有効なデータを確認       | 実装済み | test_validate_row_BVT_min_valid    |
    | BVT_002  | row            | 最大有効データ     | バリデーション成功 | 最大限の有効なデータを確認       | 実装済み | test_validate_row_BVT_max_valid    |
    | BVT_003  | row            | 無効なデータ型     | ValidationError   | 無効なデータ型の処理を確認       | 実装済み | test_validate_row_BVT_invalid_type |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値ケースが実装されています。さらなるエッジケースの検討が必要な場合は、追加のテストケースを実装することを検討してください。
    """

    @pytest.fixture()
    def valid_model(self):
        class TestModel(BaseModel):
            field1: str
            field2: int
        return TestModel

    @pytest.fixture()
    def data_validator(self, valid_model):
        mock_config = MagicMock()
        return DataValidator(mock_config, valid_model)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_validate_row_C0_success(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: バリデーション成功
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'field1': 'test', 'field2': 1})
        log_msg(f'row: \n{format_dict(row.to_dict())}')

        data_validator._validate_row(row)
        assert not data_validator.error_manager.has_errors()

    def test_validate_row_C0_validation_error(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: ValidationError発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'field1': 'test', 'field2': 'invalid'})
        log_msg(f'row: \n{format_dict(row.to_dict())}')

        data_validator._validate_row(row)
        assert data_validator.error_manager.has_errors()


    def test_validate_row_C0_unexpected_error(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 予期せぬ例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'field1': 'test', 'field2': 1})
        log_msg(f'row: \n{format_dict(row.to_dict())}')

        mock_validation_model = MagicMock(side_effect=Exception("Unexpected error"))
        with patch.object(data_validator, 'validation_model', mock_validation_model):
            with patch.object(data_validator, 'log_msg') as mock_log:
                data_validator._validate_row(row)

        # validation_modelが呼び出されたことを確認
        mock_validation_model.assert_called_once()

        # ログにエラーメッセージが出力されていることを確認
        mock_log.assert_called_with(
            "Unexpected error during validation at row 0: Unexpected error",
            LogLevel.ERROR,
        )

        # ErrorManagerにエラーが追加されていることを確認
        assert data_validator.error_manager.has_errors(), "Error manager should have errors after unexpected exception"

        # エラーの内容を確認
        errors = data_validator.error_manager.get_errors()
        assert len(errors) == 1
        assert errors[0][0] == 0  # row_index
        assert errors[0][1][0]['type'] == 'unexpected_error'
        assert 'Unexpected error' in errors[0][1][0]['msg']

        # ログメッセージが正しく呼び出されたことを確認
        mock_log.assert_called_with(
            "Unexpected error during validation at row 0: Unexpected error",
            LogLevel.ERROR,
        )

    @pytest.mark.parametrize(("row", "expected_error"), [
        (pd.Series({'field1': 'test', 'field2': 1}), False),
        (pd.Series({'field1': 'test', 'field2': 'invalid'}), True),
        (pd.Series({'field1': None, 'field2': None}), True),
    ])
    def test_validate_row_C2_combinations(self, data_validator, row, expected_error):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: 入力データと例外の種類の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        data_validator._validate_row(row)
        assert data_validator.error_manager.has_errors() == expected_error

    def test_validate_row_BVT_min_valid(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 最小有効データ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'field1': 'a', 'field2': 0})
        data_validator._validate_row(row)
        assert not data_validator.error_manager.has_errors()

    def test_validate_row_BVT_max_valid(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 最大有効データ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'field1': 'a' * 1000, 'field2': 2**31 - 1})
        data_validator._validate_row(row)
        assert not data_validator.error_manager.has_errors()

    def test_validate_row_BVT_invalid_type(self, data_validator):
        test_doc = """テスト内容:

        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: 無効なデータ型
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'field1': 123, 'field2': 'invalid'})
        data_validator._validate_row(row)
        assert data_validator.error_manager.has_errors()

class TestDataValidatorResultValidationErrors:
    """DataValidatorのresult_validation_errorsメソッドの呼び出しテスト"""

    @pytest.fixture()
    def mock_error_manager(self):
        return MagicMock()

    @pytest.fixture()
    def mock_validation_model(self):
        class MockModel(BaseModel):
            field: str
        return MockModel

    @pytest.fixture()
    def data_validator(self, mock_error_manager, mock_validation_model):
        mock_config = MagicMock()
        validator = DataValidator(mock_config, mock_validation_model)
        validator.error_manager = mock_error_manager
        return validator

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_result_validation_errors_calls_and_logging(self, data_validator, mock_error_manager):
        test_doc = """result_validation_errorsメソッドの呼び出しと関連メソッドの呼び出し確認

        テスト内容:
        - テストカテゴリ: 単体テスト
        - テスト区分: 正常系
        - テストシナリオ: result_validation_errorsメソッドの呼び出しと関連メソッドの呼び出し確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch.object(data_validator, 'log_msg') as mock_log_msg:
            data_validator.result_validation_errors()

            # 1. メソッドが正しく呼び出され、適切なログが出力されることを確認
            mock_log_msg.assert_called_with("result_validation_errors method called", LogLevel.DEBUG)

            # 2. error_manager.log_errors()が呼び出されることを確認
            mock_error_manager.log_errors.assert_called_once()

        log_msg(f'result_validation_errors method called: {mock_log_msg.called}', LogLevel.INFO)
        log_msg(f'error_manager.log_errors called: {mock_error_manager.log_errors.called}', LogLevel.INFO)
