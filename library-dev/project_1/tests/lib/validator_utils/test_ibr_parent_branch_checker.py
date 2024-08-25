import pytest
from pathlib import Path
import pandas as pd
import pickle

####################################
# テスト対象モジュールimport
####################################
from src.lib.validator_utils.ibr_parent_branch_checker import ParentBranchChecker

####################################
# テストサポートモジュールimport
####################################
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestParentBranchCheckerInit:
    """ParentBranchCheckerの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なファイル名でインスタンス生成
    │   └── 異常系: 無効なファイル名で例外発生
    ├── C1: ファイル名の有効性チェック
    │   ├── 正常系: 有効なファイル名
    │   └── 異常系: 無効なファイル名
    └── C2: ファイルの種類と内容の組み合わせ
        ├── 正常系: application_data_fileとreference_data_fileが両方有効
        ├── 異常系: application_data_fileが無効
        ├── 異常系: reference_data_fileが無効
        └── 異常系: 両方のファイルが無効

    # C1のディシジョンテーブル
    | 条件                                | ケース1 | ケース2 | ケース3 | ケース4 |
    |-------------------------------------|---------|---------|---------|---------|
    | application_data_fileが有効         | Y       | N       | Y       | N       |
    | reference_data_fileが有効           | Y       | Y       | N       | N       |
    | 出力                                | 正常    | 例外    | 例外    | 例外    |
    """

    @classmethod
    def setup_class(cls) -> None:
        cls.table_dir = Path("src/table")
        cls.table_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def teardown_class(cls) -> None:
        for file in cls.table_dir.glob("*.pkl"):
            file.unlink(missing_ok=True)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_application_data(self):
        """有効な申請データのfixture"""
        file_name = "valid_application.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['1234567', '2345678'],
            'section_gr_code_bpr': ['0', '1'],
            'section_gr_name_bpr': ['[グループなし]部門', '営業部門'],
            'branch_name_bpr': ['東京支店', '大阪支店'],
            'parent_branch_code': ['1234', '2345'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    @pytest.fixture()
    def valid_reference_data(self):
        """有効なリファレンスデータのfixture"""
        file_name = "valid_reference.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['3456789', '4567890'],
            'section_gr_code_bpr': ['0', '1'],
            'section_gr_name_bpr': ['[グループなし]部門', '管理部門'],
            'branch_name_bpr': ['名古屋支店', '福岡支店'],
            'parent_branch_code': ['3456', '4567'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    def test_init_C0_valid_files(self, valid_application_data, valid_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なファイル名でインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(valid_application_data, valid_reference_data)
        assert isinstance(checker.application_searcher, TableSearcher)
        assert isinstance(checker.reference_searcher, TableSearcher)

    def test_init_C0_invalid_application_file(self, valid_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 無効な申請データファイル名で例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_file = "invalid_application.pkl"
        with pytest.raises(FileNotFoundError):
            ParentBranchChecker(invalid_file, valid_reference_data)

    def test_init_C1_valid_files(self, valid_application_data, valid_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 有効なファイル名
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(valid_application_data, valid_reference_data)
        assert checker.application_searcher.table_name == valid_application_data
        assert checker.reference_searcher.table_name == valid_reference_data

    def test_init_C1_invalid_reference_file(self, valid_application_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効なリファレンスデータファイル名
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_file = "invalid_reference.pkl"
        with pytest.raises(FileNotFoundError):
            ParentBranchChecker(valid_application_data, invalid_file)

    @pytest.mark.parametrize(("app_file", "ref_file", "expected_exception"), [
        (True, True, None),
        (False, True, FileNotFoundError),
        (True, False, FileNotFoundError),
        (False, False, FileNotFoundError),
    ])
    def test_init_C2_file_combinations(self, app_file, ref_file, expected_exception, valid_application_data, valid_reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: ファイルの種類と内容の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        app_name = valid_application_data if app_file else "invalid_app.pkl"
        ref_name = valid_reference_data if ref_file else "invalid_ref.pkl"

        if expected_exception:
            with pytest.raises(expected_exception):
                ParentBranchChecker(app_name, ref_name)
        else:
            checker = ParentBranchChecker(app_name, ref_name)
            assert isinstance(checker.application_searcher, TableSearcher)
            assert isinstance(checker.reference_searcher, TableSearcher)

class TestParentBranchCheckerCheckCondition1:
    """ParentBranchCheckerのcheck_condition_1メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 条件を満たす場合
    │   └── 正常系: 条件を満たさない場合
    ├── C1: データソース分岐
    │   ├── 申請明細レコードで条件を満たす
    │   ├── リファレンステーブルで条件を満たす
    │   └── どちらのテーブルでも条件を満たさない
    └── C2: 条件の組み合わせ
        ├── 正常系: 前方4桁一致、課Grコード0、[グループなし]含む
        ├── 異常系: 前方4桁不一致
        ├── 異常系: 課Grコード0以外
        └── 異常系: [グループなし]を含まない

    # C1のディシジョンテーブル
    | 条件                                | ケース1 | ケース2 | ケース3 |
    |-------------------------------------|---------|---------|---------|
    | 申請明細レコードで条件を満たす      | Y       | N       | N       |
    | リファレンステーブルで条件を満たす  | N       | Y       | N       |
    | 出力                                | True    | True    | False   |
    """

    @classmethod
    def setup_class(cls) -> None:
        cls.table_dir = Path("src/table")
        cls.table_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def teardown_class(cls) -> None:
        for file in cls.table_dir.glob("*.pkl"):
            file.unlink(missing_ok=True)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def application_data(self):
        """申請データのfixture"""
        file_name = "application_data.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['1234567', '2345678', '3456789'],
            'section_gr_code_bpr': ['0', '1', '0'],
            'section_gr_name_bpr': ['[グループなし]部門', '営業部門', '管理部門'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    @pytest.fixture()
    def reference_data(self):
        """リファレンスデータのfixture"""
        file_name = "reference_data.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['4567890', '5678901', '6789012'],
            'section_gr_code_bpr': ['0', '1', '0'],
            'section_gr_name_bpr': ['[グループなし]部門', '営業部門', '管理部門'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    def test_check_condition_1_C0_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たす場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_1('1234567')
        #assert result == True
        assert result

    def test_check_condition_1_C0_no_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たさない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_1('9999999')
        #assert result == False
        assert not result

    def test_check_condition_1_C1_application_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 申請明細レコードで条件を満たす
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_1('1234567')
        #assert result == True
        assert result

    def test_check_condition_1_C1_reference_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: リファレンステーブルで条件を満たす
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_1('4567890')
        #assert result == True
        assert result

    def test_check_condition_1_C1_no_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: どちらのテーブルでも条件を満たさない
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_1('9999999')
        #assert result == False
        assert not result

    @pytest.mark.parametrize(("branch_code", "expected"), [
        ('1234567', True),   # 正常系: 前方4桁一致、課Grコード0、[グループなし]含む
        ('9999999', False),  # 異常系: 前方4桁不一致
        ('2345678', False),  # 異常系: 課Grコード0以外
        ('3456789', False),  # 異常系: [グループなし]を含まない
    ])
    def test_check_condition_1_C2_combinations(self, application_data, reference_data, branch_code, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: 条件の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_1(branch_code)
        assert result == expected

class TestParentBranchCheckerCheckCondition2:
    """ParentBranchCheckerのcheck_condition_2メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 条件を満たす場合
    │   └── 正常系: 条件を満たさない場合
    ├── C1: データソース分岐
    │   ├── 申請明細レコードで条件を満たす
    │   ├── リファレンステーブルで条件を満たす
    │   └── どちらのテーブルでも条件を満たさない
    └── C2: 条件の組み合わせ
        ├── 正常系: 前方4桁一致、（大阪）含む
        ├── 正常系: 前方4桁一致、（名古屋）含む
        ├── 異常系: 前方4桁不一致
        └── 異常系: （大阪）も（名古屋）も含まない

    # C1のディシジョンテーブル
    | 条件                                | ケース1 | ケース2 | ケース3 |
    |-------------------------------------|---------|---------|---------|
    | 申請明細レコードで条件を満たす      | Y       | N       | N       |
    | リファレンステーブルで条件を満たす  | N       | Y       | N       |
    | 出力                                | True    | True    | False   |
    """

    @classmethod
    def setup_class(cls) -> None:
        cls.table_dir = Path("src/table")
        cls.table_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def teardown_class(cls) -> None:
        for file in cls.table_dir.glob("*.pkl"):
            file.unlink(missing_ok=True)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def application_data(self):
        """申請データのfixture"""
        file_name = "application_data.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['1234567', '2345678', '3456789', '4567890'],
            'branch_name_bpr': ['東京支店（大阪）', '名古屋支店', '福岡支店（名古屋）', '大阪支店'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    @pytest.fixture()
    def reference_data(self):
        """リファレンスデータのfixture"""
        file_name = "reference_data.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['5678901', '6789012', '7890123'],
            'branch_name_bpr': ['札幌支店', '仙台支店（大阪）', '広島支店'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    def test_check_condition_2_C0_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たす場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_2('1234567')
        #assert result == True
        assert result

    def test_check_condition_2_C0_no_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たさない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_2('4567890')
        #assert result == False
        assert not result

    def test_check_condition_2_C1_application_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 申請明細レコードで条件を満たす
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_2('1234567')
        #assert result == True
        assert result

    def test_check_condition_2_C1_reference_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: リファレンステーブルで条件を満たす
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_2('6789012')
        #assert result == True
        assert result

    def test_check_condition_2_C1_no_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: どちらのテーブルでも条件を満たさない
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_2('9999999')
        #assert result == False
        assert not result

    @pytest.mark.parametrize(("branch_code", "expected"), [
        ('1234567', True),   # 正常系: 前方4桁一致、（大阪）含む
        ('3456789', True),   # 正常系: 前方4桁一致、（名古屋）含む
        ('2345678', False),  # 異常系: 前方4桁一致するが、（大阪）（名古屋）を含まない
        ('4567890', False),  # 異常系: 前方4桁一致するが、（大阪）（名古屋）を含まない
        ('6789012', True),   # 正常系: 前方4桁一致、（大阪）含む（リファレンスデータ）
        ('7890123', False),  # 異常系: 前方4桁一致するが、（大阪）（名古屋）を含まない（リファレンスデータ）
        ('9999999', False),  # 異常系: 前方4桁不一致
    ])
    def test_check_condition_2_C2_combinations(self, application_data, reference_data, branch_code, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: 条件の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_2(branch_code)
        assert result == expected


class TestParentBranchCheckerCheckCondition3:
    """ParentBranchCheckerのcheck_condition_3メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 条件を満たす場合
    │   └── 正常系: 条件を満たさない場合
    ├── C1: データソース分岐
    │   ├── リファレンステーブルで条件を満たす
    │   ├── 申請明細レコードで条件を満たす
    │   └── どちらのテーブルでも条件を満たさない
    └── C2: 条件の組み合わせ
        ├── 正常系: リファレンステーブルで親部店コード一致
        ├── 正常系: 申請明細レコードで親部店コード一致
        └── 異常系: どちらのテーブルでも親部店コード不一致

    # C1のディシジョンテーブル
    | 条件                                | ケース1 | ケース2 | ケース3 |
    |-------------------------------------|---------|---------|---------|
    | リファレンステーブルで条件を満たす  | Y       | N       | N       |
    | 申請明細レコードで条件を満たす      | N       | Y       | N       |
    | 出力                                | True    | True    | False   |
    """

    @classmethod
    def setup_class(cls) -> None:
        cls.table_dir = Path("src/table")
        cls.table_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def teardown_class(cls) -> None:
        for file in cls.table_dir.glob("*.pkl"):
            file.unlink(missing_ok=True)

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def application_data(self):
        """申請データのfixture"""
        file_name = "application_data.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['1234567', '2345678', '3456789', '4567890'],
            'parent_branch_code': ['1234', '2345', '3456', '4567'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    @pytest.fixture()
    def reference_data(self):
        """リファレンスデータのfixture"""
        file_name = "reference_data.pkl"
        file_path = self.table_dir / file_name
        _df = pd.DataFrame({
            'branch_code_bpr': ['5678901', '6789012', '7890123'],
            'parent_branch_code': ['5678', '6789', '7890'],
        })
        with file_path.open('wb') as f:
            pickle.dump(_df, f)
        yield file_name
        file_path.unlink(missing_ok=True)

    def test_check_condition_3_C0_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たす場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_3('1234567')
        #assert result == True
        assert result

    def test_check_condition_3_C0_no_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 条件を満たさない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_3('9999999')
        #assert result == False
        assert not result

    def test_check_condition_3_C1_reference_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: リファレンステーブルで条件を満たす
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_3('5678901')
        #assert result == True
        assert result

    def test_check_condition_3_C1_application_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 申請明細レコードで条件を満たす
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_3('1234567')
        #assert result == True
        assert result

    def test_check_condition_3_C1_no_match(self, application_data, reference_data):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: どちらのテーブルでも条件を満たさない
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_3('9999999')
        #assert result == False
        assert not result

    @pytest.mark.parametrize(("branch_code", "expected"), [
        ('5678901', True),   # 正常系: リファレンステーブルで親部店コード一致
        ('1234567', True),   # 正常系: 申請明細レコードで親部店コード一致
        ('9999999', False),  # 異常系: どちらのテーブルでも親部店コード不一致
        ('2345678', True),   # 正常系: 申請明細レコードで親部店コード一致（別のケース）
        ('7890123', True),   # 正常系: リファレンステーブルで親部店コード一致（別のケース）
        ('8901234', False),  # 異常系: どちらのテーブルでも親部店コード不一致（別のケース）
    ])
    def test_check_condition_3_C2_combinations(self, application_data, reference_data, branch_code, expected):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: 条件の組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = ParentBranchChecker(application_data, reference_data)
        result = checker.check_condition_3(branch_code)
        assert result == expected
