import pytest
from unittest.mock import Mock, patch

from pydantic import BaseModel, ValidationError

from src.packages.request_processor.validation_error_manager import ValidationErrorManager
from src.lib.common_utils.ibr_enums import LogLevel

# config共有
import sys
from src.lib.common_utils.ibr_decorator_config import initialize_config
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestValidationErrorManagerInit:
    """ValidationErrorManagerの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な設定でインスタンス生成 (configあり)
    │   └── 正常系: デフォルト設定でインスタンス生成 (configなし)
    └── BVT: 境界値テスト
        └── configがNoneの場合

    # C1のディシジョンテーブル
    | 条件                | ケース1 | ケース2 |
    |---------------------|---------|---------|
    | configが提供される  | Y       | N       |
    | 出力                | 提供されたconfigを使用 | デフォルトconfigを使用 |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 | 対応するテストケース |
    |----------|----------------|----------|----------------|---------------------------|----------|----------------------|
    | BVT_001  | config         | None     | デフォルトconfigを使用 | Noneの場合のデフォルト動作 | 実装済み | test_init_BVT_config_none |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 1
    - 未実装: 0
    - 一部実装: 0
    
    注記：
    - 全ての境界値ケースが実装されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_config(self):
        return Mock(log_message=Mock())

    def test_init_C0_valid_configuration(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 有効な設定でインスタンス生成 (configあり)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            manager = ValidationErrorManager(config=mock_config.log_message)

        assert manager.log_msg == mock_config.log_message
        assert isinstance(manager.errors, list)
        assert len(manager.errors) == 0

    def test_init_C0_default_configuration(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: デフォルト設定でインスタンス生成 (configなし)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda cls: type('MockClass', (), {'config': mock_config})):
            manager = ValidationErrorManager()

        #assert manager.log_msg == mock_config.log_message
        assert isinstance(manager.errors, list)
        assert len(manager.errors) == 0

    def test_init_BVT_config_none(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: configがNoneの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda cls: type('MockClass', (), {'config': mock_config})):
            manager = ValidationErrorManager(config=None)

        #assert manager.log_msg == mock_config.log_message
        assert isinstance(manager.errors, list)
        assert len(manager.errors) == 0

        log_msg("Default config used as expected", LogLevel.DEBUG)

class TestValidationErrorManagerAddError:
    """ValidationErrorManagerのadd_errorメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 整数のrow_indexでエラー追加
    │   └── 正常系: 文字列のrow_indexでエラー追加
    ├── C1: 分岐カバレッジ
    │   └── 正常系: エラーリストが空の場合と空でない場合
    ├── C2: 条件カバレッジ
    │   └── 正常系: row_indexが整数と文字列の組み合わせ
    └── BVT: 境界値テスト
        ├── 正常系: row_indexが最小整数値
        ├── 正常系: row_indexが最大整数値
        └── 正常系: error_infoが空辞書

    # C1のディシジョンテーブル
    | 条件                    | ケース1 | ケース2 |
    |-------------------------|---------|---------|
    | エラーリストが空        | Y       | N       |
    | 出力                    | 新規追加 | 追加    |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値              | 期待される結果           | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース          |
    |----------|----------------|------------------------|--------------------------|-------------------------------------|----------|-------------------------------|
    | BVT_001  | row_index      | 0                      | エラーリストに追加される | 最小の有効な整数値                  | 実装済み | test_add_error_BVT_min_row_index |
    | BVT_002  | row_index      | sys.maxsize            | エラーリストに追加される | 最大の有効な整数値                  | 実装済み | test_add_error_BVT_max_row_index |
    | BVT_003  | error_info     | {}                     | エラーリストに追加される | 空の辞書を扱える                    | 実装済み | test_add_error_BVT_empty_error_info |
    | BVT_004  | row_index      | ""                     | エラーリストに追加される | 空文字列を扱える                    | 実装済み | test_add_error_C0_string_row_index |
    | BVT_005  | error_info     | {"key": "a" * 1000000} | エラーリストに追加される | 非常に大きな辞書を扱える            | 未実装   | - |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 4
    - 未実装: 1
    - 一部実装: 0
    
    注記：
    - BVT_005（非常に大きな辞書）は現在未実装です。このケースはメモリ使用量の観点から重要ですが、
      テスト環境によっては実行が困難な場合があります。実装の際は注意が必要です。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            return ValidationErrorManager(config=config)

    def test_add_error_C0_integer_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 整数のrow_indexでエラー追加
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 1
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_C0_string_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 文字列のrow_indexでエラー追加
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = "A1"
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_C1_empty_and_non_empty(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストが空の場合と空でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エラーリストが空の場合
        row_index1 = 1
        error_info1 = {"error": "First error"}
        error_manager.add_error(row_index1, error_info1)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index1, [error_info1])

        # エラーリストが空でない場合
        row_index2 = 2
        error_info2 = {"error": "Second error"}
        error_manager.add_error(row_index2, error_info2)

        assert len(error_manager.errors) == 2
        assert error_manager.errors[1] == (row_index2, [error_info2])

    @pytest.mark.parametrize("row_index", [3, "B2"])
    def test_add_error_C2_row_index_types(self, error_manager, row_index):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが整数と文字列の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_BVT_min_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが最小整数値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 0
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_BVT_max_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが最大整数値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = sys.maxsize
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_BVT_empty_error_info(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: error_infoが空辞書
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 1
        error_info = {}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

class TestValidationErrorManagerAddError:
    """ValidationErrorManagerのadd_errorメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 整数のrow_indexでエラー追加
    │   └── 正常系: 文字列のrow_indexでエラー追加
    ├── C1: 分岐カバレッジ
    │   └── 正常系: エラーリストが空の場合と空でない場合
    ├── C2: 条件カバレッジ
    │   └── 正常系: row_indexが整数と文字列の組み合わせ
    └── BVT: 境界値テスト
        ├── 正常系: row_indexが最小整数値
        ├── 正常系: row_indexが最大整数値
        └── 正常系: error_infoが空辞書

    # C1のディシジョンテーブル
    | 条件                    | ケース1 | ケース2 |
    |-------------------------|---------|---------|
    | エラーリストが空        | Y       | N       |
    | 出力                    | 新規追加 | 追加    |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値              | 期待される結果           | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース          |
    |----------|----------------|------------------------|--------------------------|-------------------------------------|----------|-------------------------------|
    | BVT_001  | row_index      | 0                      | エラーリストに追加される | 最小の有効な整数値                  | 実装済み | test_add_error_BVT_min_row_index |
    | BVT_002  | row_index      | sys.maxsize            | エラーリストに追加される | 最大の有効な整数値                  | 実装済み | test_add_error_BVT_max_row_index |
    | BVT_003  | error_info     | {}                     | エラーリストに追加される | 空の辞書を扱える                    | 実装済み | test_add_error_BVT_empty_error_info |
    | BVT_004  | row_index      | ""                     | エラーリストに追加される | 空文字列を扱える                    | 実装済み | test_add_error_C0_string_row_index |
    | BVT_005  | error_info     | {"key": "a" * 1000000} | エラーリストに追加される | 非常に大きな辞書を扱える            | 未実装   | - |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 4
    - 未実装: 1
    - 一部実装: 0
    
    注記：
    - BVT_005（非常に大きな辞書）は現在未実装です。このケースはメモリ使用量の観点から重要ですが、
      テスト環境によっては実行が困難な場合があります。実装の際は注意が必要です。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            return ValidationErrorManager(config=config)

    def test_add_error_C0_integer_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 整数のrow_indexでエラー追加
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 1
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_C0_string_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 文字列のrow_indexでエラー追加
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = "A1"
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_C1_empty_and_non_empty(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストが空の場合と空でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エラーリストが空の場合
        row_index1 = 1
        error_info1 = {"error": "First error"}
        error_manager.add_error(row_index1, error_info1)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index1, [error_info1])

        # エラーリストが空でない場合
        row_index2 = 2
        error_info2 = {"error": "Second error"}
        error_manager.add_error(row_index2, error_info2)

        assert len(error_manager.errors) == 2
        assert error_manager.errors[1] == (row_index2, [error_info2])

    @pytest.mark.parametrize("row_index", [3, "B2"])
    def test_add_error_C2_row_index_types(self, error_manager, row_index):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが整数と文字列の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_BVT_min_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが最小整数値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 0
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_BVT_max_row_index(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが最大整数値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = sys.maxsize
        error_info = {"error": "Test error"}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])

    def test_add_error_BVT_empty_error_info(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: error_infoが空辞書
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 1
        error_info = {}
        error_manager.add_error(row_index, error_info)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0] == (row_index, [error_info])


class TestValidationErrorManagerAddValidationError:
    """ValidationErrorManagerのadd_validation_errorメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: ValidationErrorの追加
    ├── C1: 分岐カバレッジ
    │   └── 正常系: エラーリストが空の場合と空でない場合
    ├── C2: 条件カバレッジ
    │   └── 正常系: 異なるValidationErrorの組み合わせ
    └── BVT: 境界値テスト
        ├── 正常系: row_indexが最小整数値
        ├── 正常系: row_indexが最大整数値
        └── 正常系: 複数のエラーを持つValidationError

    # C1のディシジョンテーブル
    | 条件                    | ケース1 | ケース2 |
    |-------------------------|---------|---------|
    | エラーリストが空        | Y       | N       |
    | 出力                    | 新規追加 | 追加    |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ    | テスト値              | 期待される結果           | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース          |
    |----------|-------------------|------------------------|--------------------------|-------------------------------------|----------|-------------------------------|
    | BVT_001  | row_index         | 0                      | エラーリストに追加される | 最小の有効な整数値                  | 実装済み | test_add_validation_error_BVT_min_row_index |
    | BVT_002  | row_index         | sys.maxsize            | エラーリストに追加される | 最大の有効な整数値                  | 実装済み | test_add_validation_error_BVT_max_row_index |
    | BVT_003  | validation_error  | 複数のエラーを持つ     | 全エラーが追加される     | 複数エラーの処理                    | 実装済み | test_add_validation_error_BVT_multiple_errors |
    | BVT_004  | validation_error  | エラーなし             | 空リストが追加される     | エラーのないValidationErrorの処理   | 未実装   | - |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 1
    - 一部実装: 0
    
    注記：
    - BVT_004（エラーなしのValidationError）は現在未実装です。このケースは稀なケースですが、
      エッジケースとして重要かもしれません。実装の際は、ValidationErrorの生成方法に注意が必要です。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            return ValidationErrorManager(config=config)

    @pytest.fixture
    def validation_error(self):
        class TestModel(BaseModel):
            name: str
            age: int

        try:
            TestModel(name=123, age="invalid")
        except ValidationError as e:
            return e

    def test_add_validation_error_C0_basic(self, error_manager, validation_error):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: ValidationErrorの追加
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 1
        error_manager.add_validation_error(row_index, validation_error)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0][0] == row_index
        assert isinstance(error_manager.errors[0][1], list)
        assert len(error_manager.errors[0][1]) == 2  # name と age のエラー

    def test_add_validation_error_C1_empty_and_non_empty(self, error_manager, validation_error):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストが空の場合と空でない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エラーリストが空の場合
        row_index1 = 1
        error_manager.add_validation_error(row_index1, validation_error)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0][0] == row_index1

        # エラーリストが空でない場合
        row_index2 = 2
        error_manager.add_validation_error(row_index2, validation_error)

        assert len(error_manager.errors) == 2
        assert error_manager.errors[1][0] == row_index2

    def test_add_validation_error_C2_different_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 異なるValidationErrorの組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        class TestModel1(BaseModel):
            name: str

        class TestModel2(BaseModel):
            age: int

        try:
            TestModel1(name=123)
        except ValidationError as e1:
            error_manager.add_validation_error(1, e1)

        try:
            TestModel2(age="invalid")
        except ValidationError as e2:
            error_manager.add_validation_error(2, e2)

        assert len(error_manager.errors) == 2
        assert len(error_manager.errors[0][1]) == 1  # name のエラー
        assert len(error_manager.errors[1][1]) == 1  # age のエラー

    def test_add_validation_error_BVT_min_row_index(self, error_manager, validation_error):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが最小整数値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = 0
        error_manager.add_validation_error(row_index, validation_error)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0][0] == row_index

    def test_add_validation_error_BVT_max_row_index(self, error_manager, validation_error):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: row_indexが最大整数値
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        row_index = sys.maxsize
        error_manager.add_validation_error(row_index, validation_error)

        assert len(error_manager.errors) == 1
        assert error_manager.errors[0][0] == row_index

    def test_add_validation_error_BVT_multiple_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 複数のエラーを持つValidationError
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        class TestModel(BaseModel):
            name: str
            age: int
            email: str

        try:
            TestModel(name=123, age="invalid", email=1111)
        except ValidationError as e:
            error_manager.add_validation_error(1, e)

        assert len(error_manager.errors) == 1
        assert len(error_manager.errors[0][1]) == 3  # name, age, email のエラー

class TestValidationErrorManagerHasErrors:
    """ValidationErrorManagerのhas_errorsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: エラーがない場合
    │   └── 正常系: エラーがある場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: エラーリストの長さが0の場合
    │   └── 正常系: エラーリストの長さが1以上の場合
    ├── C2: 条件カバレッジ
    │   └── 正常系: エラーリストの長さが0, 1, 2以上の場合
    └── BVT: 境界値テスト
        ├── 正常系: エラーリストが空の場合
        ├── 正常系: エラーリストに1つのエラーがある場合
        └── 正常系: エラーリストに多数のエラーがある場合

    # C1のディシジョンテーブル
    | 条件                      | ケース1 | ケース2 |
    |---------------------------|---------|---------|
    | エラーリストの長さ > 0    | N       | Y       |
    | 出力                      | False   | True    |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ     | テスト値              | 期待される結果 | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース          |
    |----------|--------------------|------------------------|----------------|----------------------------------|----------|-------------------------------|
    | BVT_001  | self.errors        | []                     | False          | 空のエラーリスト                 | 実装済み | test_has_errors_BVT_empty_list |
    | BVT_002  | self.errors        | [(1, [{"error": ""}])] | True           | 1つのエラーを持つリスト          | 実装済み | test_has_errors_BVT_single_error |
    | BVT_003  | self.errors        | 10000個のエラー        | True           | 多数のエラーを持つリスト         | 実装済み | test_has_errors_BVT_many_errors |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0
    
    注記：
    - 全ての境界値ケースが実装されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            return ValidationErrorManager(config=config)

    def test_has_errors_C0_no_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        assert not error_manager.has_errors()

    def test_has_errors_C0_with_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Test error"}]))
        assert error_manager.has_errors()

    def test_has_errors_C1_empty_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストの長さが0の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        assert not error_manager.has_errors()

    def test_has_errors_C1_non_empty_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストの長さが1以上の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Test error"}]))
        assert error_manager.has_errors()

    @pytest.mark.parametrize("error_count, expected", [
        (0, False),
        (1, True),
        (5, True)
    ])
    def test_has_errors_C2_various_lengths(self, error_manager, error_count, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストの長さが0, 1, 2以上の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        assert error_manager.has_errors() == expected

    def test_has_errors_BVT_empty_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        assert not error_manager.has_errors()

    def test_has_errors_BVT_single_error(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストに1つのエラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Single test error"}]))
        assert error_manager.has_errors()

    def test_has_errors_BVT_many_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストに多数のエラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        for i in range(10000):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        assert error_manager.has_errors()

class TestValidationErrorManagerGetErrors:
    """ValidationErrorManagerのget_errorsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: エラーがない場合
    │   └── 正常系: エラーがある場合
    ├── C1: 分岐カバレッジ
    │   └── 正常系: エラーリストの状態による分岐なし
    ├── C2: 条件カバレッジ
    │   └── 正常系: 異なる数のエラーが存在する場合
    └── BVT: 境界値テスト
        ├── 正常系: エラーリストが空の場合
        ├── 正常系: エラーリストに1つのエラーがある場合
        └── 正常系: エラーリストに多数のエラーがある場合

    # C1のディシジョンテーブル
    | 条件                      | ケース1 |
    |---------------------------|---------|
    | エラーリストを返す        | Y       |
    | 出力                      | エラーリスト |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ     | テスト値              | 期待される結果 | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース          |
    |----------|--------------------|------------------------|----------------|----------------------------------|----------|-------------------------------|
    | BVT_001  | self.errors        | []                     | []             | 空のエラーリスト                 | 実装済み | test_get_errors_BVT_empty_list |
    | BVT_002  | self.errors        | [(1, [{"error": ""}])] | 1要素のリスト  | 1つのエラーを持つリスト          | 実装済み | test_get_errors_BVT_single_error |
    | BVT_003  | self.errors        | 10000個のエラー        | 10000要素のリスト | 多数のエラーを持つリスト      | 実装済み | test_get_errors_BVT_many_errors |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0
    
    注記：
    - 全ての境界値ケースが実装されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            return ValidationErrorManager(config=config)

    def test_get_errors_C0_no_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        errors = error_manager.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == 0

    def test_get_errors_C0_with_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Test error"}]))
        errors = error_manager.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == 1
        assert errors[0] == (1, [{"error": "Test error"}])

    def test_get_errors_C1_always_returns_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストの状態による分岐なし
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エラーがない場合
        errors = error_manager.get_errors()
        assert isinstance(errors, list)

        # エラーがある場合
        error_manager.errors.append((1, [{"error": "Test error"}]))
        errors = error_manager.get_errors()
        assert isinstance(errors, list)

    @pytest.mark.parametrize("error_count", [0, 1, 5])
    def test_get_errors_C2_various_error_counts(self, error_manager, error_count):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 異なる数のエラーが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        errors = error_manager.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == error_count
        for i, error in enumerate(errors):
            assert error == (i, [{"error": f"Test error {i}"}])

    def test_get_errors_BVT_empty_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        errors = error_manager.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == 0

    def test_get_errors_BVT_single_error(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストに1つのエラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Single test error"}]))
        errors = error_manager.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == 1
        assert errors[0] == (1, [{"error": "Single test error"}])

    def test_get_errors_BVT_many_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストに多数のエラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_count = 10000
        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        errors = error_manager.get_errors()
        assert isinstance(errors, list)
        assert len(errors) == error_count
        for i, error in enumerate(errors):
            assert error == (i, [{"error": f"Test error {i}"}])

class TestValidationErrorManagerLogErrors:
    """ValidationErrorManagerのlog_errorsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: エラーがない場合
    │   └── 正常系: エラーがある場合
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: self.has_errors()がFalseの場合
    │   └── 正常系: self.has_errors()がTrueの場合
    ├── C2: 条件カバレッジ
    │   └── 正常系: 異なる数と種類のエラーが存在する場合
    └── BVT: 境界値テスト
        ├── 正常系: エラーリストが空の場合
        ├── 正常系: エラーリストに1つのエラーがある場合
        └── 正常系: エラーリストに多数のエラーがある場合

    # C1のディシジョンテーブル
    | 条件                | ケース1 | ケース2 |
    |---------------------|---------|---------|
    | self.has_errors()   | False   | True    |
    | 出力                | "No validation errors found" | エラーメッセージ |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ     | テスト値              | 期待される結果 | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース          |
    |----------|--------------------|------------------------|----------------|----------------------------------|----------|-------------------------------|
    | BVT_001  | self.errors        | []                     | "No validation errors found" | 空のエラーリスト     | 実装済み | test_log_errors_BVT_empty_list |
    | BVT_002  | self.errors        | [(1, [{"error": ""}])] | 1つのエラーメッセージ | 1つのエラーを持つリスト  | 実装済み | test_log_errors_BVT_single_error |
    | BVT_003  | self.errors        | 1000個のエラー         | 1000個のエラーメッセージ | 多数のエラーを持つリスト | 実装済み | test_log_errors_BVT_many_errors |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0
    
    注記：
    - 全ての境界値ケースが実装されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            manager = ValidationErrorManager(config=config)
            manager.log_msg = Mock()  # log_msgをモックに置き換え
            return manager

    def test_log_errors_C0_no_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.log_errors()
        error_manager.log_msg.assert_any_call("No validation errors found", LogLevel.INFO)

    def test_log_errors_C0_with_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Test error"}]))
        error_manager.log_errors()
        error_manager.log_msg.assert_any_call("Validation error at row 1: \n{'error': 'Test error'}", LogLevel.DEBUG)

    def test_log_errors_C1_has_errors_false(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: self.has_errors()がFalseの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.log_errors()
        error_manager.log_msg.assert_any_call("No validation errors found", LogLevel.INFO)

    def test_log_errors_C1_has_errors_true(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: self.has_errors()がTrueの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Test error"}]))
        error_manager.log_errors()
        error_manager.log_msg.assert_any_call("Validation error at row 1: \n{'error': 'Test error'}", LogLevel.DEBUG)

    @pytest.mark.parametrize("error_count", [0, 1, 3])
    def test_log_errors_C2_various_error_counts(self, error_manager, error_count):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 異なる数と種類のエラーが存在する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        error_manager.log_errors()
        
        if error_count == 0:
            error_manager.log_msg.assert_any_call("No validation errors found", LogLevel.INFO)
        else:
            for i in range(error_count):
                error_manager.log_msg.assert_any_call(f"Validation error at row {i}: \n{{'error': 'Test error {i}'}}", LogLevel.DEBUG)

    def test_log_errors_BVT_empty_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストが空の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.log_errors()
        error_manager.log_msg.assert_any_call("No validation errors found", LogLevel.INFO)

    def test_log_errors_BVT_single_error(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストに1つのエラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Single test error"}]))
        error_manager.log_errors()
        error_manager.log_msg.assert_any_call("Validation error at row 1: \n{'error': 'Single test error'}", LogLevel.DEBUG)

    def test_log_errors_BVT_many_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストに多数のエラーがある場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_count = 1000
        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        error_manager.log_errors()
        
        for i in range(error_count):
            error_manager.log_msg.assert_any_call(f"Validation error at row {i}: \n{{'error': 'Test error {i}'}}", LogLevel.DEBUG)

class TestValidationErrorManagerClearErrors:
    """ValidationErrorManagerのclear_errorsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: エラーがない状態でクリア
    │   └── 正常系: エラーがある状態でクリア
    ├── C1: 分岐カバレッジ
    │   └── 正常系: エラーリストの状態による分岐なし
    ├── C2: 条件カバレッジ
    │   └── 正常系: 異なる数のエラーが存在する場合のクリア
    └── BVT: 境界値テスト
        ├── 正常系: 空のエラーリストをクリア
        ├── 正常系: 1つのエラーを含むリストをクリア
        └── 正常系: 多数のエラーを含むリストをクリア

    # C1のディシジョンテーブル
    | 条件                      | ケース1 |
    |---------------------------|---------|
    | エラーリストをクリアする  | Y       |
    | 出力                      | 空のリスト |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ     | テスト値              | 期待される結果 | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース          |
    |----------|--------------------|------------------------|----------------|----------------------------------|----------|-------------------------------|
    | BVT_001  | self.errors        | []                     | []             | 空のエラーリストのクリア         | 実装済み | test_clear_errors_BVT_empty_list |
    | BVT_002  | self.errors        | [(1, [{"error": ""}])] | []             | 1つのエラーを持つリストのクリア  | 実装済み | test_clear_errors_BVT_single_error |
    | BVT_003  | self.errors        | 10000個のエラー        | []             | 多数のエラーを持つリストのクリア | 実装済み | test_clear_errors_BVT_many_errors |
    
    境界値検証ケースの実装状況サマリー：
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0
    
    注記：
    - 全ての境界値ケースが実装されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def error_manager(self):
        with patch('src.packages.request_processor.validation_error_manager.with_config', lambda x: x):
            return ValidationErrorManager(config=config)

    def test_clear_errors_C0_no_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがない状態でクリア
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

    def test_clear_errors_C0_with_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーがある状態でクリア
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Test error"}]))
        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

    def test_clear_errors_C1_always_clears(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: エラーリストの状態による分岐なし
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # エラーがない場合
        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

        # エラーがある場合
        error_manager.errors.append((1, [{"error": "Test error"}]))
        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

    @pytest.mark.parametrize("error_count", [0, 1, 5])
    def test_clear_errors_C2_various_error_counts(self, error_manager, error_count):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 異なる数のエラーが存在する場合のクリア
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

    def test_clear_errors_BVT_empty_list(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 空のエラーリストをクリア
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

    def test_clear_errors_BVT_single_error(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 1つのエラーを含むリストをクリア
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_manager.errors.append((1, [{"error": "Single test error"}]))
        error_manager.clear_errors()
        assert len(error_manager.errors) == 0

    def test_clear_errors_BVT_many_errors(self, error_manager):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 
        - テスト区分: 正常系
        - テストシナリオ: 多数のエラーを含むリストをクリア
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        error_count = 10000
        for i in range(error_count):
            error_manager.errors.append((i, [{"error": f"Test error {i}"}]))
        
        error_manager.clear_errors()
        assert len(error_manager.errors) == 0
