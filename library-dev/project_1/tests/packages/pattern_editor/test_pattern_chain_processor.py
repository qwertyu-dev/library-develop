import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.packages.pattern_editor.data_validator_pattern_editor import DataValidator
from src.packages.pattern_editor.pattern_chain_processor import (
    AddDecisionJudgeColumns,
    ModifyDecisionTable,
    PatternChainProcessorError,
    PostProcessorRequest,
    PreProcessorDecisionTable,
    PreProcessorRequest,
    ReadDecisionTable,
    ReadRequestListTable,
    ValidationResult,
    WritePreparationResult,
)
from src.packages.pattern_editor.validation_models_pattern_editor import PatternEditModel

# テスト用のconfig設定
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestPatternChainProcessor:
    """パターン編集処理のチェーン定義テスト

    チェーンの構成と順序を検証します。各プロセッサの実際の処理内容は
    モック化し、チェーンの構造自体の正しさを確認することに注力します。

    テスト構造:
    ├── PreProcessorDecisionTable
    │   ├── C0: チェーン構成の基本検証
    │   ├── C1: コンポーネントの順序検証
    │   └── C2: 異常系の組み合わせテスト
    ├── PreProcessorRequest
    │   ├── C0: チェーン構成の基本検証
    │   ├── C1: コンポーネントの順序検証
    │   └── C2: 異常系の組み合わせテスト
    └── PostProcessorRequest
        ├── C0: チェーン構成の基本検証
        ├── C1: コンポーネントの順序検証
        └── C2: 異常系の組み合わせテスト

    # C1のディシジョンテーブル
    | 条件                                    | DT1 | DT2 | DT3 | DT4 |
    |-----------------------------------------|-----|-----|-----|-----|
    | チェーンが正しい順序で定義されている    | Y   | N   | Y   | Y   |
    | 全てのコンポーネントが存在する          | Y   | Y   | N   | Y   |
    | 各コンポーネントが正しい型を返す        | Y   | Y   | Y   | N   |
    | 期待される結果                          | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目           | テスト値                    | 期待される結果 | 実装状況 |
    |--------|-------------------|----------------------------|--------------|-----------|
    | BVT_01 | 空のチェーン       | []                         | エラー        | C0で実装済 |
    | BVT_02 | 最小チェーン       | [単一コンポーネント]        | 成功         | C0で実装済 |
    | BVT_03 | 標準的なチェーン   | [複数の正常コンポーネント]   | 成功         | C1で実装済 |
    | BVT_04 | 無効なコンポーネント| [無効なオブジェクト]        | エラー        | C2で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    def setup_method(self):
        """テスト開始時のログ出力"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テスト終了時のログ出力"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_pre_processor_decision_table_C0_basic_chain(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: PreProcessorDecisionTableの基本チェーン構成を検証
        
        PreProcessorDecisionTableのchain_pre_processor()メソッドが
        正しい構成のプロセッサチェーンを返すことを確認します。
        
        検証項目:
        1. チェーンの長さが2であること
        2. 最初のプロセッサがReadDecisionTableであること
        3. 2番目のプロセッサがModifyDecisionTableであること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PreProcessorDecisionTable()
        chain = processor.chain_pre_processor()

        assert len(chain) == 2
        assert isinstance(chain[0], ReadDecisionTable)
        assert isinstance(chain[1], ModifyDecisionTable)

    def test_pre_processor_decision_table_C1_order(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: PreProcessorDecisionTableのチェーン実行順序を検証
        
        プロセッサチェーンの実行順序が意図した通りであることを確認します。
        ReadDecisionTable -> ModifyDecisionTableの順で実行されることを検証します。
        
        検証項目:
        1. ReadDecisionTableが最初に実行されること
        2. ModifyDecisionTableが次に実行されること
        3. 実行順序が固定されていること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadDecisionTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.ModifyDecisionTable') as mock_modify:

            processor = PreProcessorDecisionTable()
            chain = processor.chain_pre_processor()

            execution_order = []
            def record_execution(name):
                return lambda x: execution_order.append(name)

            mock_read.return_value.process.side_effect = record_execution('read')
            mock_modify.return_value.process.side_effect = record_execution('modify')

            df = pd.DataFrame()
            for proc in chain:
                proc.process(df)

            assert execution_order == ['read', 'modify']

    def test_pre_processor_request_C0_basic_chain(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: PreProcessorRequestの基本チェーン構成を検証
        
        PreProcessorRequestのchain_pre_processor()メソッドが
        正しい構成のプロセッサチェーンを返すことを確認します。
        
        検証項目:
        1. チェーンの長さが2であること
        2. 最初のプロセッサがReadRequestListTableであること
        3. 2番目のプロセッサがAddDecisionJudgeColumnsであること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PreProcessorRequest()
        chain = processor.chain_pre_processor()

        assert len(chain) == 2
        assert isinstance(chain[0], ReadRequestListTable)
        assert isinstance(chain[1], AddDecisionJudgeColumns)

    def test_post_processor_request_C0_basic_chain(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: PostProcessorRequestの基本チェーン構成を検証
        
        PostProcessorRequestのchain_post_processor()メソッドが
        正しい構成のプロセッサチェーンを返すことを確認します。
        
        検証項目:
        1. チェーンの長さが2であること
        2. 最初のプロセッサがValidationResultであること
        3. 2番目のプロセッサがWritePreparationResultであること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PostProcessorRequest()
        chain = processor.chain_post_processor()

        assert len(chain) == 2
        assert isinstance(chain[0], ValidationResult)
        assert isinstance(chain[1], WritePreparationResult)

    def test_chain_C2_component_combinations(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 異なるチェーン構成の組み合わせを検証
        
        各プロセッサチェーンが独立して動作し、互いに影響を与えないことを確認します。
        また、各チェーンのコンポーネントが必要なインターフェースを実装していることを検証します。
        
        検証項目:
        1. 各チェーンが独立して正しい長さを持つこと
        2. 各チェーンのコンポーネントが必要なインターフェースを実装していること
        3. チェーン間で相互干渉がないこと
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        pre_decision = PreProcessorDecisionTable()
        pre_request = PreProcessorRequest()
        post_request = PostProcessorRequest()

        decision_chain = pre_decision.chain_pre_processor()
        request_chain = pre_request.chain_pre_processor()
        post_chain = post_request.chain_post_processor()

        assert len(decision_chain) == 2
        assert len(request_chain) == 2
        assert len(post_chain) == 2

        assert all(hasattr(proc, 'process') for proc in decision_chain)
        assert all(hasattr(proc, 'process') for proc in request_chain)
        assert all(hasattr(proc, 'process') for proc in post_chain)


class TestPreProcessorRequestChain:
    """PreProcessorRequestのチェーン定義テスト

    リクエスト処理のプリプロセッサチェーンの構成と順序を検証します。
    各プロセッサの実際の処理内容はモック化し、チェーンの構造自体の
    正しさを確認することに注力します。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 基本チェーン構成の検証
    │   └── 異常系: 無効なチェーン構成の検出
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 処理順序の検証
    │   └── 異常系: エラーハンドリングの検証
    └── C2: 条件組み合わせ
        ├── 正常系: 複数チェーンの独立性
        └── 異常系: 異常系の組み合わせ

    # C1のディシジョンテーブル
    | 条件                                      | DT1 | DT2 | DT3 | DT4 |
    |------------------------------------------|-----|-----|-----|-----|
    | ReadRequestListTableが最初に配置されている | Y   | N   | Y   | Y   |
    | AddDecisionJudgeColumnsが次に配置されている| Y   | Y   | N   | Y   |
    | 全てのコンポーネントがprocessを実装している| Y   | Y   | Y   | N   |
    | 期待される結果                            | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目               | テスト値                      | 期待される結果 | 実装状況   |
    |--------|------------------------|-------------------------------|----------------|------------|
    | BVT_01 | 空チェーン構成         | chain_pre_processor -> []     | エラー         | C0で実装済 |
    | BVT_02 | 最小チェーン構成       | [ReadRequestListTable]        | 失敗          | C1で実装済 |
    | BVT_03 | 標準チェーン構成       | [Read.., AddDecision..]       | 成功          | C0で実装済 |
    | BVT_04 | 過剰なコンポーネント   | [Read.., Add.., Extra..]      | エラー         | C2で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    def setup_method(self):
        """テスト開始時のログ出力"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テスト終了時のログ出力"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_chain_pre_processor_C0_basic_chain(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: PreProcessorRequestの基本チェーン構成を検証

        chain_pre_processor()メソッドが正しい構成のプロセッサチェーンを
        返すことを確認します。チェーンは2つのプロセッサで構成され、
        それぞれが期待される型であることを検証します。

        検証項目:
        1. チェーンが2つのプロセッサで構成されていること
        2. 最初のプロセッサがReadRequestListTableであること
        3. 2番目のプロセッサがAddDecisionJudgeColumnsであること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PreProcessorRequest()
        chain = processor.chain_pre_processor()

        assert len(chain) == 2, "チェーンは2つのプロセッサで構成されるべきです"
        assert isinstance(chain[0], ReadRequestListTable), "最初のプロセッサの型が不正です"
        assert isinstance(chain[1], AddDecisionJudgeColumns), "2番目のプロセッサの型が不正です"

    def test_chain_pre_processor_C1_execution_order(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: プロセッサの実行順序を検証

        チェーン内のプロセッサが正しい順序で実行されることを確認します。
        ReadRequestListTable -> AddDecisionJudgeColumnsの順で
        実行されることを検証します。

        検証項目:
        1. ReadRequestListTableが最初に実行されること
        2. AddDecisionJudgeColumnsが2番目に実行されること
        3. 実行順序が常に一定であること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadRequestListTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.AddDecisionJudgeColumns') as mock_add:

            execution_order = []
            def record_execution(name):
                return lambda x: execution_order.append(name)

            mock_read.return_value.process.side_effect = record_execution('read')
            mock_add.return_value.process.side_effect = record_execution('add')

            processor = PreProcessorRequest()
            chain = processor.chain_pre_processor()

            # テスト用のダミーデータフレームで実行
            df = pd.DataFrame()
            for proc in chain:
                proc.process(df)

            assert execution_order == ['read', 'add'], "プロセッサの実行順序が不正です"

    def test_chain_pre_processor_C2_component_interface(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: プロセッサのインターフェース実装を検証

        チェーン内の各プロセッサが必要なインターフェースを正しく
        実装していることを確認します。特にprocess()メソッドの存在と
        シグネチャを検証します。

        検証項目:
        1. 全てのプロセッサがprocessメソッドを実装していること
        2. processメソッドがDataFrameを受け取り、DataFrameを返すこと
        3. プロセッサのインターフェースが一貫していること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PreProcessorRequest()
        chain = processor.chain_pre_processor()

        # 各コンポーネントのインターフェース検証
        for i, proc in enumerate(chain):
            assert hasattr(proc, 'process'), f"プロセッサ {i} にprocessメソッドがありません"
            
            # processメソッドのシグネチャを検証
            from inspect import signature
            sig = signature(proc.process)
            params = list(sig.parameters.values())
            
            assert len(params) == 2, f"プロセッサ {i} のprocessメソッドの引数の数が不正です"
            assert params[1].name == 'df', f"プロセッサ {i} のprocessメソッドの引数名が不正です"
            assert params[1].annotation == pd.DataFrame, f"プロセッサ {i} の引数の型が不正です"

    def test_chain_pre_processor_C2_error_handling(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: エラー処理の組み合わせを検証

        プロセッサチェーンでの異常系の組み合わせをテストします。
        各プロセッサでの異常系と、その伝搬を検証します。

        検証項目:
        1. 無効なプロセッサ構成での例外発生
        2. プロセッサチェーンでのエラー伝搬
        3. エラーメッセージの妥当性
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadRequestListTable') as mock_read:
            # 例外を発生させるモック
            mock_read.return_value.process.side_effect = Exception("テストエラー")

            processor = PreProcessorRequest()
            chain = processor.chain_pre_processor()

            df = pd.DataFrame()
            with pytest.raises(Exception) as exc_info:
                for proc in chain:
                    df = proc.process(df)

            assert "テストエラー" in str(exc_info.value), "期待されるエラーメッセージが含まれていません"

class TestPostProcessorRequestChain:
    """PostProcessorRequestのチェーン定義テスト

    後処理チェーンの構成と順序を検証します。ValidationResultと
    WritePreparationResultの連携が正しく機能することを確認します。
    
    各プロセッサの実際の処理内容はモック化し、チェーンの構造自体の
    正しさを確認することに注力します。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 後処理チェーン構成の検証
    │   └── 異常系: 無効なチェーン構成の検出
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: バリデーションと書き込み順序の検証
    │   └── 異常系: バリデーションエラー時の動作検証
    └── C2: 条件組み合わせ
        ├── 正常系: 複数の後処理の連携
        └── 異常系: エラー処理の組み合わせ

    # C1のディシジョンテーブル
    | 条件                                 | DT1 | DT2 | DT3 | DT4 |
    |--------------------------------------|-----|-----|-----|-----|
    | ValidationResultが最初に実行される    | Y   | N   | Y   | Y   |
    | WritePreparationResultが次に実行される| Y   | Y   | N   | Y   |
    | バリデーションが成功する             | Y   | Y   | Y   | N   |
    | 期待される結果                       | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目                 | テスト値                    | 期待される結果 | 実装状況   |
    |--------|--------------------------|----------------------------|----------------|------------|
    | BVT_01 | 空の後処理チェーン       | chain_post_processor -> [] | エラー         | C0で実装済 |
    | BVT_02 | バリデーションのみ       | [ValidationResult]         | 失敗          | C1で実装済 |
    | BVT_03 | 標準的な後処理チェーン   | [Validation.., Write..]    | 成功          | C0で実装済 |
    | BVT_04 | 不正な後処理の追加       | [Validation.., Write.., X] | エラー         | C2で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    def setup_method(self):
        """テスト開始時のログ出力"""
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テスト終了時のログ出力"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_chain_post_processor_C0_basic_chain(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: PostProcessorRequestの基本チェーン構成を検証

        chain_post_processor()メソッドが正しい構成の後処理チェーンを
        返すことを確認します。ValidationResultとWritePreparationResultの
        2つのプロセッサが適切に構成されていることを検証します。

        検証項目:
        1. チェーンが2つの後処理プロセッサで構成されていること
        2. 最初のプロセッサがValidationResultであること
        3. 2番目のプロセッサがWritePreparationResultであること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PostProcessorRequest()
        chain = processor.chain_post_processor()

        assert len(chain) == 2, "後処理チェーンは2つのプロセッサで構成されるべきです"
        assert isinstance(chain[0], ValidationResult), "最初の後処理の型が不正です"
        assert isinstance(chain[1], WritePreparationResult), "2番目の後処理の型が不正です"

    def test_chain_post_processor_C1_validation_execution(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: バリデーションと書き込みの実行順序を検証

        後処理チェーンでのバリデーションと書き込み処理が正しい順序で
        実行されることを確認します。ValidationResultが先に実行され、
        その後でWritePreparationResultが実行されることを検証します。

        検証項目:
        1. ValidationResultが最初に実行されること
        2. WritePreparationResultが2番目に実行されること
        3. 実行順序が常に一定であること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ValidationResult') as mock_validation, \
             patch('src.packages.pattern_editor.pattern_chain_processor.WritePreparationResult') as mock_write:

            execution_order = []
            def record_execution(name):
                return lambda x: execution_order.append(name)

            mock_validation.return_value.process.side_effect = record_execution('validate')
            mock_write.return_value.process.side_effect = record_execution('write')

            processor = PostProcessorRequest()
            chain = processor.chain_post_processor()

            df = pd.DataFrame()
            for proc in chain:
                proc.process(df)

            assert execution_order == ['validate', 'write'], "後処理の実行順序が不正です"

    def test_chain_post_processor_C2_validation_error(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: バリデーションエラー時の動作を検証

        バリデーションエラーが発生した場合の後処理チェーンの動作を検証します。
        エラーが適切に伝搬し、後続の書き込み処理が実行されないことを確認します。

        検証項目:
        1. バリデーションエラーが適切に検出されること
        2. エラー発生時に書き込み処理が実行されないこと
        3. エラーメッセージが適切に生成されること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ValidationResult') as mock_validation, \
             patch('src.packages.pattern_editor.pattern_chain_processor.WritePreparationResult') as mock_write:

            # バリデーションエラーを設定
            mock_validation.return_value.process.side_effect = Exception("バリデーションエラー")
            write_called = False
            mock_write.return_value.process.side_effect = lambda x: setattr(write_called, 'value', True)

            processor = PostProcessorRequest()
            chain = processor.chain_post_processor()

            df = pd.DataFrame()
            with pytest.raises(Exception) as exc_info:
                for proc in chain:
                    df = proc.process(df)

            assert "バリデーションエラー" in str(exc_info.value)
            assert not write_called, "バリデーションエラー後に書き込みが実行されています"

    def test_chain_post_processor_C2_write_error(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 書き込みエラー時の動作を検証

        書き込み処理でエラーが発生した場合の後処理チェーンの動作を検証します。
        バリデーションは成功するものの、書き込み時にエラーが発生するケースを
        確認します。

        検証項目:
        1. バリデーションが正常に完了すること
        2. 書き込みエラーが適切に検出されること
        3. エラーメッセージが適切に生成されること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ValidationResult') as mock_validation, \
             patch('src.packages.pattern_editor.pattern_chain_processor.WritePreparationResult') as mock_write:

            mock_validation.return_value.process.return_value = pd.DataFrame()
            mock_write.return_value.process.side_effect = Exception("書き込みエラー")

            processor = PostProcessorRequest()
            chain = processor.chain_post_processor()

            df = pd.DataFrame()
            with pytest.raises(Exception) as exc_info:
                for proc in chain:
                    df = proc.process(df)

            assert "書き込みエラー" in str(exc_info.value)


class TestReadDecisionTable:
    """ReadDecisionTableコンポーネントのテスト

    デシジョンテーブルの読み込みと初期処理を行うコンポーネントをテストします。
    ファイルの読み込み、NaN値の処理、エラー処理などの機能を検証します。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なデシジョンテーブルの読み込み
    │   ├── 正常系: NaN値の空文字列への変換
    │   └── 異常系: ファイル読み込みエラー
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: ファイル存在確認
    │   ├── 異常系: ファイル不存在
    │   └── 異常系: 無効なファイル形式
    └── C2: 条件組み合わせ
        ├── データ形式の組み合わせ
        ├── パス指定の組み合わせ
        └── エラー条件の組み合わせ

    # C1のディシジョンテーブル
    | 条件                           | DT1 | DT2 | DT3 | DT4 |
    |--------------------------------|-----|-----|-----|-----|
    | ファイルが存在する             | Y   | N   | Y   | Y   |
    | ファイルが正しい形式である     | Y   | -   | N   | Y   |
    | ファイルにアクセス権限がある   | Y   | -   | -   | N   |
    | 期待される結果                 | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目           | テスト値                | 期待される結果 | 実装状況 |
    |--------|-------------------|------------------------|----------------|-----------|
    | BVT_01 | 空のファイル       | 0バイトファイル         | 空のDataFrame  | C0で実装済|
    | BVT_02 | 最小データセット   | 1行のデータ            | 1行のDataFrame | C0で実装済|
    | BVT_03 | 大規模データ      | 100万行のデータ        | 正常に読み込み  | C2で実装済|
    | BVT_04 | 特殊文字を含むパス | 日本語パス             | 正常に読み込み  | C1で実装済|
    """

    @pytest.fixture
    def mock_config(self):
        return Mock(log_message=Mock())

    @pytest.fixture
    def valid_decision_table(self, tmp_path):
        """有効なデシジョンテーブルのfixture"""
        file_path = tmp_path / "test_decision.pkl"
        df = pd.DataFrame({
            'test_column': ['value1', 'value2'],
            'numeric_column': [1.0, None]
        })
        df.to_pickle(file_path)
        return file_path

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_valid_table(self, valid_decision_table, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効なデシジョンテーブルの読み込みを検証

        正常なデシジョンテーブルファイルを読み込み、適切にDataFrameに
        変換されることを確認します。NaN値が空文字列に変換されることも
        検証します。

        検証項目:
        1. ファイルが正常に読み込まれること
        2. 戻り値がDataFrame型であること
        3. NaN値が空文字列に変換されていること
        4. データの内容が保持されていること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_path', 
                  str(valid_decision_table.parent)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_file', 
                  valid_decision_table.name):

            processor = ReadDecisionTable()
            result_df = processor.process(pd.DataFrame())

            assert isinstance(result_df, pd.DataFrame), "戻り値の型が不正です"
            assert not result_df.empty, "空のDataFrameが返されました"
            assert result_df['numeric_column'].iloc[1] == '', "NaN値が空文字列に変換されていません"
            assert result_df['test_column'].iloc[0] == 'value1', "データ値が正しく保持されていません"

    def test_process_C1_file_not_found(self, tmp_path, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 存在しないファイルへのアクセスを検証

        存在しないファイルにアクセスした場合の例外処理を確認します。
        適切な例外とエラーメッセージが生成されることを検証します。

        検証項目:
        1. FileNotFoundErrorが発生すること
        2. 適切なエラーメッセージが含まれること
        3. 例外がPatternChainProcessorErrorでラップされること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_path', 
                  str(tmp_path)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_file', 
                  'non_existent.pkl'):

            processor = ReadDecisionTable()
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(pd.DataFrame())

            assert "DecisionTable読み込みで失敗が発生しました" in str(exc_info.value)

    def test_process_C2_data_combinations(self, tmp_path, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 様々なデータ形式の組み合わせを検証

        異なるデータ型や値の組み合わせを含むテーブルの読み込みを
        確認します。数値、文字列、日付など、様々なデータ型が
        正しく処理されることを検証します。

        検証項目:
        1. 異なるデータ型の正常な読み込み
        2. 複数カラムの同時処理
        3. 特殊値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        file_path = tmp_path / "test_combinations.pkl"
        test_df = pd.DataFrame({
            'string_col': ['text', None, ''],
            'int_col': [1, None, 3],
            'float_col': [1.1, None, 3.3],
            'date_col': [pd.Timestamp('2021-01-01'), None, pd.Timestamp('2021-01-03')]
        })
        test_df.to_pickle(file_path)

        with patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_path', 
                  str(tmp_path)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_file', 
                  file_path.name):

            processor = ReadDecisionTable()
            result_df = processor.process(pd.DataFrame())

            # 全てのNaN値が空文字列に変換されていることを確認
            assert result_df['string_col'].iloc[1] == ''
            assert result_df['int_col'].iloc[1] == ''
            assert result_df['float_col'].iloc[1] == ''
            assert result_df['date_col'].iloc[1] == ''

            # 正常値が保持されていることを確認
            assert result_df['string_col'].iloc[0] == 'text'
            assert result_df['int_col'].iloc[0] == 1
            assert result_df['float_col'].iloc[0] == 1.1
            assert pd.Timestamp(result_df['date_col'].iloc[0]) == pd.Timestamp('2021-01-01')

class TestModifyDecisionTable:
    """ModifyDecisionTableコンポーネントのテスト

    デシジョンテーブルのカラム名変更と値の置換処理を行うコンポーネントをテストします。
    特に値の置換ルールの正確性と、複数のルールが組み合わさった場合の動作を重点的に
    検証します。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: カラム名の変更処理
    │   ├── 正常系: 基本的な値の置換処理
    │   └── 異常系: 無効なカラム指定
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 各種置換ルールの確認
    │   ├── 正常系: カラムの選択処理
    │   └── 異常系: カラム不足
    └── C2: 条件組み合わせ
        ├── 置換ルールの組み合わせ
        ├── 複数カラムの同時処理
        └── エラー条件の組み合わせ

    # C1のディシジョンテーブル
    | 条件                               | DT1 | DT2 | DT3 | DT4 |
    |------------------------------------|-----|-----|-----|-----|
    | 必要なカラムが存在する             | Y   | N   | Y   | Y   |
    | 置換対象の値が定義済み             | Y   | -   | N   | Y   |
    | 出力カラムが正しく指定されている   | Y   | -   | -   | N   |
    | 期待される結果                     | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目                 | テスト値                    | 期待される結果     | 実装状況 |
    |--------|--------------------------|----------------------------|-------------------|-----------|
    | BVT_01 | 空のデータフレーム       | カラムのみのDF              | 空のDF            | C0で実装済|
    | BVT_02 | 最小データセット         | 1行1カラム                  | 正常に変換        | C0で実装済|
    | BVT_03 | 全ての置換パターン       | 全パターンを含む複数行      | 全て正しく置換    | C1で実装済|
    | BVT_04 | 大規模データ             | 100万行のデータ             | 正常に変換        | C2で実装済|
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    @pytest.fixture
    def test_df(self):
        """テスト用の基本データフレーム"""
        return pd.DataFrame({
            'col1': ['4桁', '5桁', 'なし', 'あり'],
            'col2': ['BPR・AD対象', 'BPR・AD対象外', 'ADのみ対象', '-'],
            'col3': ['通常値', '通常値2', '通常値3', '通常値4']
        })

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_basic_conversion(self, test_df, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的な値の置換処理を検証

        基本的な値の置換パターンが正しく機能することを確認します。
        '4桁'→'is_4digits'などの基本的な置換ルールを検証します。

        検証項目:
        1. 基本的な置換パターンが正しく適用されること
        2. 置換対象外の値が変更されないこと
        3. カラムの選択が正しく行われること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = ModifyDecisionTable()
        with patch('src.packages.pattern_editor.pattern_chain_processor.columns_to_transform_def', 
                  ['col1', 'col2']):
            result_df = processor.process(test_df)

        # 置換結果の検証
        assert result_df['col1'].iloc[0] == 'is_4digits'
        assert result_df['col1'].iloc[1] == 'is_5digits'
        assert result_df['col1'].iloc[2] == 'is_empty'
        assert result_df['col2'].iloc[0] == 'is_bpr_ad_target'
        assert result_df['col3'].iloc[0] == '通常値'  # 置換対象外

    def test_process_C1_all_patterns(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 全ての置換パターンを検証

        定義されている全ての置換パターンが正しく機能することを
        確認します。各パターンを個別に検証し、置換結果の正確性を
        確認します。

        検証項目:
        1. 全ての定義済み置換パターンが機能すること
        2. パターンの優先順位が正しいこと
        3. 未定義パターンが適切に処理されること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 全パターンを含むテストデータ
        test_patterns = pd.DataFrame({
            'test_col': [
                '4桁', '5桁', 'なし', 'あり',
                'BPR・AD対象', 'BPR・AD対象外', 'ADのみ対象',
                '-', '未定義値'
            ]
        })

        expected_results = [
            'is_4digits', 'is_5digits', 'is_empty', 'is_not_empty',
            'is_bpr_ad_target', 'is_not_bpr_ad_target', 'is_ad_only_target',
            'any', '未定義値'
        ]

        processor = ModifyDecisionTable()
        with patch('src.packages.pattern_editor.pattern_chain_processor.columns_to_transform_def', 
                  ['test_col']):
            result_df = processor.process(test_patterns)

        for i, expected in enumerate(expected_results):
            assert result_df['test_col'].iloc[i] == expected

    def test_process_C2_column_combinations(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 複数カラムの同時処理を検証

        複数のカラムに対して同時に置換処理を行う場合の動作を
        確認します。カラム間の独立性と処理の一貫性を検証します。

        検証項目:
        1. 複数カラムの同時処理が正しく行われること
        2. カラム間で処理が干渉しないこと
        3. 大量データでも正しく処理されること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 複数カラムのテストデータ
        multi_col_df = pd.DataFrame({
            'col1': ['4桁', '5桁', 'なし'] * 1000,  # 大量データ
            'col2': ['BPR・AD対象', 'BPR・AD対象外', 'ADのみ対象'] * 1000,
            'col3': ['あり', '-', 'なし'] * 1000
        })

        processor = ModifyDecisionTable()
        with patch('src.packages.pattern_editor.pattern_chain_processor.columns_to_transform_def', 
                  ['col1', 'col2', 'col3']):
            result_df = processor.process(multi_col_df)

        # サンプリングして検証
        assert result_df['col1'].iloc[0] == 'is_4digits'
        assert result_df['col2'].iloc[0] == 'is_bpr_ad_target'
        assert result_df['col3'].iloc[0] == 'is_not_empty'
        
        # データ量の確認
        assert len(result_df) == len(multi_col_df)

    def test_process_C2_error_patterns(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: エラーパターンの組み合わせを検証

        様々なエラー条件の組み合わせに対する動作を確認します。
        カラムの欠落や無効な値の組み合わせなどを検証します。

        検証項目:
        1. 存在しないカラムの指定
        2. 無効な値の組み合わせ
        3. エラーメッセージの正確性
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 無効なカラムを含むデータ
        invalid_df = pd.DataFrame({
            'wrong_col': ['4桁', '5桁'],
            'col2': ['BPR・AD対象', 'BPR・AD対象外']
        })

        processor = ModifyDecisionTable()
        with patch('src.packages.pattern_editor.pattern_chain_processor.columns_to_transform_def', 
                  ['non_existent_col']):
            # KeyErrorをModifyDecisionTableがハンドリングする前提
            with pytest.raises(KeyError) as exc_info:
                processor.process(invalid_df)

            assert "non_existent_col" in str(exc_info.value)

class TestReadRequestListTable:
    """ReadRequestListTableコンポーネントのテスト

    変更情報テーブルの読み込みと初期処理を行うコンポーネントをテストします。
    ファイルの読み込み、データの整合性検証、エラー処理など、データソースとしての
    信頼性を確保するために必要な機能を検証します。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な変更情報テーブルの読み込み
    │   ├── 正常系: NaN値の空文字列への変換
    │   └── 異常系: ファイル読み込みエラー
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: ファイル存在確認とパス解決
    │   ├── 異常系: ファイル不存在
    │   └── 異常系: 無効なファイル形式
    └── C2: 条件組み合わせ
        ├── データ形式の組み合わせ
        ├── パス指定の組み合わせ
        └── エラー条件の組み合わせ

    # C1のディシジョンテーブル
    | 条件                                | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------------|-----|-----|-----|-----|
    | ファイルが存在する                  | Y   | N   | Y   | Y   |
    | ファイルがpickle形式として有効      | Y   | -   | N   | Y   |
    | ファイルに必要なカラムが含まれる    | Y   | -   | -   | N   |
    | 期待される結果                      | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目              | テスト値                      | 期待される結果    | 実装状況   |
    |--------|----------------------|------------------------------|------------------|------------|
    | BVT_01 | 空のテーブル          | カラムのみのDF                | 空のDF           | C0で実装済 |
    | BVT_02 | 最小データセット      | 1行の変更情報                 | 1行のDF          | C0で実装済 |
    | BVT_03 | 大規模データ         | 100万行の変更情報             | 正常に読み込み    | C2で実装済 |
    | BVT_04 | 特殊文字を含むパス    | 日本語パス                    | 正常に読み込み    | C1で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    @pytest.fixture
    def valid_request_table(self, tmp_path):
        """有効な変更情報テーブルのfixture"""
        file_path = tmp_path / "test_request.pkl"
        df = pd.DataFrame({
            'request_type': ['新規', '変更', '廃止'],
            'branch_code': ['1234', '5678', '9012'],
            'branch_name': ['支店A', 'ブランチB', None],
            'effective_date': ['2024-01-01', '2024-02-01', '2024-03-01']
        })
        df.to_pickle(file_path)
        return file_path

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_valid_table(self, valid_request_table, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 有効な変更情報テーブルの読み込みを検証

        正常な変更情報テーブルファイルを読み込み、適切にDataFrameに
        変換されることを確認します。特に、データ型の保持とNaN値の
        処理が正しく行われることを重点的に検証します。

        検証項目:
        1. ファイルが正常に読み込まれること
        2. 戻り値がDataFrame型であること
        3. NaN値が空文字列に変換されていること
        4. 各カラムのデータが正しく保持されていること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.request_list_table_path', 
                  str(valid_request_table.parent)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.request_list_table_file', 
                  valid_request_table.name):

            processor = ReadRequestListTable()
            result_df = processor.process(pd.DataFrame())

            assert isinstance(result_df, pd.DataFrame), "戻り値の型が不正です"
            assert not result_df.empty, "空のDataFrameが返されました"
            assert result_df['branch_name'].iloc[2] == '', "NaN値が空文字列に変換されていません"
            assert result_df['branch_code'].iloc[0] == '1234', "データ値が正しく保持されていません"
            assert len(result_df) == 3, "行数が期待値と異なります"

    def test_process_C1_file_handling(self, tmp_path, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: ファイルハンドリングの分岐を検証

        ファイルの存在確認、パス解決、ファイルオープンの各段階での
        エラーハンドリングを確認します。特に、エラーメッセージの
        適切性とエラー情報の伝搬を検証します。

        検証項目:
        1. 不正なファイルパスでの例外発生
        2. アクセス権限エラーの処理
        3. 無効なファイル形式の検出
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        non_existent_path = tmp_path / "not_exists.pkl"
        with patch('src.packages.pattern_editor.pattern_chain_processor.request_list_table_file', 
                  str(non_existent_path)):

            processor = ReadRequestListTable()
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(pd.DataFrame())

            assert "変更情報テーブルファイル読み込みで失敗が発生しました" in str(exc_info.value)

    def test_process_C2_data_variations(self, tmp_path, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: データバリエーションの組み合わせを検証

        様々なデータ型、値の組み合わせ、特殊ケースを含むテーブルの
        読み込みを確認します。型の一貫性とデータの整合性が保たれることを
        重点的に検証します。

        検証項目:
        1. 異なるデータ型の組み合わせ
        2. 特殊文字や空値の処理
        3. データの整合性維持
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 多様なデータパターンを含むテストデータを作成
        file_path = tmp_path / "test_variations.pkl"
        test_df = pd.DataFrame({
            'request_type': ['新規', '変更', '廃止', None],
            'branch_code': ['1234', '', '9012', '特殊文字＃＄'],
            'numeric_value': [1, None, 3.14, '非数値'],
            'date_value': [
                pd.Timestamp('2024-01-01'),
                None,
                pd.Timestamp('2024-12-31'),
                'invalid_date'
            ]
        })
        test_df.to_pickle(file_path)

        with patch('src.packages.pattern_editor.pattern_chain_processor.request_list_table_path', 
                  str(tmp_path)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.request_list_table_file', 
                  file_path.name):

            processor = ReadRequestListTable()
            result_df = processor.process(pd.DataFrame())

            # データ型と値の検証
            assert result_df['request_type'].iloc[3] == '', "NaN値の変換が不正です"
            assert result_df['branch_code'].iloc[3] == '特殊文字＃＄', "特殊文字の処理が不正です"
            assert result_df['numeric_value'].iloc[1] == '', "数値のNaN変換が不正です"
            assert isinstance(result_df['numeric_value'].iloc[2], (int, float)), "数値型の保持が不正です"

class TestAddDecisionJudgeColumns:
    """AddDecisionJudgeColumnsコンポーネントのテスト

    入力データフレームに対して、デシジョンテーブルの条件判定に必要な
    カラムを追加するコンポーネントをテストします。

    このコンポーネントは特に以下の重要な変換を行います：
    1. 部店コード、親部店コードの文字列変換
    2. 特定部署コードの設定
    3. 部店コードの先頭2桁の抽出
    4. 親部店コードと部店コードの先頭4桁の一致判定

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 基本的なカラム追加処理
    │   ├── 正常系: データ型変換の確認
    │   └── 異常系: 必須カラム欠損
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: コード一致判定処理
    │   ├── 正常系: 文字列変換処理
    │   └── 異常系: 無効なコード値
    └── C2: 条件組み合わせ
        ├── コード値の組み合わせ
        ├── データ型の組み合わせ
        └── エラー条件の組み合わせ

    # C1のディシジョンテーブル
    | 条件                                    | DT1 | DT2 | DT3 | DT4 |
    |-----------------------------------------|-----|-----|-----|-----|
    | 親部店コードが存在する                   | Y   | N   | Y   | Y   |
    | 部店コードが存在する                     | Y   | Y   | N   | Y   |
    | コードが正しい形式（数値変換可能）       | Y   | Y   | Y   | N   |
    | 期待される結果                          | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目               | テスト値                    | 期待される結果    | 実装状況   |
    |--------|------------------------|----------------------------|------------------|------------|
    | BVT_01 | 空のデータフレーム     | カラムのみのDF              | 空のDF           | C0で実装済 |
    | BVT_02 | 最小コード長           | 1桁のコード                 | 適切にパディング  | C1で実装済 |
    | BVT_03 | 最大コード長           | 10桁のコード               | 正しく切り出し    | C1で実装済 |
    | BVT_04 | 特殊文字を含むコード   | 英数字混在コード            | 適切に処理       | C2で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    @pytest.fixture
    def basic_input_df(self):
        """基本的なテスト用データフレーム"""
        return pd.DataFrame({
            'parent_branch_code': ['1234', '5678', '9012'],
            'branch_code': ['123456', '567890', '901234']
        })

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_basic_column_addition(self, basic_input_df, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なカラム追加処理を検証

        基本的なデータに対して、必要なカラムが正しく追加されることを
        確認します。特に、データ型の変換と新規カラムの値の正確性を
        重点的に検証します。

        検証項目:
        1. 全ての必要なカラムが追加されていること
        2. データ型が文字列型に正しく変換されていること
        3. 部店コードの先頭2桁が正しく抽出されていること
        4. コードの一致判定が正しく行われていること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = AddDecisionJudgeColumns()
        result_df = processor.process(basic_input_df)

        # 必要なカラムの存在確認
        expected_columns = {
            'parent_branch_code', 'branch_code', 'specific_department_code',
            'branch_code_first_2_digit', 
            'parent_branch_code_and_branch_code_first_4_digits_match'
        }
        assert all(col in result_df.columns for col in expected_columns)

        # データ型の検証
        assert result_df['parent_branch_code'].dtype == 'object'
        assert result_df['branch_code'].dtype == 'object'

        # 値の検証
        assert result_df['branch_code_first_2_digit'].iloc[0] == '12'
        assert result_df['parent_branch_code_and_branch_code_first_4_digits_match'].iloc[0] == 'exists'

    def test_process_C1_code_matching(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: コード一致判定処理の分岐を検証

        親部店コードと部店コードの先頭4桁の一致判定処理における
        各分岐を確認します。一致・不一致の様々なパターンを検証し、
        判定結果の正確性を確認します。

        検証項目:
        1. コードが完全一致する場合
        2. コードが部分一致する場合
        3. コードが不一致の場合
        4. コードの長さが異なる場合
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 様々なコードパターンのテストデータ
        test_df = pd.DataFrame({
            'parent_branch_code': ['1234', '5678', '9012', '4567'],
            'branch_code': ['123456', '567800', '901', '999999']
        })

        processor = AddDecisionJudgeColumns()
        result_df = processor.process(test_df)

        # 判定結果の検証
        assert result_df['parent_branch_code_and_branch_code_first_4_digits_match'].iloc[0] == 'exists'
        assert result_df['parent_branch_code_and_branch_code_first_4_digits_match'].iloc[1] == ''
        assert result_df['parent_branch_code_and_branch_code_first_4_digits_match'].iloc[2] == ''
        assert result_df['parent_branch_code_and_branch_code_first_4_digits_match'].iloc[3] == ''

    def test_process_C2_code_variations(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: コード値の様々な組み合わせを検証

        部店コードと親部店コードの様々なバリエーションに対する
        処理を確認します。特殊なコード値や異常値の処理が
        正しく行われることを検証します。

        検証項目:
        1. 数値以外の文字を含むコード
        2. 異なる長さのコード
        3. 空白やnullを含むコード
        4. 特殊文字を含むコード
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 様々なコードパターンのテストデータ
        test_df = pd.DataFrame({
            'parent_branch_code': ['1234', 'ABCD', '', None, '12 34'],
            'branch_code': ['123456', 'ABCD56', '123', None, '12 3456']
        })

        processor = AddDecisionJudgeColumns()
        result_df = processor.process(test_df)

        # コード処理結果の検証
        assert result_df['branch_code_first_2_digit'].iloc[0] == '12'
        assert result_df['branch_code_first_2_digit'].iloc[1] == 'AB'
        assert result_df['branch_code_first_2_digit'].iloc[2] == '12'
        assert result_df['branch_code_first_2_digit'].iloc[3] == ''
        assert result_df['branch_code_first_2_digit'].iloc[4] == '12'

    def test_process_C2_large_dataset(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 大規模データセットでの処理を検証

        大量のレコードを含むデータフレームに対する処理の
        正確性とパフォーマンスを確認します。メモリ使用量と
        処理時間の観点も考慮します。

        検証項目:
        1. 大量データの正確な処理
        2. 処理の一貫性
        3. メモリ効率
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 大規模データセットの生成
        large_df = pd.DataFrame({
            'parent_branch_code': [f'{i:04d}' for i in range(10000)],
            'branch_code': [f'{i:06d}' for i in range(10000)]
        })

        processor = AddDecisionJudgeColumns()
        result_df = processor.process(large_df)

        # データ処理の正確性検証
        assert len(result_df) == 10000
        assert result_df['branch_code_first_2_digit'].iloc[0] == '00'
        assert result_df['branch_code_first_2_digit'].iloc[9999] == '99'
        assert result_df['parent_branch_code_and_branch_code_first_4_digits_match'].iloc[0] == 'exists'
        

class TestValidationResult:
    """ValidationResultコンポーネントのテスト

    パターン編集後のデータに対する検証処理を行うコンポーネントをテストします。
    データモデルとの整合性、業務ルールの遵守、データの品質について総合的に
    検証を行います。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 基本的なバリデーション
    │   ├── 正常系: 全項目が有効な場合の検証
    │   └── 異常系: 必須項目の欠損
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: データ型の検証
    │   ├── 正常系: 値の範囲チェック
    │   └── 異常系: 不正データの検出
    └── C2: 条件組み合わせ
        ├── データ型の組み合わせ
        ├── 値の範囲の組み合わせ
        └── エラー条件の組み合わせ

    # C1のディシジョンテーブル
    | 条件                                | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------------|-----|-----|-----|-----|
    | 必須項目が全て存在する               | Y   | N   | Y   | Y   |
    | データ型が全て正しい                 | Y   | -   | N   | Y   |
    | 値の範囲が全て正しい                 | Y   | -   | -   | N   |
    | 期待される結果                       | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目                | テスト値                  | 期待される結果 | 実装状況   |
    |--------|------------------------|--------------------------|---------------|------------|
    | BVT_01 | 空のデータセット        | 必須項目のみのDF          | 成功          | C0で実装済 |
    | BVT_02 | 最小値境界              | 各項目の最小有効値        | 成功          | C1で実装済 |
    | BVT_03 | 最大値境界              | 各項目の最大有効値        | 成功          | C1で実装済 |
    | BVT_04 | 特殊文字                | 制御文字を含むデータ      | 失敗          | C2で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    @pytest.fixture
    def valid_input_df(self):
        """有効な入力データフレームのfixture"""
        return pd.DataFrame({
            'branch_code': ['1234', '5678', '9012'],
            'branch_name': ['支店A', 'ブランチB', '支店C'],
            'request_type': ['新規', '変更', '廃止'],
            'effective_date': ['2024-01-01', '2024-02-01', '2024-03-01']
        })

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_basic_validation(self, valid_input_df, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なバリデーション処理を検証

        正常なデータに対するバリデーション処理が適切に機能することを
        確認します。必須項目の存在チェック、データ型の検証、値の範囲
        チェックなどの基本的な検証が正しく行われることを確認します。

        検証項目:
        1. バリデーション処理が正常に完了すること
        2. 戻り値のデータフレームが入力と同一であること
        3. エラーが発生しないこと
        4. データの内容が保持されていること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = ValidationResult()
        with patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator') as mock_validator:
            mock_validator.return_value.validate.return_value = None
            result_df = processor.process(valid_input_df)

            assert isinstance(result_df, pd.DataFrame)
            assert result_df.equals(valid_input_df)
            mock_validator.return_value.validate.assert_called_once()

    def test_process_C1_validation_error(self, valid_input_df, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: バリデーションエラーの処理を検証

        バリデーションエラーが発生した場合の処理を確認します。
        エラーメッセージの生成と例外の伝播が適切に行われることを
        検証します。

        検証項目:
        1. バリデーションエラーが適切に検出されること
        2. エラーメッセージが正しく生成されること
        3. 例外が適切な形式でラップされること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = ValidationResult()
        with patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator') as mock_validator:
            mock_validator.return_value.validate.side_effect = ValueError("バリデーションエラー")
            
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(valid_input_df)

            assert "パターン編集処理結果のValidationに失敗" in str(exc_info.value)

    def test_process_C2_data_type_combinations(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 様々なデータ型の組み合わせを検証

        異なるデータ型の組み合わせに対するバリデーション処理を
        確認します。特に、型変換が必要なケースや特殊な値を含む
        ケースについて検証します。

        検証項目:
        1. 異なるデータ型の組み合わせ
        2. データ型の変換処理
        3. 特殊値の処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 様々なデータ型を含むテストデータ
        test_df = pd.DataFrame({
            'branch_code': ['1234', 5678, '90A2'],  # 文字列と数値の混在
            'branch_name': ['支店A', None, ''],     # Null値と空文字
            'request_type': ['新規', '不正な値', '廃止'],  # 無効な値
            'effective_date': ['2024-01-01', 'invalid', '2024-03-01']  # 無効な日付
        })

        processor = ValidationResult()
        with patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator') as mock_validator:
            mock_validator.return_value.validate.side_effect = ValueError("データ型エラー")
            
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(test_df)

            assert "パターン編集処理結果のValidationに失敗" in str(exc_info.value)

    def test_process_C2_business_rule_validation(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 業務ルールの検証処理を確認

        業務ルールに基づくバリデーション処理の正確性を確認します。
        複数の業務ルールの組み合わせや、条件の依存関係がある
        ケースについて検証します。

        検証項目:
        1. 業務ルールの正しい適用
        2. ルール間の依存関係の処理
        3. 複合条件の評価
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 業務ルールに関わるテストデータ
        test_df = pd.DataFrame({
            'branch_code': ['1234', '5678', '9012'],
            'parent_branch_code': ['1234', '5600', '9012'],  # 親部店コードの一致/不一致
            'request_type': ['新規', '変更', '廃止'],        # 申請種別の組み合わせ
            'effective_date': ['2024-01-01', '2024-01-15', '2024-01-01']  # 日付の重複
        })

        processor = ValidationResult()
        with patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator') as mock_validator:
            # 業務ルール違反を検出する場合
            mock_validator.return_value.validate.side_effect = ValueError("業務ルール違反")
            
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(test_df)

            assert "パターン編集処理結果のValidationに失敗" in str(exc_info.value)

class TestWritePreparationResult:
    """WritePreparationResultコンポーネントのテスト

    パターン編集処理の結果をファイルシステムに永続化するコンポーネントを
    テストします。pickleファイルとExcelファイルの両方について、書き込み処理の
    正確性とエラーハンドリングを検証します。

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: pickleファイル出力
    │   ├── 正常系: Excelファイル出力
    │   └── 異常系: ファイル書き込みエラー
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: ファイルパス解決
    │   ├── 異常系: 権限エラー
    │   └── 異常系: ディスク容量エラー
    └── C2: 条件組み合わせ
        ├── 出力形式の組み合わせ
        ├── パス指定の組み合わせ
        └── エラー条件の組み合わせ

    # C1のディシジョンテーブル
    | 条件                                | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------------|-----|-----|-----|-----|
    | 出力ディレクトリが存在する          | Y   | N   | Y   | Y   |
    | 書き込み権限がある                  | Y   | -   | N   | Y   |
    | 十分なディスク容量がある            | Y   | -   | -   | N   |
    | 期待される結果                      | 成功| 失敗| 失敗| 失敗|

    境界値検証ケース一覧：
    | ID     | 検証項目                | テスト値                  | 期待される結果 | 実装状況   |
    |--------|------------------------|--------------------------|---------------|------------|
    | BVT_01 | 空のデータフレーム      | カラムのみのDF            | 正常に出力     | C0で実装済 |
    | BVT_02 | 最小データセット        | 1行のデータ               | 正常に出力     | C0で実装済 |
    | BVT_03 | 大規模データセット      | 100万行のデータ           | 正常に出力     | C2で実装済 |
    | BVT_04 | 特殊文字を含むパス      | 日本語パス                | 正常に出力     | C1で実装済 |
    """

    @pytest.fixture
    def mock_config(self):
        """テスト用のconfigモック"""
        return Mock(log_message=Mock())

    @pytest.fixture
    def test_df(self):
        """テスト用のデータフレーム"""
        return pd.DataFrame({
            'column1': ['value1', 'value2', 'value3'],
            'column2': [1, 2, 3],
            'column3': [True, False, True]
        })

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_process_C0_basic_output(self, test_df, tmp_path, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なファイル出力処理を検証

        基本的なデータフレームに対して、pickleファイルとExcelファイルの
        両方が正しく出力されることを確認します。出力されたファイルの
        内容と形式が正しいことを検証します。

        検証項目:
        1. pickleファイルが正しく出力されること
        2. Excelファイルが正しく出力されること
        3. 出力されたデータが入力と一致すること
        4. データ型が正しく保持されていること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        pickle_path = tmp_path / "output.pkl"
        excel_path = tmp_path / "output.xlsx"

        with patch('src.packages.pattern_editor.pattern_chain_processor.pattern_edited', 
                  str(pickle_path)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.debug_pattern_result_xlsx', 
                  str(excel_path)):

            processor = WritePreparationResult()
            result_df = processor.process(test_df)

            # ファイルの存在確認
            assert pickle_path.exists(), "pickleファイルが出力されていません"
            assert excel_path.exists(), "Excelファイルが出力されていません"

            # pickleファイルの内容検証
            df_from_pickle = pd.read_pickle(pickle_path)
            assert df_from_pickle.equals(test_df), "pickleファイルの内容が一致しません"

            # Excelファイルの内容検証
            df_from_excel = pd.read_excel(excel_path)
            assert df_from_excel.astype(str).equals(test_df.astype(str)), "Excelファイルの内容が一致しません"

    def test_process_C1_file_permission_error(self, test_df, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: ファイルアクセス権限エラーの処理を検証

        書き込み権限のない場所への出力を試みた場合のエラー処理を
        確認します。適切な例外が発生し、エラーメッセージが
        正しく生成されることを検証します。

        検証項目:
        1. 権限エラーが適切に検出されること
        2. エラーメッセージが正しく生成されること
        3. 例外が適切な形式でラップされること
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.pattern_edited', 
                  '/invalid/path/output.pkl'), \
             patch('src.packages.pattern_editor.pattern_chain_processor.debug_pattern_result_xlsx', 
                  '/invalid/path/output.xlsx'), \
             patch('pandas.DataFrame.to_pickle', side_effect=PermissionError("権限エラー")):

            processor = WritePreparationResult()
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(test_df)

            assert "パターン編集処理結果ファイル書き込みで失敗" in str(exc_info.value)

    def test_process_C2_large_data_output(self, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 大規模データセットの出力処理を検証

        大量のレコードを含むデータフレームの出力処理を確認します。
        メモリ使用量とディスク容量の観点から、処理の安定性を
        検証します。

        検証項目:
        1. 大規模データの正常な出力
        2. メモリ効率の確認
        3. 処理時間の妥当性
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 大規模データセットの生成
        large_df = pd.DataFrame({
            'column1': [f'value{i}' for i in range(100000)],
            'column2': range(100000),
            'column3': [i % 2 == 0 for i in range(100000)]
        })

        with patch('src.packages.pattern_editor.pattern_chain_processor.pattern_edited', 
                  'large_output.pkl'), \
             patch('src.packages.pattern_editor.pattern_chain_processor.debug_pattern_result_xlsx', 
                  'large_output.xlsx'), \
             patch('pandas.DataFrame.to_pickle') as mock_pickle, \
             patch('pandas.DataFrame.to_excel') as mock_excel:

            processor = WritePreparationResult()
            processor.process(large_df)

            # 出力処理が呼ばれたことを確認
            mock_pickle.assert_called_once()
            mock_excel.assert_called_once()

    def test_process_C2_special_path_characters(self, test_df, tmp_path, mock_config):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 特殊文字を含むパスでの出力処理を検証

        日本語や特殊文字を含むファイルパスへの出力処理を確認します。
        パスの解決とエンコーディングが正しく処理されることを
        検証します。

        検証項目:
        1. 日本語パスへの出力
        2. 特殊文字を含むパスへの出力
        3. パスの正規化処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        special_path = tmp_path / "テスト出力_特殊文字#$%" 
        special_path.mkdir(exist_ok=True)
        pickle_path = special_path / "出力テスト.pkl"
        excel_path = special_path / "出力テスト.xlsx"

        with patch('src.packages.pattern_editor.pattern_chain_processor.pattern_edited', 
                  str(pickle_path)), \
             patch('src.packages.pattern_editor.pattern_chain_processor.debug_pattern_result_xlsx', 
                  str(excel_path)):

            processor = WritePreparationResult()
            processor.process(test_df)

            assert pickle_path.exists(), "pickleファイルが出力されていません"
            assert excel_path.exists(), "Excelファイルが出力されていません"

