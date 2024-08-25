import pytest
import pandas as pd
import pickle
import time

from unittest.mock import Mock

from pathlib import Path
from typing import Generator, Callable, Any


from src.lib.validator_utils.ibr_dynamic_blacklist_checker import BlacklistChecker, BlacklistCheckerError, RuleApplicationError
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

# C2テストサポート関数
def get_scenario_description(scenario: str) -> str:
    scenarios = {
        "全て適用": "全てのルールが適用",
        "適用なし": "どのルールも適用されない",
        "ルールなし": "ルールが存在しない",
        "一部エラー": "一部のルールでエラーが発生",
    }
    return scenarios.get(scenario, "不明なシナリオ")


@pytest.fixture(scope="module")
def setup_test_data() -> None:
    # テスト用のディレクトリとファイルを作成
    test_dir = Path("src/table")
    test_dir.mkdir(parents=True, exist_ok=True)

    # リファレンステーブル用のDataFrame
    reference_df = pd.DataFrame({
        "部店コード": ["1001", "1002", "1003"],
        "部店名称": ["営業部", "人事部", "総務部"],
        "重要度": [5, 3, 4],
    })

    # 申請テーブル用のDataFrame
    application_df = pd.DataFrame({
        "申請ID": ["A001", "A002", "A003"],
        "部店コード": ["1001", "1002", "1004"],
        "種類": ["変更", "新規", "削除"],
    })

    # DataFrameをpickleファイルとして保存
    with (test_dir / "reference_table.pkl").open("wb") as f:
        pickle.dump(reference_df, f)

    with (test_dir / "application_table.pkl").open("wb") as f:
        pickle.dump(application_df, f)

    yield

    # テスト終了後、作成したファイルを削除
    (test_dir / "reference_table.pkl").unlink()
    (test_dir / "application_table.pkl").unlink()

class TestBlacklistCheckerInit:
    """BlacklistCheckerの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 有効なパラメータでのインスタンス生成
    ├── C1: 分岐カバレッジ
    │   ├── 異常系: 無効なreference_searcherでの初期化
    │   └── 異常系: 無効なapplication_searcherでの初期化
    └── C2: 条件組み合わせ
        ├── 正常系: 両方のsearcherが有効な場合
        ├── 異常系: reference_searcherのみ無効な場合
        ├── 異常系: application_searcherのみ無効な場合
        └── 異常系: 両方のsearcherが無効な場合

    C1のディシジョンテーブル:
    | 条件                               | ケース1 | ケース2 | ケース3 | ケース4 |
    |------------------------------------|---------|---------|---------|---------|
    | reference_searcherが有効           | Y       | N       | Y       | N       |
    | application_searcherが有効         | Y       | Y       | N       | N       |
    | 結果                               | 正常    | エラー  | エラー  | エラー  |
    """

    @pytest.fixture(scope="class")
    def valid_reference_searcher(self) -> TableSearcher:
        return TableSearcher("reference_table.pkl")

    @pytest.fixture(scope="class")
    def valid_application_searcher(self) -> TableSearcher:
        return TableSearcher("application_table.pkl")

    def setup_method(self) -> None:
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self) -> None:
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_init_C0_valid_parameters(self, setup_test_data, valid_reference_searcher, valid_application_searcher) -> None:
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なパラメータでのインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        checker = BlacklistChecker(valid_reference_searcher, valid_application_searcher)
        assert isinstance(checker, BlacklistChecker)
        assert checker.reference_searcher == valid_reference_searcher
        assert checker.application_searcher == valid_application_searcher

    def test_init_C1_invalid_reference_searcher(self, setup_test_data, valid_application_searcher) -> None:
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効なreference_searcherでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_reference_searcher = "invalid_searcher"
        with pytest.raises(BlacklistCheckerError):
            BlacklistChecker(invalid_reference_searcher, valid_application_searcher)

    def test_init_C1_invalid_application_searcher(self, setup_test_data, valid_reference_searcher) -> None:
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効なapplication_searcherでの初期化
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_application_searcher = "invalid_searcher"
        with pytest.raises(BlacklistCheckerError):
            BlacklistChecker(valid_reference_searcher, invalid_application_searcher)


    @pytest.mark.parametrize(
        ("reference_searcher", "application_searcher", "expected_result"),
        [
            ("valid_reference_searcher", "valid_application_searcher", True),
            ("invalid_searcher", "valid_application_searcher", False),
            ("valid_reference_searcher", "invalid_searcher", False),
            ("invalid_searcher", "invalid_searcher", False),
        ],
        ids=["両方有効", "reference無効", "application無効", "両方無効"],
    )
    def test_init_C2_searcher_combinations(
        self, setup_test_data, reference_searcher: str, application_searcher: str,
        expected_result: bool, valid_reference_searcher: TableSearcher,
        valid_application_searcher: TableSearcher,
    ) -> None:
        test_doc = f"""テスト内容:
        - テストカテゴリ: C2
        - テスト区分: {'正常系' if expected_result else '異常系'}
        - テストシナリオ: {' / '.join(filter(None, [
            '両方のsearcherが有効' if expected_result else None,
            'reference_searcherが無効' if reference_searcher == "invalid_searcher" else None,
            'application_searcherが無効' if application_searcher == "invalid_searcher" else None
        ]))}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        ref_searcher = valid_reference_searcher if reference_searcher == "valid_reference_searcher" else "invalid_searcher"
        app_searcher = valid_application_searcher if application_searcher == "valid_application_searcher" else "invalid_searcher"

        if expected_result:
            checker = BlacklistChecker(ref_searcher, app_searcher)
            assert isinstance(checker, BlacklistChecker)
        else:
            with pytest.raises(BlacklistCheckerError):
                BlacklistChecker(ref_searcher, app_searcher)

class TestBlacklistCheckerAddRule:
    """BlacklistCheckerのadd_ruleメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: 有効なルールの追加
    ├── C1: 分岐カバレッジ
    │   ├── 異常系: 無効な名前でのルール追加
    │   └── 異常系: 無効な条件関数でのルール追加
    └── C2: 条件組み合わせ
        ├── 正常系: 有効な名前と有効な条件関数
        ├── 異常系: 無効な名前と有効な条件関数
        ├── 異常系: 有効な名前と無効な条件関数
        └── 異常系: 無効な名前と無効な条件関数

    C1のディシジョンテーブル:
    | 条件           | ケース1 | ケース2 | ケース3 | ケース4 |
    |----------------|---------|---------|---------|---------|
    | 名前が有効     | Y       | N       | Y       | N       |
    | 条件関数が有効 | Y       | Y       | N       | N       |
    | 結果           | 正常    | エラー  | エラー  | エラー  |
    """

    @pytest.fixture(scope="class")
    def blacklist_checker(self) -> BlacklistChecker:
        reference_searcher = TableSearcher("reference_table.pkl")
        application_searcher = TableSearcher("application_table.pkl")
        return BlacklistChecker(reference_searcher, application_searcher)

    @pytest.fixture()
    def valid_condition(self) -> Callable[[pd.DataFrame, pd.DataFrame], pd.Series]:
        def condition(ref_df: pd.DataFrame, app_df: pd.DataFrame) -> pd.Series:
            return app_df["種類"] == "変更"
        return condition

    def setup_method(self) -> None:
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self) -> None:
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_add_rule_C0_valid_rule(self, setup_test_data, blacklist_checker, valid_condition) -> None:
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なルールの追加
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        rule_name = "test_rule"
        blacklist_checker.add_rule(rule_name, valid_condition)
        assert any(rule["name"] == rule_name for rule in blacklist_checker.rules)

    def test_add_rule_C1_invalid_name(self, setup_test_data, blacklist_checker, valid_condition) -> None:
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効な名前でのルール追加
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ValueError):
            blacklist_checker.add_rule("", valid_condition)


    def test_add_rule_C1_invalid_condition(self, setup_test_data, blacklist_checker) -> None:
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効な条件関数でのルール追加
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(TypeError):
            blacklist_checker.add_rule("test_rule", "invalid_condition")

    @pytest.mark.parametrize(
        ("rule_name", "condition", "expected_result"),
        [
            ("valid_rule", "valid_condition", True),
            ("", "valid_condition", False),
            ("valid_rule", "invalid_condition", False),
            ("", "invalid_condition", False),
        ],
        ids=["両方有効", "名前無効", "条件無効", "両方無効"],
    )
    def test_add_rule_C2_combinations(
        self, setup_test_data, blacklist_checker, valid_condition,
        rule_name: str, condition: str, expected_result: bool,
    ) -> None:
        test_doc = f"""テスト内容:
        - テストカテゴリ: C2
        - テスト区分: {'正常系' if expected_result else '異常系'}
        - テストシナリオ: {' / '.join(filter(None, [
            '両方有効' if expected_result else None,
            '名前無効' if rule_name == "" else None,
            '条件無効' if condition == "invalid_condition" else None
        ]))}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        condition_func = valid_condition if condition == "valid_condition" else "invalid_condition"

        if expected_result:
            blacklist_checker.add_rule(rule_name, condition_func)
            assert any(rule["name"] == rule_name for rule in blacklist_checker.rules)
        else:
            with pytest.raises((ValueError, TypeError)):
                blacklist_checker.add_rule(rule_name, condition_func)

class TestBlacklistCheckerCheckBlacklist:
    """BlacklistCheckerのcheck_blacklistメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: ルールが存在する場合の検査
    │   └── 正常系: ルールが存在しない場合の検査
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 複数ルールの適用
    │   ├── 異常系: 無効なルール条件関数
    └── C2: 条件組み合わせ
        ├── 正常系: 全てのルールが適用される場合
        ├── 正常系: 一部のルールのみが適用される場合
        ├── 正常系: どのルールも適用されない場合
        └── 異常系: 一部のルールでエラーが発生する場合

    C1のディシジョンテーブル:
    | 条件                     | ケース1 | ケース2 | ケース3 | ケース4 |
    |--------------------------|---------|---------|---------|---------|
    | 有効なルールが存在       | Y       | Y       | N       | Y       |
    | 無効なルールが含まれる   | N       | Y       | -       | N       |
    | データフレーム操作エラー | N       | N       | -       | Y       |
    | 結果                     | 正常    | エラー  | 空結果  | エラー  |
    """

    @pytest.fixture(scope="class")
    def blacklist_checker(self) -> BlacklistChecker:
        reference_searcher = TableSearcher("reference_table.pkl")
        application_searcher = TableSearcher("application_table.pkl")
        return BlacklistChecker(reference_searcher, application_searcher)

    @pytest.fixture
    def valid_rule(self) -> Callable[[pd.DataFrame, pd.DataFrame], pd.Series]:
        def rule(ref_df: pd.DataFrame, app_df: pd.DataFrame) -> pd.Series:
            return app_df["種類"] == "変更"
        return rule

    @pytest.fixture
    def invalid_rule(self) -> Callable[[pd.DataFrame, pd.DataFrame], Any]:
        def rule(ref_df: pd.DataFrame, app_df: pd.DataFrame) -> str:
            return "Invalid result"
        return rule

    def setup_method(self) -> None:
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self) -> None:
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_check_blacklist_C0_with_rules(self, setup_test_data, blacklist_checker, valid_rule) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: ルールが存在する場合の検査
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        blacklist_checker.add_rule("test_rule", valid_rule)
        result = blacklist_checker.check_blacklist()
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert "rule_name" in result.columns

    def test_check_blacklist_C0_without_rules(self, setup_test_data, blacklist_checker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: ルールが存在しない場合の検査
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        blacklist_checker.rules = []
        result = blacklist_checker.check_blacklist()
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_check_blacklist_C1_multiple_rules(self, setup_test_data, blacklist_checker, valid_rule) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 複数ルールの適用
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        blacklist_checker.add_rule("rule1", valid_rule)
        blacklist_checker.add_rule("rule2", lambda ref, app: app["部店コード"] == "1001")
        result = blacklist_checker.check_blacklist()
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert set(result["rule_name"]) == {"rule1", "rule2"}

    def test_check_blacklist_C1_invalid_rule(self, setup_test_data, blacklist_checker, invalid_rule) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 無効なルール条件関数
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        blacklist_checker.add_rule("invalid_rule", invalid_rule)
        with pytest.raises(RuleApplicationError):
            blacklist_checker.check_blacklist()

    @pytest.mark.parametrize(
        ("scenario", "rules", "expected_result"),
        [
            ("全て適用", [
                ("rule1", lambda ref, app: app["種類"] == "変更"),
                ("rule2", lambda ref, app: app["部店コード"] == "1001")
            ], True),
            ("適用なし", [
                ("rule1", lambda ref, app: app["種類"] == "不存在"),
                ("rule2", lambda ref, app: app["部店コード"] == "9999")
            ], False),
            ("ルールなし", [], False),
            ("一部エラー", [
                ("valid_rule", lambda ref, app: app["種類"] == "変更"),
                ("invalid_rule", "not_a_function")
            ], "error"),
        ]
    )
    def test_check_blacklist_C2_combinations(
        self,
        setup_test_data,
        blacklist_checker: BlacklistChecker,
        scenario: str,
        rules: list[tuple[str, Callable | str]],
        expected_result: bool | str,
    ) -> None:
        test_doc = f"""テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: {'正常系' if expected_result != "error" else '異常系'}
        - テストシナリオ: {get_scenario_description(scenario)}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        blacklist_checker.rules = []
        for name, rule in rules:
            if callable(rule):
                blacklist_checker.add_rule(name, rule)
            else:
                blacklist_checker.add_rule(name, lambda ref, app: True)  # ダミールール

        if expected_result == "error":
            with pytest.raises(RuleApplicationError):
                blacklist_checker.check_blacklist()
        else:
            result = blacklist_checker.check_blacklist()
            assert isinstance(result, pd.DataFrame)
            assert (not result.empty) == expected_result


class TestBlacklistCheckerRefreshData:
    """BlacklistCheckerのrefresh_dataメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   └── 正常系: データの更新
    └── C1: 分岐カバレッジ
        ├── 正常系: 両方のsearcherのデータが更新される
        ├── 異常系: reference_searcherの更新でエラー
        └── 異常系: application_searcherの更新でエラー

    C1のディシジョンテーブル:
    | 条件                               | ケース1 | ケース2 | ケース3 |
    |------------------------------------|---------|---------|---------|
    | reference_searcherの更新が成功     | Y       | N       | Y       |
    | application_searcherの更新が成功   | Y       | Y       | N       |
    | 結果                               | 正常    | エラー  | エラー  |
    """
    @pytest.fixture
    def blacklist_checker(self) -> BlacklistChecker:
        reference_searcher = TableSearcher("reference_table.pkl")
        application_searcher = TableSearcher("application_table.pkl")
        return BlacklistChecker(reference_searcher, application_searcher)

    def setup_method(self) -> None:
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self) -> None:
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def update_test_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        test_dir = Path("src/table")
        time.sleep(1)  # ファイルの更新時刻を確実に変更するために1秒待機

        new_reference_df = pd.DataFrame({
            "部店コード": ["1001", "1002", "1003", "1004"],
            "部店名称": ["営業部", "人事部", "総務部", "経理部"],
            "重要度": [5, 3, 4, 2]
        })
        
        new_application_df = pd.DataFrame({
            "申請ID": ["A001", "A002", "A003", "A004"],
            "部店コード": ["1001", "1002", "1004", "1003"],
            "種類": ["変更", "新規", "削除", "変更"]
        })

        with (test_dir / "reference_table.pkl").open("wb") as f:
            pickle.dump(new_reference_df, f)
        
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(new_application_df, f)

        return new_reference_df, new_application_df

    def test_refresh_data_C0_basic_functionality(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
    
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: データの更新
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        # 初期データを取得
        initial_ref_data = blacklist_checker.reference_searcher.df.copy()
        initial_app_data = blacklist_checker.application_searcher.df.copy()
    
        # テストデータを更新
        test_dir = Path("src/table")
        time.sleep(1)  # ファイルの更新時刻を確実に変更するために1秒待機
    
        new_reference_df = pd.DataFrame({
            "部店コード": ["1001", "1002", "1003", "1004"],
            "部店名称": ["営業部", "人事部", "総務部", "経理部"],
            "重要度": [5, 3, 4, 2]
        })
        
        new_application_df = pd.DataFrame({
            "申請ID": ["A001", "A002", "A003", "A004"],
            "部店コード": ["1001", "1002", "1004", "1003"],
            "種類": ["変更", "新規", "削除", "変更"]
        })
    
        with (test_dir / "reference_table.pkl").open("wb") as f:
            pickle.dump(new_reference_df, f)
        
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(new_application_df, f)
    
        # refresh_data呼び出し
        blacklist_checker.refresh_data()
    
        # 更新後のデータを取得
        updated_ref_data = blacklist_checker.reference_searcher.df
        updated_app_data = blacklist_checker.application_searcher.df
    
        # データが更新されたことを確認
        assert not initial_ref_data.equals(updated_ref_data), "Reference data was not updated"
        assert not initial_app_data.equals(updated_app_data), "Application data was not updated"
    
        # is_updatedフラグを確認
        assert blacklist_checker.reference_searcher.is_updated, "Reference searcher was not marked as updated"
        assert blacklist_checker.application_searcher.is_updated, "Application searcher was not marked as updated"
    
        log_msg(f"Reference searcher updated: {blacklist_checker.reference_searcher.is_updated}", LogLevel.DEBUG)
        log_msg(f"Application searcher updated: {blacklist_checker.application_searcher.is_updated}", LogLevel.DEBUG)
    


    @pytest.mark.parametrize(
        ("reference_success", "application_success", "expected_result"),
        [
            (True, True, "success"),
            (False, True, "error"),
            (True, False, "error"),
        ],
        ids=["両方成功", "reference失敗", "application失敗"]
    )
    def test_refresh_data_C1_combinations(
        self,
        setup_test_data,
        blacklist_checker: BlacklistChecker,
        monkeypatch: Any,
        reference_success: bool,
        application_success: bool,
        expected_result: str
    ) -> None:
        test_doc = f"""テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: {'正常系' if expected_result == 'success' else '異常系'}
        - テストシナリオ: reference_searcher更新{'成功' if reference_success else '失敗'}、
                         application_searcher更新{'成功' if application_success else '失敗'}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

    def test_refresh_data_C1_both_searchers_update(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 両方のsearcherのデータが更新される
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        self.update_test_data()
        blacklist_checker.refresh_data()

        assert blacklist_checker.reference_searcher.is_updated, "Reference searcher was not updated"
        assert blacklist_checker.application_searcher.is_updated, "Application searcher was not updated"

    def test_refresh_data_C1_reference_searcher_error(self, setup_test_data, blacklist_checker: BlacklistChecker, monkeypatch: Any) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: reference_searcherの更新でエラー
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        mock_refresh_data = Mock(side_effect=Exception("Mock refresh data error"))
        monkeypatch.setattr(blacklist_checker.reference_searcher, "refresh_data", mock_refresh_data)
        
        with pytest.raises(BlacklistCheckerError):
            blacklist_checker.refresh_data()
            

    def test_refresh_data_C1_application_searcher_error(self, setup_test_data, blacklist_checker: BlacklistChecker, monkeypatch: Any) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: application_searcherの更新でエラー
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def mock_refresh_data_error(self):
            raise Exception("Mock refresh data error")

        monkeypatch.setattr(blacklist_checker.application_searcher, "refresh_data", mock_refresh_data_error)
        
        with pytest.raises(BlacklistCheckerError):
            blacklist_checker.refresh_data()

#    @pytest.mark.parametrize(
#        ("reference_success", "application_success", "expected_result"),
#        [
#            (True, True, "success"),
#            (False, True, "error"),
#            (True, False, "error"),
#        ],
#        ids=["両方成功", "reference失敗", "application失敗"]
#    )
#    def test_refresh_data_C1_combinations(
#        self,
#        setup_test_data,
#        blacklist_checker: BlacklistChecker,
#        monkeypatch: Any,
#        reference_success: bool,
#        application_success: bool,
#        expected_result: str
#    ) -> None:
#        test_doc = f"""テスト内容:
#        
#        - テストカテゴリ: C1
#        - テスト区分: {'正常系' if expected_result == 'success' else '異常系'}
#        - テストシナリオ: reference_searcher更新{'成功' if reference_success else '失敗'}、
#                         application_searcher更新{'成功' if application_success else '失敗'}
#        """
#        log_msg(f"\n{test_doc}", LogLevel.INFO)
#
#        def mock_refresh_data(self):
#            if self == blacklist_checker.reference_searcher and not reference_success:
#                raise Exception("Mock reference refresh data error")
#            if self == blacklist_checker.application_searcher and not application_success:
#                raise Exception("Mock application refresh data error")
#            # 成功した場合は実際のrefresh_dataを呼び出す
#            # type(self).refresh_data(self)
#
#        monkeypatch.setattr(TableSearcher, "refresh_data", mock_refresh_data)
#
#        self.update_test_data()  # テストデータを更新
#
#        if expected_result == "success":
#            blacklist_checker.refresh_data()
#            assert blacklist_checker.reference_searcher.is_updated
#            assert blacklist_checker.application_searcher.is_updated
#        else:
#            with pytest.raises(BlacklistCheckerError):
#                blacklist_checker.refresh_data()

    @pytest.mark.parametrize(
        ("reference_success", "application_success", "expected_result"),
        [
            (True, True, "success"),
            (False, True, "error"),
            (True, False, "error"),
        ],
        ids=["両方成功", "reference失敗", "application失敗"]
    )
    def test_refresh_data_C1_combinations(
        self,
        setup_test_data,
        blacklist_checker: BlacklistChecker,
        monkeypatch: Any,
        reference_success: bool,
        application_success: bool,
        expected_result: str
    ) -> None:
        test_doc = f"""テスト内容:
    
        - テストカテゴリ: C1
        - テスト区分: {'正常系' if expected_result == 'success' else '異常系'}
        - テストシナリオ: reference_searcher更新{'成功' if reference_success else '失敗'}、
                         application_searcher更新{'成功' if application_success else '失敗'}
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        def mock_refresh_data(self):
            if self == blacklist_checker.reference_searcher and not reference_success:
                raise Exception("Mock reference refresh data error")
            if self == blacklist_checker.application_searcher and not application_success:
                raise Exception("Mock application refresh data error")
            # 成功した場合は is_updated フラグを設定
            self.is_updated = True
    
        monkeypatch.setattr(TableSearcher, "refresh_data", mock_refresh_data)
    
        self.update_test_data()  # テストデータを更新
    
        if expected_result == "success":
            blacklist_checker.refresh_data()
            assert blacklist_checker.reference_searcher.is_updated
            assert blacklist_checker.application_searcher.is_updated
        else:
            with pytest.raises(BlacklistCheckerError):
                blacklist_checker.refresh_data()
