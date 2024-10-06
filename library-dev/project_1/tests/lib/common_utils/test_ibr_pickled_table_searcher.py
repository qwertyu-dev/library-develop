import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import pickle
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher, ErrorMessages
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel

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
    | 条件                         | ケース1 | ケース2 | ケース3 | ケース4 |
    |------------------------------|---------|---------|---------|---------|
    | file_pathが指定される        | Y       | N       | Y       | N       |
    | get_file_modified_timeが指定 | Y       | Y       | N       | N       |
    | 期待される動作               | カスタム| デフォルト | カスタム | デフォルト |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                             | 期待される結果  | テストの目的/検証ポイント                        | 実装状況 | 対応するテストケース             |
    |----------|----------------|--------------------------------------|-----------------|--------------------------------------------------|----------|----------------------------------|
    | BVT_001  | table_name     | ""                                   | ValueError      | 空文字列の処理を確認                             | 実装済み | test_init_C0_empty_table_name    |
    | BVT_002  | table_name     | "a" * 255 + ".pkl"                   | 正常終了        | 最大長の文字列での動作を確認                     | 実装済み | test_init_BVT_max_length_table_name |
    | BVT_003  | file_path      | Path("a" * 255)                      | 正常終了        | 最大長のパスでの動作を確認                       | 実装済み | test_init_BVT_max_length_file_path |
    | BVT_004  | file_path      | None                                 | 正常終了        | Noneが指定された場合のデフォルト動作を確認       | 実装済み | test_init_C1_default_file_path   |
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

        #with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe):
        #    searcher = TableSearcher("test_table.pkl", config=mock_config)
        #assert str(searcher.file_path) == str(Path("/default/path/test_table.pkl"))

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


    #    custom_time_func = lambda: 12345.0
    #    with patch("src.lib.common_utils.ibr_pickled_table_searcher.pd.read_pickle", return_value=mock_dataframe):
    #        searcher = TableSearcher("test_table.pkl", get_file_modified_time=custom_time_func, config=mock_config)
    #    assert searcher.get_file_modified_time() == 12345.0


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
        ("/custom/path", lambda: 12345.0, "/custom/path/test_table.pkl", 12345.0),
        (None, lambda: 12345.0, "/default/path/test_table.pkl", 12345.0),
        ("/custom/path", None, "/custom/path/test_table.pkl", 67890.0),
        (None, None, "/default/path/test_table.pkl", 67890.0),
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

