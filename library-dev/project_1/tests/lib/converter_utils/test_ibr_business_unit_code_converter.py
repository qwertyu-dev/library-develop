"""BusinessUnitCodeConverter test class"""
import pickle
from pathlib import Path

import pandas as pd
import pytest

####################################
# テストサポートモジュール
####################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

####################################
# テスト対象モジュール
####################################
from src.lib.converter_utils.ibr_business_unit_code_converter import BusinessUnitCodeConverter

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestBusinessUnitCodeConverterInit:
    """BusinessUnitCodeConverterの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な変換テーブルファイルでインスタンス生成
    │   ├── 異常系: 存在しないファイルでFileNotFoundError
    │   └── 異常系: 無効なファイル形式でException
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try文が正常に実行される
    │   ├── 異常系: FileNotFoundError分岐
    │   ├── 異常系: 無効なファイル形式でその他のException分岐
    │   └── 異常系: 権限エラーでその他のException分岐
    └── C2: 条件組み合わせ
        ├── 正常系: 有効なファイルでインスタンスが正常に生成される
        ├── 異常系: 存在しないファイルでFileNotFoundError
        ├── 異常系: 無効なpickleファイルでException
        ├── 異常系: 空のDataFrameを含むpickleファイルでException
        └── 異常系: 無効な構造のDataFrameを含むpickleファイルでException

    C1 ディシジョンテーブル
    | 条件 | ケース1 | ケース2 | ケース3 | ケース4 |
    |------|--------|--------|--------|--------|
    | ファイルが存在する | Y | N | Y | Y |
    | ファイルが有効なpickle形式 | Y | - | N | Y |
    | ファイルに読み取り権限がある | Y | - | - | N |
    | 出力 | 正常にインスタンス生成 | FileNotFoundError | Exception (無効なファイル) | Exception (権限エラー) |
    """
    @pytest.fixture()
    def valid_conversion_table(self, tmp_path):
        """有効な変換テーブルのfixture"""
        file_path = tmp_path / "valid_table.pkl"
        _df = pd.DataFrame({
            'business_unit_code_jinji': ['001', '002'],
            'main_business_unit_code_jinji': ['M001', 'M002'],
            'business_unit_code_bpr': ['B001', 'B002'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        return file_path

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_valid_file(self, valid_conversion_table):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な変換テーブルファイルでインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        converter = BusinessUnitCodeConverter(valid_conversion_table)
        assert isinstance(converter.conversion_table, pd.DataFrame)
        assert not converter.conversion_table.empty

    def test_init_C0_file_not_found(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 存在しないファイルでFileNotFoundError
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        non_existent_file = tmp_path / "non_existent.pkl"
        with pytest.raises(FileNotFoundError):
            BusinessUnitCodeConverter(non_existent_file)

    def test_init_C0_invalid_file(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 無効なファイル形式でException
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not a pickle file")
        with pytest.raises(Exception):
            BusinessUnitCodeConverter(invalid_file)

    def test_init_C1_valid_file(self, valid_conversion_table):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効なファイルでtry文が正常に実行される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        converter = BusinessUnitCodeConverter(valid_conversion_table)
        assert isinstance(converter.conversion_table, pd.DataFrame)
        assert not converter.conversion_table.empty

    def test_init_C1_file_not_found(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 存在しないファイルでFileNotFoundError分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        non_existent_file = tmp_path / "non_existent.pkl"
        with pytest.raises(FileNotFoundError) as excinfo:
            BusinessUnitCodeConverter(non_existent_file)
        assert "変換テーブルファイルが見つかりません" in str(excinfo.value)


    def test_init_C1_invalid_file(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効なファイル形式でその他のException分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not a pickle file")
        with pytest.raises(Exception) as excinfo:
            BusinessUnitCodeConverter(invalid_file)
        assert "変換テーブルの読み込み中にエラーが発生しました" in str(excinfo.value)

    def test_init_C1_permission_error(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 権限エラーでその他のException分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        no_permission_file = tmp_path / "no_permission.pkl"
        no_permission_file.touch(mode=0o000)  # 読み取り権限のないファイルを作成
        with pytest.raises(Exception) as excinfo:
            BusinessUnitCodeConverter(no_permission_file)
        assert "変換テーブルの読み込み中にエラーが発生しました" in str(excinfo.value)

    def test_init_C2_valid_file(self, valid_conversion_table):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 有効なファイルでインスタンスが正常に生成される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        converter = BusinessUnitCodeConverter(valid_conversion_table)
        assert isinstance(converter.conversion_table, pd.DataFrame)
        assert not converter.conversion_table.empty
        assert list(converter.conversion_table.columns) == ['main_business_unit_code_jinji', 'business_unit_code_bpr']

    def test_init_C2_file_not_found(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 存在しないファイルでFileNotFoundErrorが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        non_existent_file = tmp_path / "non_existent.pkl"
        with pytest.raises(FileNotFoundError) as excinfo:
            BusinessUnitCodeConverter(non_existent_file)
        assert "変換テーブルファイルが見つかりません" in str(excinfo.value)

    def test_init_C2_invalid_pickle(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効なpickleファイルでExceptionが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        invalid_pickle = tmp_path / "invalid.pkl"
        with invalid_pickle.open('wb') as f:
            pickle.dump("This is not a DataFrame", f)
        with pytest.raises(Exception) as excinfo:
            BusinessUnitCodeConverter(invalid_pickle)
        assert "変換テーブルの読み込み中にエラーが発生しました" in str(excinfo.value)

    def test_init_C2_empty_dataframe(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 空のDataFrameを含むpickleファイルでExceptionが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        empty_df_file = tmp_path / "empty_df.pkl"
        with empty_df_file.open('wb') as f:
            pickle.dump(pd.DataFrame(), f)
        with pytest.raises(Exception) as excinfo:
            BusinessUnitCodeConverter(empty_df_file)
        assert "変換テーブルの読み込み中にエラーが発生しました" in str(excinfo.value)

    def test_init_C2_invalid_dataframe_structure(self, tmp_path):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効な構造のDataFrameを含むpickleファイルでExceptionが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        invalid_df_file = tmp_path / "invalid_df.pkl"
        invalid_df = pd.DataFrame({'column1': [1, 2], 'column2': [3, 4]})
        with invalid_df_file.open('wb') as f:
            pickle.dump(invalid_df, f)
        with pytest.raises(Exception) as excinfo:
            BusinessUnitCodeConverter(invalid_df_file)
        assert "変換テーブルの読み込み中にエラーが発生しました" in str(excinfo.value)

class TestBusinessUnitCodeConverterGetMain:
    """BusinessUnitCodeConverterのget_business_unit_code_mainメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な人事部門コードで主管部門コードを取得
    │   ├── 異常系: 存在しない人事部門コードでKeyErrorが発生
    │   └── 異常系: データフレーム操作中に例外が発生
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try文が正常に実行される
    │   ├── 異常系: 存在しない人事部門コードでIndexError分岐に入る
    │   ├── 異常系: DataFrameの操作でエラーが発生し、Exception分岐に入る
    │   └── 異常系: 検索結果が空の場合にIndexError分岐に入る
    └── C2: 条件組み合わせ
        ├── 正常系: 有効な人事部門コードで主管部門コードを取得
        ├── 異常系: 存在しない人事部門コードでKeyErrorが発生
        ├── 異常系: 空の人事部門コードでKeyErrorが発生
        ├── 異常系: 文字列でない人事部門コードでTypeErrorが発生
        ├── 正常系: DataFrameの最初の人事部門コードで主管部門コードを取得
        └── 正常系: DataFrameの最後の人事部門コードで主管部門コードを取得

    # C1のディシジョンテーブル
    | 条件 | ケース1 | ケース2 | ケース3 | ケース4 |
    |------|--------|--------|--------|--------|
    | 人事部門コードが存在する | Y | N | Y | Y |
    | DataFrameの操作が成功する | Y | Y | N | Y |
    | 検索結果が空ではない | Y | - | - | N |
    | 出力 | 主管部門コード | KeyError | Exception | KeyError |
    """

    @pytest.fixture()
    def converter(self, tmp_path):
        """テスト用のBusinessUnitCodeConverterインスタンスを作成するフィクスチャ"""
        file_path = tmp_path / "test_table.pkl"
        _df = pd.DataFrame({
            'business_unit_code_jinji': ['001', '002', '003', '004', '005'],
            'main_business_unit_code_jinji': ['M001', 'M002', 'M003', 'M004', 'M005'],
            'business_unit_code_bpr': ['B001', 'B002', 'B003', 'B004', 'B005'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        return BusinessUnitCodeConverter(file_path)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)


    # C0テスト
    def test_get_business_unit_code_main_C0_valid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_main('001')
        assert result == 'M001'

    def test_get_business_unit_code_main_C0_invalid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 存在しない人事部門コードでKeyErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_main('999')
        assert "指定された人事部門コードは変換テーブルに存在しません" in str(excinfo.value)

    def test_get_business_unit_code_main_C1_dataframe_error(self, converter, monkeypatch):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DataFrameの操作でエラーが発生し、Exception分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        def mock_loc(*args: list, **kwargs: dict) -> None:
            err_msg = "Mock DataFrame error"
            raise pd.errors.InvalidIndexError(err_msg)

        monkeypatch.setattr(pd.DataFrame, 'loc', property(mock_loc))  # propertyとしてモックする

        with pytest.raises(Exception) as excinfo:
            converter.get_business_unit_code_main('001')
        assert "主管部門コードの取得中にエラーが発生しました" in str(excinfo.value)


    # C1テスト
    def test_get_business_unit_code_main_C1_valid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効な人事部門コードで主管部門コードを取得 try文が正常に実行される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_main('001')
        assert result == 'M001'

    def test_get_business_unit_code_main_C1_invalid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 存在しない人事部門コードでIndexError分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_main('999')
        assert "指定された人事部門コードは変換テーブルに存在しません: 999" in str(excinfo.value)

    def test_get_business_unit_code_main_C1_empty_result(self, converter, monkeypatch):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 検索結果が空の場合にValueErrorが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        def mock_loc(*args: list, **kwargs: dict) -> pd.DataFrame:
            return pd.DataFrame({'main_business_unit_code_jinji': []})

        monkeypatch.setattr(pd.DataFrame, 'loc', mock_loc)

        with pytest.raises(Exception) as excinfo:
            converter.get_business_unit_code_main('001')
        assert "主管部門コードの取得中にエラーが発生しました" in str(excinfo.value)

    # C2テスト
    def test_get_business_unit_code_main_C2_valid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 有効な人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_main('003')
        assert result == 'M003'

    def test_get_business_unit_code_main_C2_invalid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 存在しない人事部門コードでKeyErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_main('999')
        assert "指定された人事部門コードは変換テーブルに存在しません: 999" in str(excinfo.value)

    def test_get_business_unit_code_main_C2_empty_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 空の人事部門コードでKeyErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_main('')
        assert "指定された人事部門コードは変換テーブルに存在しません: " in str(excinfo.value)

    def test_get_business_unit_code_main_C2_non_string_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 文字列でない人事部門コードでValueErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_main(123)
        assert "指定された人事部門コードは変換テーブルに存在しません: " in str(excinfo.value)

    def test_get_business_unit_code_main_C2_first_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameの最初の人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_main('001')
        assert result == 'M001'

    def test_get_business_unit_code_main_C2_last_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameの最後の人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_main('005')
        assert result == 'M005'

class TestBusinessUnitCodeConverterGetBpr:
    """BusinessUnitCodeConverterのget_business_unit_code_bprメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な人事部門コードで主管部門コードを取得
    │   ├── 異常系: 存在しない人事部門コードでKeyErrorが発生
    │   └── 異常系: データフレーム操作中に例外が発生
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try文が正常に実行される
    │   ├── 異常系: 存在しない人事部門コードでIndexError分岐に入る
    │   ├── 異常系: DataFrameの操作でエラーが発生し、Exception分岐に入る
    │   └── 異常系: 検索結果が空の場合にIndexError分岐に入る
    └── C2: 条件組み合わせ
        ├── 正常系: 有効な人事部門コードで主管部門コードを取得
        ├── 異常系: 存在しない人事部門コードでKeyErrorが発生
        ├── 異常系: 空の人事部門コードでKeyErrorが発生
        ├── 異常系: 文字列でない人事部門コードでTypeErrorが発生
        ├── 正常系: DataFrameの最初の人事部門コードで主管部門コードを取得
        └── 正常系: DataFrameの最後の人事部門コードで主管部門コードを取得

    # C1のディシジョンテーブル
    | 条件 | ケース1 | ケース2 | ケース3 | ケース4 |
    |------|--------|--------|--------|--------|
    | 人事部門コードが存在する | Y | N | Y | Y |
    | DataFrameの操作が成功する | Y | Y | N | Y |
    | 検索結果が空ではない | Y | - | - | N |
    | 出力 | 主管部門コード | KeyError | Exception | KeyError |
    """

    @pytest.fixture()
    def converter(self, tmp_path):
        """テスト用のBusinessUnitCodeConverterインスタンスを作成するフィクスチャ"""
        file_path = tmp_path / "test_table.pkl"
        df = pd.DataFrame({
            'business_unit_code_jinji': ['001', '002', '003', '004', '005'],
            'main_business_unit_code_jinji': ['M001', 'M002', 'M003', 'M004', 'M005'],
            'business_unit_code_bpr': ['B001', 'B002', 'B003', 'B004', 'B005'],
        })
        with file_path.open('wb') as f:
            pickle.dump(df, f)
        return BusinessUnitCodeConverter(file_path)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)


    # C0テスト
    def test_get_business_unit_code_bpr_C0_valid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効な人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_bpr('001')
        assert result == 'B001'

    def test_get_business_unit_code_bpr_C0_invalid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 存在しない人事部門コードでKeyErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_bpr('999')
        assert "指定された人事部門コードは変換テーブルに存在しません" in str(excinfo.value)

    def test_get_business_unit_code_bpr_C1_dataframe_error(self, converter, monkeypatch):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DataFrameの操作でエラーが発生し、Exception分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        def mock_loc(*args: list, **kwargs: dict) -> None:
            err_msg = "Mock DataFrame error"
            raise pd.errors.InvalidIndexError(err_msg)

        monkeypatch.setattr(pd.DataFrame, 'loc', property(mock_loc))  # propertyとしてモックする

        with pytest.raises(Exception) as excinfo:
            converter.get_business_unit_code_bpr('001')
        assert "BPR部門コードの取得中にエラーが発生しました" in str(excinfo.value)

    # C1テスト
    def test_get_business_unit_code_bpr_C1_valid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効な人事部門コードで主管部門コードを取得 try文が正常に実行される
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_bpr('001')
        assert result == 'B001'

    def test_get_business_unit_code_bpr_C1_invalid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 存在しない人事部門コードでIndexError分岐に入る
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_bpr('999')
        assert "指定された人事部門コードは変換テーブルに存在しません: 999" in str(excinfo.value)

    def test_get_business_unit_code_bpr_C1_empty_result(self, converter, monkeypatch):
        test_doc = """テスト内容:

        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 検索結果が空の場合にValueErrorが発生する
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        def mock_loc(*args: list, **kwargs: dict) -> pd.DataFrame:
            return pd.DataFrame({'main_business_unit_code_jinji': []})

        monkeypatch.setattr(pd.DataFrame, 'loc', mock_loc)

        with pytest.raises(Exception) as excinfo:
            converter.get_business_unit_code_bpr('001')
        assert "BPR部門コードの取得中にエラーが発生しました" in str(excinfo.value)

    # C2テスト
    def test_get_business_unit_code_bpr_C2_valid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 有効な人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_bpr('003')
        assert result == 'B003'

    def test_get_business_unit_code_bpr_C2_invalid_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 存在しない人事部門コードでKeyErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_bpr('999')
        assert "指定された人事部門コードは変換テーブルに存在しません: 999" in str(excinfo.value)

    def test_get_business_unit_code_bpr_C2_empty_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 空の人事部門コードでKeyErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_bpr('')
        assert "指定された人事部門コードは変換テーブルに存在しません: " in str(excinfo.value)

    def test_get_business_unit_code_bpr_C2_non_string_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 文字列でない人事部門コードでValueErrorが発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with pytest.raises(ValueError) as excinfo:
            converter.get_business_unit_code_bpr(123)
        assert "指定された人事部門コードは変換テーブルに存在しません: " in str(excinfo.value)

    def test_get_business_unit_code_bpr_C2_first_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameの最初の人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_bpr('001')
        assert result == 'B001'

    def test_get_business_unit_code_bpr_C2_last_code(self, converter):
        test_doc = """テスト内容:

        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: DataFrameの最後の人事部門コードで主管部門コードを取得
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = converter.get_business_unit_code_bpr('005')
        assert result == 'B005'
