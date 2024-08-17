import os
import pytest
from pathlib import Path
import pandas as pd
import time
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher, FileConfig
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestTableSearcherInit:
    """TableSearcherの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: デフォルト値での初期化
    │   └── 正常系: カスタム値での初期化
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: file_pathが指定されている場合
    │   └── 正常系: file_pathが指定されていない場合
    └── C2: 条件カバレッジ
        ├── 異常系: 無効なテーブル名（空文字列）
        ├── 異常系: 無効なテーブル名（空白文字のみ）
        └── 異常系: 無効なファイルパス
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_df(self):
        return pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})

    @pytest.fixture
    def mock_file_path(self, tmp_path, mock_df):
        file_path = tmp_path / "test_table.pkl"
        mock_df.to_pickle(file_path)
        return file_path

    def test_init_C0_default_values(self, mock_file_path, mock_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: デフォルト値での初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        searcher = TableSearcher("test_table.pkl", file_path=mock_file_path)
        
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == mock_file_path
        assert isinstance(searcher.df, pd.DataFrame)
        assert not searcher.df.empty

    def test_init_C0_custom_values(self, mock_file_path, mock_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: カスタム値での初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        custom_df_loader = lambda x: pd.read_pickle(x).head(2)
        searcher = TableSearcher("test_table.pkl", file_path=mock_file_path, df_loader=custom_df_loader)
        
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == mock_file_path
        assert len(searcher.df) == 2

    def test_init_C1_file_path_specified(self, mock_file_path, mock_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: file_pathが指定されている場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        searcher = TableSearcher("test_table.pkl", file_path=mock_file_path)
        
        assert searcher.file_path == mock_file_path

    def test_init_C1_file_path_not_specified(self, mocker, tmp_path, mock_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: file_pathが指定されていない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # テスト用のpickleファイルを作成
        test_file = tmp_path / "test_table.pkl"
        mock_df.to_pickle(test_file)

        # _default_get_table_pathをモック化
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_table_path', return_value=str(tmp_path))

        searcher = TableSearcher("test_table.pkl")
        
        assert searcher.file_path == test_file
        assert isinstance(searcher.df, pd.DataFrame)
        assert not searcher.df.empty

    def test_init_C2_invalid_table_name_empty(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効なテーブル名（空文字列）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError) as exc_info:
            TableSearcher("")
        
        assert "テーブル名は空であってはいけません。" in str(exc_info.value)

    def test_init_C2_invalid_table_name_whitespace(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効なテーブル名（空白文字のみ）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError) as exc_info:
            TableSearcher("   ")
        
        assert "テーブル名は空であってはいけません。" in str(exc_info.value)

    def test_init_C2_invalid_file_path(self):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効なファイルパス
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(FileNotFoundError):
            TableSearcher("test_table.pkl", file_path=Path("/non/existent/path/test_table.pkl"))

import pytest
from pathlib import Path
import pandas as pd
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher, FileConfig
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestTableSearcherCreateForProduction:
    """TableSearcherのcreate_for_productionメソッドのテスト

    テスト構造:
    └── C0: 基本機能テスト
        └── 正常系: 本番環境用インスタンス作成
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_create_for_production_C0_basic_functionality(self, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 本番環境用インスタンス作成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 内部メソッドをモック化
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_table_path', return_value="/mock/path")
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_file_modified_time', return_value=1234567890.0)
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table', return_value=(pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']}), False))
        
        # Path.exists()とPath.stat()をモック化
        mocker.patch.object(Path, 'exists', return_value=True)
        mocker.patch.object(Path, 'stat', return_value=mocker.Mock(st_mtime=1234567890.0))

        searcher = TableSearcher.create_for_production("test_table.pkl")
        
        assert isinstance(searcher, TableSearcher)
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == Path("/mock/path/test_table.pkl")
        assert isinstance(searcher.df, pd.DataFrame)
        assert not searcher.df.empty
        assert searcher.last_modified_time == 1234567890.0

class TestTableSearcherCreateForTest:
    """TableSearcherのcreate_for_testメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: テスト環境用インスタンス作成（全パラメータ指定）
    └── C1: 分岐カバレッジ
        ├── 正常系: テスト環境用インスタンス作成（オプショナルパラメータなし）
        ├── 正常系: テスト環境用インスタンス作成（一部オプショナルパラメータあり - パターン1）
        └── 正常系: テスト環境用インスタンス作成（一部オプショナルパラメータあり - パターン2）

    | 条件                         | ケース1 | ケース2 | ケース3 | ケース4 |
    |------------------------------|---------|---------|---------|---------|
    | file_pathが指定される        | Y       | Y       | Y       | Y       |
    | df_loaderが指定される        | Y       | Y       | Y       | Y       |
    | get_table_pathが指定される   | Y       | N       | Y       | N       |
    | get_file_modified_timeが指定 | Y       | N       | N       | Y       |
    | load_tableが指定される       | Y       | N       | N       | N       |
    | 出力                         | 全て    | 一部    | 一部    | 一部    |
    |                              | カスタム| デフォ  | 混合    | 混合    |
    |                              |         | ルト    |         |         |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_df(self):
        return pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})

    def test_create_for_test_C0_all_parameters(self, mock_df, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: テスト環境用インスタンス作成（全パラメータ指定）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_file_path = Path("/mock/test_path/test_table.pkl")
        mock_df_loader = lambda _: mock_df
        mock_get_table_path = lambda: "/mock/test_path"
        mock_get_file_modified_time = lambda: 1234567890.0
        mock_load_table = lambda: (mock_df, False)

        searcher = TableSearcher.create_for_test(
            "test_table.pkl",
            mock_file_path,
            mock_df_loader,
            mock_get_table_path,
            mock_get_file_modified_time,
            mock_load_table
        )

        assert isinstance(searcher, TableSearcher)
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == mock_file_path
        assert searcher.df.equals(mock_df)
        assert searcher.last_modified_time == 1234567890.0
        assert searcher._df_loader == mock_df_loader
        assert searcher._get_table_path == mock_get_table_path
        assert searcher._get_file_modified_time == mock_get_file_modified_time
        assert searcher._load_table == mock_load_table

    def test_create_for_test_C1_no_optional_parameters(self, mock_df, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: テスト環境用インスタンス作成（オプショナルパラメータなし）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_file_path = Path("/mock/test_path/test_table.pkl")
        mock_df_loader = lambda _: mock_df

        # デフォルトメソッドのモック
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_table_path', return_value="/mock/test_path")
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_file_modified_time', return_value=1234567890.0)
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table', return_value=(mock_df, False))

        searcher = TableSearcher.create_for_test(
            "test_table.pkl",
            mock_file_path,
            mock_df_loader
        )

        assert isinstance(searcher, TableSearcher)
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == mock_file_path
        assert searcher.df.equals(mock_df)
        assert searcher.last_modified_time == 1234567890.0
        assert searcher._df_loader == mock_df_loader
        assert searcher._get_table_path == TableSearcher._default_get_table_path
        assert searcher._get_file_modified_time == TableSearcher._default_get_file_modified_time
        assert searcher._load_table == TableSearcher._default_load_table

    def test_create_for_test_C1_partial_parameters_pattern1(self, mock_df, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: テスト環境用インスタンス作成（一部オプショナルパラメータあり - パターン1）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_file_path = Path("/mock/test_path/test_table.pkl")
        mock_df_loader = lambda _: mock_df
        mock_get_table_path = lambda: "/mock/custom_path"

        # デフォルトメソッドのモック
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_file_modified_time', return_value=1234567890.0)
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table', return_value=(mock_df, False))

        searcher = TableSearcher.create_for_test(
            "test_table.pkl",
            mock_file_path,
            mock_df_loader,
            mock_get_table_path
        )

        assert isinstance(searcher, TableSearcher)
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == mock_file_path
        assert searcher.df.equals(mock_df)
        assert searcher.last_modified_time == 1234567890.0
        assert searcher._df_loader == mock_df_loader
        assert searcher._get_table_path == mock_get_table_path
        assert searcher._get_file_modified_time == TableSearcher._default_get_file_modified_time
        assert searcher._load_table == TableSearcher._default_load_table

    def test_create_for_test_C1_partial_parameters_pattern2(self, mock_df, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: テスト環境用インスタンス作成（一部オプショナルパラメータあり - パターン2）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_file_path = Path("/mock/test_path/test_table.pkl")
        mock_df_loader = lambda _: mock_df
        mock_get_file_modified_time = lambda: 9876543210.0

        # デフォルトメソッドのモック
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_table_path', return_value="/mock/test_path")
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table', return_value=(mock_df, False))

        searcher = TableSearcher.create_for_test(
            "test_table.pkl",
            mock_file_path,
            mock_df_loader,
            None,  # get_table_path
            mock_get_file_modified_time
        )

        assert isinstance(searcher, TableSearcher)
        assert searcher.table_name == "test_table.pkl"
        assert searcher.file_path == mock_file_path
        assert searcher.df.equals(mock_df)
        assert searcher.last_modified_time == 9876543210.0
        assert searcher._df_loader == mock_df_loader
        assert searcher._get_table_path == TableSearcher._default_get_table_path
        assert searcher._get_file_modified_time == mock_get_file_modified_time
        assert searcher._load_table == TableSearcher._default_load_table

class TestTableSearcherDefaultGetTablePath:
    """TableSearcherの_default_get_table_pathメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: デフォルトパス取得
    └── C1: 分岐カバレッジ
        ├── 正常系: 環境変数使用時のパス取得
        └── 正常系: 環境変数未設定時のデフォルトパス取得

    | 条件                     | ケース1  | ケース2  |
    |--------------------------|----------|----------|
    | 環境変数が設定されている | Y        | N        |
    | 出力                     | カスタム | デフォ   |
    |                          | パス     | ルトパス |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_project_root(self, tmp_path):
        return tmp_path / "mock_project_root"

    @pytest.fixture
    def mock_table_searcher(self, mocker, mock_project_root):
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_file_modified_time', return_value=1234567890.0)
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table', return_value=(None, False))
        
        # __file__の値をモック
        mock_file = mock_project_root / "src" / "lib" / "common_utils" / "ibr_pickled_table_searcher.py"
        mocker.patch('src.lib.common_utils.ibr_pickled_table_searcher.__file__', mock_file)

        return TableSearcher("test_table.pkl")

    def test_default_get_table_path_C0_basic_functionality(self, mock_project_root, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: デフォルトパス取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 環境変数をクリア
        mocker.patch.dict(os.environ, {}, clear=True)

        result = mock_table_searcher._default_get_table_path()

        expected_path = f"{mock_project_root}/{FileConfig.DEFAULT_EXEC_PATTERN}/{FileConfig.TABLE_DIR_NAME}"
        assert result == str(expected_path)

    def test_default_get_table_path_C1_with_env_var(self, mock_project_root, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 環境変数使用時のパス取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 環境変数を設定
        mocker.patch.dict(os.environ, {"EXEC_PATTERN": "custom_src"})

        result = mock_table_searcher._default_get_table_path()

        expected_path = f"{mock_project_root}/custom_src/{FileConfig.TABLE_DIR_NAME}"
        assert result == str(expected_path)

    def test_default_get_table_path_C1_without_env_var(self, mock_project_root, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 環境変数未設定時のデフォルトパス取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 環境変数をクリア
        mocker.patch.dict(os.environ, {}, clear=True)

        result = mock_table_searcher._default_get_table_path()

        expected_path = f"{mock_project_root}/{FileConfig.DEFAULT_EXEC_PATTERN}/{FileConfig.TABLE_DIR_NAME}"
        assert result == str(expected_path)


class TestTableSearcherDefaultGetFileModifiedTime:
    """TableSearcherの_default_get_file_modified_timeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 更新時刻取得
    ├── C1: 分岐カバレッジ
    │   └── 異常系: ファイル未存在
    └── C2: 条件カバレッジ
        └── 異常系: その他のエラー発生
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        file_path = tmp_path / "test_table.pkl"
        return TableSearcher("test_table.pkl", file_path=file_path)

    def test_default_get_file_modified_time_C0_normal(self, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 更新時刻取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_stat = mocker.Mock()
        mock_stat.st_mtime = 1234567890.0
        mocker.patch.object(Path, 'stat', return_value=mock_stat)

        result = mock_table_searcher._default_get_file_modified_time()

        assert result == 1234567890.0
        log_msg(f"取得した更新時刻: {result}", LogLevel.DEBUG)

class TestTableSearcherDefaultGetFileModifiedTime:
    """TableSearcherの_default_get_file_modified_timeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 更新時刻取得
    ├── C1: 分岐カバレッジ
    │   └── 異常系: ファイル未存在
    └── C2: 条件カバレッジ
        └── 異常系: その他のエラー発生

    | 条件                   | ケース1  | ケース2 | ケース3 |
    |------------------------|----------|---------|---------|
    | ファイルが存在する     | Y        | N       | Y       |
    | アクセス権限がある     | Y        | -       | N       |
    | 出力                   | 更新時刻 | File    | その他の|
    |                        |          | NotFound| 例外    |
    |                        |          | Error   |         |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        # テスト用のDataFrameを作成
        df = pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})
        
        # pickleファイルとして保存
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        
        # TableSearcherインスタンスを作成して返す
        return TableSearcher("test_table.pkl", file_path=file_path)

    def test_default_get_file_modified_time_C0_normal(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 更新時刻取得
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher._default_get_file_modified_time()

        assert isinstance(result, float)
        assert result > 0
        log_msg(f"取得した更新時刻: {result}", LogLevel.DEBUG)

    def test_default_get_file_modified_time_C1_file_not_found(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: ファイル未存在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # ファイルを削除してFileNotFoundErrorを発生させる
        mock_table_searcher.file_path.unlink()

        with pytest.raises(FileNotFoundError) as exc_info:
            mock_table_searcher._default_get_file_modified_time()

        assert "ファイル" in str(exc_info.value)
        assert "が見つかりません" in str(exc_info.value)
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)


    def test_default_get_file_modified_time_C2_other_error(self, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: その他のエラー発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # PermissionErrorを発生させるようにモック
        mocker.patch.object(Path, 'stat', side_effect=PermissionError)

        with pytest.raises(Exception) as exc_info:
            mock_table_searcher._default_get_file_modified_time()

        assert "ファイルの更新時刻の取得中にエラーが発生しました" in str(exc_info.value)
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)

class TestTableSearcherShouldUpdateCache:
    """TableSearcherの_should_update_cacheメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 更新不要
    │   └── 正常系: 更新必要
    ├── C1: 分岐カバレッジ
    │   └── 正常系: ファイル更新時の動作
    └── C2: 条件カバレッジ
        └── 異常系: ファイル未存在

    | 条件                     | ケース1 | ケース2 | ケース3 | ケース4 |
    |--------------------------|---------|---------|---------|---------|
    | ファイルが存在する       | Y       | Y       | Y       | N       |
    | ファイルが更新されている | N       | Y       | Y       | -       |
    | 保存時刻より新しい       | -       | N       | Y       | -       |
    | 出力                     | False   | False   | True    | True    |

    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        # テスト用のDataFrameを作成
        df = pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})
        
        # pickleファイルとして保存
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        
        # TableSearcherインスタンスを作成して返す
        searcher = TableSearcher("test_table.pkl", file_path=file_path)
        searcher.last_modified_time = file_path.stat().st_mtime
        return searcher

    def test_should_update_cache_C0_no_update(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 更新不要
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher._should_update_cache()

        assert result is False
        log_msg(f"キャッシュ更新の必要性: {result}", LogLevel.DEBUG)

    def test_should_update_cache_C0_update_needed(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 更新必要
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # ファイルの最終更新時刻を変更
        mock_table_searcher.last_modified_time -= 1

        result = mock_table_searcher._should_update_cache()

        assert result is True
        log_msg(f"キャッシュ更新の必要性: {result}", LogLevel.DEBUG)

    def test_should_update_cache_C1_file_updated(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: ファイル更新時の動作
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # ファイルを更新
        time.sleep(0.1)  # ファイルシステムの時間精度を考慮
        df = pd.DataFrame({'column1': [4, 5, 6], 'column2': ['d', 'e', 'f']})
        df.to_pickle(mock_table_searcher.file_path)

        result = mock_table_searcher._should_update_cache()

        assert result is True
        log_msg(f"キャッシュ更新の必要性: {result}", LogLevel.DEBUG)

    def test_should_update_cache_C2_file_not_found(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: ファイル未存在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # ファイルを削除
        mock_table_searcher.file_path.unlink()

        result = mock_table_searcher._should_update_cache()

        assert result is True
        log_msg(f"キャッシュ更新の必要性: {result}", LogLevel.DEBUG)

class TestTableSearcherDefaultLoadTable:
    """TableSearcherの_default_load_tableメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: キャッシュ更新不要時の読み込み
    ├── C1: 分岐カバレッジ
    │   └── 正常系: キャッシュ更新必要時の読み込み
    └── C2: 条件カバレッジ
        ├── 異常系: ファイル未存在
        └── 異常系: 読み込みエラー

    | 条件                   | ケース1   | ケース2   | ケース3  | ケース4 | ケース5  |
    |------------------------|-----------|-----------|----------|---------|----------|
    | ファイルが存在する     | Y         | Y         | Y        | N       | Y        |
    | キャッシュ更新が必要   | N         | Y         | N        | Y       | Y        |
    | 読み込みエラーが発生   | N         | N         | N        | -       | Y        |
    | 出力                   | DataFrame | DataFrame | DataFrame| FileNot | Exception|
    |                        | False     | True      | False    | Found   |          |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        # テスト用のDataFrameを作成
        df = pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})
        
        # pickleファイルとして保存
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        
        # TableSearcherインスタンスを作成して返す
        searcher = TableSearcher("test_table.pkl", file_path=file_path)
        searcher.last_modified_time = file_path.stat().st_mtime
        return searcher

    def test_default_load_table_C0_no_update(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: キャッシュ更新不要時の読み込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        df, is_updated = mock_table_searcher._default_load_table()

        assert isinstance(df, pd.DataFrame)
        assert df.equals(pd.read_pickle(mock_table_searcher.file_path))
        assert is_updated is False
        log_msg(f"読み込んだDataFrame: \n{df}\n更新フラグ: {is_updated}", LogLevel.DEBUG)

    def test_default_load_table_C1_update_needed(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: キャッシュ更新必要時の読み込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # キャッシュをクリア
        mock_table_searcher._default_load_table.cache_clear()

        # ファイルを更新
        time.sleep(0.1)  # ファイルシステムの時間精度を考慮
        new_df = pd.DataFrame({'column1': [4, 5, 6], 'column2': ['d', 'e', 'f']})
        new_df.to_pickle(mock_table_searcher.file_path)

        # last_modified_timeを更新前の時刻に設定
        mock_table_searcher.last_modified_time -= 1

        df, is_updated = mock_table_searcher._default_load_table()

        assert isinstance(df, pd.DataFrame)
        assert df.equals(new_df)
        assert is_updated is True
        log_msg(f"読み込んだDataFrame: \n{df}\n更新フラグ: {is_updated}", LogLevel.DEBUG)

    def test_default_load_table_C2_file_not_found(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: ファイル未存在
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # キャッシュをクリア
        mock_table_searcher._default_load_table.cache_clear()

        # ファイルを削除
        mock_table_searcher.file_path.unlink()

        # last_modified_timeを更新して_should_update_cacheがTrueを返すようにする
        mock_table_searcher.last_modified_time = 0

        with pytest.raises(FileNotFoundError) as exc_info:
            mock_table_searcher._default_load_table()

        assert "テーブルファイル" in str(exc_info.value)
        assert "が見つかりません" in str(exc_info.value)
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)


    def test_default_load_table_C2_read_error(self, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 読み込みエラー
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # キャッシュをクリア
        mock_table_searcher._default_load_table.cache_clear()

        # _should_update_cacheメソッドをモックしてTrueを返すようにする
        mocker.patch.object(TableSearcher, '_should_update_cache', return_value=True)

        # pd.read_pickleでエラーを発生させる
        mocker.patch('pandas.read_pickle', side_effect=Exception("読み込みエラー"))

        # デバッグ情報を追加
        def mock_df_loader(*args, **kwargs):
            log_msg("mock_df_loader called", LogLevel.DEBUG)
            raise Exception("読み込みエラー")
        
        mock_table_searcher._df_loader = mock_df_loader

        with pytest.raises(Exception) as exc_info:
            result = mock_table_searcher._default_load_table()
            log_msg(f"Unexpected result: {result}", LogLevel.ERROR)

        assert "テーブルの読み込み中にエラーが発生しました" in str(exc_info.value)
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)


    def test_default_load_table_cache_behavior(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: キャッシュの動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # キャッシュをクリア
        mock_table_searcher._default_load_table.cache_clear()

        # 1回目の呼び出し
        df1, is_updated1 = mock_table_searcher._default_load_table()
        
        # 2回目の呼び出し（キャッシュから取得されるはず）
        df2, is_updated2 = mock_table_searcher._default_load_table()
        
        assert df1.equals(df2)
        assert is_updated1 is False
        assert is_updated2 is False
        
        # キャッシュをクリア
        mock_table_searcher._default_load_table.cache_clear()
        
        # ファイルを更新
        time.sleep(0.1)  # ファイルシステムの時間精度を考慮
        new_df = pd.DataFrame({'column1': [7, 8, 9], 'column2': ['g', 'h', 'i']})
        new_df.to_pickle(mock_table_searcher.file_path)

        # last_modified_timeを更新前の時刻に設定
        mock_table_searcher.last_modified_time -= 1

        # 3回目の呼び出し（再度ファイルから読み込まれるはず）
        df3, is_updated3 = mock_table_searcher._default_load_table()
        
        assert df3.equals(new_df)
        assert is_updated3 is True
        
        log_msg(f"キャッシュ動作確認結果: \n1回目更新フラグ: {is_updated1}\n2回目更新フラグ: {is_updated2}\n3回目更新フラグ: {is_updated3}", LogLevel.DEBUG)

class TestTableSearcherRefreshData:
    """TableSearcherのrefresh_dataメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: データ再読み込み
    └── C1: 分岐カバレッジ
        ├── 正常系: 更新されたデータの再読み込み
        └── 異常系: 再読み込み時のエラー

    | 条件                     | ケース1 | ケース2 | ケース3 |
    |--------------------------|---------|---------|---------|
    | キャッシュがクリアされる | Y       | Y       | Y       |
    | データが更新される       | N       | Y       | -       |
    | エラーが発生する         | N       | N       | Y       |
    | 出力                     | 元のDF  | 更新DF  | 例外    |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        df = pd.DataFrame({'column1': [1, 2, 3], 'column2': ['a', 'b', 'c']})
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        searcher = TableSearcher("test_table.pkl", file_path=file_path)
        searcher.last_modified_time = file_path.stat().st_mtime
        searcher.df = df
        return searcher

    def test_refresh_data_C0_basic_functionality(self, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: データ再読み込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # _default_load_tableメソッドをモック
        mock_load_table = mocker.patch.object(
            mock_table_searcher, '_default_load_table',
            return_value=(mock_table_searcher.df, False)
        )

        # cache_clearメソッドをモック
        mock_cache_clear = mocker.patch.object(mock_table_searcher._default_load_table, 'cache_clear')

        # refresh_dataメソッドを呼び出す
        mock_table_searcher.refresh_data()

        # キャッシュクリアメソッドが呼ばれたことを確認
        mock_cache_clear.assert_called_once()
        
        # _default_load_tableが呼ばれたことを確認
        mock_load_table.assert_called_once()

        log_msg(f"データ再読み込み後のDataFrame: \n{mock_table_searcher.df}", LogLevel.DEBUG)

    def test_refresh_data_C1_updated_data(self, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 更新されたデータの再読み込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        updated_df = pd.DataFrame({'column1': [4, 5, 6], 'column2': ['d', 'e', 'f']})

        # _default_load_tableメソッドをモック
        mock_load_table = mocker.patch.object(
            mock_table_searcher, '_default_load_table',
            return_value=(updated_df, True)
        )

        # cache_clearメソッドをモック
        mock_cache_clear = mocker.patch.object(mock_table_searcher._default_load_table, 'cache_clear')

        # refresh_dataメソッドを呼び出す
        mock_table_searcher.refresh_data()

        # キャッシュクリアメソッドが呼ばれたことを確認
        mock_cache_clear.assert_called_once()
        
        # _default_load_tableが呼ばれたことを確認
        mock_load_table.assert_called_once()

        # データが更新されたことを確認
        pd.testing.assert_frame_equal(mock_table_searcher.df, updated_df)

        log_msg(f"更新後のDataFrame: \n{mock_table_searcher.df}", LogLevel.DEBUG)

    def test_refresh_data_C1_error_on_reload(self, mock_table_searcher, mocker):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 再読み込み時のエラー
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # _default_load_tableメソッドをモックしてエラーを発生させる
        mock_load_table = mocker.patch.object(
            mock_table_searcher, '_default_load_table',
            side_effect=Exception("読み込みエラー")
        )

        # cache_clearメソッドをモック
        mock_cache_clear = mocker.patch.object(mock_table_searcher._default_load_table, 'cache_clear')

        with pytest.raises(Exception) as exc_info:
            mock_table_searcher.refresh_data()

        # キャッシュクリアメソッドが呼ばれたことを確認
        mock_cache_clear.assert_called_once()
        
        # _default_load_tableが呼ばれたことを確認
        mock_load_table.assert_called_once()

        assert "読み込みエラー" in str(exc_info.value)
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)


#----------------------------------------------------------------

class TestTableSearcherSimpleSearch:
    """TableSearcherのsimple_searchメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 単一条件での検索（AND）
    │   └── 正常系: 単一条件での検索（OR）
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 複数条件での検索（AND）
    │   ├── 正常系: 複数条件での検索（OR）
    │   └── 正常系: startswith検索
    └── C2: 条件カバレッジ
        ├── 異常系: 無効なoperator指定
        └── 正常系: 空の結果
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 40, 30],
            'city': ['New York', 'London', 'Paris', 'Tokyo', 'London']
        })
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        searcher = TableSearcher("test_table.pkl", file_path=file_path)
        searcher.df = df
        log_msg(f"テストデータ: \n{df}", LogLevel.DEBUG)
        return searcher

    def test_simple_search_C0_single_condition_AND(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 単一条件での検索（AND）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher.simple_search({"name": "Alice"}, operator='AND')
        
        log_msg(f"検索条件: name=Alice", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 1, f"期待される結果の件数: 1, 実際の件数: {len(result)}"
        assert result.iloc[0]['name'] == 'Alice', f"期待される名前: Alice, 実際の名前: {result.iloc[0]['name']}"

    def test_simple_search_C0_single_condition_OR(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 単一条件での検索（OR）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher.simple_search({"age": 30}, operator='OR')
        
        log_msg(f"検索条件: age=30", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 2, f"期待される結果の件数: 2, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Bob', 'Eve'}, f"期待される名前: Bob, Eve, 実際の名前: {result['name'].tolist()}"

    def test_simple_search_C1_multiple_conditions_AND(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複数条件での検索（AND）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher.simple_search({"age": 30, "city": "London"}, operator='AND')
        
        log_msg(f"検索条件: age=30 AND city=London", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 2, f"期待される結果の件数: 2, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Bob', 'Eve'}, f"期待される名前: Bob, Eve, 実際の名前: {result['name'].tolist()}"

    def test_simple_search_C1_multiple_conditions_OR(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複数条件での検索（OR）
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher.simple_search({"age": 30, "city": "Tokyo"}, operator='OR')
        
        log_msg(f"検索条件: age=30 OR city=Tokyo", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 3, f"期待される結果の件数: 3, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Bob', 'David', 'Eve'}, f"期待される名前: Bob, David, Eve, 実際の名前: {result['name'].tolist()}"

    def test_simple_search_C1_startswith(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: startswith検索
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher.simple_search({"name": "startswith:A"}, operator='AND')
        
        log_msg(f"検索条件: name startswith A", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 1, f"期待される結果の件数: 1, 実際の件数: {len(result)}"
        assert result.iloc[0]['name'] == 'Alice', f"期待される名前: Alice, 実際の名前: {result.iloc[0]['name']}"

    def test_simple_search_C2_invalid_operator(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効なoperator指定
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError) as exc_info:
            mock_table_searcher.simple_search({"name": "Alice"}, operator='INVALID')
        
        assert "operatorは'AND'または'OR'である必要があります" in str(exc_info.value)
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)

    def test_simple_search_C2_empty_result(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 空の結果
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        result = mock_table_searcher.simple_search({"name": "NonExistent"}, operator='AND')
        
        log_msg(f"検索条件: name=NonExistent", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 0, f"期待される結果の件数: 0, 実際の件数: {len(result)}"


class TestTableSearcherAdvancedSearch:
    """TableSearcherのadvanced_searchメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: カスタム条件での検索
    └── C1: 分岐カバレッジ
        ├── 正常系: 複雑な条件での検索
        └── 異常系: 無効な条件関数
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher(self, tmp_path):
        df = pd.DataFrame({
            'id': [1, 2, 3, 4, 5],
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'age': [25, 30, 35, 40, 30],
            'city': ['New York', 'London', 'Paris', 'Tokyo', 'London']
        })
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        searcher = TableSearcher("test_table.pkl", file_path=file_path)
        searcher.df = df
        log_msg(f"テストデータ: \n{df}", LogLevel.DEBUG)
        return searcher

    @pytest.fixture
    def mock_table_searcher2(self, tmp_path):
        """C2

        | 条件                   | ケース1 | ケース2 | ケース3 | ケース4 | ケース5 | ケース6 | ケース7 |
        |------------------------|---------|---------|---------|---------|---------|---------|---------|
        | 複数カラムの使用       | Y       | N       | N       | N       | N       | N       | N       |
        | データ型変換           | N       | Y       | N       | N       | N       | N       | N       |
        | 統計的計算             | N       | N       | Y       | N       | N       | N       | N       |
        | 文字列操作             | N       | N       | N       | Y       | N       | N       | N       |
        | 日付操作               | N       | N       | N       | N       | Y       | N       | N       |
        | 全行該当               | N       | N       | N       | N       | N       | Y       | N       |
        | 該当行なし             | N       | N       | N       | N       | N       | N       | Y       |
        | 出力                   | 部分    | 部分    | 部分    | 部分    | 部分    | 全行    | 空      |
        |                        | 結果    | 結果    | 結果    | 結果    | 結果    | 結果    | 結果    |
        """
        df = pd.DataFrame({
            'id': range(1, 11),
            'name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack'],
            'age': [25, 30, 35, 40, 30, 45, 28, 33, 37, 29],
            'city': ['New York', 'London', 'Paris', 'Tokyo', 'London', 'Berlin', 'Sydney', 'Moscow', 'Beijing', 'Toronto'],
            'salary': [50000, 60000, 75000, 90000, 55000, 80000, 65000, 70000, 85000, 62000],
            'department': ['IT', 'HR', 'Finance', 'IT', 'Marketing', 'Finance', 'HR', 'IT', 'Marketing', 'IT'],
            'join_date': pd.date_range(start='2020-01-01', periods=10, freq='M'),
            'performance_score': [4.5, 3.8, 4.2, 4.7, 3.9, 4.1, 4.3, 4.0, 4.6, 3.7],
        })
        file_path = tmp_path / "test_table.pkl"
        df.to_pickle(file_path)
        searcher = TableSearcher("test_table.pkl", file_path=file_path)
        searcher.df = df
        log_msg(f"テストデータ: \n{df}", LogLevel.DEBUG)
        return searcher


    def test_advanced_search_C0_custom_condition(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: カスタム条件での検索
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def custom_condition(df):
            return (df['age'] > 30) & (df['city'] != 'London')

        result = mock_table_searcher.advanced_search(custom_condition)
        
        log_msg(f"検索条件: age > 30 and city != 'London'", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 2, f"期待される結果の件数: 2, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Charlie', 'David'}, f"期待される名前: Charlie, David, 実際の名前: {result['name'].tolist()}"

    def test_advanced_search_C1_complex_condition(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複雑な条件での検索
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def complex_condition(df):
            return (df['age'].between(25, 35)) & (df['city'].isin(['New York', 'London'])) | (df['name'].str.startswith('D'))

        result = mock_table_searcher.advanced_search(complex_condition)
        
        log_msg(f"検索条件: (25 <= age <= 35 and city in ['New York', 'London']) or name startswith 'D'", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 4, f"期待される結果の件数: 4, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Alice', 'Bob', 'David', 'Eve'}, f"期待される名前: Alice, Bob, David, Eve, 実際の名前: {result['name'].tolist()}"

    def test_advanced_search_C1_invalid_condition(self, mock_table_searcher):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効な条件関数
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def invalid_condition(df):
            return "This is not a valid condition"

        with pytest.raises(Exception) as exc_info:
            mock_table_searcher.advanced_search(invalid_condition)
        
        log_msg(f"発生したエラー: {exc_info.value}", LogLevel.DEBUG)
        assert "Invalid condition function result" in str(exc_info.value) or "条件関数の結果が無効です" in str(exc_info.value)



    def test_advanced_search_C2_multiple_columns(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 複数カラムを使用した複雑な条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def complex_condition(df):
            return (df['age'] > 30) & (df['salary'] > 70000) & (df['department'].isin(['IT', 'Finance']))

        result = mock_table_searcher2.advanced_search(complex_condition)
        
        log_msg(f"検索条件: age > 30 AND salary > 70000 AND department in ['IT', 'Finance']", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 3, f"期待される結果の件数: 3, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Charlie', 'David', 'Frank'}, f"期待される名前: Charlie, David, Ivy, 実際の名前: {result['name'].tolist()}"

    def test_advanced_search_C2_data_type_conversion(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: データ型変換を含む条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def conversion_condition(df):
            return (df['salary'].astype(str).str.startswith('8')) | (df['age'] == df['salary'] // 2000)

        result = mock_table_searcher2.advanced_search(conversion_condition)
        
        log_msg(f"検索条件: salary starts with '8' OR age == salary // 2000", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 4, f"期待される結果の件数: 4, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Alice', 'Bob', 'Frank', 'Ivy'}, f"期待される名前: Alice, Bob, Frank, Ivy, 実際の名前: {result['name'].tolist()}"

    def test_advanced_search_C2_statistical_calculation(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 統計的計算を含む条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def statistical_condition(df):
            return (df['age'] > df['age'].mean()) & (df['salary'] > df['salary'].median())

        result = mock_table_searcher2.advanced_search(statistical_condition)
        
        log_msg(f"検索条件: age > mean(age) AND salary > median(salary)", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 4, f"期待される結果の件数: 4, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Charlie', 'David', 'Frank', 'Ivy'}, f"期待される名前: Charlie, David, Ivy, 実際の名前: {result['name'].tolist()}"


    def test_advanced_search_C2_string_operation(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 文字列操作を含む条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def string_condition(df):
            return df['name'].str.contains('a', case=False) & (df['city'].str.len() > 5)

        result = mock_table_searcher2.advanced_search(string_condition)
        
        log_msg(f"検索条件: name contains 'a' (case-insensitive) AND length of city > 5", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 4, f"期待される結果の件数: 4, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Alice', 'Frank', 'Grace', 'Jack'}, f"期待される名前: Alice, Frank, Grace, Jack, 実際の名前: {result['name'].tolist()}"


    def test_advanced_search_C2_date_operation(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 日付操作を含む条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def date_condition(df):
            return (df['join_date'] > '2020-06-01') & (df['performance_score'] > 4.0)

        result = mock_table_searcher2.advanced_search(date_condition)
        
        log_msg(f"検索条件: join_date > '2020-06-01' AND performance_score > 4.0", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 3, f"期待される結果の件数: 3, 実際の件数: {len(result)}"
        assert set(result['name'].tolist()) == {'Frank', 'Grace', 'Ivy'}, f"期待される名前: Frank, ,Grace, Ivy, 実際の名前: {result['name'].tolist()}"

    def test_advanced_search_C2_all_rows(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 全ての行が該当する条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def all_rows_condition(df):
            return df['age'] > 0

        result = mock_table_searcher2.advanced_search(all_rows_condition)
        
        log_msg(f"検索条件: age > 0", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == len(mock_table_searcher2.df), f"期待される結果の件数: {len(mock_table_searcher2.df)}, 実際の件数: {len(result)}"

    def test_advanced_search_C2_no_rows(self, mock_table_searcher2):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 該当する行がない条件
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def no_rows_condition(df):
            return df['age'] < 0

        result = mock_table_searcher2.advanced_search(no_rows_condition)
        
        log_msg(f"検索条件: age < 0", LogLevel.DEBUG)
        log_msg(f"検索結果: \n{result}", LogLevel.DEBUG)
        
        assert len(result) == 0, f"期待される結果の件数: 0, 実際の件数: {len(result)}"



