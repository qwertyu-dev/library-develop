# config共有
import sys
from unittest.mock import MagicMock, patch

import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.packages.request_processor.factory_registry import FactoryRegistry, FactoryRegistryError

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestFactoryRegistry__init__:
    """FactoryRegistryの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な設定でインスタンス生成
    │   └── 異常系: 無効な設定でのエラー処理
    ├── C1: 分岐カバレッジ
    │   ├── config引数がNoneの場合
    │   └── config引数が指定されている場合
    ├── C2: 条件カバレッジ
    │   ├── 全てのファクトリータイプが正常にロードされる場合
    │   ├── 一部のファクトリータイプのロードに失敗する場合
    │   └── 全てのファクトリータイプのロードに失敗する場合
    └── BVT: 境界値テスト
        ├── 最小限の設定でのインスタンス生成
        └── 大量のファクトリー定義がある場合の処理

    C1のディシジョンテーブル:
    | 条件                     | DT_01 | DT_02 | DT_03 | DT_04 |
    |--------------------------|-------|-------|-------|-------|
    | config引数がNone         | Y     | N     | N     | N     |
    | model_factoryロード成功  | Y     | Y     | N     | N     |
    | processor_factoryロード成功| Y     | Y     | Y     | N     |
    | file_configuration_factoryロード成功| Y     | Y     | Y     | N     |
    | 結果                     | 成功   | 成功   | 一部失敗| 全て失敗 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント       | 実装状況 | 対応するテストケース     |
    |----------|----------------|----------------------------|----------------|----------------------------------|----------|--------------------------|
    | BVT_001  | config         | None                       | 成功           | Noneの場合のデフォルト動作確認   | 実装済み | test_init_C1_DT_01_config_none |
    | BVT_002  | config         | {}                         | 成功           | 空の辞書での最小限の設定確認     | 実装済み | test_init_BVT_minimal_config |
    | BVT_003  | config         | 大量のファクトリー定義を含む辞書 | 成功     | 大量データ処理の性能確認         | 実装済み | test_init_BVT_large_config |
    """

    def setup_method(self):
        # テスト定義をログ出力
        log_msg("test start", LogLevel.INFO)

        self.mock_config = MagicMock()
        self.mock_config.log_message = MagicMock()
        self.mock_config.package_config = {
            'model_factory': {'key1': 'path1'},
            'processor_factory': {'key2': 'path2'},
            'file_configuration_factory': {'key3': 'path3'}
        }

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_load_factories(self):
        with patch.object(FactoryRegistry, '_load_factories', return_value={'key': 'value'}):
            yield

    def test_init_C0_valid_config(self, mock_load_factories):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 有効な設定でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        registry = FactoryRegistry(self.mock_config)
        assert registry.config == self.mock_config
        assert registry.log_msg == self.mock_config.log_message
        assert registry.model_factories == {'key': 'value'}
        assert registry.processor_factories == {'key': 'value'}
        assert registry.file_configuration_factories == {'key': 'value'}

    def test_init_C1_DT_01_config_none(self, mock_load_factories):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: config引数がNoneの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.request_processor.factory_registry.with_config', lambda x: x):
            registry = FactoryRegistry()
            assert registry.config is not None
            assert registry.log_msg is not None

    def test_init_C2_partial_load_failure(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 一部のファクトリータイプのロードに失敗する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        def mock_load_factories(factory_type):
            if factory_type == 'model_factory':
                raise ImportError("Mock import error")
            return {'key': 'value'}

        with patch.object(FactoryRegistry, '_load_factories', side_effect=mock_load_factories):
            with pytest.raises(ImportError):
                FactoryRegistry(self.mock_config)

    def test_init_BVT_minimal_config(self, mock_load_factories):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 最小限の設定でのインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_config = MagicMock()
        minimal_config.package_config = {
            'model_factory': {},
            'processor_factory': {},
            'file_configuration_factory': {}
        }
        registry = FactoryRegistry(minimal_config)
        assert registry.model_factories == {'key': 'value'}
        assert registry.processor_factories == {'key': 'value'}
        assert registry.file_configuration_factories == {'key': 'value'}

    def test_init_BVT_large_config(self, mock_load_factories):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 大量のファクトリー定義がある場合の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        large_config = MagicMock()
        large_config.package_config = {
            'model_factory': {f'key{i}': f'path{i}' for i in range(1000)},
            'processor_factory': {f'key{i}': f'path{i}' for i in range(1000)},
            'file_configuration_factory': {f'key{i}': f'path{i}' for i in range(1000)}
        }
        registry = FactoryRegistry(large_config)
        assert len(registry.model_factories) == 1
        assert len(registry.processor_factories) == 1
        assert len(registry.file_configuration_factories) == 1

class TestFactoryRegistry_load_factories:
    """FactoryRegistryの_load_factoriesメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なファクトリー定義でのロード
    │   └── 異常系: 無効なファクトリー定義でのエラー処理
    ├── C1: 分岐カバレッジ
    │   ├── ImportErrorが発生する場合
    │   └── AttributeErrorが発生する場合
    ├── C2: 条件カバレッジ
    │   ├── 存在するモジュールと存在するクラス
    │   ├── 存在するモジュールと存在しないクラス
    │   └── 存在しないモジュール
    └── BVT: 境界値テスト
        ├── 空のファクトリー定義
        └── 大量のファクトリー定義

    C1のディシジョンテーブル:
    | 条件                 | DT_01 | DT_02 | DT_03 | DT_04 |
    |----------------------|-------|-------|-------|-------|
    | モジュールが存在する | Y     | Y     | N     | Y     |
    | クラスが存在する     | Y     | N     | -     | Y     |
    | ImportError発生      | N     | N     | Y     | N     |
    | AttributeError発生   | N     | Y     | N     | N     |
    | 結果                 | 成功   | 失敗   | 失敗   | 成功   |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント     | 実装状況 | 対応するテストケース     |
    |----------|----------------|----------------------------|----------------|------------------------------|----------|--------------------------|
    | BVT_001  | factory_type   | 空の辞書                   | 空の辞書       | 空のファクトリー定義の処理   | 実装済み | test_load_factories_BVT_empty_definition |
    | BVT_002  | factory_type   | 1000個のファクトリー定義   | 1000個の辞書   | 大量データの処理性能         | 実装済み | test_load_factories_BVT_large_definition |
    """

    def setup_method(self):
        # テスト定義をログ出力
        log_msg("test start", LogLevel.INFO)

        self.mock_config = MagicMock()
        self.mock_config.package_config = {
            'model_factory': {
                'key1': 'module1.class1',
                'key2': 'module2.class2'
            },
            'processor_factory': {
                'key3': 'module3.class3',
                'key4': 'module4.class4'
            },
            'file_configuration_factory': {
                'key5': 'module5.class5',
                'key6': 'module6.class6'
            },
            'test_factory': {
                'key7': 'module7.class7',
                'key8': 'module8.class8'
            }
        }
        # _load_factoriesメソッドをモック化
        with patch.object(FactoryRegistry, '_load_factories', return_value={}):
            self.registry = FactoryRegistry(self.mock_config)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_load_factories_C0_valid_definition(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 有効なファクトリー定義でのロード
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_class = MagicMock()
            mock_import.return_value = mock_module
            mock_module.class1 = mock_class
            mock_module.class2 = mock_class

            result = self.registry._load_factories('model_factory')
            assert len(result) == 2
            assert 'key1' in result
            assert 'key2' in result
            assert isinstance(result['key1'], MagicMock)
            assert isinstance(result['key2'], MagicMock)

    def test_load_factories_C1_DT_03_import_error(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: ImportErrorが発生する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('importlib.import_module', side_effect=ImportError("Mock ImportError")):
            with pytest.raises(ImportError):
                self.registry._load_factories('model_factory')

    def test_load_factories_C1_DT_02_attribute_error(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: AttributeErrorが発生する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_import.return_value = mock_module
            del mock_module.class1

            with pytest.raises(AttributeError):
                self.registry._load_factories('model_factory')

    def test_load_factories_C2_existing_module_existing_class(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 存在するモジュールと存在するクラス
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_class = MagicMock()
            mock_import.return_value = mock_module
            mock_module.class1 = mock_class
            mock_module.class2 = mock_class

            result = self.registry._load_factories('model_factory')
            assert len(result) == 2
            assert all(isinstance(v, MagicMock) for v in result.values())


    def test_load_factories_BVT_empty_definition(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空のファクトリー定義
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.package_config['empty_factory'] = {}
        result = self.registry._load_factories('empty_factory')
        assert result == {}

    def test_load_factories_BVT_large_definition(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 大量のファクトリー定義
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        large_factory = {f'key{i}': f'module{i}.class{i}' for i in range(1000)}
        self.mock_config.package_config['large_factory'] = large_factory

        with patch('importlib.import_module') as mock_import:
            mock_module = MagicMock()
            mock_class = MagicMock()
            mock_import.return_value = mock_module
            for i in range(1000):
                setattr(mock_module, f'class{i}', mock_class)

            result = self.registry._load_factories('large_factory')
            assert len(result) == 1000
            assert all(isinstance(v, MagicMock) for v in result.values())

class TestFactoryRegistry_get_processor_factory:
    """FactoryRegistryのget_processor_factoryメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 存在するキーでの取得
    │   └── 異常系: 存在しないキーでの取得
    ├── C1: 分岐カバレッジ (分岐なし)
    ├── C2: 条件カバレッジ (条件なし)
    └── BVT: 境界値テスト
        ├── 空文字列キー
        └── 長い文字列キー

    C1のディシジョンテーブル:
    | 条件               | DT_01 | DT_02 |
    |--------------------|-------|-------|
    | キーが存在する     | Y     | N     |
    | 結果               | 成功   | None  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント     | 実装状況 | 対応するテストケース     |
    |----------|----------------|----------------------------|----------------|------------------------------|----------|--------------------------|
    | BVT_001  | key            | ""                         | None           | 空文字列キーの処理           | 実装済み | test_get_processor_factory_BVT_empty_key |
    | BVT_002  | key            | "a" * 1000                 | None           | 非常に長いキーの処理         | 実装済み | test_get_processor_factory_BVT_long_key |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.package_config = {
            'processor_factory': {
                'key1': 'module1.class1',
                'key2': 'module2.class2'
            }
        }
        with patch.object(FactoryRegistry, '_load_factories', return_value={
            'key1': MagicMock(),
            'key2': MagicMock()
        }):
            self.registry = FactoryRegistry(self.mock_config)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_get_processor_factory_C0_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 存在するキーでの取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_processor_factory('key1')
        assert result is not None
        assert isinstance(result, MagicMock)

    def test_get_processor_factory_C0_non_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 存在しないキーでの取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_processor_factory('non_existing_key')
        assert result is None

    def test_get_processor_factory_C1_DT_01_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: 存在するキーでの取得 (DT_01)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_processor_factory('key1')
        assert result is not None
        assert isinstance(result, MagicMock)

    def test_get_processor_factory_C1_DT_02_non_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: 存在しないキーでの取得 (DT_02)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_processor_factory('non_existing_key')
        assert result is None

    def test_get_processor_factory_BVT_empty_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空文字列キー
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_processor_factory('')
        assert result is None

    def test_get_processor_factory_BVT_long_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 長い文字列キー
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_key = 'a' * 1000
        result = self.registry.get_processor_factory(long_key)
        assert result is None

class TestFactoryRegistry_get_model_factory:
    """FactoryRegistryのget_model_factoryメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 存在するキーでの取得
    │   └── 異常系: 存在しないキーでの取得
    ├── C1: 分岐カバレッジ (分岐なし)
    ├── C2: 条件カバレッジ (条件なし)
    └── BVT: 境界値テスト
        ├── 空文字列キー
        └── 長い文字列キー

    C1のディシジョンテーブル:
    | 条件               | DT_01 | DT_02 |
    |--------------------|-------|-------|
    | キーが存在する     | Y     | N     |
    | 結果               | 成功   | None  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント     | 実装状況 | 対応するテストケース     |
    |----------|----------------|----------------------------|----------------|------------------------------|----------|--------------------------|
    | BVT_001  | key            | ""                         | None           | 空文字列キーの処理           | 実装済み | test_get_model_factory_BVT_empty_key |
    | BVT_002  | key            | "a" * 1000                 | None           | 非常に長いキーの処理         | 実装済み | test_get_model_factory_BVT_long_key |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.package_config = {
            'model_factory': {
                'key1': 'module1.class1',
                'key2': 'module2.class2'
            },
            'processor_factory': {
                'key3': 'module3.class3',
                'key4': 'module4.class4'
            },
            'file_configuration_factory': {
                'key5': 'module5.class5',
                'key6': 'module6.class6'
            }
        }
        with patch.object(FactoryRegistry, '_load_factories', return_value={
            'key1': MagicMock(),
            'key2': MagicMock(),
            'key3': MagicMock(),
            'key4': MagicMock(),
            'key5': MagicMock(),
            'key6': MagicMock()
        }):
            self.registry = FactoryRegistry(self.mock_config)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_get_model_factory_C0_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 存在するキーでの取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_model_factory('key1')
        assert result is not None
        assert isinstance(result, MagicMock)

    def test_get_model_factory_C0_non_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 存在しないキーでの取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_model_factory('non_existing_key')
        assert result is None

    def test_get_model_factory_C1_DT_01_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: 存在するキーでの取得 (DT_01)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_model_factory('key1')
        assert result is not None
        assert isinstance(result, MagicMock)

    def test_get_model_factory_C1_DT_02_non_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: 存在しないキーでの取得 (DT_02)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_model_factory('non_existing_key')
        assert result is None

    def test_get_model_factory_BVT_empty_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空文字列キー
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_model_factory('')
        assert result is None

    def test_get_model_factory_BVT_long_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 長い文字列キー
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_key = 'a' * 1000
        result = self.registry.get_model_factory(long_key)
        assert result is None


class TestFactoryRegistry_get_file_configuration_factory:
    """FactoryRegistryのget_file_configuration_factoryメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 存在するキーでの取得
    │   └── 異常系: 存在しないキーでの取得
    ├── C1: 分岐カバレッジ (分岐なし)
    ├── C2: 条件カバレッジ (条件なし)
    └── BVT: 境界値テスト
        ├── 空文字列キー
        └── 長い文字列キー

    C1のディシジョンテーブル:
    | 条件               | DT_01 | DT_02 |
    |--------------------|-------|-------|
    | キーが存在する     | Y     | N     |
    | 結果               | 成功   | None  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果 | テストの目的/検証ポイント     | 実装状況 | 対応するテストケース     |
    |----------|----------------|----------------------------|----------------|------------------------------|----------|--------------------------|
    | BVT_001  | key            | ""                         | None           | 空文字列キーの処理           | 実装済み | test_get_file_configuration_factory_BVT_empty_key |
    | BVT_002  | key            | "a" * 1000                 | None           | 非常に長いキーの処理         | 実装済み | test_get_file_configuration_factory_BVT_long_key |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.package_config = {
            'model_factory': {
                'key1': 'module1.class1',
                'key2': 'module2.class2',
            },
            'processor_factory': {
                'key3': 'module3.class3',
                'key4': 'module4.class4',
            },
            'file_configuration_factory': {
                'key5': 'module5.class5',
                'key6': 'module6.class6',
            },
        }
        with patch.object(FactoryRegistry, '_load_factories') as mock_load_factories:
            mock_load_factories.side_effect = lambda factory_type: {
                'model_factory': {'key1': MagicMock(), 'key2': MagicMock()},
                'processor_factory': {'key3': MagicMock(), 'key4': MagicMock()},
                'file_configuration_factory': {'key5': MagicMock(), 'key6': MagicMock()},
            }[factory_type]
            self.registry = FactoryRegistry(self.mock_config)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_get_file_configuration_factory_C0_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 存在するキーでの取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_file_configuration_factory('key5')
        assert result is not None
        assert isinstance(result, MagicMock)


    def test_get_file_configuration_factory_C0_non_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 存在しないキーでの取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_file_configuration_factory('non_existing_key')
        assert result is None

    def test_get_file_configuration_factory_C1_DT_01_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: 存在するキーでの取得 (DT_01)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_file_configuration_factory('key5')
        assert result is not None
        assert isinstance(result, MagicMock)

    def test_get_file_configuration_factory_C1_DT_02_non_existing_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1, DT
        テストケース: 存在しないキーでの取得 (DT_02)
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_file_configuration_factory('non_existing_key')
        assert result is None

    def test_get_file_configuration_factory_BVT_empty_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 空文字列キー
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.registry.get_file_configuration_factory('')
        assert result is None

    def test_get_file_configuration_factory_BVT_long_key(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストケース: 長い文字列キー
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_key = 'a' * 1000
        result = self.registry.get_file_configuration_factory(long_key)
        assert result is None
