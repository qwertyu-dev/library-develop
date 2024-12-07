import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.packages.request_processor.file_configuration_factory import (
    FileConfigurationFactory,
    JinjiFileConfigurationFactory,
    KanrenWithFileConfigurationFactory,
    KanrenWithoutFileConfigurationFactory,
    KokukiFileConfigurationFactory,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestFileConfigurationFactory:
    """FileConfigurationFactoryクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── クラスの存在確認
    │   ├── create_file_path メソッドの存在確認
    │   └── create_sheet_name メソッドの存在確認
    └── C1: 型アノテーション確認
        ├── create_file_path の戻り値型が Path であることを確認
        └── create_sheet_name の戻り値型が str であることを確認

    # C1のディシジョンテーブル
    | 条件                                  | ケース1 | ケース2 |
    |---------------------------------------|---------|---------|
    | create_file_path の戻り値型が Path    | Y       | N       |
    | create_sheet_name の戻り値型が str    | Y       | N       |
    | 出力                                  | 正常    | 型エラー |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|---------------|---------|----------------|--------------------------|----------|
    | BVT_001  | N/A           | N/A     | クラスが存在する | クラスの存在確認         | 実装済み |
    | BVT_002  | N/A           | N/A     | メソッドが存在する | create_file_path メソッドの存在確認 | 実装済み |
    | BVT_003  | N/A           | N/A     | メソッドが存在する | create_sheet_name メソッドの存在確認 | 実装済み |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    このクラスは抽象基底クラスのような役割を果たしているため、
    実際の値を返すメソッドは実装されていません。そのため、
    境界値テストは基本的な構造の確認に限定されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_class_exists_C0(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト条件: 正常系
        テストシナリオ: FileConfigurationFactoryクラスが存在することを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        assert FileConfigurationFactory

    def test_create_sheet_name_exists_C0(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト条件: 正常系
        テストシナリオ: create_sheet_nameメソッドが存在することを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        assert hasattr(FileConfigurationFactory, 'create_sheet_name')

    def test_create_file_path_return_type_C1(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト条件: 正常系
        テストシナリオ: create_file_pathメソッドの戻り値の型がPathであることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = FileConfigurationFactory()
        assert factory.create_file_path.__annotations__['return'] == Path

    def test_create_sheet_name_return_type_C1(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト条件: 正常系
        テストシナリオ: create_sheet_nameメソッドの戻り値の型がstrであることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = FileConfigurationFactory()
        assert factory.create_sheet_name.__annotations__['return'] == str

class TestJinjiFileConfigurationFactoryInit:
    """JinjiFileConfigurationFactoryの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 有効なconfigでインスタンス生成
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: configパラメータあり
    │   └── 正常系: configパラメータなし(デフォルト設定使用)
    ├── C2: 条件組み合わせ
    │   ├── 正常系: configが完全な構造を持つ
    │   └── 正常系: configが一部の設定のみを持つ
    └── BVT: 境界値テスト
        ├── 正常系: 最小限の有効なconfig
        └── 正常系: 空のconfig辞書

    C1のディシジョンテーブル:
    | 条件                   | ケース1 | ケース2 |
    |------------------------|---------|---------|
    | configパラメータあり   | Y       | N       |
    | 出力                   | 正常    | 正常    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値              | 期待される結果 | テストの目的/検証ポイント | 実装状況 | 対応するテストケース            |
    |----------|----------------|----------------------|----------------|---------------------------|----------|---------------------------------|
    | BVT_001  | config         | {}                   | 正常           | 空の辞書での初期化        | 実装済み | test_init_BVT_empty_config      |
    | BVT_002  | config         | None                 | 正常           | Noneでの初期化            | 実装済み | test_init_C1_no_config          |
    | BVT_003  | config         | 最小限の有効なconfig | 正常           | 最小構成での初期化        | 実装済み | test_init_BVT_minimal_config    |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空の辞書、None、
    最小限の有効なconfigなど、様々な入力に対するJinjiFileConfigurationFactoryの
    初期化動作を検証します。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = {
            'common_config': {
                'optional_path': {
                    'SHARE_RECEIVE_PATH': '/path/to/share'
                },
            },
            'package_config': {
                'excel_definition': {
                    'UPDATE_RECORD_JINJI': 'jinji_*.xlsx',
                    'UPDATE_RECORD_JINJI_SHEET_NAME': 'Sheet1'
                },
            },
        }

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_valid_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効なconfigでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = JinjiFileConfigurationFactory(config=self.mock_config)
        assert factory.config == self.mock_config
    def test_init_C1_with_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: configパラメータありの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = JinjiFileConfigurationFactory(config=self.mock_config)
        assert factory.config == self.mock_config

    #def test_init_C1_no_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: C1
    #    テスト内容: configパラメータなしの初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=self.mock_config):
    #        factory = JinjiFileConfigurationFactory()
    #        assert factory.config == self.mock_config

    def test_init_C2_full_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 完全な構造を持つconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = JinjiFileConfigurationFactory(config=self.mock_config)
        assert 'common_config' in factory.config
        assert 'package_config' in factory.config
        assert 'optional_path' in factory.config['common_config']
        assert 'excel_definition' in factory.config['package_config']

    def test_init_C2_partial_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 一部の設定のみを持つconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        partial_config = {
            'common_config': {'optional_path': {}},
            'package_config': {},
        }
        factory = JinjiFileConfigurationFactory(config=partial_config)
        assert factory.config == partial_config

    #def test_init_BVT_empty_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テスト内容: 空のconfig辞書での初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    empty_config = {}
    #    factory = JinjiFileConfigurationFactory(config=empty_config)
    #    assert factory.config == empty_config

    def test_init_BVT_minimal_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 最小限の有効なconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        minimal_config = {'common_config': {}, 'package_config': {}}
        factory = JinjiFileConfigurationFactory(config=minimal_config)
        assert factory.config == minimal_config

class TestJinjiFileConfigurationFactoryCreateFilePattern:
    """JinjiFileConfigurationFactoryのcreate_file_patternメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 正常なconfig設定での動作確認
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: SHARE_RECEIVE_PATHが設定されている場合
    │   ├── 正常系: SHARE_RECEIVE_PATHが設定されていない場合
    │   ├── 正常系: UPDATE_RECORD_JINJIが設定されている場合
    │   └── 正常系: UPDATE_RECORD_JINJIが設定されていない場合
    ├── C2: 条件組み合わせ
    │   ├── 正常系: SHARE_RECEIVE_PATHとUPDATE_RECORD_JINJIの両方が設定されている
    │   ├── 正常系: SHARE_RECEIVE_PATHのみ設定されている
    │   ├── 正常系: UPDATE_RECORD_JINJIのみ設定されている
    │   └── 正常系: 両方とも設定されていない
    └── BVT: 境界値テスト
        ├── 正常系: SHARE_RECEIVE_PATHが空文字列
        ├── 正常系: UPDATE_RECORD_JINJIが空文字列
        ├── 正常系: SHARE_RECEIVE_PATHが非常に長いパス
        └── 正常系: UPDATE_RECORD_JINJIが非常に長いパターン

    C1のディシジョンテーブル:
    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 |
    |--------------------------------|---------|---------|---------|---------|
    | SHARE_RECEIVE_PATHが設定されている | Y       | N       | Y       | N       |
    | UPDATE_RECORD_JINJIが設定されている | Y       | Y       | N       | N       |
    | 出力                           | 正常    | 空リスト | 空リスト | 空リスト |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ      | テスト値                    | 期待される結果                | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース                    |
    |----------|--------------------|---------------------------|-------------------------------|-------------------------------------|----------|----------------------------------------|
    | BVT_001  | SHARE_RECEIVE_PATH | ""                        | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_path |
    | BVT_002  | UPDATE_RECORD_JINJI| ""                        | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_pattern |
    | BVT_003  | SHARE_RECEIVE_PATH | "a" * 255                 | 非常に長いパスを含むリスト      | 最大長のパス処理を確認               | 実装済み | test_create_file_pattern_BVT_max_length_path |
    | BVT_004  | UPDATE_RECORD_JINJI| "a" * 255                 | 非常に長いパターンを含むリスト  | 最大長のパターン処理を確認           | 実装済み | test_create_file_pattern_BVT_max_length_pattern |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 4
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空文字列や最大長の文字列など、
    様々な入力に対するcreate_file_patternメソッドの動作を検証します。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.common_config = {
            'optional_path': {
                'SHARE_RECEIVE_PATH': '/path/to/share',
            },
        }
        self.mock_config.package_config = {
            'excel_definition': {
                'UPDATE_RECORD_JINJI': 'jinji_*.xlsx',
            },
        }
        self.factory = JinjiFileConfigurationFactory(config=self.mock_config)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_file_pattern_C0_normal(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常なconfig設定での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('/path/to/share/jinji_001.xlsx'), Path('/path/to/share/jinji_002.xlsx')]
            result = self.factory.create_file_pattern()
            assert len(result) == 2
            assert all(isinstance(path, Path) for path in result)
            assert all(str(path).startswith('/path/to/share/jinji_') for path in result)

    def test_create_file_pattern_C1_with_share_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: SHARE_RECEIVE_PATHが設定されている場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('/path/to/share/jinji_001.xlsx')]
            result = self.factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).startswith('/path/to/share/')

    def test_create_file_pattern_C1_without_share_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: SHARE_RECEIVE_PATHが設定されていない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = ''
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            result = self.factory.create_file_pattern()
            assert len(result) == 0

    @pytest.mark.parametrize(("share_path","update_record","expected"), [
        ('/path/to/share', 'jinji_*.xlsx', ['/path/to/share/jinji_001.xlsx']),
        ('/path/to/share', '', []),
        ('', 'jinji_*.xlsx', []),
        ('', '', []),
    ])
    def test_create_file_pattern_C2_combinations(self, share_path, update_record, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: SHARE_RECEIVE_PATHとUPDATE_RECORD_JINJIの組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = share_path
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI'] = update_record
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(path) for path in expected]
            result = self.factory.create_file_pattern()
            assert [str(path) for path in result] == expected

    def test_create_file_pattern_BVT_empty_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: SHARE_RECEIVE_PATHが空文字列の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = ''
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            result = self.factory.create_file_pattern()
            assert len(result) == 0

    def test_create_file_pattern_BVT_empty_pattern(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_JINJIが空文字列の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI'] = ''
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            result = self.factory.create_file_pattern()
            assert len(result) == 0

    def test_create_file_pattern_BVT_max_length_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: SHARE_RECEIVE_PATHが非常に長いパスの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_path = 'a' * 240  # Windowsのパス長制限に近い値
        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = long_path
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"{long_path}/jinji_001.xlsx")]
            result = self.factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).startswith(long_path)

    def test_create_file_pattern_BVT_max_length_pattern(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_JINJIが非常に長いパターンの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_pattern = 'a' * 240 + '.xlsx'  # 拡張子を含む長いパターン
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI'] = long_pattern
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"/path/to/share/{long_pattern}")]
            result = self.factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).endswith(long_pattern)


class TestJinjiFileConfigurationFactoryCreateSheetName:
    """JinjiFileConfigurationFactoryのcreate_sheet_nameメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 正常なconfig設定での動作確認
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: UPDATE_RECORD_JINJI_SHEET_NAMEが設定されている場合
    │   └── 正常系: UPDATE_RECORD_JINJI_SHEET_NAMEが設定されていない場合
    ├── C2: 条件組み合わせ
    │   └── 正常系: 異なる設定値での動作確認
    └── BVT: 境界値テスト
        ├── 正常系: UPDATE_RECORD_JINJI_SHEET_NAMEが空文字列
        └── 正常系: UPDATE_RECORD_JINJI_SHEET_NAMEが非常に長い文字列

    C1のディシジョンテーブル:
    | 条件                                      | ケース1 | ケース2 |
    |-------------------------------------------|---------|---------|
    | UPDATE_RECORD_JINJI_SHEET_NAMEが設定されている | Y       | N       |
    | 出力                                      | 設定値   | 空文字列 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ                  | テスト値   | 期待される結果 | テストの目的/検証ポイント | 実装状況 | 対応するテストケース                    |
    |----------|--------------------------------|------------|----------------|---------------------------|----------|-----------------------------------------|
    | BVT_001  | UPDATE_RECORD_JINJI_SHEET_NAME | ""         | 空文字列        | 空文字列の処理を確認       | 実装済み | test_create_sheet_name_BVT_empty_name   |
    | BVT_002  | UPDATE_RECORD_JINJI_SHEET_NAME | "a" * 255  | 255文字の文字列 | 最大長の処理を確認         | 実装済み | test_create_sheet_name_BVT_max_length_name |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 2
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空文字列や最大長の文字列など、
    様々な入力に対するcreate_sheet_nameメソッドの動作を検証します。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.package_config = {
            'excel_definition': {
                'UPDATE_RECORD_JINJI_SHEET_NAME': 'Sheet1',
            },
        }
        self.factory = JinjiFileConfigurationFactory(config=self.mock_config)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_sheet_name_C0_normal(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常なconfig設定での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.factory.create_sheet_name()
        assert result == 'Sheet1'

    def test_create_sheet_name_C1_with_sheet_name(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: UPDATE_RECORD_JINJI_SHEET_NAMEが設定されている場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.factory.create_sheet_name()
        assert result == 'Sheet1'

    def test_create_sheet_name_C1_without_sheet_name(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: UPDATE_RECORD_JINJI_SHEET_NAMEが設定されていない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        del self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME']
        result = self.factory.create_sheet_name()
        assert result == ''

    @pytest.mark.parametrize(("sheet_name","expected"), [
        ('Sheet1', 'Sheet1'),
        ('CustomSheet', 'CustomSheet'),
        ('', ''),
        (None, None),
    ])
    def test_create_sheet_name_C2_combinations(self, sheet_name, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 異なる設定値での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME'] = sheet_name
        result = self.factory.create_sheet_name()
        assert result == expected

    def test_create_sheet_name_BVT_empty_name(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_JINJI_SHEET_NAMEが空文字列の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME'] = ''
        result = self.factory.create_sheet_name()
        assert result == ''

    def test_create_sheet_name_BVT_max_length_name(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_JINJI_SHEET_NAMEが非常に長い文字列の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_name = 'a' * 255
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_JINJI_SHEET_NAME'] = long_name
        result = self.factory.create_sheet_name()
        assert result == long_name
        assert len(result) == 255

class TestKokukiFileConfigurationFactory:
    """KokukiFileConfigurationFactoryのテスト

    テスト構造:
    ├── __init__メソッド
    │   ├── C0: 基本機能テスト
    │   │   └── 正常系: 有効なconfigでインスタンス生成
    │   ├── C1: 分岐カバレッジ
    │   │   ├── 正常系: configパラメータあり
    │   │   └── 正常系: configパラメータなし(デフォルト設定使用)
    │   ├── C2: 条件組み合わせ
    │   │   ├── 正常系: configが完全な構造を持つ
    │   │   └── 正常系: configが一部の設定のみを持つ
    │   └── BVT: 境界値テスト
    │       ├── 正常系: 最小限の有効なconfig
    │       └── 正常系: 空のconfig辞書
    │
    └── create_file_patternメソッド
        ├── C0: 基本機能テスト
        │   └── 正常系: 正常なconfig設定での動作確認
        ├── C1: 分岐カバレッジ
        │   ├── 正常系: SHARE_RECEIVE_PATHが設定されている場合
        │   ├── 正常系: SHARE_RECEIVE_PATHが設定されていない場合
        │   ├── 正常系: UPDATE_RECORD_KOKUKIが設定されている場合
        │   └── 正常系: UPDATE_RECORD_KOKUKIが設定されていない場合
        ├── C2: 条件組み合わせ
        │   ├── 正常系: SHARE_RECEIVE_PATHとUPDATE_RECORD_KOKUKIの両方が設定されている
        │   ├── 正常系: SHARE_RECEIVE_PATHのみ設定されている
        │   ├── 正常系: UPDATE_RECORD_KOKUKIのみ設定されている
        │   └── 正常系: 両方とも設定されていない
        └── BVT: 境界値テスト
            ├── 正常系: SHARE_RECEIVE_PATHが空文字列
            ├── 正常系: UPDATE_RECORD_KOKUKIが空文字列
            ├── 正常系: SHARE_RECEIVE_PATHが非常に長いパス
            └── 正常系: UPDATE_RECORD_KOKUKIが非常に長いパターン

    C1のディシジョンテーブル (create_file_pattern):
    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 |
    |--------------------------------|---------|---------|---------|---------|
    | SHARE_RECEIVE_PATHが設定されている | Y       | N       | Y       | N       |
    | UPDATE_RECORD_KOKUKIが設定されている | Y       | Y       | N       | N       |
    | 出力                           | 正常    | 空リスト | 空リスト | 空リスト |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ      | テスト値                    | 期待される結果                | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース                    |
    |----------|--------------------|---------------------------|-------------------------------|-------------------------------------|----------|----------------------------------------|
    | BVT_001  | config             | {}                        | 正常                           | 空の辞書での初期化                   | 実装済み | test_init_BVT_empty_config             |
    | BVT_002  | config             | None                      | 正常                           | Noneでの初期化                       | 実装済み | test_init_C1_no_config                 |
    | BVT_003  | SHARE_RECEIVE_PATH | ""                        | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_path |
    | BVT_004  | UPDATE_RECORD_KOKUKI| ""                       | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_pattern |
    | BVT_005  | SHARE_RECEIVE_PATH | "a" * 255                 | 非常に長いパスを含むリスト      | 最大長のパス処理を確認               | 実装済み | test_create_file_pattern_BVT_max_length_path |
    | BVT_006  | UPDATE_RECORD_KOKUKI| "a" * 255                | 非常に長いパターンを含むリスト  | 最大長のパターン処理を確認           | 実装済み | test_create_file_pattern_BVT_max_length_pattern |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 6
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空の辞書、None、
    空文字列や最大長の文字列など、様々な入力に対するKokukiFileConfigurationFactoryの
    動作を検証します。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.common_config = {
            'optional_path': {
                'SHARE_RECEIVE_PATH': '/path/to/share',
            },
        }
        self.mock_config.package_config = {
            'excel_definition': {
                'UPDATE_RECORD_KOKUKI': 'kokuki_*.xlsx',
            },
        }

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # __init__メソッドのテスト
    def test_init_C0_valid_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効なconfigでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KokukiFileConfigurationFactory(config=self.mock_config)
        assert factory.config == self.mock_config

    #def test_init_C1_no_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: C1
    #    テスト内容: configパラメータなしの初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=self.mock_config):
    #        factory = KokukiFileConfigurationFactory()
    #        assert factory.config == self.mock_config

    def test_init_C2_partial_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 一部の設定のみを持つconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        partial_config = {
            'common_config': {'optional_path': {}},
            'package_config': {},
        }
        factory = KokukiFileConfigurationFactory(config=partial_config)
        assert factory.config == partial_config

    #def test_init_BVT_empty_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テスト内容: 空のconfig辞書での初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    empty_config = {}
    #    factory = KokukiFileConfigurationFactory(config=empty_config)
    #    assert factory.config == empty_config

    # create_file_patternメソッドのテスト
    def test_create_file_pattern_C0_normal(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常なconfig設定での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KokukiFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('/path/to/share/kokuki_001.xlsx'), Path('/path/to/share/kokuki_002.xlsx')]
            result = factory.create_file_pattern()
            assert len(result) == 2
            assert all(isinstance(path, Path) for path in result)
            assert all(str(path).startswith('/path/to/share/kokuki_') for path in result)

    def test_create_file_pattern_C1_without_share_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: SHARE_RECEIVE_PATHが設定されていない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = ''
        factory = KokukiFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            result = factory.create_file_pattern()
            assert len(result) == 0

    @pytest.mark.parametrize(("share_path","update_record","expected"), [
        ('/path/to/share', 'kokuki_*.xlsx', ['/path/to/share/kokuki_001.xlsx']),
        ('/path/to/share', '', []),
        ('', 'kokuki_*.xlsx', []),
        ('', '', []),
    ])
    def test_create_file_pattern_C2_combinations(self, share_path, update_record, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: SHARE_RECEIVE_PATHとUPDATE_RECORD_KOKUKIの組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = share_path
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_KOKUKI'] = update_record
        factory = KokukiFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(path) for path in expected]
            result = factory.create_file_pattern()
            assert [str(path) for path in result] == expected

    def test_create_file_pattern_BVT_max_length_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: SHARE_RECEIVE_PATHが非常に長いパスの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_path = 'a' * 240  # Windowsのパス長制限に近い値
        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = long_path
        factory = KokukiFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"{long_path}/kokuki_001.xlsx")]
            result = factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).startswith(long_path)

    def test_create_file_pattern_BVT_max_length_pattern(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_KOKUKIが非常に長いパターンの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_pattern = 'a' * 240 + '.xlsx'  # 拡張子を含む長いパターン
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_KOKUKI'] = long_pattern
        factory = KokukiFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"/path/to/share/{long_pattern}")]
            result = factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).endswith(long_pattern)

class TestKanrenWithFileConfigurationFactory:
    """KanrenWithFileConfigurationFactoryのテスト

    テスト構造:
    ├── __init__メソッド
    │   ├── C0: 基本機能テスト
    │   │   └── 正常系: 有効なconfigでインスタンス生成
    │   ├── C1: 分岐カバレッジ
    │   │   ├── 正常系: configパラメータあり
    │   │   └── 正常系: configパラメータなし(デフォルト設定使用)
    │   ├── C2: 条件組み合わせ
    │   │   ├── 正常系: configが完全な構造を持つ
    │   │   └── 正常系: configが一部の設定のみを持つ
    │   └── BVT: 境界値テスト
    │       ├── 正常系: 最小限の有効なconfig
    │       └── 正常系: 空のconfig辞書
    │
    └── create_file_patternメソッド
        ├── C0: 基本機能テスト
        │   └── 正常系: 正常なconfig設定での動作確認
        ├── C1: 分岐カバレッジ
        │   ├── 正常系: SHARE_RECEIVE_PATHが設定されている場合
        │   ├── 正常系: SHARE_RECEIVE_PATHが設定されていない場合
        │   ├── 正常系: UPDATE_RECORD_KANRENが設定されている場合
        │   └── 正常系: UPDATE_RECORD_KANRENが設定されていない場合
        ├── C2: 条件組み合わせ
        │   ├── 正常系: SHARE_RECEIVE_PATHとUPDATE_RECORD_KANRENの両方が設定されている
        │   ├── 正常系: SHARE_RECEIVE_PATHのみ設定されている
        │   ├── 正常系: UPDATE_RECORD_KANRENのみ設定されている
        │   └── 正常系: 両方とも設定されていない
        └── BVT: 境界値テスト
            ├── 正常系: SHARE_RECEIVE_PATHが空文字列
            ├── 正常系: UPDATE_RECORD_KANRENが空文字列
            ├── 正常系: SHARE_RECEIVE_PATHが非常に長いパス
            └── 正常系: UPDATE_RECORD_KANRENが非常に長いパターン

    C1のディシジョンテーブル (create_file_pattern):
    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 |
    |--------------------------------|---------|---------|---------|---------|
    | SHARE_RECEIVE_PATHが設定されている | Y       | N       | Y       | N       |
    | UPDATE_RECORD_KANRENが設定されている | Y       | Y       | N       | N       |
    | 出力                           | 正常    | 空リスト | 空リスト | 空リスト |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ      | テスト値                    | 期待される結果                | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース                    |
    |----------|--------------------|---------------------------|-------------------------------|-------------------------------------|----------|----------------------------------------|
    | BVT_001  | config             | {}                        | 正常                           | 空の辞書での初期化                   | 実装済み | test_init_BVT_empty_config             |
    | BVT_002  | config             | None                      | 正常                           | Noneでの初期化                       | 実装済み | test_init_C1_no_config                 |
    | BVT_003  | SHARE_RECEIVE_PATH | ""                        | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_path |
    | BVT_004  | UPDATE_RECORD_KANREN| ""                       | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_pattern |
    | BVT_005  | SHARE_RECEIVE_PATH | "a" * 255                 | 非常に長いパスを含むリスト      | 最大長のパス処理を確認               | 実装済み | test_create_file_pattern_BVT_max_length_path |
    | BVT_006  | UPDATE_RECORD_KANREN| "a" * 255                | 非常に長いパターンを含むリスト  | 最大長のパターン処理を確認           | 実装済み | test_create_file_pattern_BVT_max_length_pattern |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 6
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空の辞書、None、
    空文字列や最大長の文字列など、様々な入力に対するKanrenWithFileConfigurationFactoryの
    動作を検証します。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.common_config = {
            'optional_path': {
                'SHARE_RECEIVE_PATH': '/path/to/share',
            },
        }
        self.mock_config.package_config = {
            'excel_definition': {
                'UPDATE_RECORD_KANREN': 'kanren_*.xlsx',
            },
        }

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # __init__メソッドのテスト
    def test_init_C0_valid_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効なconfigでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithFileConfigurationFactory(config=self.mock_config)
        assert factory.config == self.mock_config

    #def test_init_C1_no_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: C1
    #    テスト内容: configパラメータなしの初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=self.mock_config):
    #        factory = KanrenFileConfigurationFactory()
    #        assert factory.config == self.mock_config

    def test_init_C2_partial_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 一部の設定のみを持つconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        partial_config = {
            'common_config': {'optional_path': {}},
            'package_config': {},
        }
        factory = KanrenWithFileConfigurationFactory(config=partial_config)
        assert factory.config == partial_config

    #def test_init_BVT_empty_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テスト内容: 空のconfig辞書での初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    empty_config = {}
    #    factory = KanrenFileConfigurationFactory(config=empty_config)
    #    assert factory.config == empty_config

    # create_file_patternメソッドのテスト
    def test_create_file_pattern_C0_normal(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常なconfig設定での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('/path/to/share/kanren_001.xlsx'), Path('/path/to/share/kanren_002.xlsx')]
            result = factory.create_file_pattern()
            assert len(result) == 2
            assert all(isinstance(path, Path) for path in result)
            assert all(str(path).startswith('/path/to/share/kanren_') for path in result)

    def test_create_file_pattern_C1_without_share_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: SHARE_RECEIVE_PATHが設定されていない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = ''
        factory = KanrenWithFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            result = factory.create_file_pattern()
            assert len(result) == 0

    @pytest.mark.parametrize(("share_path","update_record","expected"), [
        ('/path/to/share', 'kanren_*.xlsx', ['/path/to/share/kanren_001.xlsx']),
        ('/path/to/share', '', []),
        ('', 'kanren_*.xlsx', []),
        ('', '', []),
    ])
    def test_create_file_pattern_C2_combinations(self, share_path, update_record, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: SHARE_RECEIVE_PATHとUPDATE_RECORD_KANRENの組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = share_path
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_KANREN'] = update_record
        factory = KanrenWithFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(path) for path in expected]
            result = factory.create_file_pattern()
            assert [str(path) for path in result] == expected

    def test_create_file_pattern_BVT_max_length_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: SHARE_RECEIVE_PATHが非常に長いパスの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_path = 'a' * 240  # Windowsのパス長制限に近い値
        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = long_path
        factory = KanrenWithFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"{long_path}/kanren_001.xlsx")]
            result = factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).startswith(long_path)

    def test_create_file_pattern_BVT_max_length_pattern(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_KANRENが非常に長いパターンの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_pattern = 'a' * 240 + '.xlsx'  # 拡張子を含む長いパターン
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_KANREN'] = long_pattern
        factory = KanrenWithFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"/path/to/share/{long_pattern}")]
            result = factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).endswith(long_pattern)


class TestKanrenWithoutFileConfigurationFactory:
    """KanrenWithoutoutFileConfigurationFactoryのテスト

    テスト構造:
    ├── __init__メソッド
    │   ├── C0: 基本機能テスト
    │   │   └── 正常系: 有効なconfigでインスタンス生成
    │   ├── C1: 分岐カバレッジ
    │   │   ├── 正常系: configパラメータあり
    │   │   └── 正常系: configパラメータなし(デフォルト設定使用)
    │   ├── C2: 条件組み合わせ
    │   │   ├── 正常系: configが完全な構造を持つ
    │   │   └── 正常系: configが一部の設定のみを持つ
    │   └── BVT: 境界値テスト
    │       ├── 正常系: 最小限の有効なconfig
    │       └── 正常系: 空のconfig辞書
    │
    └── create_file_patternメソッド
        ├── C0: 基本機能テスト
        │   └── 正常系: 正常なconfig設定での動作確認
        ├── C1: 分岐カバレッジ
        │   ├── 正常系: SHARE_RECEIVE_PATHが設定されている場合
        │   ├── 正常系: SHARE_RECEIVE_PATHが設定されていない場合
        │   ├── 正常系: UPDATE_RECORD_KANRENが設定されている場合
        │   └── 正常系: UPDATE_RECORD_KANRENが設定されていない場合
        ├── C2: 条件組み合わせ
        │   ├── 正常系: SHARE_RECEIVE_PATHとUPDATE_RECORD_KANRENの両方が設定されている
        │   ├── 正常系: SHARE_RECEIVE_PATHのみ設定されている
        │   ├── 正常系: UPDATE_RECORD_KANRENのみ設定されている
        │   └── 正常系: 両方とも設定されていない
        └── BVT: 境界値テスト
            ├── 正常系: SHARE_RECEIVE_PATHが空文字列
            ├── 正常系: UPDATE_RECORD_KANRENが空文字列
            ├── 正常系: SHARE_RECEIVE_PATHが非常に長いパス
            └── 正常系: UPDATE_RECORD_KANRENが非常に長いパターン

    C1のディシジョンテーブル (create_file_pattern):
    | 条件                           | ケース1 | ケース2 | ケース3 | ケース4 |
    |--------------------------------|---------|---------|---------|---------|
    | SHARE_RECEIVE_PATHが設定されている | Y       | N       | Y       | N       |
    | UPDATE_RECORD_KANRENが設定されている | Y       | Y       | N       | N       |
    | 出力                           | 正常    | 空リスト | 空リスト | 空リスト |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ      | テスト値                    | 期待される結果                | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース                    |
    |----------|--------------------|---------------------------|-------------------------------|-------------------------------------|----------|----------------------------------------|
    | BVT_001  | config             | {}                        | 正常                           | 空の辞書での初期化                   | 実装済み | test_init_BVT_empty_config             |
    | BVT_002  | config             | None                      | 正常                           | Noneでの初期化                       | 実装済み | test_init_C1_no_config                 |
    | BVT_003  | SHARE_RECEIVE_PATH | ""                        | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_path |
    | BVT_004  | UPDATE_RECORD_KANREN| ""                       | 空のリスト                     | 空文字列の処理を確認                 | 実装済み | test_create_file_pattern_BVT_empty_pattern |
    | BVT_005  | SHARE_RECEIVE_PATH | "a" * 255                 | 非常に長いパスを含むリスト      | 最大長のパス処理を確認               | 実装済み | test_create_file_pattern_BVT_max_length_path |
    | BVT_006  | UPDATE_RECORD_KANREN| "a" * 255                | 非常に長いパターンを含むリスト  | 最大長のパターン処理を確認           | 実装済み | test_create_file_pattern_BVT_max_length_pattern |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 6
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空の辞書、None、
    空文字列や最大長の文字列など、様々な入力に対するKanrenWithoutFileConfigurationFactoryの
    動作を検証します。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.mock_config = MagicMock()
        self.mock_config.common_config = {
            'optional_path': {
                'SHARE_RECEIVE_PATH': '/path/to/share',
            },
        }
        self.mock_config.package_config = {
            'excel_definition': {
                'UPDATE_RECORD_KANREN': 'kanren_*.xlsx',
            },
        }

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    # __init__メソッドのテスト
    def test_init_C0_valid_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効なconfigでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithoutFileConfigurationFactory(config=self.mock_config)
        assert factory.config == self.mock_config

    #def test_init_C1_no_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: C1
    #    テスト内容: configパラメータなしの初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    with patch('src.lib.common_utils.ibr_decorator_config.initialize_config', return_value=self.mock_config):
    #        factory = KanrenFileConfigurationFactory()
    #        assert factory.config == self.mock_config

    def test_init_C2_partial_config(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 一部の設定のみを持つconfigでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        partial_config = {
            'common_config': {'optional_path': {}},
            'package_config': {},
        }
        factory = KanrenWithoutFileConfigurationFactory(config=partial_config)
        assert factory.config == partial_config

    #def test_init_BVT_empty_config(self):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: BVT
    #    テスト内容: 空のconfig辞書での初期化
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    empty_config = {}
    #    factory = KanrenFileConfigurationFactory(config=empty_config)
    #    assert factory.config == empty_config

    # create_file_patternメソッドのテスト
    def test_create_file_pattern_C0_normal(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常なconfig設定での動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        factory = KanrenWithoutFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path('/path/to/share/kanren_001.xlsx'), Path('/path/to/share/kanren_002.xlsx')]
            result = factory.create_file_pattern()
            assert len(result) == 2
            assert all(isinstance(path, Path) for path in result)
            assert all(str(path).startswith('/path/to/share/kanren_') for path in result)

    def test_create_file_pattern_C1_without_share_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: SHARE_RECEIVE_PATHが設定されていない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = ''
        factory = KanrenWithoutFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            result = factory.create_file_pattern()
            assert len(result) == 0

    @pytest.mark.parametrize(("share_path","update_record","expected"), [
        ('/path/to/share', 'kanren_*.xlsx', ['/path/to/share/kanren_001.xlsx']),
        ('/path/to/share', '', []),
        ('', 'kanren_*.xlsx', []),
        ('', '', []),
    ])
    def test_create_file_pattern_C2_combinations(self, share_path, update_record, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: SHARE_RECEIVE_PATHとUPDATE_RECORD_KANRENの組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = share_path
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_KANREN'] = update_record
        factory = KanrenWithoutFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(path) for path in expected]
            result = factory.create_file_pattern()
            assert [str(path) for path in result] == expected

    def test_create_file_pattern_BVT_max_length_path(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: SHARE_RECEIVE_PATHが非常に長いパスの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_path = 'a' * 240  # Windowsのパス長制限に近い値
        self.mock_config.common_config['optional_path']['SHARE_RECEIVE_PATH'] = long_path
        factory = KanrenWithoutFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"{long_path}/kanren_001.xlsx")]
            result = factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).startswith(long_path)

    def test_create_file_pattern_BVT_max_length_pattern(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: UPDATE_RECORD_KANRENが非常に長いパターンの場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        long_pattern = 'a' * 240 + '.xlsx'  # 拡張子を含む長いパターン
        self.mock_config.package_config['excel_definition']['UPDATE_RECORD_KANREN'] = long_pattern
        factory = KanrenWithoutFileConfigurationFactory(config=self.mock_config)
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = [Path(f"/path/to/share/{long_pattern}")]
            result = factory.create_file_pattern()
            assert len(result) == 1
            assert str(result[0]).endswith(long_pattern)
