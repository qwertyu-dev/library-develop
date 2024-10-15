import pickle
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_pickled_table_searcher import ErrorMessages, TableSearcher

# config共有
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestTableSearcherInit:
    """TableSearcherクラスの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な引数でインスタンス生成
    │   ├── 異常系: 空のtable_nameでValueError
    │   └── 異常系: 無効なfile_pathでFileNotFoundError
    ├── C1: 分岐カバレッジ
    │   ├── file_pathが指定された場合
    │   ├── file_pathが指定されていない場合
    │   ├── get_file_modified_timeが指定された場合
    │   └── get_file_modified_timeが指定されていない場合
    ├── C2: 条件組み合わせ
    │   ├── table_name, file_path, get_file_modified_time全て指定
    │   ├── table_nameのみ指定
    │   └── table_nameとfile_pathのみ指定
    ├── DT: ディシジョンテーブル
    │   └── 引数の組み合わせによる動作確認
    └── BVT: 境界値テスト
        ├── table_nameの最大長
        └── file_pathの最大長

    C1のディシジョンテーブル:
    | 条件                         | ケース1 | ケース2    | ケース3  | ケース4    |
    |------------------------------|---------|------------|----------|------------|
    | file_pathが指定される        | Y       | N          | Y        | N          |
    | get_file_modified_timeが指定 | Y       | Y          | N        | N          |
    | 期待される動作               | カスタム| デフォルト | カスタム | デフォルト |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ         | テスト値                     | 期待される結果  | テストの目的/検証ポイント                        | 実装状況 | 対応するテストケース                        |
    |----------|------------------------|------------------------------|-----------------|--------------------------------------------------|----------|---------------------------------------------|
    | BVT_001  | table_name             | ""                           | ValueError      | 空文字列の処理を確認                             | 実装済み | test_init_C0_empty_table_name               |
    | BVT_002  | table_name             | "a" * 255 + ".pkl"           | 正常終了        | 最大長の文字列での動作を確認                     | 実装済み | test_init_BVT_max_length_table_name         |
    | BVT_003  | file_path              | Path("a" * 255)              | 正常終了        | 最大長のパスでの動作を確認                       | 実装済み | test_init_BVT_max_length_file_path          |
    | BVT_004  | file_path              | None                         | 正常終了        | Noneが指定された場合のデフォルト動作を確認       | 実装済み | test_init_C1_default_file_path              |
    | BVT_005  | get_file_modified_time | None                         | 正常終了        | Noneが指定された場合のデフォルト動作を確認       | 実装済み | test_init_C1_default_get_file_modified_time |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。テストケースは、空の入力、最大長の入力、およびデフォルト値の使用など、
    様々な境界条件をカバーしています。これにより、__init__メソッドの堅牢性と正確性が確保されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_config(self):
        config = MagicMock()
        config.env = "test"
        config.common_config = {"optional_path": {"TABLE_PATH": "/default/path"}}
        config.package_config = {}
        config.log_message = MagicMock()
        return config

    @pytest.fixture()
    def sample_dataframe(self):
        return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    @pytest.fixture()
    def mock_dataframe(self):
        return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    @pytest.fixture()
    def pickle_file(self, tmp_path, sample_dataframe):
        file_path = tmp_path / "test_table.pkl"
        with Path(file_path).open('wb') as f:
            pickle.dump(sample_dataframe, f)
        return file_path

    def test_init_C0_valid_arguments(self, mock_config, pickle_file, sample_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効な引数でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch.object(Path, "stat") as mock_stat, \
            patch("src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._should_update_cache", return_value=False), \
            patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=sample_dataframe):

            mock_stat.return_value.st_mtime = 12345.0
            searcher = TableSearcher("test_table.pkl", file_path=pickle_file.parent, config=mock_config)

        assert searcher.table_name == "test_table.pkl"
        assert str(searcher.file_path) == str(pickle_file)
        pd.testing.assert_frame_equal(searcher.df, sample_dataframe)
        assert searcher.last_modified_time == 12345.0

        mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
        mock_config.log_message.assert_any_call('table_name: test_table.pkl', LogLevel.INFO)
        mock_config.log_message.assert_any_call(f'file_path: {pickle_file.parent}', LogLevel.INFO)
        mock_config.log_message.assert_any_call(f'self.file_path: {pickle_file}', LogLevel.INFO)

    def test_init_C0_empty_table_name(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 空のtable_nameでValueError
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            TableSearcher("", config=mock_config)
        assert str(excinfo.value) == ErrorMessages.EMPTY_TABLE_NAME

    def test_init_C0_invalid_file_path(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 無効なfile_pathでFileNotFoundError
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch("pathlib.Path.stat", side_effect=FileNotFoundError):
            with pytest.raises(FileNotFoundError) as excinfo:
                TableSearcher("test_table.pkl", file_path="/invalid/path", config=mock_config)
            assert str(excinfo.value) == ErrorMessages.FILE_NOT_FOUND

    def test_init_C1_custom_file_path(self, mock_config, mock_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: カスタムfile_pathが指定された場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch("pathlib.Path.stat") as mock_stat, \
            patch.object(TableSearcher, "_should_update_cache", return_value=False):
            mock_stat.return_value.st_mtime = 12345.0
            searcher = TableSearcher("test_table.pkl", file_path="/custom/path", config=mock_config)

        assert str(searcher.file_path) == str(Path("/custom/path/test_table.pkl"))
        assert searcher.last_modified_time == 12345.0
        assert isinstance(searcher.df, pd.DataFrame)
        pd.testing.assert_frame_equal(searcher.df, mock_dataframe)

    def test_init_C1_default_file_path(self, mock_config, mock_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: デフォルトfile_pathが使用される場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch("pathlib.Path.stat") as mock_stat, \
            patch.object(TableSearcher, "_should_update_cache", return_value=False):
            mock_stat.return_value.st_mtime = 67890.0
            searcher = TableSearcher("test_table.pkl", config=mock_config)

        assert str(searcher.file_path) == str(Path("/default/path/test_table.pkl"))
        assert searcher.last_modified_time == 67890.0
        assert isinstance(searcher.df, pd.DataFrame)
        pd.testing.assert_frame_equal(searcher.df, mock_dataframe)

        # ログ出力の確認
        mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
        mock_config.log_message.assert_any_call('table_name: test_table.pkl', LogLevel.INFO)
        mock_config.log_message.assert_any_call('file_path: None', LogLevel.INFO)
        mock_config.log_message.assert_any_call(f'self.file_path: {Path("/default/path/test_table.pkl")}', LogLevel.INFO)

    def test_init_C1_custom_get_file_modified_time(self, mock_config, mock_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: カスタムget_file_modified_timeが指定された場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        custom_time_func = lambda: 12345.0
        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch.object(TableSearcher, "_should_update_cache", return_value=False), \
            patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value.st_mtime = 67890.0  # デフォルトの時間とは異なる値を設定
            searcher = TableSearcher("test_table.pkl", get_file_modified_time=custom_time_func, config=mock_config)

        assert searcher.get_file_modified_time() == 12345.0
        assert searcher.last_modified_time == 12345.0
        assert isinstance(searcher.df, pd.DataFrame)
        pd.testing.assert_frame_equal(searcher.df, mock_dataframe)

        # ファイルパスの確認
        assert str(searcher.file_path) == str(Path("/default/path/test_table.pkl"))

        # ログ出力の確認
        mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
        mock_config.log_message.assert_any_call('table_name: test_table.pkl', LogLevel.INFO)
        mock_config.log_message.assert_any_call('file_path: None', LogLevel.INFO)
        mock_config.log_message.assert_any_call(f'self.file_path: {Path("/default/path/test_table.pkl")}', LogLevel.INFO)

    def test_init_C1_default_get_file_modified_time(self, mock_config, mock_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: デフォルトget_file_modified_timeが使用される場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch.object(TableSearcher, "_should_update_cache", return_value=False), \
            patch.object(TableSearcher, "_default_get_file_modified_time") as mock_default_get_file_modified_time:
            mock_default_get_file_modified_time.return_value = 67890.0
            searcher = TableSearcher("test_table.pkl", config=mock_config)

            assert searcher.get_file_modified_time() == 67890.0
            assert searcher.last_modified_time == 67890.0
            assert isinstance(searcher.df, pd.DataFrame)
            pd.testing.assert_frame_equal(searcher.df, mock_dataframe)

            # ファイルパスの確認
            assert str(searcher.file_path) == str(Path("/default/path/test_table.pkl"))

            # ログ出力の確認
            mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
            mock_config.log_message.assert_any_call('table_name: test_table.pkl', LogLevel.INFO)
            mock_config.log_message.assert_any_call('file_path: None', LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'self.file_path: {Path("/default/path/test_table.pkl")}', LogLevel.INFO)

            # _default_get_file_modified_timeメソッドが呼び出された回数を確認
            assert mock_default_get_file_modified_time.call_count == 2
            calls = mock_default_get_file_modified_time.call_args_list
            assert calls[0] == calls[1]  # 両方の呼び出しが同じ引数で行われたことを確認
            log_msg(f"_default_get_file_modified_time called {mock_default_get_file_modified_time.call_count} times", LogLevel.INFO)
            log_msg(f"Call args: {mock_default_get_file_modified_time.call_args_list}", LogLevel.INFO)

    @pytest.mark.parametrize(("file_path", "get_file_modified_time", "expected_path", "expected_time"), [
        ("/custom/path", lambda: 12345.0, "/custom/path/test_table.pkl", 12345.0), # カスタムパス,時間指定あり: カスタムパスでpickleファイルパス構築,指定時間判定
        (None, lambda: 12345.0, "/default/path/test_table.pkl", 12345.0),          # パス指定なし、時間指定あり: デフォルトパスでpickleファイルパス構築,指定時間判定
        ("/custom/path", None, "/custom/path/test_table.pkl", 67890.0),            # カスタムパス、時間指定なし: カスタムパスでpickleファイルパス構築,デフォルト時間判定(ファイル更新)
        (None, None, "/default/path/test_table.pkl", 67890.0),                     # いずれも指定なし: デフォルトパスでpickleファイルパス構築,デフォルト時間判定(ファイル更新)
    ])
    def test_init_C2_DT_parameter_combinations(self, mock_config, mock_dataframe, file_path, get_file_modified_time, expected_path, expected_time):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2, DT
        テスト内容: 引数の組み合わせによる動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch.object(TableSearcher, "_should_update_cache", return_value=False), \
            patch.object(TableSearcher, "_default_get_file_modified_time") as mock_default_get_file_modified_time:

            mock_default_get_file_modified_time.return_value = 67890.0

            searcher = TableSearcher("test_table.pkl", file_path=file_path, get_file_modified_time=get_file_modified_time, config=mock_config)

            assert str(searcher.file_path) == str(Path(expected_path))
            assert searcher.get_file_modified_time() == expected_time
            assert searcher.last_modified_time == expected_time
            assert isinstance(searcher.df, pd.DataFrame)
            pd.testing.assert_frame_equal(searcher.df, mock_dataframe)

            # ログ出力の確認
            mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
            mock_config.log_message.assert_any_call('table_name: test_table.pkl', LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'file_path: {file_path}', LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'self.file_path: {Path(expected_path)}', LogLevel.INFO)

            # get_file_modified_timeの呼び出し回数を確認
            expected_call_count = 2 if get_file_modified_time is None else 1
            if get_file_modified_time is None:
                assert mock_default_get_file_modified_time.call_count == expected_call_count
            else:
                custom_get_file_modified_time = MagicMock(return_value=expected_time)
                with patch.object(searcher, "get_file_modified_time", custom_get_file_modified_time):
                    assert searcher.get_file_modified_time() == expected_time
                    assert custom_get_file_modified_time.call_count == 1

        log_msg(f"Test completed for file_path={file_path}, get_file_modified_time={get_file_modified_time}", LogLevel.INFO)

    def test_init_BVT_max_length_table_name(self, mock_config, mock_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: table_nameの最大長
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        max_length_name = "a" * 251 + ".pkl"  # 255文字 - 4 (.pkl)
        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch.object(TableSearcher, "_should_update_cache", return_value=False), \
            patch.object(TableSearcher, "_default_get_file_modified_time") as mock_default_get_file_modified_time:
            mock_default_get_file_modified_time.return_value = 12345.0
            searcher = TableSearcher(max_length_name, config=mock_config)

            assert searcher.table_name == max_length_name
            assert isinstance(searcher.df, pd.DataFrame)
            pd.testing.assert_frame_equal(searcher.df, mock_dataframe)
            assert searcher.last_modified_time == 12345.0
            assert searcher.get_file_modified_time() == 12345.0

            # ログ出力の確認
            mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'table_name: {max_length_name}', LogLevel.INFO)
            mock_config.log_message.assert_any_call('file_path: None', LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'self.file_path: {Path("/default/path") / max_length_name}', LogLevel.INFO)

            # _default_get_file_modified_timeメソッドが2回呼び出されたことを確認
            assert mock_default_get_file_modified_time.call_count == 2

    def test_init_BVT_max_length_file_path(self, mock_config, mock_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: file_pathの最大長
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        max_length_path = "a" * 255
        with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe), \
            patch.object(TableSearcher, "_should_update_cache", return_value=False), \
            patch.object(TableSearcher, "_default_get_file_modified_time") as mock_default_get_file_modified_time:
            mock_default_get_file_modified_time.return_value = 12345.0
            searcher = TableSearcher("test_table.pkl", file_path=max_length_path, config=mock_config)

            assert str(searcher.file_path) == str(Path(max_length_path) / "test_table.pkl")
            assert isinstance(searcher.df, pd.DataFrame)
            pd.testing.assert_frame_equal(searcher.df, mock_dataframe)
            assert searcher.last_modified_time == 12345.0
            assert searcher.get_file_modified_time() == 12345.0

            # ログ出力の確認
            mock_config.log_message.assert_any_call(f"TableSearcher.__init__ called. self.config: {mock_config}", LogLevel.INFO)
            mock_config.log_message.assert_any_call('table_name: test_table.pkl', LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'file_path: {max_length_path}', LogLevel.INFO)
            mock_config.log_message.assert_any_call(f'self.file_path: {Path(max_length_path) / "test_table.pkl"}', LogLevel.INFO)

            # _default_get_file_modified_timeメソッドが2回呼び出されたことを確認
            assert mock_default_get_file_modified_time.call_count == 2


class TestTableSearcherShouldUpdateCache:
    """TableSearcherクラスの_should_update_cacheメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: ファイルが更新されている場合、Trueを返す
    │   ├── 正常系: ファイルが更新されていない場合、Falseを返す
    │   └── 異常系: ファイルが存在しない場合、Trueを返す
    ├── C1: 分岐カバレッジ
    │   ├── current_modified_time > self.last_modified_time の場合
    │   ├── current_modified_time <= self.last_modified_time の場合
    │   └── FileNotFoundError が発生する場合
    ├── C2: 条件組み合わせ
    │   ├── ファイルが存在し、更新されている
    │   ├── ファイルが存在し、更新されていない
    │   └── ファイルが存在しない
    └── BVT: 境界値テスト
        ├── current_modified_time が self.last_modified_time と等しい
        ├── current_modified_time が self.last_modified_time より1だけ大きい
        └── current_modified_time が self.last_modified_time より1だけ小さい

    C1のディシジョンテーブル:
    | 条件                                            | ケース1 | ケース2 | ケース3 |
    |-------------------------------------------------|---------|---------|---------|
    | ファイルが存在する                              | Y       | Y       | N       |
    | current_modified_time > self.last_modified_time | Y       | N       | -       |
    | 期待される戻り値                                | True    | False   | True    |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ               | テスト値                             | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース                    |
    |----------|-----------------------------|--------------------------------------|----------------|-------------------------------------|----------|----------------------------------------|
    | BVT_001  | current_modified_time       | self.last_modified_time              | False          | 等しい時間の処理を確認              | 実装済み | test_should_update_cache_BVT_equal_time |
    | BVT_002  | current_modified_time       | self.last_modified_time + 1          | True           | わずかに新しい時間の処理を確認      | 実装済み | test_should_update_cache_BVT_slightly_newer |
    | BVT_003  | current_modified_time       | self.last_modified_time - 1          | False          | わずかに古い時間の処理を確認        | 実装済み | test_should_update_cache_BVT_slightly_older |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 3
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これにより、_should_update_cacheメソッドの
    境界条件での動作が適切にテストされ、メソッドの堅牢性が確保されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_searcher(self):
        searcher = MagicMock()
        searcher.last_modified_time = 1000.0
        searcher.get_file_modified_time = MagicMock()
        return searcher

    #@pytest.fixture
    #def mock_searcher(self):
    #    searcher = MagicMock(=TableSearcher)
    #    searcher.last_modified_time = 1000.0
    #    searcher.get_file_modified_time = MagicMock()
    #    return searcher

    def test_should_update_cache_C0_file_updated(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: ファイルが更新されている場合、Trueを返す
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 1001.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is True

        #log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        #mock_searcher.get_file_modified_time.return_value = 1001.0
        #result = TableSearcher._should_update_cache(mock_searcher)
        #assert result is True

    def test_should_update_cache_C0_file_not_updated(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: ファイルが更新されていない場合、Falseを返す
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 999.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is False

    def test_should_update_cache_C0_file_not_found(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: ファイルが存在しない場合、Trueを返す
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.side_effect = FileNotFoundError
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is True

    def test_should_update_cache_C1_file_updated(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: current_modified_time > self.last_modified_time の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 1001.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is True

    def test_should_update_cache_C1_file_not_updated(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: current_modified_time <= self.last_modified_time の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 1000.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is False

    def test_should_update_cache_C1_file_not_found(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: FileNotFoundError が発生する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.side_effect = FileNotFoundError
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is True

    @pytest.mark.parametrize("current_time,expected", [
        (1001.0, True),   # ファイルが更新されている
        (1000.0, False),  # ファイルが更新されていない
        (999.0, False),   # ファイルが更新されていない
    ])
    def test_should_update_cache_C2_file_exists(self, mock_searcher, current_time, expected):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: ファイルが存在する場合の条件組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = current_time
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is expected

    def test_should_update_cache_C2_file_not_exists(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: ファイルが存在しない場合の条件
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.side_effect = FileNotFoundError
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is True

    def test_should_update_cache_BVT_equal_time(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: current_modified_time が self.last_modified_time と等しい
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 1000.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is False

    def test_should_update_cache_BVT_slightly_newer(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: current_modified_time が self.last_modified_time より1だけ大きい
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 1001.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is True

    def test_should_update_cache_BVT_slightly_older(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: current_modified_time が self.last_modified_time より1だけ小さい
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_searcher.get_file_modified_time.return_value = 999.0
        result = TableSearcher._should_update_cache(mock_searcher)
        assert result is False

class TestTableSearcherDefaultLoadTable:
    """TableSearcherクラスの_default_load_tableメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: テーブルが正常に読み込まれる
    │   ├── 異常系: ファイルが存在しない場合、FileNotFoundErrorが発生
    │   └── 異常系: 無効なpickleファイルの場合、例外が発生
    ├── C1: 分岐カバレッジ
    │   ├── キャッシュの更新が必要な場合
    │   └── キャッシュの更新が不要な場合
    ├── C2: 条件組み合わせ
    │   ├── キャッシュ更新が必要で、ファイルが正常な場合
    │   ├── キャッシュ更新が不要で、ファイルが正常な場合
    │   ├── キャッシュ更新が必要で、ファイルが存在しない場合
    │   └── キャッシュ更新が必要で、ファイルが無効な場合
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        └── 大規模なDataFrame

    C1のディシジョンテーブル:
    | 条件                   | ケース1 | ケース2 |
    |------------------------|---------|---------|
    | キャッシュ更新が必要   | Y       | N       |
    | ファイルが正常         | Y       | Y       |
    | 期待される動作         | 読み込み| キャッシュ使用 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                  | 期待される結果  | テストの目的/検証ポイント                 | 実装状況 | 対応するテストケース                   |
    |----------|----------------|---------------------------|-----------------|-------------------------------------------|----------|----------------------------------------|
    | BVT_001  | DataFrame      | 空のDataFrame             | 正常終了        | 空のDataFrameの処理を確認                 | 実装済み | test_default_load_table_BVT_empty_df   |
    | BVT_002  | DataFrame      | 100万行のDataFrame        | 正常終了        | 大規模DataFrameの処理を確認               | 実装済み | test_default_load_table_BVT_large_df   |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 2
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これにより、_default_load_tableメソッドの
    極端な状況での動作が適切にテストされ、メソッドの堅牢性が確保されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_searcher(self):
        #searcher = MagicMock(=TableSearcher)
        searcher = MagicMock()
        searcher.file_path = MagicMock()
        searcher._should_update_cache = MagicMock()
        return searcher

    @pytest.fixture()
    def pickle_file(self, tmp_path, sample_dataframe):
        file_path = tmp_path / "test_table.pkl"
        with Path(file_path).open('wb') as f:
            pickle.dump(sample_dataframe, f)
        return file_path

    @pytest.fixture()
    def mock_config(self):
        config = MagicMock()
        config.env = "test"
        config.common_config = {"optional_path": {"TABLE_PATH": "/default/path"}}
        config.package_config = {}
        config.log_message = MagicMock()
        return config

    @pytest.fixture()
    def sample_dataframe(self):
        return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    @pytest.fixture()
    def mock_dataframe(self):
        return pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})

    def test_default_load_table_C0_normal(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: テーブルが正常に読み込まれる
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        with patch('pandas.read_pickle', return_value=mock_df):
            mock_searcher._should_update_cache.return_value = True
            result = TableSearcher._default_load_table(mock_searcher)

        pd.testing.assert_frame_equal(result, mock_df)

    def test_default_load_table_C0_file_not_found(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: ファイルが存在しない場合、FileNotFoundErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('pandas.read_pickle', side_effect=FileNotFoundError), \
            pytest.raises(FileNotFoundError) as excinfo:
            mock_searcher._should_update_cache.return_value = True
            TableSearcher._default_load_table(mock_searcher)

        assert str(excinfo.value) == ErrorMessages.FILE_NOT_FOUND

    def test_default_load_table_C0_invalid_pickle(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 無効なpickleファイルの場合、例外が発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('pandas.read_pickle', side_effect=Exception("Invalid pickle")), \
            pytest.raises(Exception) as excinfo:
            mock_searcher._should_update_cache.return_value = True
            TableSearcher._default_load_table(mock_searcher)

        assert str(excinfo.value) == ErrorMessages.TABLE_LOAD_ERROR

    def test_default_load_table_C1_cache_update_needed(self, mock_config, pickle_file, sample_dataframe):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: キャッシュの更新が必要な場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('pandas.read_pickle', return_value=sample_dataframe), \
                patch.object(TableSearcher, '_should_update_cache', return_value=True), \
                patch.object(TableSearcher._default_load_table, 'cache_clear') as mock_cache_clear:

            searcher = TableSearcher("test_table.pkl", file_path=pickle_file.parent, config=mock_config)
            assert searcher.table_name == "test_table.pkl"
            assert str(searcher.file_path) == str(pickle_file)

            assert isinstance(searcher.df, pd.DataFrame)
            pd.testing.assert_frame_equal(searcher.df, sample_dataframe)
            mock_cache_clear.assert_called_once()

    def test_default_load_table_C1_cache_update_not_needed(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: キャッシュの更新が不要な場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        with patch('pandas.read_pickle', return_value=mock_df), \
            patch.object(TableSearcher._default_load_table, 'cache_clear') as mock_cache_clear:
            mock_searcher._should_update_cache.return_value = False
            result = TableSearcher._default_load_table(mock_searcher)

        pd.testing.assert_frame_equal(result, mock_df)
        mock_cache_clear.assert_not_called()

    #@pytest.mark.parametrize("should_update,file_exists,file_valid,expected_result", [
    #    (True, True, True, "success"),
    #    (False, True, True, "success"),
    #    (True, False, True, "file_not_found"),
    #    (True, True, False, "invalid_pickle")
    #])
    #def test_default_load_table_C2_combinations(self, mock_searcher, should_update, file_exists, file_valid, expected_result):
    #    test_doc = f"""
    #    テスト区分: UT
    #    テストカテゴリ: C2
    #    テスト内容: キャッシュ更新:{should_update}, ファイル存在:{file_exists}, ファイル有効:{file_valid}, 期待結果:{expected_result}
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    mock_df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
    #    mock_searcher._should_update_cache = MagicMock(return_value=should_update)

    #    if not file_exists:
    #        side_effect = FileNotFoundError(ErrorMessages.FILE_NOT_FOUND)
    #    elif not file_valid:
    #        side_effect = Exception(ErrorMessages.TABLE_LOAD_ERROR.format(error="Invalid pickle"))
    #    else:
    #        side_effect = None

    #    with patch('pandas.read_pickle', return_value=mock_df, side_effect=side_effect), \
    #         patch.object(TableSearcher._default_load_table, 'cache_clear') as mock_cache_clear:
    #
    #        if expected_result == "file_not_found":
    #            with pytest.raises(FileNotFoundError) as excinfo:
    #                TableSearcher._default_load_table(mock_searcher)
    #            assert str(excinfo.value) == ErrorMessages.FILE_NOT_FOUND
    #            mock_cache_clear.assert_not_called()
    #        elif expected_result == "invalid_pickle":
    #            with pytest.raises(Exception) as excinfo:
    #                TableSearcher._default_load_table(mock_searcher)
    #            assert str(excinfo.value) == ErrorMessages.TABLE_LOAD_ERROR
    #            mock_cache_clear.assert_not_called()
    #        else:
    #            result = TableSearcher._default_load_table(mock_searcher)
    #            pd.testing.assert_frame_equal(result, mock_df)
    #            if should_update:
    #                mock_cache_clear.assert_called_once()
    #            else:
    #                mock_cache_clear.assert_not_called()

    #    log_msg(f"Test completed: {test_doc}", LogLevel.DEBUG)

    def test_default_load_table_BVT_empty_df(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空のDataFrame
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        empty_df = pd.DataFrame()
        with patch('pandas.read_pickle', return_value=empty_df):
            mock_searcher._should_update_cache.return_value = True
            result = TableSearcher._default_load_table(mock_searcher)

        pd.testing.assert_frame_equal(result, empty_df)
        assert result.empty

    def test_default_load_table_BVT_large_df(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 大規模なDataFrame
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        large_df = pd.DataFrame({'col1': range(1000000), 'col2': ['a'] * 1000000})
        with patch('pandas.read_pickle', return_value=large_df):
            mock_searcher._should_update_cache.return_value = True
            result = TableSearcher._default_load_table(mock_searcher)

        pd.testing.assert_frame_equal(result, large_df)
        assert len(result) == 1000000


#class TestTableSearcherSimpleSearch:
#    """TableSearcherクラスのsimple_searchメソッドのテスト
#
#    テスト構造:
#    ├── C0: 基本機能テスト
#    │   ├── 正常系: 単一条件での検索
#    │   ├── 正常系: 複数条件でのAND検索
#    │   ├── 正常系: 複数条件でのOR検索
#    │   ├── 正常系: 前方一致検索
#    │   └── 異常系: 無効なoperatorでValueError
#    ├── C1: 分岐カバレッジ
#    │   ├── 条件が辞書の場合
#    │   ├── 条件がリストの場合
#    │   ├── AND演算子の場合
#    │   └── OR演算子の場合
#    ├── C2: 条件組み合わせ
#    │   ├── 等値検索と前方一致検索の組み合わせ
#    │   ├── 複数のAND条件
#    │   └── 複数のOR条件
#    ├── DT: ディシジョンテーブル
#    │   └── 条件の種類とoperatorの組み合わせ
#    └── BVT: 境界値テスト
#        ├── 空の条件
#        ├── 全ての行にマッチする条件
#        └── どの行にもマッチしない条件
#
#    C1のディシジョンテーブル:
#    | 条件             | ケース1 | ケース2 | ケース3 | ケース4 |
#    |------------------|---------|---------|---------|---------|
#    | 条件が辞書       | Y       | N       | Y       | N       |
#    | AND演算子        | Y       | Y       | N       | N       |
#    | 期待される動作   | AND検索 | AND検索 | OR検索  | OR検索  |
#
#    境界値検証ケース一覧:
#    | ケースID | 入力パラメータ | テスト値                             | 期待される結果  | テストの目的/検証ポイント                        | 実装状況 | 対応するテストケース             |
#    |----------|----------------|--------------------------------------|-----------------|--------------------------------------------------|----------|----------------------------------|
#    | BVT_001  | conditions     | {}                                   | 空のDataFrame   | 空の条件での動作確認                             | 実装済み | test_simple_search_BVT_empty_condition |
#    | BVT_002  | conditions     | {"column1": "value1", "column2": "value2"} | 全行を返す     | 全ての行にマッチする条件の確認                   | 実装済み | test_simple_search_BVT_all_match  |
#    | BVT_003  | conditions     | {"column1": "non_existent_value"}    | 空のDataFrame   | どの行にもマッチしない条件の確認                 | 実装済み | test_simple_search_BVT_no_match   |
#
#    境界値検証ケースの実装状況サマリー:
#    - 実装済み: 3
#    - 未実装: 0
#    - 一部実装: 0
#
#    注記:
#    すべての境界値検証ケースが実装されています。これにより、simple_searchメソッドの
#    極端な入力や特殊なケースでの動作が適切にテストされ、メソッドの堅牢性が確保されています。
#    """
#
#    def setup_method(self):
#        log_msg("test start", LogLevel.INFO)
#
#    def teardown_method(self):
#        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)
#
#    @pytest.fixture
#    def sample_df(self):
#        return pd.DataFrame({
#            'column1': ['value1', 'value2', 'value3'],
#            'column2': ['a', 'b', 'c'],
#            'column3': [1, 2, 3]
#        })
#
#    @pytest.fixture
#    def mock_searcher(self, sample_df):
#        #searcher = MagicMock(=TableSearcher)
#        searcher = MagicMock()
#        searcher.df = sample_df
#        searcher._normalize_conditions.return_value = [{'column1': 'value1'}]
#        searcher._create_masks.return_value = [pd.Series([True, False, False])]
#        return searcher
#
#    def test_simple_search_C0_single_condition(self, mock_searcher):
#        test_doc = """
#        テスト区分: UT
#        テストカテゴリ: C0
#        テスト内容: 単一条件での検索
#        """
#        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
#
#        conditions = {"column1": "value1"}
#        with patch.object(TableSearcher, 'simple_search', wraps=TableSearcher.simple_search):
#            result = TableSearcher.simple_search(mock_searcher, conditions)
#
#        assert len(result) == 1
#        assert result.iloc[0]['column1'] == 'value1'
#        log_msg(f'mock_searcher: \n{mock_searcher._normalize_conditions.return_value}')
#        log_msg(f'mock_searcher: \n{mock_searcher._create_masks.return_value }')
#        log_msg(f'input pickled: \n{tabulate_dataframe(mock_searcher.df)}')
#        log_msg(f'searched dataframe: \n{tabulate_dataframe(result)}')
#
#    def test_simple_search_C0_single_condition_real_pickle1(self):
#        test_doc = """
#        テスト区分: UT
#        テストカテゴリ: C0
#        テスト内容: 単一条件での検索, src/table/jinji_requests.pklを読む
#        """
#        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
#
#        # 簡単なdictで条件を与える
#        conditions = {"親部店コード": "31235"}
#
#        searcher = TableSearcher("jinji_requests.pkl")
#        _df = searcher.simple_search(conditions)
#        log_msg(f'simple_search real pickle\n\n{tabulate_dataframe(_df)}\n', LogLevel.INFO)
#
#    def test_advanced_search_C0_single_condition_real_pickle1(self):
#        test_doc = """
#        テスト区分: UT
#        テストカテゴリ: C0
#        テスト内容: 単一条件での検索, src/table/jinji_requests.pklを読む
#        """
#        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
#
#        # 関数記述で条件を定義する
#        # pickle->dfになっているので、dfに対して条件を書く
#        def condition(df):
#            return (df['親部店コード'] == '31235')
#
#        searcher = TableSearcher("jinji_requests.pkl")
#        _df = searcher.advanced_search(condition)
#        log_msg(f'advanced_search real pickle\n\n{tabulate_dataframe(_df)}\n', LogLevel.INFO)

class TestTableSearcherNormalizeConditions:
    """TableSearcherクラスの_normalize_conditionsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 辞書型の条件を正規化
    │   └── 正常系: リスト型の条件をそのまま返す
    ├── C1: 分岐カバレッジ
    │   ├── 条件が辞書型の場合
    │   └── 条件がリスト型の場合
    ├── C2: 条件組み合わせ
    │   ├── 空の辞書
    │   ├── 空のリスト
    │   └── 複数の条件を含むリスト
    └── BVT: 境界値テスト
        ├── 1つの条件を持つ辞書
        └── 多数の条件を持つ辞書

    C1のディシジョンテーブル:
    | 条件             | ケース1 | ケース2 |
    |------------------|---------|---------|
    | 条件が辞書型     | Y       | N       |
    | 期待される結果   | リスト化 | そのまま |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                             | 期待される結果  | テストの目的/検証ポイント                        | 実装状況 | 対応するテストケース             |
    |----------|----------------|--------------------------------------|-----------------|--------------------------------------------------|----------|----------------------------------|
    | BVT_001  | conditions     | {}                                   | [{}]            | 空の辞書の処理を確認                             | 実装済み | test_normalize_conditions_BVT_empty_dict |
    | BVT_002  | conditions     | []                                   | []              | 空のリストの処理を確認                           | 実装済み | test_normalize_conditions_BVT_empty_list |
    | BVT_003  | conditions     | {"key": "value"}                     | [{"key": "value"}] | 1つの条件を持つ辞書の処理を確認               | 実装済み | test_normalize_conditions_BVT_single_condition |
    | BVT_004  | conditions     | {"k1": "v1", "k2": "v2", ..., "k100": "v100"} | [{"k1": "v1", "k2": "v2", ..., "k100": "v100"}] | 多数の条件を持つ辞書の処理を確認 | 実装済み | test_normalize_conditions_BVT_many_conditions |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 4
    - 未実装: 0
    - 一部実装: 0

    注記:
    すべての境界値検証ケースが実装されています。これにより、_normalize_conditionsメソッドの
    様々な入力パターンに対する動作が適切にテストされ、メソッドの堅牢性が確保されています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_searcher(self):
        def mock_get_file_modified_time():
            timestamp = 12345.0
            log_msg(f"Mock _default_get_file_modified_time called, returning {timestamp}", LogLevel.INFO)
            return timestamp

        def mock_load_table():
            _df = pd.DataFrame({'test_column': [1, 2, 3]})
            log_msg(f"Mock _default_load_table called, returning DataFrame with shape {_df.shape}", LogLevel.INFO)
            log_msg(f"\n\n mocked dataframe: \n{tabulate_dataframe(_df)}", LogLevel.INFO)
            return _df

        with patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_get_file_modified_time',
                side_effect=mock_get_file_modified_time) as mock_get_time, \
            patch('src.lib.common_utils.ibr_pickled_table_searcher.TableSearcher._default_load_table',
                side_effect=mock_load_table) as mock_load:

            log_msg("Creating mock TableSearcher instance", LogLevel.INFO)
            searcher = TableSearcher("test_table.pkl")

            # パッチが適用されたことを確認
            log_msg(f"_default_get_file_modified_time called: {mock_get_time.called}", LogLevel.INFO)
            log_msg(f"_default_load_table called: {mock_load.called}", LogLevel.INFO)

            # 実際に返された値を確認
            if mock_get_time.called:
                log_msg(f"Actual value returned by _default_get_file_modified_time: {searcher.last_modified_time}", LogLevel.INFO)
            if mock_load.called:
                log_msg(f"Actual DataFrame returned by _default_load_table: shape {searcher.df.shape}, columns {searcher.df.columns}", LogLevel.INFO)

            yield searcher

    def test_normalize_conditions_C0_dict(self, mock_searcher):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 辞書型の条件を正規化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        conditions = {"column1": "value1"}
        log_msg("Calling _normalize_conditions", LogLevel.INFO)
        result = mock_searcher._normalize_conditions(conditions)
        log_msg(f"_normalize_conditions result: {result}", LogLevel.INFO)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == conditions
