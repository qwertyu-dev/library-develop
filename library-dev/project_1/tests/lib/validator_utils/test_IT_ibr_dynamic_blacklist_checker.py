import pytest
import pandas as pd
import pickle
from pathlib import Path
from typing import Generator, Any, Callable
import time

from src.lib.validator_utils.ibr_dynamic_blacklist_checker import BlacklistChecker, BlacklistCheckerError, RuleApplicationError
from src.lib.common_utils.ibr_pickled_table_searcher import TableSearcher
from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

package_path = Path(__file__)
config = Config.load(package_path)

log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

@pytest.fixture(scope="module")
def setup_test_data() -> Generator[None, None, None]:
    test_dir = Path("src/table")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    reference_df = pd.DataFrame({
        "部店コード": ["1001", "1002", "1003", "1004", "1005"],
        "部店名称": ["営業部", "人事部", "総務部", "経理部", "企画部"],
        "重要度": [5, 3, 4, 2, 5]
    })
    
    application_df = pd.DataFrame({
        "申請ID": ["A001", "A002", "A003", "A004", "A005"],
        "部店コード": ["1001", "1002", "1004", "1003", "1005"],
        "種類": ["変更", "新規", "削除", "変更", "新規"]
    })
    
    with (test_dir / "reference_table.pkl").open("wb") as f:
        pickle.dump(reference_df, f)
    
    with (test_dir / "application_table.pkl").open("wb") as f:
        pickle.dump(application_df, f)
    
    yield
    
    (test_dir / "reference_table.pkl").unlink()
    (test_dir / "application_table.pkl").unlink()

class TestBlacklistCheckerIntegration:
    """BlacklistCheckerの統合テスト"""

    @pytest.fixture(scope="class")
    def blacklist_checker(self) -> BlacklistChecker:
        reference_searcher = TableSearcher("reference_table.pkl")
        application_searcher = TableSearcher("application_table.pkl")
        return BlacklistChecker(reference_searcher, application_searcher)

    def setup_method(self) -> None:
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self) -> None:
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_integration_C0_multiple_rules(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 複数ルールの追加と検査
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # ルール1: 重要度が4以上の部店の変更申請
        rule1 = lambda ref, app: (app["種類"] == "変更") & (app["部店コード"].isin(ref[ref["重要度"] >= 4]["部店コード"]))
        blacklist_checker.add_rule("重要部店変更", rule1)

        # ルール2: 新規申請
        rule2 = lambda ref, app: app["種類"] == "新規"
        blacklist_checker.add_rule("新規申請", rule2)

        result = blacklist_checker.check_blacklist()
        
        log_msg(f"検出されたブラックリスト項目:\n{result}", LogLevel.INFO)
        
        assert len(result) == 4, f"期待値: 4, 実際の結果: {len(result)}"
        assert set(result["rule_name"]) == {"重要部店変更", "新規申請"}, f"検出されたルール: {set(result['rule_name'])}"
        assert sum(result["rule_name"] == "重要部店変更") == 2, f"重要部店変更の検出数: {sum(result['rule_name'] == '重要部店変更')}"
        assert sum(result["rule_name"] == "新規申請") == 2, f"新規申請の検出数: {sum(result['rule_name'] == '新規申請')}"

        expected_ids = {"A001", "A002", "A004", "A005"}
        actual_ids = set(result["申請ID"])
        assert actual_ids == expected_ids, f"期待される申請ID: {expected_ids}, 実際の申請ID: {actual_ids}"

    def test_integration_C1_data_update(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: データ更新後の検査
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 初期状態でのチェック
        initial_result = blacklist_checker.check_blacklist()
        log_msg(f"初期状態の検出結果:\n{initial_result}", LogLevel.INFO)

        # データの更新
        test_dir = Path("src/table")
        new_application_df = pd.DataFrame({
            "申請ID": ["A006", "A007"],
            "部店コード": ["1001", "1005"],
            "種類": ["変更", "変更"]
        })
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(new_application_df, f)

        # データの更新とブラックリストチェック
        blacklist_checker.refresh_data()
        updated_result = blacklist_checker.check_blacklist()
        log_msg(f"更新後の検出結果:\n{updated_result}", LogLevel.INFO)

        assert len(updated_result) == 2, f"期待値: 2, 実際の結果: {len(updated_result)}"
        assert set(updated_result["rule_name"]) == {"重要部店変更"}, f"検出されたルール: {set(updated_result['rule_name'])}"
        assert len(updated_result) != len(initial_result), "更新前後で結果が変化していません"

        expected_ids = {"A006", "A007"}
        actual_ids = set(updated_result["申請ID"])
        assert actual_ids == expected_ids, f"期待される申請ID: {expected_ids}, 実際の申請ID: {actual_ids}"

    def test_integration_C1_error_handling(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
    
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: エラー発生時の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        def error_rule(ref: pd.DataFrame, app: pd.DataFrame) -> pd.Series:
            raise ValueError("Intentional error for testing")
    
        blacklist_checker.add_rule("エラールール", error_rule)
    
        with pytest.raises(ValueError) as exc_info:
            blacklist_checker.check_blacklist()
        
        assert str(exc_info.value) == "Intentional error for testing", f"期待されるエラーメッセージが含まれていません。実際のエラー: {str(exc_info.value)}"
    
        log_msg(f"エラーメッセージ: {str(exc_info.value)}", LogLevel.INFO)

    @pytest.mark.parametrize(
        ("rules", "expected_count", "expected_rule_names"),
        [
            ([("重要部店", lambda ref, app: app["部店コード"].isin(ref[ref["重要度"] >= 4]["部店コード"]))], 2, {"重要部店"}),
            ([("変更申請", lambda ref, app: app["種類"] == "変更")], 2, {"変更申請"}),
            ([("重要部店", lambda ref, app: app["部店コード"].isin(ref[ref["重要度"] >= 4]["部店コード"])),
              ("変更申請", lambda ref, app: app["種類"] == "変更")], 4, {"重要部店", "変更申請"}),
        ],
        ids=["重要部店のみ", "変更申請のみ", "重要部店と変更申請"]
    )
    def test_integration_C2_rule_combinations(
        self,
        setup_test_data,
        blacklist_checker: BlacklistChecker,
        rules: list[tuple[str, Callable]],
        expected_count: int,
        expected_rule_names: set[str]
    ) -> None:
        test_doc = f"""テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 様々なルールの組み合わせでの検査 ({", ".join(rule[0] for rule in rules)})
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        blacklist_checker.rules = []  # ルールをリセット
        for name, rule in rules:
            blacklist_checker.add_rule(name, rule)

        result = blacklist_checker.check_blacklist()
        log_msg(f"検出結果:\n{result}", LogLevel.INFO)

        log_msg(f"参照テーブル:\n{blacklist_checker.reference_searcher.df}", LogLevel.INFO)
        log_msg(f"申請テーブル:\n{blacklist_checker.application_searcher.df}", LogLevel.INFO)
        
        result = blacklist_checker.check_blacklist()
        log_msg(f"検出結果:\n{result}", LogLevel.INFO)
    
        # 結果の詳細な分析
        for index, row in result.iterrows():
            log_msg(f"検出項目 {index + 1}:", LogLevel.INFO)
            log_msg(f"  申請ID: {row['申請ID']}", LogLevel.INFO)
            log_msg(f"  部店コード: {row['部店コード']}", LogLevel.INFO)
            log_msg(f"  種類: {row['種類']}", LogLevel.INFO)
            log_msg(f"  適用ルール: {row['rule_name']}", LogLevel.INFO)
            
            # 参照テーブルの対応する行を表示
            ref_row = blacklist_checker.reference_searcher.df[blacklist_checker.reference_searcher.df['部店コード'] == row['部店コード']]
            log_msg(f"  対応する参照データ:\n{ref_row}", LogLevel.INFO)


        assert len(result) == expected_count, f"期待値: {expected_count}, 実際の結果: {len(result)}"
        assert set(result["rule_name"]) == expected_rule_names, f"期待されるルール: {expected_rule_names}, 検出されたルール: {set(result['rule_name'])}"


    def test_integration_C2_data_comparison(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
    
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: データ更新前後での結果の比較
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        blacklist_checker.rules = []  # ルールをリセット
        blacklist_checker.add_rule("全申請", lambda ref, app: pd.Series([True] * len(app)))
        
        # 初期状態の確認
        initial_df = blacklist_checker.application_searcher.df
        log_msg(f"初期状態の申請テーブル:\n{initial_df}", LogLevel.INFO)
        
        initial_result = blacklist_checker.check_blacklist()
        log_msg(f"初期状態の検出結果:\n{initial_result}", LogLevel.INFO)
    
        assert len(initial_result) == len(initial_df), f"初期状態の期待値: {len(initial_df)}, 実際の結果: {len(initial_result)}"
    
        # データの更新
        test_dir = Path("src/table")
        new_application_df = pd.DataFrame({
            "申請ID": ["A006", "A007", "A008"],
            "部店コード": ["1001", "1005", "1006"],
            "種類": ["変更", "変更", "新規"]
        })
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(new_application_df, f)
    
        blacklist_checker.refresh_data()
        updated_result = blacklist_checker.check_blacklist()
        log_msg(f"更新後の検出結果:\n{updated_result}", LogLevel.INFO)
    
        assert len(updated_result) == 3, f"更新後の期待値: 3, 実際の結果: {len(updated_result)}"
        assert set(updated_result["申請ID"]) == {"A006", "A007", "A008"}, f"期待される申請ID: {{'A006', 'A007', 'A008'}}, 実際の申請ID: {set(updated_result['申請ID'])}"
    
        # 更新前後でのデータの変化を確認
        assert len(updated_result) != len(initial_result), "更新前後でデータ数が変化していません"
        assert set(updated_result["申請ID"]) != set(initial_result["申請ID"]), "更新前後で申請IDが変化していません"


    def test_integration_C2_performance(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 大規模データセットでのパフォーマンス検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 大規模データの生成
        test_dir = Path("src/table")
        large_reference_df = pd.DataFrame({
            "部店コード": [f"{i:04d}" for i in range(10000)],
            "部店名称": [f"部店{i}" for i in range(10000)],
            "重要度": [i % 5 + 1 for i in range(10000)]
        })
        large_application_df = pd.DataFrame({
            "申請ID": [f"A{i:05d}" for i in range(20000)],
            "部店コード": [f"{i%10000:04d}" for i in range(20000)],
            "種類": ["変更" if i % 3 == 0 else "新規" if i % 3 == 1 else "削除" for i in range(20000)]
        })

        with (test_dir / "reference_table.pkl").open("wb") as f:
            pickle.dump(large_reference_df, f)
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(large_application_df, f)

        blacklist_checker.refresh_data()
        blacklist_checker.rules = []  # ルールをリセット
        blacklist_checker.add_rule("重要部店変更", lambda ref, app: (app["種類"] == "変更") & (app["部店コード"].isin(ref[ref["重要度"] >= 4]["部店コード"])))

        start_time = time.time()
        result = blacklist_checker.check_blacklist()
        end_time = time.time()
        processing_time = end_time - start_time

        log_msg(f"処理時間: {processing_time:.2f}秒", LogLevel.INFO)
        log_msg(f"結果件数: {len(result)}", LogLevel.INFO)

        assert len(result) > 0, "検出結果が0件です"
        assert processing_time < 5, f"処理時間が5秒を超えています: {processing_time:.2f}秒"
        
        # 結果の妥当性チェック
        assert all(result["種類"] == "変更"), "変更以外の申請が含まれています"
        assert all(result["部店コード"].astype(int) % 5 >= 3), "重要度が4未満の部店が含まれています"

    def test_integration_edge_cases(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: エッジケースの検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # ケース1: 空のデータフレーム
        test_dir = Path("src/table")
        empty_df = pd.DataFrame(columns=["申請ID", "部店コード", "種類"])
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(empty_df, f)
        
        blacklist_checker.refresh_data()
        result = blacklist_checker.check_blacklist()
        assert len(result) == 0, f"空のデータフレームに対して結果が返されました: {result}"

        # ケース2: 全ての申請が条件に合致
        all_match_df = pd.DataFrame({
            "申請ID": ["A001", "A002", "A003"],
            "部店コード": ["1001", "1002", "1003"],
            "種類": ["変更", "変更", "変更"]
        })
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(all_match_df, f)
        
        blacklist_checker.refresh_data()
        blacklist_checker.rules = []
        blacklist_checker.add_rule("全て一致", lambda ref, app: pd.Series([True] * len(app)))
        result = blacklist_checker.check_blacklist()
        assert len(result) == 3, f"全ての申請が一致するはずですが、結果は {len(result)} 件でした"

        # ケース3: 条件に合致する申請がない
        no_match_df = pd.DataFrame({
            "申請ID": ["A001", "A002", "A003"],
            "部店コード": ["1001", "1002", "1003"],
            "種類": ["新規", "新規", "新規"]
        })
        with (test_dir / "application_table.pkl").open("wb") as f:
            pickle.dump(no_match_df, f)
        
        blacklist_checker.refresh_data()
        blacklist_checker.rules = []
        blacklist_checker.add_rule("一致なし", lambda ref, app: app["種類"] == "変更")
        result = blacklist_checker.check_blacklist()
        assert len(result) == 0, f"一致する申請がないはずですが、結果は {len(result)} 件でした"

    def test_integration_rule_priority(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
    
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: ルールの優先順位の検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
    
        blacklist_checker.rules = []
        blacklist_checker.add_rule("ルール1", lambda ref, app: app["種類"] == "変更")
        blacklist_checker.add_rule("ルール2", lambda ref, app: app["種類"] == "新規")
        blacklist_checker.add_rule("ルール3", lambda ref, app: pd.Series([True] * len(app)))
    
        result = blacklist_checker.check_blacklist()
        log_msg(f"検出結果:\n{result}", LogLevel.INFO)
    
        # 申請の総数を確認
        total_applications = len(blacklist_checker.application_searcher.df)
        assert len(result) == total_applications * 2, f"各申請が2回ずつ検出されるはずですが、結果は {len(result)} 件でした"
    
        # ルールの適用順序を確認
        assert list(result['rule_name']) == ['ルール2'] * total_applications + ['ルール3'] * total_applications, "ルールの適用順序が期待と異なります"
    
        # 各ルールの適用回数を確認
        rule_counts = result['rule_name'].value_counts()
        assert rule_counts['ルール2'] == total_applications, f"ルール2の適用回数が期待と異なります: {rule_counts['ルール2']}"
        assert rule_counts['ルール3'] == total_applications, f"ルール3の適用回数が期待と異なります: {rule_counts['ルール3']}"
        assert 'ルール1' not in rule_counts, "ルール1が適用されているべきではありません"
    
        # 重複を除いた unique な申請 ID の数を確認
        unique_applications = result['申請ID'].nunique()
        assert unique_applications == total_applications, f"ユニークな申請数が期待と異なります: {unique_applications}"

    def test_integration_data_integrity(self, setup_test_data, blacklist_checker: BlacklistChecker) -> None:
        test_doc = """テスト内容:
        
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: データの整合性の検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # リファレンステーブルとアプリケーションテーブルの整合性チェック
        ref_df = blacklist_checker.reference_searcher.df
        app_df = blacklist_checker.application_searcher.df

        assert set(ref_df["部店コード"]).issuperset(set(app_df["部店コード"])), \
            "アプリケーションテーブルに存在する部店コードがリファレンステーブルに存在しません"

        # 結果の整合性チェック
        blacklist_checker.rules = []
        blacklist_checker.add_rule("全て検出", lambda ref, app: pd.Series([True] * len(app)))
        result = blacklist_checker.check_blacklist()

        assert set(result["申請ID"]) == set(app_df["申請ID"]), \
            "結果の申請IDがアプリケーションテーブルと一致しません"
        assert set(result["部店コード"]) == set(app_df["部店コード"]), \
            "結果の部店コードがアプリケーションテーブルと一致しません"
        assert set(result["種類"]) == set(app_df["種類"]), \
            "結果の種類がアプリケーションテーブルと一致しません"

        log_msg("データの整合性チェックが完了しました", LogLevel.INFO)
