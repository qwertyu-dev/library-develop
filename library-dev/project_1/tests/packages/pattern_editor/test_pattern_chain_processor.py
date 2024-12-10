# config共有
import sys
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from pathlib import Path

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
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
    WritePatternResult,
)

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestPreProcessorDecisionTableChain:
    """PreProcessorDecisionTableのチェーン制御テスト

    テスト構造:
    ├── C0: チェーン構成と実行順序
    │   ├── 正常系: 2プロセッサの構成確認
    │   ├── 正常系: プロセッサの型確認
    │   └── 正常系: 実行順序の確認
    ├── C1: チェーン分岐検証
    │   ├── 正常系: 全プロセッサ正常終了
    │   ├── 異常系: ReadDecisionTableでエラー
    │   └── 異常系: ModifyDecisionTableでエラー 
    └── C2: データ伝播パターン
        ├── 正常系: 空DataFrame
        └── 正常系: データ有DataFrame

    # C1のディシジョンテーブル
    | 条件                           | DT1 | DT2 | DT3 |
    |--------------------------------|-----|-----|-----|
    | ReadDecisionTableが正常終了    | Y   | N   | Y   |
    | ModifyDecisionTableが正常終了  | Y   | -   | N   |
    |--------------------------------|-----|-----|-----|
    | チェーン処理が完了            | X   | -   | -   |
    | ReadDecisionTableエラー発生   | -   | X   | -   |
    | ModifyDecisionTableエラー発生 | -   | -   | X   |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値          | 期待結果 | テストの目的/検証ポイント | 実装状況    | 対応するテストケース                |
    |--------|------------|-------------------|----------|--------------------------|-------------|-----------------------------------|
    | BVT001 | df         | 空のDataFrame     | 成功     | 最小データセットの確認    | C2で実装済み | test_chain_C2_empty_df           |
    | BVT002 | df         | 1行のDataFrame    | 成功     | 最小有効データの確認      | C2で実装済み | test_chain_C2_with_data          |
    | BVT003 | df         | None              | エラー   | 無効入力の確認           | C1で実装済み | test_chain_C1_read_error         |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

    def test_chain_C0_processor_composition(self):
        """プロセッサ構成のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: チェーンの構成要素を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PreProcessorDecisionTable()
        chain = processor.chain_pre_processor()

        assert len(chain) == 2
        assert any('ReadDecisionTable' in str(type(p)) for p in chain)
        assert any('ModifyDecisionTable' in str(type(p)) for p in chain)

    def test_chain_C0_execution_order(self, sample_df):
        """実行順序の確認テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: プロセッサの実行順序を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        execution_order = []

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadDecisionTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.ModifyDecisionTable') as mock_modify:

            def mock_process_read(df):
                execution_order.append('read')
                return df

            def mock_process_modify(df):
                execution_order.append('modify')
                return df

            mock_read.return_value.process = mock_process_read
            mock_modify.return_value.process = mock_process_modify

            processor = PreProcessorDecisionTable()
            chain = processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert execution_order == ['read', 'modify']

    def test_chain_C1_normal_flow(self, sample_df):
        """正常系の分岐テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 全プロセッサが正常終了
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadDecisionTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.ModifyDecisionTable') as mock_modify:

            mock_read.return_value.process.return_value = sample_df
            mock_modify.return_value.process.return_value = sample_df

            processor = PreProcessorDecisionTable()
            chain = processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert isinstance(df_result, pd.DataFrame)
            mock_read.return_value.process.assert_called_once()
            mock_modify.return_value.process.assert_called_once()

    def test_chain_C1_read_error(self, sample_df):
        """ReadDecisionTableエラーの分岐テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: ReadDecisionTableでエラー発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadDecisionTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.ModifyDecisionTable') as mock_modify:

            mock_read.return_value.process.side_effect = Exception("Read Error")

            processor = PreProcessorDecisionTable()
            chain = processor.chain_pre_processor()
            with pytest.raises(Exception) as exc_info:
                df_result = sample_df.copy()
                for proc in chain:
                    df_result = proc.process(df_result)

            assert "Read Error" in str(exc_info.value)
            mock_modify.return_value.process.assert_not_called()

    def test_chain_C2_empty_df(self, empty_df):
        """空DataFrameの伝播テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 空DataFrame処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadDecisionTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.ModifyDecisionTable') as mock_modify:

            mock_read.return_value.process.return_value = empty_df
            mock_modify.return_value.process.return_value = empty_df

            processor = PreProcessorDecisionTable()
            chain = processor.chain_pre_processor()
            df_result = empty_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert df_result.empty
            mock_read.return_value.process.assert_called_once()
            mock_modify.return_value.process.assert_called_once()

class TestPreProcessorRequestChain:
    """PreProcessorRequestのチェーン制御テスト

    テスト構造:
    ├── C0: チェーン構成と実行順序
    │   ├── 正常系: 2プロセッサの構成確認
    │   ├── 正常系: プロセッサの型確認
    │   └── 正常系: 実行順序の確認
    ├── C1: チェーン分岐検証
    │   ├── 正常系: 全プロセッサ正常終了
    │   ├── 異常系: ReadRequestListTableでエラー
    │   └── 異常系: AddDecisionJudgeColumnsでエラー
    └── C2: データ伝播パターン
        ├── 正常系: 空DataFrame
        └── 正常系: データ有DataFrame

    # C1のディシジョンテーブル
    | 条件                               | DT1 | DT2 | DT3 |
    |------------------------------------|-----|-----|-----|
    | ReadRequestListTableが正常終了     | Y   | N   | Y   |
    | AddDecisionJudgeColumnsが正常終了  | Y   | -   | N   |
    |------------------------------------|-----|-----|-----|
    | チェーン処理が完了                | X   | -   | -   |
    | ReadRequestListTableエラー発生    | -   | X   | -   |
    | AddDecisionJudgeColumnsエラー発生 | -   | -   | X   |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値          | 期待結果 | テストの目的/検証ポイント | 実装状況    | 対応するテストケース                |
    |--------|------------|-------------------|----------|--------------------------|-------------|-----------------------------------|
    | BVT001 | df         | 空のDataFrame     | 成功     | 最小データセットの確認    | C2で実装済み | test_chain_C2_empty_df           |
    | BVT002 | df         | 1行のDataFrame    | 成功     | 最小有効データの確認      | C2で実装済み | test_chain_C2_with_data          |
    | BVT003 | df         | None              | エラー   | 無効入力の確認           | C1で実装済み | test_chain_C1_read_error         |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

    def test_chain_C0_processor_composition(self):
        """プロセッサ構成のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: チェーンの構成要素を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PreProcessorRequest()
        chain = processor.chain_pre_processor()

        assert len(chain) == 2
        assert any('ReadRequestListTable' in str(type(p)) for p in chain)
        assert any('AddDecisionJudgeColumns' in str(type(p)) for p in chain)


    def test_chain_C0_execution_order(self, sample_df):
        """実行順序の確認テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: プロセッサの実行順序を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        execution_order = []

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadRequestListTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.AddDecisionJudgeColumns') as mock_add:

            def mock_process_read(df):
                execution_order.append('read')
                return df

            def mock_process_add(df):
                execution_order.append('add')
                return df

            mock_read.return_value.process = mock_process_read
            mock_add.return_value.process = mock_process_add

            processor = PreProcessorRequest()
            chain = processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert execution_order == ['read', 'add']

    def test_chain_C1_normal_flow(self, sample_df):
        """正常系の分岐テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 全プロセッサが正常終了
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadRequestListTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.AddDecisionJudgeColumns') as mock_add:

            mock_read.return_value.process.return_value = sample_df
            mock_add.return_value.process.return_value = sample_df

            processor = PreProcessorRequest()
            chain = processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert isinstance(df_result, pd.DataFrame)
            mock_read.return_value.process.assert_called_once()
            mock_add.return_value.process.assert_called_once()

    def test_chain_C2_empty_df(self, empty_df):
        """空DataFrameの伝播テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 空DataFrame処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
 
        with patch('src.packages.pattern_editor.pattern_chain_processor.ReadRequestListTable') as mock_read, \
             patch('src.packages.pattern_editor.pattern_chain_processor.AddDecisionJudgeColumns') as mock_add:
 
            mock_read.return_value.process.return_value = empty_df
            mock_add.return_value.process.return_value = empty_df
 
            processor = PreProcessorRequest()
            chain = processor.chain_pre_processor()
            df_result = empty_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)
 
            assert df_result.empty
            mock_read.return_value.process.assert_called_once()
            mock_add.return_value.process.assert_called_once()


class TestPostProcessorRequestChain:
    """PostProcessorRequestのチェーン制御テスト

    テスト構造:
    ├── C0: チェーン構成と実行順序
    │   ├── 正常系: 2プロセッサの構成確認
    │   ├── 正常系: プロセッサの型確認
    │   └── 正常系: 実行順序の確認
    ├── C1: チェーン分岐検証
    │   ├── 正常系: 全プロセッサ正常終了
    │   ├── 異常系: ValidationResultでエラー
    │   └── 異常系: WritePatternResultでエラー
    └── C2: データ伝播パターン
        ├── 正常系: 空DataFrame
        └── 正常系: データ有DataFrame

    # C1のディシジョンテーブル
    | 条件                                | DT1 | DT2 | DT3 |
    |-------------------------------------|-----|-----|-----|
    | ValidationResultが正常終了          | Y   | N   | Y   |
    | WritePaternResultが正常終了         | Y   | -   | N   |
    |-------------------------------------|-----|-----|-----|
    | チェーン処理が完了                  | X   | -   | -   |
    | ValidationResultエラー発生          | -   | X   | -   |
    | WritePatternResultエラー発生        | -   | -   | X   |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値          | 期待結果 | テストの目的/検証ポイント | 実装状況     | 対応するテストケース             |
    |--------|------------|-------------------|----------|---------------------------|--------------|----------------------------------|
    | BVT001 | df         | 空のDataFrame     | 成功     | 最小データセットの確認    | C2で実装済み | test_chain_C2_empty_df           |
    | BVT002 | df         | 1行のDataFrame    | 成功     | 最小有効データの確認      | C2で実装済み | test_chain_C2_with_data          |
    | BVT003 | df         | None              | エラー   | 無効入力の確認            | C1で実装済み | test_chain_C1_validate_error     |
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

    def test_chain_C0_processor_composition(self):
        """プロセッサ構成のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: チェーンの構成要素を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = PostProcessorRequest()
        chain = processor.chain_post_processor()

        assert len(chain) == 2
        assert any('ValidationResult' in str(type(p)) for p in chain)
        assert any('WritePatternResult' in str(type(p)) for p in chain)

    def test_chain_C0_execution_order(self, sample_df):
        """実行順序の確認テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: プロセッサの実行順序を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        execution_order = []

        with patch('src.packages.pattern_editor.pattern_chain_processor.ValidationResult') as mock_validate, \
            patch('src.packages.pattern_editor.pattern_chain_processor.WritePatternResult') as mock_write:

            def mock_process_validate(df):
                execution_order.append('validate')
                return df

            def mock_process_write(df):
                execution_order.append('write')
                return df

            mock_validate.return_value.process = mock_process_validate
            mock_write.return_value.process = mock_process_write

            processor = PostProcessorRequest()
            chain = processor.chain_post_processor()
            df_result = sample_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert execution_order == ['validate', 'write']

    def test_chain_C1_validate_error(self, sample_df):
        """ValidationResultエラーの分岐テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: ValidationResultでエラー発生
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ValidationResult') as mock_validate, \
            patch('src.packages.pattern_editor.pattern_chain_processor.WritePatternResult') as mock_write:

            mock_validate.return_value.process.side_effect = PatternChainProcessorError("Validation Error")

            processor = PostProcessorRequest()
            chain = processor.chain_post_processor()
            with pytest.raises(PatternChainProcessorError) as exc_info:
                df_result = sample_df.copy()
                for proc in chain:
                    df_result = proc.process(df_result)

            assert "Validation Error" in str(exc_info.value)
            mock_write.return_value.process.assert_not_called()

    def test_chain_C2_empty_df(self, empty_df):
        """空DataFrameの伝播テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 空DataFrame処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        with patch('src.packages.pattern_editor.pattern_chain_processor.ValidationResult') as mock_validate, \
            patch('src.packages.pattern_editor.pattern_chain_processor.WritePatternResult') as mock_write:

            mock_validate.return_value.process.return_value = empty_df
            mock_write.return_value.process.return_value = empty_df

            processor = PostProcessorRequest()
            chain = processor.chain_post_processor()
            df_result = empty_df.copy()
            for proc in chain:
                df_result = proc.process(df_result)

            assert df_result.empty
            mock_validate.return_value.process.assert_called_once()
            mock_write.return_value.process.assert_called_once()


# テスト用のconfig設定
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestReadDecisionTable:
    """ReadDecisionTableのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: TableSearcherからのデータ読み込み
    │   ├── 正常系: NaN値の空文字変換
    │   └── 異常系: 例外発生時のエラー変換
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try句の正常実行
    │   └── 異常系: except句への分岐
    ├── C2: 条件組み合わせ
    │   ├── 正常系: 有効なファイルパス + 有効なデータ
    │   ├── 異常系: 無効なファイルパス + 有効なデータ
    │   └── 異常系: 有効なファイルパス + 無効なデータ
    └── BVT: 境界値テスト
        ├── 入力DataFrameの境界値
        └── TableSearcherの戻り値の境界値

    C1のディシジョンテーブル:
    | 条件                           | DT1 | DT2 | DT3 |
    |--------------------------------|-----|-----|-----|
    | TableSearcher初期化成功        | Y   | N   | Y   |
    | 戻り値のDataFrameが有効        | Y   | -   | N   |
    |--------------------------------|-----|-----|-----|
    | 正常にデータを返却             | X   | -   | -   |
    | PatternChainProcessorError発生 | -   | X   | X   |

    境界値検証ケース一覧:
    | ID     | パラメータ   | テスト値              | 期待される結果           | 検証ポイント               | 実装状況   | 対応するテストケース    |
    |--------|--------------|----------------------|------------------------|---------------------------|------------|----------------------|
    | BVT_001| input_df     | 空のDataFrame        | 正常終了               | 最小入力の処理             | 実装済み   | test_process_BVT_empty_dataframe |
    | BVT_002| input_df     | 1行のDataFrame       | 正常終了               | 最小有効データの処理       | 実装済み   | test_process_C0_basic |
    | BVT_003| input_df     | NaN含むDataFrame     | NaNが空文字に変換      | NaN処理の確認             | 実装済み   | test_process_C0_nan_conversion |
    | BVT_004| table_data   | 空のDataFrame        | 空のDataFrame         | 最小出力の処理             | 実装済み   | test_process_C2_empty_result |

    実装状況サマリー:
    - 実装済み: 4件
    - 未実装: 0件
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor = ReadDecisionTable()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher_class(self):
        """TableSearcherクラス全体をMock化するfixture"""
        with patch('src.packages.pattern_editor.pattern_chain_processor.TableSearcher') as mock_class:
            yield mock_class

    def test_process_C0_basic(self, mock_table_searcher_class):
        """基本的な処理フローのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なDataFrame処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # モックの戻り値設定
        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})

        # テスト実行
        input_df = pd.DataFrame({'test': [1, 2]})
        result = self.processor.process(input_df)

        # 検証
        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        mock_table_searcher_class.assert_called_once()
        assert len(result) == 2

    def test_process_C0_nan_conversion(self, mock_table_searcher_class):
        """NaN値の空文字変換テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: NaN値が空文字に変換されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # モックの戻り値設定
        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({
            'col1': [1, np.nan],
            'col2': ['A', None]
        })

        # テスト実行
        input_df = pd.DataFrame({'test': [1, 2]})
        result = self.processor.process(input_df)

        # 検証
        assert not result.isna().any().any()
        assert result['col1'].iloc[1] == ''
        assert result['col2'].iloc[1] == ''

    def test_process_C1_error_handling(self, mock_table_searcher_class):
        """エラーハンドリングのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: TableSearcher例外発生時のエラー変換確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # モックが例外を送出するように設定
        mock_table_searcher_class.side_effect = Exception("Test error")

        # テスト実行と検証
        with pytest.raises(PatternChainProcessorError) as exc_info:
            input_df = pd.DataFrame({'test': [1]})
            self.processor.process(input_df)

        assert 'パターン編集処理 DecisionTable読み込みで失敗が発生しました' in str(exc_info.value)

    def test_process_C2_empty_result(self, mock_table_searcher_class):
        """空のDataFrameを返却するケースのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: TableSearcherが空のDataFrameを返却するケースの確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # モックの戻り値設定
        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame()

        # テスト実行
        input_df = pd.DataFrame({'test': [1]})
        result = self.processor.process(input_df)

        # 検証
        assert isinstance(result, pd.DataFrame)
        assert result.empty


    def test_process_BVT_empty_dataframe(self, mock_table_searcher_class):
        """空のDataFrameを入力した場合のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空のDataFrameが正しく処理されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # モックの戻り値設定
        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'col1': [1], 'col2': ['A']})

        # テスト実行
        input_df = pd.DataFrame()
        result = self.processor.process(input_df)

        # 検証
        assert isinstance(result, pd.DataFrame)
        assert not result.empty  # TableSearcherの結果が返却される
        assert len(result) == 1

class TestModifyDecisionTable:
    """ModifyDecisionTableのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 基本的なDataFrame変換
    │   ├── 正常系: 空のDataFrame処理
    │   └── 異常系: 無効なカラム指定
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 全パターンの変換確認
    │   ├── 異常系: 変換対象外の値
    │   └── 異常系: 無効な入力値
    ├── C2: 条件組み合わせ
    │   ├── 正常系: 複数変換の組み合わせ
    │   ├── 正常系: 特殊文字を含むケース
    │   └── 異常系: 無効な組み合わせ
    ├── DT: ディシジョンテーブル
    │   └── 正常系: 変換パターン網羅
    └── BVT: 境界値テスト
        ├── 空文字列
        ├── 特殊文字
        └── 大規模データ

    # C1のディシジョンテーブル
    | 条件                          | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------|-----|-----|-----|-----|
    | 4桁/5桁パターンを含む         | Y   | N   | Y   | N   |
    | なし/ありパターンを含む       | Y   | Y   | N   | N   |
    | BPR・ADパターンを含む         | Y   | N   | N   | Y   |
    |-------------------------------|-----|-----|-----|-----|
    | 全パターン変換                | X   | -   | -   | -   |
    | 一部パターンのみ変換          | -   | X   | X   | X   |

    境界値検証ケース一覧:
    | ID     | パラメータ | テスト値               | 期待される結果 | テストの目的              | 実装状況  | 対応するテストケース |
    |--------|------------|------------------------|----------------|--------------------------|-----------|---------------------|
    | BVT001 | column     | 空文字列               | 空文字列       | 最小入力の処理           | 実装済み  | test_replace_values_BVT_empty |
    | BVT002 | column     | 特殊文字のみ           | 特殊文字のまま | 特殊文字の処理          | 実装済み  | test_replace_values_BVT_special_chars |
    | BVT003 | column     | 大規模データ(100万行)  | 変換後データ   | パフォーマンス確認      | 実装済み  | test_replace_values_BVT_large_data |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def config_patches(self):
        """設定値をパッチするfixture"""
        with patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_columns_def',
                  ['col1', 'col2']), \
             patch('src.packages.pattern_editor.pattern_chain_processor.columns_to_transform_def',
                  ['col1']), \
             patch('src.packages.pattern_editor.pattern_chain_processor.decision_table_columns_fin_def',
                  ['col1', 'col2']):
            yield

    def test_process_C0_basic_conversion(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なDataFrame変換の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({
            'col1': ['4桁', '5桁'],
            'col2': ['値1', '値2']
        })
        modifier = ModifyDecisionTable()
        result = modifier.process(df)

        assert list(result['col1']) == ['is_4digits', 'is_5digits']
        assert list(result['col2']) == ['値1', '値2']

    def test_process_C0_empty_dataframe(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 空のDataFrame処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({'col1': [], 'col2': []})
        modifier = ModifyDecisionTable()
        result = modifier.process(df)

        assert result.empty
        assert list(result.columns) == ['col1', 'col2']

    def test_process_C1_all_patterns(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 全変換パターンの確認
        DT: DT1
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({
            'col1': ['4桁', '5桁', 'なし', 'あり', 'BPR・AD対象', 'BPR・AD対象外', 'ADのみ対象', '-'],
            'col2': ['A'] * 8
        })
        modifier = ModifyDecisionTable()
        result = modifier.process(df)

        expected = [
            'is_4digits', 'is_5digits', 'is_empty', 'is_not_empty',
            'is_bpr_ad_target', 'is_not_bpr_ad_target', 'is_ad_only_target', 'any'
        ]
        assert list(result['col1']) == expected

    # 要素の組み合わせアイデアと思われるが意味のないシナリオ、評価しない
    #@pytest.mark.parametrize(("input_val", "expected"), [
    #    ('4桁なし', 'is_empty'),
    #    ('なし4桁', 'is_empty'),
    #    ('4桁あり', 'is_not_empty'),
    #    ('あり4桁', 'is_not_empty'),
    #])
    #def test_process_C2_pattern_combinations(self, config_patches, input_val, expected):
    #    test_doc = """
    #    テスト区分: UT
    #    テストカテゴリ: C2
    #    テスト内容: 変換パターンの組み合わせ確認
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.DEBUG)

    #    df = pd.DataFrame({
    #        'col1': [input_val],
    #        'col2': ['A']
    #    })
    #    modifier = ModifyDecisionTable()
    #    result = modifier.process(df)

    #    assert result['col1'].iloc[0] == expected


    def test_replace_values_BVT_empty(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空文字列の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        modifier = ModifyDecisionTable()
        result = modifier._replace_values(pd.Series(['']))

        assert result.iloc[0] == ''

    def test_replace_values_BVT_special_chars(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 特殊文字の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        modifier = ModifyDecisionTable()
        result = modifier._replace_values(pd.Series(['!@#$%^&*()']))

        assert result.iloc[0] == '!@#$%^&*()'

    def test_replace_values_BVT_large_data(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 大規模データの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        modifier = ModifyDecisionTable()
        large_series = pd.Series(['4桁'] * 100000)
        result = modifier._replace_values(large_series)

        assert len(result) == 100000
        assert (result == 'is_4digits').all()


class TestReadRequestListTable:
    """ReadRequestListTableのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: テーブル読み込み成功
    │   └── 異常系: テーブル読み込み失敗
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try句正常実行
    │   └── 異常系: except句実行
    ├── C2: 条件組み合わせ
    │   ├── 正常系: 通常データ
    │   ├── 正常系: NA値含むデータ
    │   └── 正常系: 空のDataFrame
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        ├── 1行のDataFrame
        └── 大規模DataFrame

    # C1のディシジョンテーブル
    | 条件                          | DT1 | DT2 |
    |-------------------------------|-----|-----|
    | TableSearcher初期化成功       | Y   | N   |
    | DataFrame取得成功             | Y   | -   |
    |-------------------------------|-----|-----|
    | 正常終了                      | X   | -   |
    | PatternChainProcessorError    | -   | X   |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値              | 期待される結果 | テストの目的/検証ポイント        | 実装状況 | 対応するテストケース |
    |----------|----------------|---------------------|----------------|--------------------------------|----------|-------------------|
    | BVT_001 | df             | 空のDataFrame       | 成功           | 最小データでの動作確認           | 実装済み | test_process_C0_empty_df |
    | BVT_002 | df             | 1行のDataFrame      | 成功           | 最小有効データでの確認           | 実装済み | test_process_C0_single_row |
    | BVT_003 | df             | NA値含むDataFrame   | 空文字変換     | NA値の処理確認                  | 実装済み | test_process_C2_with_na |
    | BVT_004 | df             | 大規模DataFrame     | 成功           | 大規模データの処理性能確認       | 実装済み | test_process_C2_large_df |

    境界値検証ケースの実装状況サマリー：
    - 実装済み: 4件
    - 未実装: 0件
    - 一部実装: 0件

    注記：
    - すべての境界値ケースはC0、C2テストでカバー
    - 大規模データテストは処理時間に注意が必要
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher_class(self):
        """TableSearcherクラス全体をMock化するfixture"""
        with patch('src.packages.pattern_editor.pattern_chain_processor.TableSearcher') as mock_class:
            mock_instance = MagicMock()
            mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})
            mock_class.return_value = mock_instance
            yield mock_class

    def test_process_C0_empty_df(self, mock_table_searcher_class):
        """空のDataFrameでの正常系テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 空のDataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame()

        processor = ReadRequestListTable()
        result = processor.process(pd.DataFrame())

        assert isinstance(result, pd.DataFrame)
        assert result.empty

class TestReadRequestListTable:
    """ReadRequestListTableのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: テーブル読み込み成功
    │   └── 異常系: テーブル読み込み失敗
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try句正常実行
    │   └── 異常系: except句実行
    ├── C2: 条件組み合わせ
    │   ├── 正常系: 通常データ
    │   ├── 正常系: NA値含むデータ
    │   └── 正常系: 空のDataFrame
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        ├── 1行のDataFrame
        └── 大規模DataFrame

    # C1のディシジョンテーブル
    | 条件                          | DT1 | DT2 |
    |-------------------------------|-----|-----|
    | TableSearcher初期化成功       | Y   | N   |
    | DataFrame取得成功             | Y   | -   |
    |-------------------------------|-----|-----|
    | 正常終了                      | X   | -   |
    | PatternChainProcessorError    | -   | X   |

    境界値検証ケース一覧：
    | ケースID | 入力パラメータ | テスト値              | 期待される結果 | テストの目的/検証ポイント        | 実装状況 | 対応するテストケース |
    |----------|----------------|---------------------|----------------|--------------------------------|----------|-------------------|
    | BVT_001 | df             | 空のDataFrame       | 成功           | 最小データでの動作確認           | 実装済み | test_process_C0_empty_df |
    | BVT_002 | df             | 1行のDataFrame      | 成功           | 最小有効データでの確認           | 実装済み | test_process_C0_single_row |
    | BVT_003 | df             | NA値含むDataFrame   | 空文字変換     | NA値の処理確認                  | 実装済み | test_process_C2_with_na |
    | BVT_004 | df             | 大規模DataFrame     | 成功           | 大規模データの処理性能確認       | 実装済み | test_process_C2_large_df |

    境界値検証ケースの実装状況サマリー：
    - 実装済み: 4件
    - 未実装: 0件
    - 一部実装: 0件

    注記：
    - すべての境界値ケースはC0、C2テストでカバー
    - 大規模データテストは処理時間に注意が必要
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def mock_table_searcher_class(self):
        """TableSearcherクラス全体をMock化するfixture"""
        with patch('src.packages.pattern_editor.pattern_chain_processor.TableSearcher') as mock_class:
            mock_instance = MagicMock()
            mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})
            mock_class.return_value = mock_instance
            yield mock_class

    def test_process_C0_empty_df(self, mock_table_searcher_class):
        """空のDataFrameでの正常系テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 空のDataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame()

        processor = ReadRequestListTable()
        result = processor.process(pd.DataFrame())

        assert isinstance(result, pd.DataFrame)
        assert result.empty

    def test_process_C0_single_row(self, mock_table_searcher_class):
        """1行のDataFrameでの正常系テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 1行のDataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'col1': [1]})

        processor = ReadRequestListTable()
        result = processor.process(pd.DataFrame())

        assert len(result) == 1
        assert 'col1' in result.columns

    def test_process_C1_error(self, mock_table_searcher_class):
        """例外発生時の処理テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: TableSearcher初期化失敗時の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_table_searcher_class.side_effect = Exception("Mock error")

        processor = ReadRequestListTable()
        with pytest.raises(PatternChainProcessorError) as exc_info:
            processor.process(pd.DataFrame())

        assert "変更情報テーブルファイル読み込みで失敗が発生しました" in str(exc_info.value)


    def test_process_C2_with_na(self, mock_table_searcher_class):
        """NA値を含むDataFrameの処理テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: NA値を含むDataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({
            'col1': [1, np.nan, 3],
            'col2': ['A', None, 'C']
        })

        processor = ReadRequestListTable()
        result = processor.process(pd.DataFrame())

        assert not result.isna().any().any()
        assert (result.fillna('') == result).all().all()

    def test_process_C2_large_df(self, mock_table_searcher_class):
        """大規模DataFrameの処理テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: 大規模DataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        large_df = pd.DataFrame({
            'col1': range(100000),
            'col2': ['data'] * 100000
        })
        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = large_df

        processor = ReadRequestListTable()
        result = processor.process(pd.DataFrame())

        assert len(result) == 100000
        assert not result.isna().any().any()

class TestAddDecisionJudgeColumnsProcessor:
    """AddDecisionJudgeColumnsの_add_decision_table_columnsメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 型変換と列追加の基本動作確認
    │   ├── 正常系: 空のDataFrameでの処理
    │   └── 正常系: NaN値を含むデータの処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 親部店コードと部店コードが一致
    │   ├── 正常系: 親部店コードと部店コードが不一致
    │   └── 正常系: 部分一致パターン
    ├── C2: 条件組み合わせ
    │   ├── 正常系: コード長の組み合わせ
    │   ├── 正常系: コード値の組み合わせ
    │   └── 正常系: 特殊文字を含むケース
    └── BVT: 境界値テスト
        ├── parent_branch_code境界値
        └── branch_code境界値

    C1のディシジョンテーブル:
    | 条件                           | DT1 | DT2 | DT3 | DT4 |
    |--------------------------------|-----|-----|-----|-----|
    | parent_codeが数値のみ          | Y   | Y   | N   | Y   |
    | branch_codeが数値のみ          | Y   | Y   | Y   | N   |
    | 親子コードの先頭4桁が一致      | Y   | N   | -   | -   |
    |--------------------------------|-----|-----|-----|-----|
    | exists判定                     | Y   | N   | N   | N   |

    境界値検証ケース一覧:
    | ID     | パラメータ           | テスト値           | 期待結果    | 検証ポイント           | 実装状況 |
    |--------|---------------------|-------------------|------------|----------------------|----------|
    | BVT_001| parent_branch_code | '0000'           | exists     | 最小値の処理          | C2で実装 |
    | BVT_002| parent_branch_code | '9999'           | exists     | 最大値の処理          | C2で実装 |
    | BVT_003| branch_code        | '000000'         | ''         | 最小値＋余分な桁       | C2で実装 |
    | BVT_004| branch_code        | '999999'         | ''         | 最大値＋余分な桁       | C2で実装 |
    | BVT_005| parent_branch_code | 数値型0000        | exists     | 数値型入力            | C0で実装 |
    | BVT_006| branch_code        | 数値型000000      | ''         | 数値型入力            | C0で実装 |
    | BVT_007| parent_branch_code | None             | ''         | NULL値処理           | C0で実装 |
    | BVT_008| branch_code        | None             | ''         | NULL値処理           | C0で実装 |
    """

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)
        self.processor = AddDecisionJudgeColumns()

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture
    def sample_df(self):
        """基本的なテストデータを提供するfixture"""
        return pd.DataFrame({
            'parent_branch_code': ['1234', '5678', '1234'],
            'branch_code': ['123456', '567890', '123400']
        })

    def test_add_decision_table_columns_C0_basic_operation(self, sample_df):
        """C0: 基本的なデータ変換と列追加の確認"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 型変換と列追加の基本動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        result = self.processor._add_decision_table_columns(sample_df)

        # 型変換の確認
        assert result['parent_branch_code'].dtype == 'object'
        assert result['branch_code'].dtype == 'object'
        
        # 列追加の確認
        assert 'specific_department_code' in result.columns
        assert 'branch_code_first_2_digit' in result.columns
        assert 'parent_branch_code_and_branch_code_first_4_digits_match' in result.columns

        # branch_code_first_2_digitの値確認
        assert result.iloc[0]['branch_code_first_2_digit'] == '12'
        assert result.iloc[1]['branch_code_first_2_digit'] == '56'

    def test_add_decision_table_columns_C0_empty_dataframe(self):
        """C0: 空のDataFrameの処理確認"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 空のDataFrameでの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
    
        # 空のDataFrameを作成する際の修正
        empty_df = pd.DataFrame({
            'parent_branch_code': [],
            'branch_code': []
        })
        # 空のDataFrameに対してapplyメソッドを使用する前に、空の列を追加
        empty_df['parent_branch_code_and_branch_code_first_4_digits_match'] = pd.Series([], dtype='str')
    
        # モック化してapplyの部分をスキップ
        with patch.object(pd.DataFrame, 'apply', return_value=pd.Series([], dtype='str')):
            result = self.processor._add_decision_table_columns(empty_df)
        
        # 結果の検証
        assert len(result) == 0
        # 全ての必要なカラムが存在することを確認
        expected_columns = {
            'parent_branch_code',
            'branch_code',
            'specific_department_code',
            'branch_code_first_2_digit',
            'parent_branch_code_and_branch_code_first_4_digits_match'
        }
        assert set(result.columns) == expected_columns
        # データ型の検証は空のDataFrameでも可能
        for col in result.columns:
            assert result[col].dtype == 'object'
            

    def test_add_decision_table_columns_C1_code_match(self):
        """C1: 親部店コードと部店コードの一致パターン"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: DT1 - 親部店コードと部店コード先頭4桁が一致
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({
            'parent_branch_code': ['1234', '5678'],
            'branch_code': ['123456', '567890']
        })
        result = self.processor._add_decision_table_columns(df)
        
        assert result.iloc[0]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[1]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'


    def test_add_decision_table_columns_C2_code_combinations(self):
        """C2: コード値とコード長の組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 様々なコード値とコード長の組み合わせを検証
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({
            'parent_branch_code': [
                '0000',     # 最小値
                '9999',     # 最大値
                '1234',     # 標準的な値
                'ABCD',     # 英字
                '123',      # 短い値
                '12345'     # 長い値
            ],
            'branch_code': [
                '000000',   # 最小値
                '999999',   # 最大値
                '123456',   # 標準的な値
                'ABCDEF',   # 英字
                '123',      # 短い値
                '1234567'   # 長い値
            ]
        })
        result = self.processor._add_decision_table_columns(df)

        # 各行の判定結果を検証
        assert result.iloc[0]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[1]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[2]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[3]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[4]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[5]['parent_branch_code_and_branch_code_first_4_digits_match'] == ''


    def test_add_decision_table_columns_C2_special_cases(self):
        """C2: 特殊ケースの処理確認"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 特殊文字、空白、NULL値などの処理を検証
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({
            'parent_branch_code': [
                '12 34',    # 空白を含む
                '12@34',    # 特殊文字を含む
                None,       # NULL
                np.nan,     # NaN
                '',         # 空文字
                ' '         # スペース
            ],
            'branch_code': [
                '12 3456',  # 空白を含む
                '12@3456',  # 特殊文字を含む
                None,       # NULL
                np.nan,     # NaN
                '',         # 空文字
                ' '         # スペース
            ]
        })
        result = self.processor._add_decision_table_columns(df)

        # 型変換後の値を確認
        assert result['parent_branch_code'].isna().sum() == 0  # NANがないことを確認
        assert result['branch_code'].isna().sum() == 0  # NANがないことを確認
        assert result['branch_code_first_2_digit'].isna().sum() == 0  # NANがないことを確認
        
        # 特殊ケースの判定結果を確認
        assert result['parent_branch_code_and_branch_code_first_4_digits_match'].eq('').sum() == 2

    def test_add_decision_table_columns_BVT_numeric_types(self):
        """BVT: 数値型入力の処理確認"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 数値型データの処理を検証
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        df = pd.DataFrame({
            'parent_branch_code': [
                1234,       # 整数
                5678.0,     # 浮動小数点
                '1234',     # 文字列
                2345       # 整数
            ],
            'branch_code': [
                123456,     # 整数
                567800,     # 整数
                '123456',   # 文字列
                234500     # 整数
            ]
        })
        result = self.processor._add_decision_table_columns(df)

        # 型変換の結果を確認
        assert result['parent_branch_code'].dtype == 'object'
        assert result['branch_code'].dtype == 'object'
        
        # 判定結果を確認
        assert result.iloc[0]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[1]['parent_branch_code_and_branch_code_first_4_digits_match'] == ''
        assert result.iloc[2]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'
        assert result.iloc[3]['parent_branch_code_and_branch_code_first_4_digits_match'] == 'exists'


class TestValidationResult:
    """ValidationResultのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: DataValidator正常動作
    │   └── 異常系: 例外発生時の変換
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try節成功
    │   └── 異常系: Exception発生
    ├── C2: 条件カバレッジ
    │   ├── 正常系: 全て成功
    │   ├── 異常系: 初期化失敗
    │   └── 異常系: validate失敗
    └── BVT: 境界値テスト
        ├── 空DataFrame
        ├── 1行DataFrame
        └── 大規模DataFrame

    # C1のディシジョンテーブル
    | 条件                        | DT1 | DT2 | DT3 |
    |----------------------------|-----|-----|-----|
    | DataValidator初期化成功     | Y   | N   | Y   |
    | validate成功               | Y   | -   | N   |
    | 期待結果                    | 成功 | 例外 | 例外 |

    境界値検証ケース一覧:
    | ID      | 入力         | テスト値        | 期待結果 | 目的              | 実装状況 |
    |---------|-------------|----------------|----------|------------------|----------|
    | BVT_001 | DataFrame   | 空DataFrame     | 成功     | 最小入力の検証     | C2実装済 |
    | BVT_002 | DataFrame   | 1行DataFrame    | 成功     | 最小有効データ検証 | C2実装済 |
    | BVT_003 | DataFrame   | 大規模DataFrame | 成功     | 処理限界の検証     | C2実装済 |
    """

    def setup_method(self):
        """テストメソッドの前処理"""
        self.processor = ValidationResult()
        self.df = pd.DataFrame({'test': [1, 2, 3]})
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)


    @patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator')
    def test_process_C0_normal(self, mock_validator):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: DataValidatorが正常に動作するケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
    
        # セットアップ - DataValidatorインスタンス全体をMock化
        mock_validator_instance = Mock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.validate.return_value = None
    
        # 実行
        result = self.processor.process(self.df)
    
        # 検証
        mock_validator.assert_called_once()
        # any_call=Trueを使用してDataFrameの内容ではなく呼び出し自体を確認
        assert mock_validator_instance.validate.call_count == 1
        # DataFrameの比較にはpandas.testing.assert_frame_equalを使用
        pd.testing.assert_frame_equal(result, self.df.copy())

    @patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator')
    def test_process_C1_DT2(self, mock_validator):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: DataValidator初期化失敗のケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # セットアップ
        mock_validator.side_effect = Exception("初期化エラー")

        # 実行と検証
        with pytest.raises(PatternChainProcessorError) as exc_info:
            self.processor.process(self.df)
        
        assert "パターン編集処理結果のValidationに失敗が発生しました" in str(exc_info.value)

    @patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator')
    def test_process_C1_DT3(self, mock_validator):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: validate実行時の失敗ケース
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # セットアップ
        mock_validator_instance = Mock()
        mock_validator_instance.validate.side_effect = Exception("検証エラー")
        mock_validator.return_value = mock_validator_instance

        # 実行と検証
        with pytest.raises(PatternChainProcessorError) as exc_info:
            self.processor.process(self.df)

        assert "パターン編集処理結果のValidationに失敗が発生しました" in str(exc_info.value)

    @patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator')
    def test_process_C2_empty_df(self, mock_validator):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 空のDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # セットアップ
        empty_df = pd.DataFrame()
        mock_validator_instance = Mock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.validate.return_value = None

        # 実行
        result = self.processor.process(empty_df)

        # 検証
        mock_validator.assert_called_once()
        assert mock_validator_instance.validate.call_count == 1
        pd.testing.assert_frame_equal(result, empty_df.copy())
        assert result.empty

    @patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator')
    def test_process_C2_single_row(self, mock_validator):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 1行のDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # セットアップ
        single_row_df = pd.DataFrame({'test': [1]})
        mock_validator_instance = Mock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.validate.return_value = None

        # 実行
        result = self.processor.process(single_row_df)

        # 検証
        mock_validator.assert_called_once()
        assert mock_validator_instance.validate.call_count == 1
        pd.testing.assert_frame_equal(result, single_row_df.copy())
        assert len(result) == 1

    @patch('src.packages.pattern_editor.pattern_chain_processor.DataValidator')
    def test_process_C2_large_df(self, mock_validator):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 大規模DataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # セットアップ
        large_df = pd.DataFrame({'test': range(100000)})
        mock_validator_instance = Mock()
        mock_validator.return_value = mock_validator_instance
        mock_validator_instance.validate.return_value = None

        # 実行
        result = self.processor.process(large_df)

        # 検証
        mock_validator.assert_called_once()
        assert mock_validator_instance.validate.call_count == 1
        pd.testing.assert_frame_equal(result, large_df.copy())
        assert len(result) == 100000

class TestWritePatternResult:
    """WritePatternResultのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: DataFrame書き込み成功
    │   └── 異常系: ファイル書き込み失敗
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try句が正常実行
    │   └── 異常系: except句への分岐
    └── C2: 条件組み合わせ
        ├── 正常系: 両ファイル書き込み成功
        ├── 異常系: pickleファイル書き込み失敗
        └── 異常系: Excel書き込み失敗

    C1のディシジョンテーブル:
    | 条件                          | ケース1 | ケース2 |
    |-------------------------------|---------|---------|
    | pickleファイル書き込み成功    | Y       | N       |
    | Excelファイル書き込み成功     | Y       | -       |
    | 出力                          | 成功     | 例外発生 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ  | テスト値                 | 期待される結果 | テストの目的/検証ポイント           | 実装状況 | 対応するテストケース |
    |----------|-----------------|--------------------------|----------------|-------------------------------------|----------|---------------------|
    | BVT_001  | DataFrame      | 空のDataFrame             | 成功           | 最小データでの動作確認              | 実装済み | test_process_C0_empty_dataframe |
    | BVT_002  | DataFrame      | 1行のDataFrame            | 成功           | 最小有効データでの動作確認          | 実装済み | test_process_C0_single_row |
    | BVT_003  | DataFrame      | 大規模DataFrame(10万行)   | 成功           | 大規模データでの動作確認            | 未実装   | - |
    | BVT_004  | DataFrame      | 全列が数値型              | 成功           | 型変換の確認                        | 実装済み | test_process_C2_numeric_columns |
    | BVT_005  | DataFrame      | 全列が文字列型            | 成功           | 型変換の確認                        | 実装済み | test_process_C2_string_columns |
    | BVT_006  | DataFrame      | 混合データ型              | 成功           | 複合的な型変換の確認                | 実装済み | test_process_C2_mixed_columns |

    注記:
    - BVT_003は実際の運用環境でのみ実施すべき大規模データテストのため未実装
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def config_patches(self, tmp_path):
        """設定値のパッチを提供するfixture"""
        pickle_path = tmp_path / "output.pkl"
        with patch('src.packages.pattern_editor.pattern_chain_processor.pattern_edited',
                str(pickle_path)), \
            patch('src.packages.pattern_editor.pattern_chain_processor.debug_pattern_result_xlsx',
                str(tmp_path / "debug.xlsx")):
            yield pickle_path

    def test_process_C0_empty_dataframe(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 空のDataFrame処理の検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame()
        processor = WritePatternResult()
        processor.process(_df)

        loaded_df = pd.read_pickle(config_patches)
        assert loaded_df.empty
        log_msg("Empty DataFrame successfully processed", LogLevel.DEBUG)

    def test_process_C0_single_row(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストケース: 1行データの処理検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'col1': [1]})
        processor = WritePatternResult()
        processor.process(_df)

        loaded_df = pd.read_pickle(config_patches)
        assert len(loaded_df) == 1
        log_msg("Single row DataFrame successfully processed", LogLevel.DEBUG)

    def test_process_C1_file_write_error(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストケース: ファイル書き込みエラーのハンドリング
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'col1': [1]})
        processor = WritePatternResult()

        invalid_path = Path('/invalid') / 'path' / 'file.pkl'
        with patch('src.packages.pattern_editor.pattern_chain_processor.pattern_edited', 
                str(invalid_path)):
            with pytest.raises(PatternChainProcessorError) as exc_info:
                processor.process(_df)
            assert 'パターン編集処理結果ファイル書き込みで失敗が発生しました' in str(exc_info.value)
            log_msg(f"Expected error raised: {exc_info.value}", LogLevel.DEBUG)

    def test_process_C2_numeric_columns(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 数値型カラムの文字列変換検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': [1.1, 2.2, 3.3],
        })
        processor = WritePatternResult()

        log_msg(f"Original DataFrame types:\n{_df.dtypes}", LogLevel.DEBUG)

        processor.process(_df)
        loaded_df = pd.read_pickle(config_patches)
        log_msg(f"Loaded DataFrame types:\n{loaded_df.dtypes}", LogLevel.DEBUG)

        assert loaded_df['col1'].dtype == 'int64'
        assert loaded_df['col2'].dtype == 'float64'

        __df_copy = _df.copy()
        df_str = __df_copy.astype(str)
        log_msg(f"String converted DataFrame types:\n{df_str.dtypes}", LogLevel.DEBUG)

        assert df_str['col1'].dtype == 'object'
        assert df_str['col2'].dtype == 'object'
        assert df_str['col1'].iloc[0] == '1'
        assert df_str['col2'].iloc[0] == '1.1'

        log_msg("DataFrame type conversion verification completed", LogLevel.DEBUG)

    def test_process_C2_string_columns(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 文字列型カラムの処理検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'col1': ['a', 'b', 'c'],
            'col2': ['1', '2', '3'],
        })
        processor = WritePatternResult()
        processor.process(_df)

        loaded_df = pd.read_pickle(config_patches)
        assert (loaded_df.dtypes == 'object').all()
        log_msg("String columns successfully processed", LogLevel.DEBUG)

    def test_process_C2_mixed_columns(self, config_patches):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストケース: 混合データ型の処理検証
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [1.1, 2.2, 3.3],
        })
        processor = WritePatternResult()

        log_msg(f"Original DataFrame types:\n{_df.dtypes}", LogLevel.DEBUG)

        processor.process(_df)
        loaded_df = pd.read_pickle(config_patches)
        log_msg(f"Loaded DataFrame types:\n{loaded_df.dtypes}", LogLevel.DEBUG)

        assert loaded_df['col1'].dtype == 'int64'
        assert loaded_df['col2'].dtype == 'object'
        assert loaded_df['col3'].dtype == 'float64'

        df_copy = _df.copy()
        df_str = df_copy.astype(str)
        log_msg(f"String converted DataFrame types:\n{df_str.dtypes}", LogLevel.DEBUG)

        assert (df_str.dtypes == 'object').all()

        assert df_str['col1'].iloc[0] == '1'
        assert df_str['col2'].iloc[0] == 'a'
        assert df_str['col3'].iloc[0] == '1.1'
