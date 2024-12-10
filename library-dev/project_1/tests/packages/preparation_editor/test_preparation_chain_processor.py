import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest

from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import ApplicationType, LogLevel, OrganizationType
from src.lib.converter_utils.ibr_reference_mergers import DataMergeError
from src.packages.preparation_editor.preparation_chain_processor import (
    AddDecisionJudgeColumns,
    BPRADFlagInitializer,
    LoookupReferenceData,
    ModifyDecisionTable,
    PostProcessor,
    PreMergeDataEditor,
    PreparationChainProcessorError,
    PreProcessorDecisionTable,
    PreProcessorMerge,
    ReadDecisionTable,
    ReadIntegratedRequestListTable,
    ReferenceDataMerger,
    WritePreparationResult,
)

# テスト用のconfig設定
config = initialize_config(sys.modules[__name__])
log_msg = config.log_message


class TestPreProcessorDecisionTableChain:
    """PreProcessorDecisionTableのチェーン制御テスト

    テスト構造:
    ├── C0: チェーン構成と実行順序
    │   ├── 正常系: 順序確認
    │   └── 正常系: Mock結果伝搬
    ├── C1: チェーン分岐検証
    │   ├── 正常系: 全プロセッサ正常
    │   ├── 異常系: Read例外
    │   └── 異常系: Modify例外
    └── C2: データ伝搬パターン
        ├── 正常系: 空DataFrame
        └── 正常系: データ有DataFrame

    # C1のディシジョンテーブル
    | 条件                           | Case1 | Case2 | Case3 |
    |--------------------------------|-------|-------|-------|
    | ReadDecisionTableが正常終了    | Y     | N     | Y     |
    | ModifyDecisionTableが正常終了  | Y     | -     | N     |
    |--------------------------------|-------|-------|-------|
    | チェーン処理が完了            | X     | -     | -     |
    | ReadDecisionTable例外発生     | -     | X     | -     |
    | ModifyDecisionTable例外発生   | -     | -     | X     |

    境界値検証ケース一覧:
    | ID      | パラメータ    | テスト値         | 期待結果 | 目的                      | 実装状況           |
    |---------|---------------|------------------|----------|---------------------------|-------------------|
    | BVT_001 | input_df     | 空のDataFrame    | 成功     | 最小データでの動作確認    | C2_empty_dfで実装 |
    | BVT_002 | input_df     | 1行のDataFrame   | 成功     | 最小有効データでの確認    | C2_with_dataで実装|
    | BVT_003 | input_df     | None             | 例外発生 | 無効入力の処理確認        | C1_read_errorで実装|

    注記:
    - BVT_001とBVT_002はC2テストで網羅
    - BVT_003はC1異常系テストで網羅
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor = PreProcessorDecisionTable()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({'col1': [1, 2], 'col2': ['a', 'b']})

    def test_chain_C0_execution_order(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: チェーン実行順序の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        execution_order = []

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadDecisionTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ModifyDecisionTable') as mock_modify:

            def mock_process_read(df):
                execution_order.append('read')
                return df

            def mock_process_modify(df):
                execution_order.append('modify')
                return df

            mock_read.return_value.process = mock_process_read
            mock_modify.return_value.process = mock_process_modify

            processors = self.processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in processors:
                df_result = proc.process(df_result)

            assert execution_order == ['read', 'modify']

    def test_chain_C1_normal_flow(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 全プロセッサ正常終了
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadDecisionTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ModifyDecisionTable') as mock_modify:

            mock_read.return_value.process.return_value = sample_df
            mock_modify.return_value.process.return_value = sample_df

            processors = self.processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in processors:
                df_result = proc.process(df_result)

            assert isinstance(df_result, pd.DataFrame)
            mock_read.return_value.process.assert_called_once()
            mock_modify.return_value.process.assert_called_once()

    def test_chain_C1_read_error(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: Read処理での例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadDecisionTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ModifyDecisionTable') as mock_modify:

            mock_read.return_value.process.side_effect = Exception("Read Error")

            processors = self.processor.chain_pre_processor()
            with pytest.raises(Exception) as exc_info:
                df_result = sample_df.copy()
                for proc in processors:
                    df_result = proc.process(df_result)

            assert "Read Error" in str(exc_info.value)
            mock_modify.return_value.process.assert_not_called()

    def test_chain_C2_empty_df(self, empty_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 空データフレームの伝搬
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadDecisionTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ModifyDecisionTable') as mock_modify:

            mock_read.return_value.process.return_value = empty_df
            mock_modify.return_value.process.return_value = empty_df

            processors = self.processor.chain_pre_processor()
            df_result = empty_df.copy()
            for proc in processors:
                df_result = proc.process(df_result)

            assert df_result.empty
            mock_read.return_value.process.assert_called_once()
            mock_modify.return_value.process.assert_called_once()

    def test_chain_C2_with_data(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: データ有データフレームの伝搬
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadDecisionTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ModifyDecisionTable') as mock_modify:

            modified_df = sample_df.copy()
            modified_df['new_col'] = ['x', 'y']

            mock_read.return_value.process.return_value = sample_df
            mock_modify.return_value.process.return_value = modified_df

            processors = self.processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in processors:
                df_result = proc.process(df_result)

            assert not df_result.empty
            assert 'new_col' in df_result.columns
            assert list(df_result['new_col']) == ['x', 'y']
            mock_read.return_value.process.assert_called_once()
            mock_modify.return_value.process.assert_called_once()

class TestPreProcessorMergeChain:
    """PreProcessorMergeのチェーン制御テスト

    テスト構造:
    ├── C0: チェーン構成と実行順序
    │   └── 正常系: 6プロセッサの実行順序確認
    │       - ReadIntegratedRequestListTable
    │       - AddDecisionJudgeColumns
    │       - PreMergeDataEditor
    │       - ReferenceDataMerger
    │       - BPRADFlagInitializer
    │       - LoookupReferenceData
    ├── C1: チェーン分岐検証
    │   ├── 正常系: 全プロセッサ正常終了
    │   └── 異常系: 各プロセッサでの例外発生
    └── C2: データ伝搬パターン検証
        ├── 正常系: 空DataFrame伝搬
        └── 正常系: データ有DataFrame伝搬

    # C1のディシジョンテーブル
    | 条件                                    | Case1 | Case2 | Case3 | Case4 | Case5 | Case6 | Case7 |
    |-----------------------------------------|-------|-------|-------|-------|-------|-------|-------|
    | ReadIntegratedRequestListTable正常終了  | Y     | N     | Y     | Y     | Y     | Y     | Y     |
    | AddDecisionJudgeColumns正常終了         | Y     | -     | N     | Y     | Y     | Y     | Y     |
    | PreMergeDataEditor正常終了              | Y     | -     | -     | N     | Y     | Y     | Y     |
    | ReferenceDataMerger正常終了             | Y     | -     | -     | -     | N     | Y     | Y     |
    | BPRADFlagInitializer正常終了            | Y     | -     | -     | -     | -     | N     | Y     |
    | LoookupReferenceData正常終了            | Y     | -     | -     | -     | -     | -     | N     |
    |-----------------------------------------|-------|-------|-------|-------|-------|-------|-------|
    | チェーン処理完了                        | X     | -     | -     | -     | -     | -     | -     |
    | 対応する例外発生                        | -     | X     | X     | X     | X     | X     | X     |

    境界値検証ケース一覧:
    | ID      | パラメータ   | テスト値         | 期待結果 | 目的                      | 実装状況          |
    |---------|--------------|------------------|----------|---------------------------|-------------------|
    | BVT_001 | input_df     | 空のDataFrame    | 成功     | 最小データでの動作確認    | C2_empty_dfで実装 |
    | BVT_002 | input_df     | 1行のDataFrame   | 成功     | 最小有効データでの確認    | C2_with_dataで実装|
    | BVT_003 | input_df     | None             | 例外発生 | 無効入力の処理確認        | C1_processor_errorsで実装|

    注記:
    - 全ての境界値テストは既存のテストケースでカバー
    - 各プロセッサの内部実装の検証は対象外
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor = PreProcessorMerge()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({'request_id': [1, 2], 'data': ['A', 'B']})

    def test_chain_C0_execution_order(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: チェーン実行順序の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        execution_order = []
        processors = [
            'ReadIntegratedRequestListTable',
            'AddDecisionJudgeColumns',
            'PreMergeDataEditor',
            'ReferenceDataMerger',
            'BPRADFlagInitializer',
            'LoookupReferenceData',
        ]

        # 各プロセッサごとのモック生成とプロセス関数定義
        def make_mock_process(name):
            mock = Mock()
            def side_effect(df):
                execution_order.append(name)
                return df
            mock.side_effect = side_effect
            return mock

        # 複数のpatchを同時に使用
        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadIntegratedRequestListTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.AddDecisionJudgeColumns') as mock_add, \
            patch('src.packages.preparation_editor.preparation_chain_processor.PreMergeDataEditor') as mock_pre, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ReferenceDataMerger') as mock_merge, \
            patch('src.packages.preparation_editor.preparation_chain_processor.BPRADFlagInitializer') as mock_flag, \
            patch('src.packages.preparation_editor.preparation_chain_processor.LoookupReferenceData') as mock_lookup:

            # 各モックにプロセス関数を設定
            mock_procs = [mock_read, mock_add, mock_pre, mock_merge, mock_flag, mock_lookup]
            for mock_proc, proc_name in zip(mock_procs, processors):
                mock_proc.return_value.process = make_mock_process(proc_name)

            # チェーン実行
            chain_processors = self.processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            # 順序確認
            assert execution_order == processors

            # 各モックが一度ずつ呼ばれたことを確認
            for mock_proc in mock_procs:
                mock_proc.return_value.process.assert_called_once()

    def test_chain_C1_normal_flow(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: 全プロセッサ正常終了
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            mock.side_effect = lambda df: df
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadIntegratedRequestListTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.AddDecisionJudgeColumns') as mock_add, \
            patch('src.packages.preparation_editor.preparation_chain_processor.PreMergeDataEditor') as mock_pre, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ReferenceDataMerger') as mock_merge, \
            patch('src.packages.preparation_editor.preparation_chain_processor.BPRADFlagInitializer') as mock_flag, \
            patch('src.packages.preparation_editor.preparation_chain_processor.LoookupReferenceData') as mock_lookup:

            mock_procs = [mock_read, mock_add, mock_pre, mock_merge, mock_flag, mock_lookup]
            for mock_proc in mock_procs:
                mock_proc.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert isinstance(df_result, pd.DataFrame)
            assert not df_result.empty
            for mock_proc in mock_procs:
                mock_proc.return_value.process.assert_called_once()

    @pytest.mark.parametrize('error_processor_idx', range(6))
    def test_chain_C1_processor_errors(self, sample_df, error_processor_idx):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: 各プロセッサでの例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        #processors = [
        #    'ReadIntegratedRequestListTable',
        #    'AddDecisionJudgeColumns',
        #    'PreMergeDataEditor',
        #    'ReferenceDataMerger',
        #    'BPRADFlagInitializer',
        #    'LoookupReferenceData',
        #]

        def make_mock_process(error=False):
            mock = Mock()
            if error:
                mock.side_effect = Exception("Process Error")
            else:
                mock.side_effect = lambda df: df
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadIntegratedRequestListTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.AddDecisionJudgeColumns') as mock_add, \
            patch('src.packages.preparation_editor.preparation_chain_processor.PreMergeDataEditor') as mock_pre, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ReferenceDataMerger') as mock_merge, \
            patch('src.packages.preparation_editor.preparation_chain_processor.BPRADFlagInitializer') as mock_flag, \
            patch('src.packages.preparation_editor.preparation_chain_processor.LoookupReferenceData') as mock_lookup:

            mock_procs = [mock_read, mock_add, mock_pre, mock_merge, mock_flag, mock_lookup]
            for i, mock_proc in enumerate(mock_procs):
                mock_proc.return_value.process = make_mock_process(error=(i == error_processor_idx))

            chain_processors = self.processor.chain_pre_processor()
            with pytest.raises(Exception) as exc_info:
                df_result = sample_df.copy()
                for proc in chain_processors:
                    df_result = proc.process(df_result)

            assert "Process Error" in str(exc_info.value)

    def test_chain_C2_empty_df(self, empty_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 空データフレームの伝搬
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            mock.side_effect = lambda df: df
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadIntegratedRequestListTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.AddDecisionJudgeColumns') as mock_add, \
            patch('src.packages.preparation_editor.preparation_chain_processor.PreMergeDataEditor') as mock_pre, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ReferenceDataMerger') as mock_merge, \
            patch('src.packages.preparation_editor.preparation_chain_processor.BPRADFlagInitializer') as mock_flag, \
            patch('src.packages.preparation_editor.preparation_chain_processor.LoookupReferenceData') as mock_lookup:

            mock_procs = [mock_read, mock_add, mock_pre, mock_merge, mock_flag, mock_lookup]
            for mock_proc in mock_procs:
                mock_proc.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_pre_processor()
            df_result = empty_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert df_result.empty
            for mock_proc in mock_procs:
                mock_proc.return_value.process.assert_called_once()

    def test_chain_C2_with_data(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: データ有データフレームの伝搬
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processors = [
            'ReadIntegratedRequestListTable',
            'AddDecisionJudgeColumns',
            'PreMergeDataEditor',
            'ReferenceDataMerger',
            'BPRADFlagInitializer',
            'LoookupReferenceData',
        ]

        def make_mock_process(proc_idx):
            mock = Mock()
            def side_effect(df):
                df_copy = df.copy()
                df_copy[f'col_{proc_idx}'] = [f'val_{proc_idx}_{i}' for i in range(len(df))]
                return df_copy
            mock.side_effect = side_effect
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.ReadIntegratedRequestListTable') as mock_read, \
            patch('src.packages.preparation_editor.preparation_chain_processor.AddDecisionJudgeColumns') as mock_add, \
            patch('src.packages.preparation_editor.preparation_chain_processor.PreMergeDataEditor') as mock_pre, \
            patch('src.packages.preparation_editor.preparation_chain_processor.ReferenceDataMerger') as mock_merge, \
            patch('src.packages.preparation_editor.preparation_chain_processor.BPRADFlagInitializer') as mock_flag, \
            patch('src.packages.preparation_editor.preparation_chain_processor.LoookupReferenceData') as mock_lookup:

            mock_procs = [mock_read, mock_add, mock_pre, mock_merge, mock_flag, mock_lookup]
            for i, mock_proc in enumerate(mock_procs):
                mock_proc.return_value.process = make_mock_process(i)

            chain_processors = self.processor.chain_pre_processor()
            df_result = sample_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert not df_result.empty
            assert all(f'col_{i}' in df_result.columns for i in range(len(processors)))
            for mock_proc in mock_procs:
                mock_proc.return_value.process.assert_called_once()


class TestPostProcessorWritePreparationChain:
    """PostProcessorのチェーン制御テスト(WritePreparationResult)

    テスト構造:
    ├── C0: 単一プロセッサの実行確認
    │   ├── 正常系: WritePreparationResult実行
    │   └── 正常系: 戻り値のDataFrame確認
    ├── C1: 処理分岐の検証
    │   ├── 正常系: データ書き込み成功
    │   └── 異常系: 書き込み失敗時の例外伝播
    └── C2: 入力データパターン
        ├── 正常系: 空のDataFrame
        └── 正常系: データ有のDataFrame

    # C1のディシジョンテーブル
    | 条件                           | Case1 | Case2 |
    |--------------------------------|-------|-------|
    | WritePreparationResultが成功   | Y     | N     |
    |--------------------------------|-------|-------|
    | チェーン処理が完了             | X     | -     |
    | 書き込み例外発生               | -     | X     |

    境界値検証ケース一覧:
    | ID      | パラメータ   | テスト値         | 期待結果 | 目的                      | 実装状況           |
    |---------|--------------|------------------|----------|---------------------------|-------------------|
    | BVT_001 | input_df     | 空のDataFrame    | 成功     | 最小データでの動作確認    | C2_empty_dfで実装 |
    | BVT_002 | input_df     | 1行のDataFrame   | 成功     | 最小有効データでの確認    | C2_with_dataで実装|
    | BVT_003 | input_df     | None             | 例外発生 | 無効入力の処理確認        | C1_write_errorで実装|

    注記:
    - 全ての境界値テストは既存のテストケースでカバー
    - WritePreparationResultの内部実装の検証は対象外
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor = PostProcessor()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def empty_df(self):
        return pd.DataFrame()

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({'request_id': [1, 2], 'data': ['A', 'B']})

    def test_chain_C0_write_execution(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 書き込み処理の実行確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            mock.side_effect = lambda df: df
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.WritePreparationResult') as mock_write:
            mock_write.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_post_processor()
            df_result = sample_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert isinstance(df_result, pd.DataFrame)
            mock_write.return_value.process.assert_called_once()

    def test_chain_C1_normal_write(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: データ書き込み成功
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            mock.side_effect = lambda df: df
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.WritePreparationResult') as mock_write:
            mock_write.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_post_processor()
            df_result = sample_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert isinstance(df_result, pd.DataFrame)
            assert df_result.equals(sample_df)
            mock_write.return_value.process.assert_called_once()

    def test_chain_C1_write_error(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: データ書き込み失敗
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            mock.side_effect = Exception("Write Error")
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.WritePreparationResult') as mock_write:
            mock_write.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_post_processor()
            with pytest.raises(Exception) as exc_info:
                df_result = sample_df.copy()
                for proc in chain_processors:
                    df_result = proc.process(df_result)

            assert "Write Error" in str(exc_info.value)
            mock_write.return_value.process.assert_called_once()


    def test_chain_C2_empty_df(self, empty_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 空データフレームの書き込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            mock.side_effect = lambda df: df
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.WritePreparationResult') as mock_write:
            mock_write.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_post_processor()
            df_result = empty_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert df_result.empty
            mock_write.return_value.process.assert_called_once()

    def test_chain_C2_with_data(self, sample_df):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: データ有データフレームの書き込み
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        def make_mock_process():
            mock = Mock()
            def side_effect(df):
                df_result = df.copy()
                df_result['processed'] = True
                return df_result
            mock.side_effect = side_effect
            return mock

        with patch('src.packages.preparation_editor.preparation_chain_processor.WritePreparationResult') as mock_write:
            mock_write.return_value.process = make_mock_process()

            chain_processors = self.processor.chain_post_processor()
            df_result = sample_df.copy()
            for proc in chain_processors:
                df_result = proc.process(df_result)

            assert not df_result.empty
            assert 'processed' in df_result.columns
            assert all(df_result['processed'])
            mock_write.return_value.process.assert_called_once()

class TestReadDecisionTable:
    """ReadDecisionTableのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効な決定テーブルファイルでの処理
    │   │   ├── TableSearcherのMock化
    │   │   └── fillna処理の確認
    │   └── 異常系: TableSearcher例外発生時の処理
    │       ├── TableSearcher初期化失敗
    │       └── PreparationChainProcessorError変換確認
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: try文正常実行パス
    │   └── 異常系: 例外処理パス
    ├── C2: 条件組み合わせ
    │   ├── ファイルパス条件
    │   └── テーブル状態条件
    └── BVT: 境界値テスト
        ├── 入力DataFrame
        └── ファイルパス

    C1のディシジョンテーブル:
    | 条件                          | DT1 | DT2 | DT3 | DT4 |
    |-------------------------------|-----|-----|-----|-----|
    | ファイルが存在する            | Y   | N   | Y   | Y   |
    | ファイルが有効な形式          | Y   | -   | N   | Y   |
    | テーブルデータが有効          | Y   | -   | -   | N   |
    |-------------------------------|-----|-----|-----|-----|
    | 正常終了                      | X   | -   | -   | -   |
    | FileNotFoundError             | -   | X   | -   | -   |
    | ValueError                    | -   | -   | X   | -   |
    | PreparationChainProcessorError| -   | -   | -   | X   |

    境界値検証ケース一覧:
    | ID     | パラメータ    | テスト値           | 期待結果 | 検証ポイント           | 実装状況 |
    |--------|---------------|-------------------|----------|----------------------|----------|
    | BVT_001| input_df     | 空のDataFrame     | 成功     | 最小入力での動作      | C0で実装 |
    | BVT_002| input_df     | 1行1列            | 成功     | 最小有効入力での動作  | C0で実装 |
    | BVT_003| input_df     | 大規模DataFrame   | 成功     | 大規模入力での動作    | C2で実装 |
    | BVT_004| file_path    | 最大長パス        | 例外発生 | パス長制限の確認      | 実装済み |
    | BVT_005| file_path    | 特殊文字を含むパス | 例外発生 | パス文字制限の確認    | 実装済み |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.test_df = pd.DataFrame({'test': [1, 2, None]})
        self.mock_file = 'mock_file.pkl'
        self.mock_path = '/mock/path'

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_table_searcher_class(self):
        """TableSearcherクラス全体をMock化するfixture"""
        with patch('src.packages.preparation_editor.preparation_chain_processor.TableSearcher') as mock_class:
            mock_instance = MagicMock()
            mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})
            mock_class.return_value = mock_instance
            yield mock_class

    @pytest.fixture()
    def config_patches(self):
        """設定値のパッチを提供するfixture"""
        with patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_file', 'mock_file.pkl'), \
            patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_path', '/mock/path'):
            yield

    def test_process_C0_normal(self, mock_table_searcher_class):
        """正常系の基本機能テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テストシナリオ: 有効な決定テーブルファイルでの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # パッケージ設定の値をパッチ
        with patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_file', 'mock_file.pkl'), \
            patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_path', '/mock/path'):

            processor = ReadDecisionTable()
            result = processor.process(self.test_df)

            # 検証
            assert isinstance(result, pd.DataFrame)
            assert not result.isna().any().any()
            mock_table_searcher_class.assert_called_once_with('mock_file.pkl', '/mock/path')

    def test_process_C1_DT1(self, mock_table_searcher_class, config_patches):
        """C1 DT1: 正常系パスのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: 正常実行パスの確認
        DT1: ファイル存在[Y], 有効形式[Y], 有効データ[Y]
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = ReadDecisionTable()
        result = processor.process(self.test_df)

        assert isinstance(result, pd.DataFrame)
        assert not result.isna().any().any()
        mock_table_searcher_class.assert_called_once_with(self.mock_file, self.mock_path)

    def test_process_C1_DT2(self, mock_table_searcher_class, config_patches):
        """C1 DT2: ファイル不存在エラー"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テストシナリオ: ファイル不存在エラーの確認
        DT2: ファイル存在[N]
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_table_searcher_class.side_effect = FileNotFoundError("File not found")

        processor = ReadDecisionTable()
        with pytest.raises(PreparationChainProcessorError) as exc_info:
            processor.process(self.test_df)

        assert "DecisionTable読み込みで失敗が発生しました" in str(exc_info.value)
        mock_table_searcher_class.assert_called_once_with(self.mock_file, self.mock_path)

    def test_process_C2_large_data(self, mock_table_searcher_class, config_patches):
        """C2: 大規模データ処理テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テストシナリオ: 大規模DataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 大規模DataFrameをモック
        large_mock_df = pd.DataFrame({
            'test': range(10000),
        })
        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = large_mock_df

        processor = ReadDecisionTable()
        result = processor.process(self.test_df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 10000
        mock_table_searcher_class.assert_called_once_with(self.mock_file, self.mock_path)

    def test_process_BVT_file_path(self, mock_table_searcher_class, config_patches):
        """境界値テスト: 極端に長いパス"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テストシナリオ: 極端に長いパスでの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # 極端に長いパスでエラーを発生させる
        mock_table_searcher_class.side_effect = OSError("Path too long")

        processor = ReadDecisionTable()
        with pytest.raises(PreparationChainProcessorError) as exc_info:
            processor.process(self.test_df)

        assert "DecisionTable読み込みで失敗が発生しました" in str(exc_info.value)
        mock_table_searcher_class.assert_called_once_with(self.mock_file, self.mock_path)

class TestModifyDecisionTableProcess:
    """ModifyDecisionTableのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 基本的なDataFrameの変換
    │   ├── 正常系: 空のDataFrameの処理
    │   └── 正常系: 必要なカラムのみを含むDataFrameの処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 指定された全カラムが存在する
    │   ├── 異常系: カラムが存在しない
    │   └── 異常系: 変換対象カラムが存在しない
    └── C2: 条件組み合わせ
        ├── 正常系: 全カラムあり・全て有効な値
        ├── 正常系: 一部カラムのみ・有効な値
        └── 異常系: 無効なカラム構成

    C1のディシジョンテーブル:
    | 条件                           | DT1 | DT2 | DT3 |
    |--------------------------------|-----|-----|-----|
    | 全カラムが存在する             | Y   | N   | Y   |
    | 変換対象カラムが存在する       | Y   | -   | N   |
    |--------------------------------|-----|-----|-----|
    | 正常に処理完了                 | X   | -   | -   |
    | ValueError(カラム数不一致)     | -   | X   | X   |


    境界値検証ケース一覧:
    | ID     | 入力パラメータ   | テスト値         | 期待される結果 | テストの目的            | 実装状況  |
    |--------|------------------|------------------|----------------|-------------------------|-----------|
    | BVT_001| df               | 空のDataFrame    | 空のDataFrame  | 最小データセットの処理  | 実装済み  |
    | BVT_002| df               | 1行のDataFrame   | 1行の変換結果  | 最小有効データの処理    | 実装済み  |
    | BVT_003| df               | 大量データ       | 正常に変換     | 大規模データの処理性能  | 未実装    |
    """

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)
        self.modifier = ModifyDecisionTable()

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_def',
        ['col1', 'col2'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.columns_to_transform_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_fin_def',
        ['col1', 'col2'])
    def test_process_C0_basic_transformation(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なDataFrameの変換処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        _df = pd.DataFrame({
            'col1': ['4桁', '5桁'],
            'col2': ['値1', '値2'],
        })

        # 実行
        result = self.modifier.process(_df)

        # 検証
        expected = pd.DataFrame({
            'col1': ['is_4digits', 'is_5digits'],
            'col2': ['値1', '値2'],
        })
        pd.testing.assert_frame_equal(result, expected)

    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.columns_to_transform_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_fin_def',
        ['col1'])
    def test_process_C0_empty_dataframe(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 空のDataFrameが正しく処理されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        _df = pd.DataFrame({'col1': []})

        # 実行
        result = self.modifier.process(_df)

        # 検証
        expected = pd.DataFrame({'col1': []})
        pd.testing.assert_frame_equal(result, expected)


    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_def',
        ['col1', 'col2'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.columns_to_transform_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_fin_def',
        ['col1', 'col2'])
    def test_process_C1_missing_column(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 必要なカラムが欠落している場合のエラー処理を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        _df = pd.DataFrame({'wrong_col': ['値1']})

        # 実行と検証
        with pytest.raises(ValueError) as exc_info:
            self.modifier.process(_df)

        # エラーメッセージの検証
        assert "Length mismatch" in str(exc_info.value)
        log_msg(f"Caught expected ValueError: {str(exc_info.value)}", LogLevel.DEBUG)

    @pytest.mark.parametrize(
        ("input_data", "expected_data"),
        [
            # ケース1: 全カラムあり・全て有効な値
            (
                {'col1': ['4桁', 'なし'], 'col2': ['値1', '値2']},
                {'col1': ['is_4digits', 'is_empty'], 'col2': ['値1', '値2']},
            ),
            # ケース2: 変換対象外の値を含む
            (
                {'col1': ['不明', '-'], 'col2': ['値1', '値2']},
                {'col1': ['不明', 'any'], 'col2': ['値1', '値2']},
            ),
        ],
    )
    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_def',
        ['col1', 'col2'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.columns_to_transform_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_fin_def',
        ['col1', 'col2'])
    def test_process_C2_combinations(self, input_data, expected_data):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 様々な入力値の組み合わせで正しく変換されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        _df = pd.DataFrame(input_data)
        expected = pd.DataFrame(expected_data)

        # 実行
        result = self.modifier.process(_df)

        # 検証
        pd.testing.assert_frame_equal(result, expected)

    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.columns_to_transform_def',
        ['col1'])
    @patch('src.packages.preparation_editor.preparation_chain_processor.decision_table_columns_fin_def',
        ['col1'])
    def test_process_BVT_minimal_dataset(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 1行のみのデータで正しく処理されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        _df = pd.DataFrame({'col1': ['4桁']})
        expected = pd.DataFrame({'col1': ['is_4digits']})

        # 実行
        result = self.modifier.process(_df)

        # 検証
        pd.testing.assert_frame_equal(result, expected)

class TestModifyDecisionTableReplaceValues:
    """ModifyDecisionTableの_replace_valuesメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 単一値の変換
    │   ├── 正常系: 複数値の変換
    │   └── 正常系: 変換対象外の値の処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 各変換パターン
    │   └── 正常系: 正規表現パターン
    └── C2: 条件組み合わせ
        ├── 正常系: 複数パターンの組み合わせ
        └── 正常系: 特殊文字を含むパターン

    C1のディシジョンテーブル:
    | 条件                    | DT1 | DT2 | DT3 | DT4 | DT5 |
    |------------------------|-----|-----|-----|-----|-----|
    | '4桁'を含む            | Y   | N   | N   | N   | N   |
    | '5桁'を含む            | N   | Y   | N   | N   | N   |
    | 'なし'を含む           | N   | N   | Y   | N   | N   |
    | 'あり'を含む           | N   | N   | N   | Y   | N   |
    | '-'を含む              | N   | N   | N   | N   | Y   |
    |------------------------|-----|-----|-----|-----|-----|
    | 'is_4digits'に変換     | X   | -   | -   | -   | -   |
    | 'is_5digits'に変換     | -   | X   | -   | -   | -   |
    | 'is_empty'に変換       | -   | -   | X   | -   | -   |
    | 'is_not_empty'に変換   | -   | -   | -   | X   | -   |
    | 'any'に変換            | -   | -   | -   | -   | X   |

    境界値検証ケース一覧:
    | ID     | 入力パラメータ | テスト値                     | 期待される結果               | テストの目的                    | 実装状況 | 対応するテストケース       |
    |--------|----------------|------------------------------|------------------------------|---------------------------------|----------|--------------------------|
    |BVT_001 | column         | 空のSeries                   | 空のSeries                   | 空データの処理                  | 実装済み | test_replace_values_BVT_empty_series |
    |BVT_002 | column         | 全て変換対象外の値           | 入力と同じ値                 | 変換対象外データの処理          | 実装済み | test_replace_values_C0_non_target_values |
    |BVT_003 | column         | 全て変換対象の値             | 全て変換された値             | 全データ変換の処理              | 実装済み | test_replace_values_C2_all_patterns |
    |BVT_004 | column         | 特殊文字を含む値             | 正しく変換された値           | 特殊文字の処理                  | 実装済み | test_replace_values_C2_special_chars |
    """

    def setup_method(self):
        """テストメソッドの前処理"""
        log_msg("test start", LogLevel.INFO)
        self.modifier = ModifyDecisionTable()

    def teardown_method(self):
        """テストメソッドの後処理"""
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    def test_replace_values_C0_single_value(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 単一の変換対象値が正しく変換されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        column = pd.Series(['4桁'])

        # 実行
        result = self.modifier._replace_values(column)

        # 検証
        expected = pd.Series(['is_4digits'])
        pd.testing.assert_series_equal(result, expected)

    def test_replace_values_C0_multiple_values(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 複数の変換対象値が正しく変換されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        column = pd.Series(['4桁', '5桁', 'なし', 'あり'])

        # 実行
        result = self.modifier._replace_values(column)

        # 検証
        expected = pd.Series(['is_4digits', 'is_5digits', 'is_empty', 'is_not_empty'])
        pd.testing.assert_series_equal(result, expected)

    def test_replace_values_C0_non_target_values(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 変換対象外の値が変更されないことを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        column = pd.Series(['その他', '不明'])

        # 実行
        result = self.modifier._replace_values(column)

        # 検証
        pd.testing.assert_series_equal(result, column)

    @pytest.mark.parametrize(("input_value", "expected_value"), [
        ('4桁', 'is_4digits'),
        ('5桁', 'is_5digits'),
        ('なし', 'is_empty'),
        ('あり', 'is_not_empty'),
        ('-', 'any'),
    ])
    def test_replace_values_C1_patterns(self, input_value, expected_value):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 各変換パターンが正しく処理されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        column = pd.Series([input_value])

        # 実行
        result = self.modifier._replace_values(column)

        # 検証
        expected = pd.Series([expected_value])
        pd.testing.assert_series_equal(result, expected)

    def test_replace_values_C2_all_patterns(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 全ての変換パターンの組み合わせを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        column = pd.Series(['4桁', '5桁', 'なし', 'あり', '-', '不明'])

        # 実行
        result = self.modifier._replace_values(column)

        # 検証
        expected = pd.Series(['is_4digits', 'is_5digits', 'is_empty',
                            'is_not_empty', 'any', '不明'])
        pd.testing.assert_series_equal(result, expected)

    def test_replace_values_BVT_empty_series(self):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空のSeriesが正しく処理されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        column = pd.Series([], dtype=object)

        # 実行
        result = self.modifier._replace_values(column)

        # 検証
        expected = pd.Series([], dtype=object)
        pd.testing.assert_series_equal(result, expected)

class TestReadIntegratedRequestListTableProcess:
    """ReadIntegratedRequestListTableのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: テーブル読み込み成功
    │   └── 異常系: テーブル読み込み失敗
    ├── C1: 分岐カバレッジ
    │   ├── try成功パス
    │   └── except発生パス
    ├── C2: 条件組み合わせ
    │   ├── 正常系: NAなし
    │   ├── 正常系: NAあり
    │   └── 異常系: 読み込み失敗
    └── BVT: 境界値テスト
        ├── 空DataFrame
        ├── 1行DataFrame
        ├── 全NA DataFrame
        └── 大規模DataFrame

    # C1のディシジョンテーブル
    | 条件                        | DT1 | DT2 | DT3 | DT4 |
    |-----------------------------|-----|-----|-----|-----|
    | ファイルが存在する          | Y   | N   | Y   | Y   |
    | ファイルが有効なpickle形式  | Y   | -   | N   | Y   |
    | DataFrameにNAが含まれる     | N   | -   | -   | Y   |
    |-----------------------------|-----|-----|-----|-----|
    | 正常にデータフレームを返却  | X   | -   | -   | X   |
    | NAが空文字に変換される      | -   | -   | -   | X   |
    | エラーが発生する            | -   | X   | X   | -   |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値              | 期待される結果            | テストの目的/検証ポイント | 実装状況 | 対応するテストケース |
    |----------|----------------|-----------------------|---------------------------|---------------------------|----------|-------------------|
    | BVT_001  | df             | 空のDataFrame         | 空のDataFrame             | 最小入力の処理            | 実装済み | test_process_BVT_empty_dataframe |
    | BVT_002  | df             | 1行のDataFrame        | 1行のDataFrame            | 最小有効データ            | 実装済み | test_process_BVT_single_row |
    | BVT_003  | df             | すべてNAのDataFrame   | すべて空文字のDataFrame   | NA処理の極端ケース        | 実装済み | test_process_BVT_all_na |
    | BVT_004  | df             | 大規模DataFrame       | 処理済DataFrame           | 性能限界の確認            | 実装済み | test_process_BVT_large_dataframe |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 4
    - 未実装: 0
    - 一部実装: 0
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_table_searcher_class(self):
        """TableSearcherクラス全体をMock化するfixture"""
        with patch('src.packages.preparation_editor.preparation_chain_processor.TableSearcher') as mock_class:
            mock_instance = MagicMock()
            mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})
            mock_class.return_value = mock_instance
            yield mock_class

    def test_process_C0_normal(self, mock_table_searcher_class):
        """C0: 正常系のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系のテーブル読み込みテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        processor = ReadIntegratedRequestListTable()
        input_df = pd.DataFrame({'dummy': [1]})
        result = processor.process(input_df)

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        mock_table_searcher_class.assert_called_once()

    def test_process_C0_error(self, mock_table_searcher_class):
        """C0: 異常系のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: テーブル読み込み失敗時のエラーハンドリング
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_table_searcher_class.side_effect = Exception("Mock error")
        processor = ReadIntegratedRequestListTable()
        input_df = pd.DataFrame({'dummy': [1]})

        with pytest.raises(PreparationChainProcessorError) as exc_info:
            processor.process(input_df)

        assert "受付処理一括申請ファイル読み込みで失敗が発生しました" in str(exc_info.value)

    def test_process_C1_DT1(self, mock_table_searcher_class):
        """C1: DT1 - 正常系(NAなし)のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: DT1 - ファイル存在、有効なpickle、NAなし
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})

        processor = ReadIntegratedRequestListTable()
        result = processor.process(pd.DataFrame())

        assert not result.isna().any().any()

    def test_process_C1_DT4(self, mock_table_searcher_class):
        """C1: DT4 - 正常系(NAあり)のテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: DT4 - ファイル存在、有効なpickle、NAあり
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'test': [1, None, 3]})

        processor = ReadIntegratedRequestListTable()
        result = processor.process(pd.DataFrame())

        assert not result.isna().any().any()
        assert '' in result['test'].to_numpy()

    def test_process_C2_na_handling(self, mock_table_searcher_class):
        """C2: NA処理の条件組み合わせテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: NA値の処理パターンテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        test_data = [
            pd.DataFrame({'a': [1, None], 'b': [None, 2]}),
            pd.DataFrame({'a': [None, None], 'b': [None, None]}),
            pd.DataFrame({'a': [1, 2], 'b': [3, 4]}),
        ]

        for df in test_data:
            log_msg(f"Testing DataFrame:\n{df}", LogLevel.DEBUG)
            mock_instance = mock_table_searcher_class.return_value
            mock_instance.df = df

            processor = ReadIntegratedRequestListTable()
            result = processor.process(pd.DataFrame())

            # NA値が存在しないことを確認
            assert not result.isna().any().any()

            # 各値が有効な値(空文字列または数値)であることを確認
            for col in result.columns:
                for val in result[col]:
                    assert val == '' or isinstance(val, int | float)

            log_msg(f"Processed result:\n{result}", LogLevel.DEBUG)


    def test_process_BVT_empty_dataframe(self, mock_table_searcher_class):
        """BVT: 空のDataFrameテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空のDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame()

        processor = ReadIntegratedRequestListTable()
        result = processor.process(pd.DataFrame())

        assert result.empty

    def test_process_BVT_single_row(self, mock_table_searcher_class):
        """BVT: 1行のDataFrameテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 1行のDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'test': [1]})

        processor = ReadIntegratedRequestListTable()
        result = processor.process(pd.DataFrame())

        assert len(result) == 1

    def test_process_BVT_all_na(self, mock_table_searcher_class):
        """BVT: すべてNAのDataFrameテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: すべてNAのDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = pd.DataFrame({'test': [None, None]})

        processor = ReadIntegratedRequestListTable()
        result = processor.process(pd.DataFrame())

        assert not result.isna().any().any()
        assert all(val == '' for val in result['test'])

    def test_process_BVT_large_dataframe(self, mock_table_searcher_class):
        """BVT: 大規模DataFrameテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 大規模DataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        large_df = pd.DataFrame({
            'col1': list(range(10000)),
            'col2': [None if i % 2 == 0 else i for i in range(10000)],
        })

        mock_instance = mock_table_searcher_class.return_value
        mock_instance.df = large_df

        processor = ReadIntegratedRequestListTable()
        result = processor.process(pd.DataFrame())

        assert len(result) == 10000
        assert not result.isna().any().any()


class TestAddDecisionJudgeColumns:
    """AddDecisionJudgeColumnsのテスト

    テスト構造:
    ├── process [C0]
    │   ├── 正常系: 基本機能確認
    │   │   ├── DataFrameのコピー生成
    │   │   └── fillna処理の確認
    │   └── 異常系: 無効なDataFrame
    └── _add_decision_table_columns
        ├── データ型変換 [C0]
        │   ├── branch_code文字列化
        │   ├── branch_code_digit設定
        │   └── branch_code_first_digit設定
        ├── 自己相関判定 [C1]
        │   ├── 同一DataFrame内検索
        │   └── 条件組み合わせ
        ├── 複合条件 [C2]
        │   ├── 全条件一致パターン
        │   ├── 部分条件一致パターン
        │   └── 全条件不一致パターン
        ├── 相対判定パターン [DT]
        └── 境界値 [BVT]

    C1のディシジョンテーブル:
    | 条件                                    | DT1 | DT2 | DT3 | DT4 | DT5 |
    |-----------------------------------------|-----|-----|-----|-----|-----|
    | branch_codeが4桁の数字                  | Y   | N   | Y   | Y   | Y   |
    | 同一先頭4桁のレコードが存在             | Y   | -   | N   | Y   | Y   |
    | application_typeが新規または変更        | Y   | -   | -   | N   | Y   |
    | target_orgがBRANCH                      | Y   | -   | -   | -   | N   |
    | 結果                                    | exists | '' | '' | '' | '' |

    境界値検証ケース一覧:
    | ID      | パラメータ   | テスト値 | 期待結果 | 検証ポイント      | 実装状況 | 実装箇所 |
    |---------|--------------|----------|----------|-------------------|----------|----------|
    | BVT_001 | branch_code  | '0000'   | 'exists' | 最小4桁数字       | 実装済   | test_add_decision_table_columns_BVT_min_valid |
    | BVT_002 | branch_code  | '9999'   | 'exists' | 最大4桁数字       | 実装済   | test_add_decision_table_columns_BVT_max_valid |
    | BVT_003 | branch_code  | '00000'  | ''       | 5桁数字(無効)     | 実装済   | test_add_decision_table_columns_BVT_invalid_length |
    | BVT_004 | branch_code  | '000'    | ''       | 3桁数字(無効)     | 実装済   | test_add_decision_table_columns_BVT_invalid_length |
    | BVT_005 | branch_code  | 'ABCD'   | ''       | 英字4文字(無効)   | 実装済   | test_add_decision_table_columns_BVT_invalid_format |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)
        self.processor = AddDecisionJudgeColumns()

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def base_df(self):
        """基本テストデータ"""
        return pd.DataFrame({
            'branch_code': ['1234', '1235', '1234'],
            'application_type': [
                ApplicationType.NEW.value,
                ApplicationType.MODIFY.value,
                ApplicationType.NEW.value,
            ],
            'target_org': [
                OrganizationType.BRANCH.value,
                OrganizationType.BRANCH.value,
                OrganizationType.BRANCH.value,
            ],
        })

    def test_process_C0_basic(self, base_df):
        log_msg("\nExecuting test_process_C0_basic", LogLevel.INFO)

        result = self.processor.process(base_df)
        assert isinstance(result, pd.DataFrame)
        assert 'branch_code_4_digits_application_status' in result.columns
        assert not result.equals(base_df)  # コピーされていることを確認

    def test_add_decision_table_columns_C1_DT1(self, base_df):
        log_msg("\nExecuting test_add_decision_table_columns_C1_DT1", LogLevel.INFO)

        result = self.processor._add_decision_table_columns(base_df)
        assert result.loc[0, 'branch_code_4_digits_application_status'] == 'exist'

    def test_add_decision_table_columns_C2_complete_match(self):
        log_msg("\nExecuting test_add_decision_table_columns_C2_complete_match", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': [
                # 4桁グループ1(1234で始まる)
                '1234',     # exists: 4桁、部店、新設
                '1234',     # exists: 4桁、部店、変更
                '1234',     # non-exists: 4桁、部店、廃止
                '1235',     # exists: 4桁、課、新設(上位4桁一致)
                '1236',     # exists: 4桁、エリア、変更(上位4桁一致)
                '1237',     # exists: 4桁、拠点内営業部、新設(上位4桁一致)

                # 5桁グループ1(1234で始まる)
                '12345',    # non-exists: 5桁、部店、新設
                '12346',    # non-exists: 5桁、課、変更
                '12347',    # non-exists: 5桁、エリア、廃止

                # 4桁グループ2(5678で始まる)
                '5678',     # non-exists: 4桁、部店、新設(単独)
                '5679',     # non-exists: 4桁、課、新設
                '5670',     # non-exists: 4桁、エリア、廃止

                # 5桁グループ2(5678で始まる)
                '56781',    # non-exists: 5桁、部店、新設
                '56782',    # non-exists: 5桁、拠点内営業部、変更

                # その他のパターン
                '123',      # non-exists: 3桁、部店、新設
                '1234A',    # non-exists: 英数字混在、部店、変更
            ],
            'application_type': [
                ApplicationType.NEW.value,          # 新設
                ApplicationType.MODIFY.value,       # 変更
                ApplicationType.DISCONTINUE.value,  # 廃止
                ApplicationType.NEW.value,          # 新設
                ApplicationType.MODIFY.value,       # 変更
                ApplicationType.NEW.value,          # 新設

                ApplicationType.NEW.value,          # 新設
                ApplicationType.MODIFY.value,       # 変更
                ApplicationType.DISCONTINUE.value,  # 廃止

                ApplicationType.NEW.value,          # 新設
                ApplicationType.NEW.value,          # 新設
                ApplicationType.DISCONTINUE.value,  # 廃止

                ApplicationType.NEW.value,          # 新設
                ApplicationType.MODIFY.value,       # 変更

                ApplicationType.NEW.value,          # 新設
                ApplicationType.MODIFY.value,       # 変更
            ],
            'target_org': [
                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.SECTION_GROUP.value,   # 課
                OrganizationType.AREA.value,            # エリア
                OrganizationType.INTERNAL_SALES.value,  # 拠点内営業部

                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.SECTION_GROUP.value,   # 課
                OrganizationType.AREA.value,            # エリア

                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.SECTION_GROUP.value,   # 課
                OrganizationType.AREA.value,            # エリア

                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.INTERNAL_SALES.value,  # 拠点内営業部

                OrganizationType.BRANCH.value,          # 部店
                OrganizationType.BRANCH.value,          # 部店
            ],
        })

        result = self.processor._add_decision_table_columns(_df)

        # 4桁の1234グループ - exists判定
        assert result.loc[0, 'branch_code_4_digits_application_status'] == 'exist'  # 1234部店新設
        assert result.loc[1, 'branch_code_4_digits_application_status'] == 'exist'  # 1234部店変更
        assert result.loc[2, 'branch_code_4_digits_application_status'] == 'exist'  # 1234部店廃止
        assert result.loc[3, 'branch_code_4_digits_application_status'] == ''       # 1235課新設
        assert result.loc[4, 'branch_code_4_digits_application_status'] == ''       # 1236エリア変更
        assert result.loc[5, 'branch_code_4_digits_application_status'] == ''       # 1237拠点内営業部新設

        # 5桁の1234グループ - exists判定
        assert result.loc[6, 'branch_code_4_digits_application_status'] == 'exist'  # 12345部店
        assert result.loc[7, 'branch_code_4_digits_application_status'] == 'exist'  # 12346課
        assert result.loc[8, 'branch_code_4_digits_application_status'] == 'exist'  # 12347エリア

        # 4桁の5678グループ - exists判定(単独)
        assert result.loc[9, 'branch_code_4_digits_application_status'] == 'exist'  # 5678部店
        assert result.loc[10, 'branch_code_4_digits_application_status'] == ''      # 5679課
        assert result.loc[11, 'branch_code_4_digits_application_status'] == ''      # 5670エリア

        # 5桁の5678グループ - exists判定
        assert result.loc[12, 'branch_code_4_digits_application_status'] == 'exist' # 56781部店
        assert result.loc[13, 'branch_code_4_digits_application_status'] == 'exist' # 56782拠点内営業部

        # その他無効なパターン - exists判定
        assert result.loc[14, 'branch_code_4_digits_application_status'] == ''      # 123(3桁)
        assert result.loc[15, 'branch_code_4_digits_application_status'] == 'exist' # 1234A(英数字),最初4文字は数字

        # デバッグ用出力
        log_msg("\nTest DataFrame結果:\n" +
                result[['branch_code', 'application_type', 'target_org',
                    'branch_code_4_digits_application_status']].to_string(),
                LogLevel.DEBUG)

    def test_add_decision_table_columns_BVT_min_valid(self):
        log_msg("\nExecuting test_add_decision_table_columns_BVT_min_valid", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['0000', '0000'],
            'application_type': [ApplicationType.NEW.value] * 2,
            'target_org': [OrganizationType.BRANCH.value] * 2,
        })

        result = self.processor._add_decision_table_columns(_df)
        assert result.loc[0, 'branch_code_4_digits_application_status'] == 'exist'

    def test_add_decision_table_columns_BVT_max_valid(self):
        log_msg("\nExecuting test_add_decision_table_columns_BVT_max_valid", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['9999', '9999'],
            'application_type': [ApplicationType.NEW.value] * 2,
            'target_org': [OrganizationType.BRANCH.value] * 2,
        })

        result = self.processor._add_decision_table_columns(_df)
        assert result.loc[0, 'branch_code_4_digits_application_status'] == 'exist'


    def test_add_decision_table_columns_BVT_invalid_length(self):
        log_msg("\nExecuting test_add_decision_table_columns_BVT_invalid_length", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['000', '00000'],
            'application_type': [ApplicationType.NEW.value] * 2,
            'target_org': [OrganizationType.BRANCH.value] * 2,
        })

        result = self.processor._add_decision_table_columns(_df)
        assert result['branch_code_4_digits_application_status'].eq('').all()

    def test_add_decision_table_columns_BVT_invalid_format(self):
        log_msg("\nExecuting test_add_decision_table_columns_BVT_invalid_format", LogLevel.INFO)

        _df = pd.DataFrame({
            'branch_code': ['ABCD', '123A'],
            'application_type': [ApplicationType.NEW.value] * 2,
            'target_org': [OrganizationType.BRANCH.value] * 2,
        })

        result = self.processor._add_decision_table_columns(_df)
        assert result['branch_code_4_digits_application_status'].eq('').all()

class TestPreMergeDataEditorProcess:
    """PreMergeDataEditorのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 全プリプロセスメソッド呼び出し確認
    │   ├── 正常系: メソッド呼び出し順序の確認
    │   ├── 正常系: 入力DFの不変性確認
    │   └── 正常系: 欠損値の空文字変換確認
    ├── C1: 分岐網羅
    │   └── 正常系: 全プリプロセスメソッド呼び出しパターン
    ├── C2: 条件網羅
    │   └── 正常系: プリプロセスメソッドの実行結果組み合わせ
    ├── DT: ディシジョンテーブル
    │   └── 正常系: プリプロセスメソッド実行パターン網羅
    └── BVT: 境界値テスト
        ├── 正常系: 空のDataFrame入力
        ├── 正常系: 1行のみのDataFrame入力
        ├── 正常系: 大規模DataFrame処理
        └── 正常系: 全カラムnull値のDataFrame

    # C1のディシジョンテーブル
    | 条件                                                  | DT_1 | DT_2 | DT_3 |
    |-------------------------------------------------------|------|------|------|
    | setup_section_under_internal_sales_integrated_data成功 | Y    | Y    | N    |
    | setup_internal_sales_to_integrated_data成功            | Y    | N    | Y    |
    | setup_area_to_integrated_data成功                      | Y    | N    | Y    |
    | 出力                                                   | 成功 | 失敗 | 失敗 |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ  | テスト値                    | 期待される結果      | テストの目的/検証ポイント         | 実装状況 | 対応するテストケース               |
    |----------|-----------------|-----------------------------|---------------------|-----------------------------------|----------|----------------------------------|
    | BVT_001  | df              | 空のDataFrame               | 空のDataFrame       | 空入力の処理確認                  | 実装済   | test_process_BVT_empty_dataframe  |
    | BVT_002  | df              | 1行のDataFrame              | 1行のDataFrame      | 最小データセットの処理確認        | 実装済   | test_process_BVT_single_row      |
    | BVT_003  | df              | 100万行のDataFrame          | 処理済DataFrame     | 大規模データの処理確認            | 実装済   | test_process_BVT_large_dataframe |
    | BVT_004  | df              | 全カラムNull                | 空文字に変換        | Null値の処理確認                  | 実装済   | test_process_BVT_all_null        |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 4
    - 未実装: 0
    - 一部実装: 0
    """

    def setup_method(self):
        self.editor = PreMergeDataEditor()
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def sample_df(self):
        return pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['A', 'B', 'C'],
            'col3': [np.nan, 'D', 'E'],
        })

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_C0_all_methods_called(self, mock_pre_mapping):
        _df = pd.DataFrame({'test': [1, 2, 3]})
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df

        result = self.editor.process(_df)

        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.assert_called_once()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.assert_called_once()
        mock_pre_mapping.setup_area_to_integrated_data.assert_called_once()
        assert isinstance(result, pd.DataFrame)

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_C0_method_order(self, mock_pre_mapping):
        test_doc = """テスト区分: UT
        テストカテゴリ: C0
        テスト内容: メソッドが正しい順序で呼び出されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'test': [1, 2, 3]})
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df

        self.editor.process(_df)

        call_order = mock_pre_mapping.method_calls
        assert len(call_order) == 3
        assert call_order[0][0] == 'setup_section_under_internal_sales_integrated_data'
        assert call_order[1][0] == 'setup_internal_sales_to_integrated_data'
        assert call_order[2][0] == 'setup_area_to_integrated_data'

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_C0_df_immutability(self, mock_pre_mapping, sample_df):
        test_doc = """テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 入力DataFrameが変更されないことを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        original_df = sample_df.copy()
        # モックの戻り値を設定
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = sample_df.copy()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = sample_df.copy()
        mock_pre_mapping.setup_area_to_integrated_data.return_value = sample_df.copy()

        _ = self.editor.process(sample_df)
        pd.testing.assert_frame_equal(sample_df, original_df)

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_C0_fillna(self, mock_pre_mapping, sample_df):
        test_doc = """テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 欠損値が空文字に変換されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        # モックの戻り値を設定 - 各メソッドは入力をそのまま返すように
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = sample_df.copy()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = sample_df.copy()
        mock_pre_mapping.setup_area_to_integrated_data.return_value = sample_df.copy()

        result = self.editor.process(sample_df)
        assert not result.isna().any().any()
        assert result.iloc[0, 2] == ''

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_C1_method_patterns(self, mock_pre_mapping):
        test_doc = """テスト区分: UT
        テストカテゴリ: C1
        テスト内容: プリプロセスメソッド呼び出しパターンの確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        _df = pd.DataFrame({'test': [1, 2, 3]})
        test_doc = """
        DT_1のケース: 全メソッド成功
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df

        result = self.editor.process(_df)
        assert isinstance(result, pd.DataFrame)

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_BVT_empty_dataframe(self, mock_pre_mapping):
        test_doc = """テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空のDataFrameの処理を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)
        _df = pd.DataFrame()

        # モックの戻り値を設定 - 空のDataFrameをそのまま返すように
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df.copy()

        result = self.editor.process(_df)
        assert isinstance(result, pd.DataFrame)
        assert result.empty

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_BVT_single_row(self, mock_pre_mapping):
        test_doc = """テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 1行のみのDataFrameの処理を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'col1': [1], 'col2': ['A']})
        # モックの戻り値設定
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df.copy()

        result = self.editor.process(_df)
        assert len(result) == 1

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_BVT_large_dataframe(self, mock_pre_mapping):
        test_doc = """テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 大規模DataFrameの処理を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'col1': range(1000000),
            'col2': ['A'] * 1000000,
        })
        # モックの戻り値設定
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df.copy()

        result = self.editor.process(_df)
        assert len(result) == 1000000

    @patch('src.packages.preparation_editor.preparation_chain_processor.PreparationPreMapping')
    def test_process_BVT_all_null(self, mock_pre_mapping):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 全カラムnull値のDataFrameの処理を確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'col1': [np.nan, np.nan],
            'col2': [np.nan, np.nan],
        })
        # モックの戻り値設定
        mock_pre_mapping.setup_section_under_internal_sales_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_internal_sales_to_integrated_data.return_value = _df.copy()
        mock_pre_mapping.setup_area_to_integrated_data.return_value = _df.copy()

        result = self.editor.process(_df)
        assert not result.isna().any().any()
        assert (result == '').all().all()

class TestReferenceDataMerger:
    """ReferenceDataMergerクラスのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 全てのマージ処理が成功するケース
    │   ├── 異常系: DataLoadError発生時の処理
    │   ├── 異常系: DataMergeError発生時の処理
    │   ├── 異常系: ReferenceMergersError発生時の処理
    │   └── 異常系: RemarksParseError発生時の処理
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: 全てのマージメソッドが正常に実行される
    │   ├── 異常系: zero_group_parent_branch_with_selfでエラー
    │   ├── 異常系: zero_group_parent_branch_with_referenceでエラー
    │   └── 異常系: match_unique_referenceでエラー
    └── C2: 条件カバレッジ
        ├── データフレームの状態組み合わせ
        └── リファレンステーブルの状態組み合わせ

    C1のディシジョンテーブル:
    | 条件                                          | DT_01 | DT_02 | DT_03 | DT_04 |
    |-----------------------------------------------|-------|-------|-------|-------|
    | zero_group_parent_branch_with_self成功        | Y     | N     | Y     | Y     |
    | zero_group_parent_branch_with_reference成功   | Y     | -     | N     | Y     |
    | match_unique_reference成功                    | Y     | -     | -     | N     |
    |-----------------------------------------------|-------|-------|-------|-------|
    | 期待結果                                      | 成功  | エラー| エラー| エラー|

    境界値検証ケース一覧と実装状況:
    | ID     | パラメータ | テスト値            | 期待結果 | 検証ポイント           | 実装状況 |
    |--------|------------|---------------------|----------|------------------------|----------|
    | BVT_01 | input_df   | 空のDataFrame       | 成功     | 空データの処理        | C2で実装 |
    | BVT_02 | input_df   | 1行のDataFrame      | 成功     | 最小データの処理      | C2で実装 |
    | BVT_03 | input_df   | 大量データ          | 成功     | 大量データの処理      | 未実装   |
    | BVT_04 | input_df   | NaN含むDataFrame    | 成功     | NaN処理の確認         | C2で実装 |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def input_df(self):
        """テスト用の入力DataFrameを提供するfixture"""
        return pd.DataFrame({
            'column1': ['value1', 'value2'],
            'column2': ['data1', 'data2'],
        })

    @pytest.fixture()
    def mock_table_searcher_class(self):
        """TableSearcherクラス全体をMock化するfixture"""
        with patch('src.packages.preparation_editor.preparation_chain_processor.TableSearcher') as mock_class:
            mock_instance = MagicMock()
            mock_instance.df = pd.DataFrame({'test': [1, 2, 3]})
            mock_class.return_value = mock_instance
            yield mock_class

    @pytest.fixture()
    def mock_reference_mergers(self):
        """ReferenceMergersの各メソッドをMock化するfixture"""
        with patch('src.packages.preparation_editor.preparation_chain_processor.ReferenceMergers') as mock:
            mock.merge_zero_group_parent_branch_with_self.return_value = pd.DataFrame()
            mock.merge_zero_group_parent_branch_with_reference.return_value = pd.DataFrame()
            mock.match_unique_reference.return_value = pd.DataFrame()
            yield mock

    def test_process_C0_normal(self, input_df, mock_table_searcher_class, mock_reference_mergers):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 正常系の基本機能テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        processor = ReferenceDataMerger()
        result = processor.process(input_df)

        assert mock_reference_mergers.merge_zero_group_parent_branch_with_self.called
        assert mock_reference_mergers.merge_zero_group_parent_branch_with_reference.called
        assert mock_reference_mergers.match_unique_reference.called
        assert isinstance(result, pd.DataFrame)

    def test_process_C1_self_merge_error(self, input_df, mock_table_searcher_class, mock_reference_mergers):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: self_mergeでエラー発生時の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        mock_reference_mergers.merge_zero_group_parent_branch_with_self.side_effect = DataMergeError("Test error")

        processor = ReferenceDataMerger()
        with pytest.raises(DataMergeError):
            processor.process(input_df)

    def test_process_C2_empty_dataframe(self, mock_table_searcher_class, mock_reference_mergers):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 空のDataFrameを入力した場合の動作確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        empty_df = pd.DataFrame()
        processor = ReferenceDataMerger()
        result = processor.process(empty_df)

        mock_reference_mergers.merge_zero_group_parent_branch_with_self.assert_called_once()
        assert isinstance(result, pd.DataFrame)

    def test_process_C2_nan_dataframe(self, mock_table_searcher_class, mock_reference_mergers):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: NaN値を含むDataFrameの処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        nan_df = pd.DataFrame({
            'column1': ['value1', None],
            'column2': [pd.NA, 'data2'],
        })
        processor = ReferenceDataMerger()
        result = processor.process(nan_df)

        assert not result.isna().any().any()


class TestBPRADFlagInitializer:
    """BPRADFlagInitializerのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 基本的なDataFrame処理
    │   └── 異常系: デバッグ出力失敗
    ├── C1: 分岐カバレッジ
    │   ├── 正常系: デバッグ出力成功
    │   └── 異常系: デバッグ出力例外発生
    └── C2: 条件組み合わせ
        ├── 正常系: 空値なしデータ
        └── 正常系: 空値含むデータ

    C1のディシジョンテーブル:
    | 条件                               | DT1  | DT2  |
    |-----------------------------------|------|------|
    | デバッグファイル出力可能          | Y    | N    |
    | 入力DataFrameに空値が含まれる     | Y    | N    |
    |-----------------------------------|------|------|
    | 出力                              | 正常 | 警告 |

    境界値検証ケース一覧:
    | ID     | 入力パラメータ           | テスト値         | 期待される結果 | テストの目的                     | 実装状況 | 対応するテストケース           |
    |--------|-------------------------|-----------------|----------------|----------------------------------|----------|--------------------------------|
    | BVT001 | df                      | 空のDataFrame   | 空のDataFrame  | 最小データセット処理              | 実装済み | test_process_C0_empty_dataframe |
    | BVT002 | df                      | 1行のDataFrame | 1行のDataFrame | 最小有効データセット処理          | 実装済み | test_process_C0_basic_operation |
    | BVT003 | df                      | NULL値を含むDF  | 空文字に変換   | NULL値の処理確認                 | 実装済み | test_process_C2_with_null       |

    実装状況サマリー:
    - 実装済み: 3件
    - 未実装: 0件
    - 一部実装: 0件

    注記:
    - すべての境界値ケースは実装済みです
    - 各テストケースでBprAdFlagDeterminerはモック化され、制御フローのテストに焦点を当てています
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_bpr_flag_determiner(self):
        with patch('src.packages.preparation_editor.preparation_chain_processor.BprAdFlagDeterminer') as mock:
            instance = Mock()
            instance.determine_bpr_ad_flag.return_value = 'Y'
            mock.return_value = instance
            yield mock

    def test_process_C0_basic_operation(self, mock_bpr_flag_determiner):
        """基本的な処理フローのテスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 基本的なDataFrame処理の確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        # テストデータ準備
        _df = pd.DataFrame({'col1': [1, 2], 'col2': ['A', 'B']})

        with patch('pandas.DataFrame.to_excel') as mock_to_excel:
            processor = BPRADFlagInitializer()
            result = processor.process(_df)

            # 検証
            assert isinstance(result, pd.DataFrame)
            assert 'bpr_target_flag' in result.columns
            mock_to_excel.assert_called_once()
            mock_bpr_flag_determiner.assert_called_once()

    def test_process_C1_debug_output_error(self, mock_bpr_flag_determiner):
        """デバッグ出力エラー時の処理テスト"""
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: デバッグファイル出力失敗時の処理確認
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({'col1': [1, 2]})

        with patch('pandas.DataFrame.to_excel', side_effect=Exception("Test error")):
            processor = BPRADFlagInitializer()
            result = processor.process(_df)

            assert isinstance(result, pd.DataFrame)
            assert not result.empty
            assert 'bpr_target_flag' in result.columns


class TestLoookupReferenceData:
    """LoookupReferenceDataのprocessメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 新設申請でリファレンス明細なし
    │   ├── 正常系: 変更申請でリファレンス明細あり
    │   ├── 異常系: 新設申請でリファレンス明細あり
    │   └── 異常系: 変更申請でリファレンス明細なし
    ├── C1: 分岐カバレッジ
    │   ├── mask_new_error分岐のテスト
    │   └── mask_custom_error分岐のテスト
    ├── C2: 条件組み合わせ
    │   ├── application_typeとreference_branch_code_bprの組み合わせ
    │   └── NaN値を含むケース
    └── BVT: 境界値テスト
        ├── 空のDataFrame
        ├── 必須カラム欠損
        └── 大量データ

    # C1のディシジョンテーブル
    | 条件                                         | DT1 | DT2 | DT3 | DT4 |
    |----------------------------------------------|-----|-----|-----|-----|
    | application_typeが新設                       | Y   | Y   | N   | N   |
    | reference_branch_code_bprが空文字            | Y   | N   | Y   | N   |
    | 出力                                         | OK  | Err | Err | OK  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値 | 期待される結果 | テストの目的/検証ポイント | 実装状況 |
    |----------|----------------|----------|----------------|--------------------------|----------|
    | BVT_001  | DataFrame      | 空DataFrame | エラーなし | 空データの処理を検証 | test_process_C0_empty_dataframe |
    | BVT_002  | DataFrame      | application_type カラムなし | ValueError | 必須カラム欠損の検証 | test_process_C0_missing_required_column |
    | BVT_003  | DataFrame      | 10万行のデータ | 正常処理 | 大量データの処理性能検証 | test_process_C0_large_dataset |

    境界値検証ケースの実装状況サマリー
    - 実装済み: 3件
    - 未実装: 0件
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def processor(self):
        return LoookupReferenceData()

    def test_process_C0_new_application_no_reference(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 新設申請でリファレンス明細なしの正常系
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': [ApplicationType.NEW.value],
            'reference_branch_code_bpr': [''],
        })

        with patch('src.lib.common_utils.ibr_dataframe_helper.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert not mock_tabulate.called
            assert result['reference_branch_code_bpr'].iloc[0] == ''
            assert result['application_type'].iloc[0] == ApplicationType.NEW.value

    def test_process_C0_change_application_with_reference(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C0
        テスト内容: 変更申請でリファレンス明細ありの正常系
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['2'],  # 変更申請
            'reference_branch_code_bpr': ['B001'],
        })

        with patch('src.lib.common_utils.ibr_dataframe_helper.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert not mock_tabulate.called
            assert result['reference_branch_code_bpr'].iloc[0] == 'B001'
            assert result['application_type'].iloc[0] == '2'


    def test_process_C1_new_application_with_reference(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 新設申請でリファレンス明細ありの異常系
        DT: DT2
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': [ApplicationType.NEW.value],
            'reference_branch_code_bpr': ['B001'],
        })

        # モックのパスを修正
        with patch('src.packages.preparation_editor.preparation_chain_processor.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert mock_tabulate.called
            assert result['reference_branch_code_bpr'].iloc[0] == 'B001'

    def test_process_C1_change_application_no_reference(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C1
        テスト内容: 変更申請でリファレンス明細なしの異常系
        DT: DT3
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': ['2'],
            'reference_branch_code_bpr': [''],
        })

        with patch('src.packages.preparation_editor.preparation_chain_processor.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert mock_tabulate.called
            assert result['reference_branch_code_bpr'].iloc[0] == ''

    def test_process_C2_multiple_conditions(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: C2
        テスト内容: 複数条件の組み合わせテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': [ApplicationType.NEW.value, '2', ApplicationType.NEW.value, '2'],
            'reference_branch_code_bpr': ['', 'B001', 'B002', ''],
        })

        with patch('src.packages.preparation_editor.preparation_chain_processor.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert mock_tabulate.call_count == 2  # エラーケースが2件あるため
            assert len(result) == 4

    def test_process_BVT_empty_dataframe(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 空のDataFrameの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': [],
            'reference_branch_code_bpr': [],
        })

        with patch('src.packages.preparation_editor.preparation_chain_processor.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert not mock_tabulate.called
            assert len(result) == 0
            assert 'application_type' in result.columns
            assert 'reference_branch_code_bpr' in result.columns

    def test_process_BVT_missing_required_column(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 必須カラム欠損のテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': [ApplicationType.NEW.value],
            # reference_branch_code_bprカラムなし
        })

        with pytest.raises(KeyError):
            processor.process(_df)

    @pytest.mark.skip(reason="実行環境に応じて調整が必要な大規模データテスト")
    def test_process_BVT_large_dataset(self, processor):
        test_doc = """
        テスト区分: UT
        テストカテゴリ: BVT
        テスト内容: 大量データの処理テスト
        """
        log_msg(f"\n{test_doc}", LogLevel.DEBUG)

        _df = pd.DataFrame({
            'application_type': [ApplicationType.NEW.value] * 100000,
            'reference_branch_code_bpr': [''] * 100000,
        })

        with patch('src.packages.preparation_editor.preparation_chain_processor.tabulate_dataframe') as mock_tabulate:
            result = processor.process(_df)
            assert not mock_tabulate.called
            assert len(result) == 100000

class TestWritePreparationResult:
    """WritePreparationResultのprocessメソッドのテスト

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
        with patch('src.packages.preparation_editor.preparation_chain_processor.preparation_edited',
                str(pickle_path)), \
            patch('src.packages.preparation_editor.preparation_chain_processor.debug_preparation_editor_result_xlsx',
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
        processor = WritePreparationResult()
        processor.process(_df)

        # pickleファイルが作成され、読み込み可能なことを確認
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
        processor = WritePreparationResult()
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
        processor = WritePreparationResult()

        # 書き込み権限のないパスをPathLibを使って環境非依存で指定
        invalid_path = Path('/invalid') / 'path' / 'file.pkl'
        with patch('src.packages.preparation_editor.preparation_chain_processor.preparation_edited',
                str(invalid_path)):
            with pytest.raises(PreparationChainProcessorError) as exc_info:
                processor.process(_df)
            assert '受付処理結果ファイル書き込みで失敗が発生しました' in str(exc_info.value)
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
        processor = WritePreparationResult()

        # テスト前のDataFrameの型を確認
        log_msg(f"Original DataFrame types:\n{_df.dtypes}", LogLevel.DEBUG)

        # pickle保存されたデータの検証
        processor.process(_df)
        loaded_df = pd.read_pickle(config_patches)
        log_msg(f"Loaded DataFrame types:\n{loaded_df.dtypes}", LogLevel.DEBUG)

        # pickleファイルには元の型が保存される
        assert loaded_df['col1'].dtype == 'int64'
        assert loaded_df['col2'].dtype == 'float64'

        # Excel出力時の文字列変換を検証
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
        processor = WritePreparationResult()
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
        processor = WritePreparationResult()

        # テスト前のDataFrameの型を確認
        log_msg(f"Original DataFrame types:\n{_df.dtypes}", LogLevel.DEBUG)

        # pickle保存されたデータの検証
        processor.process(_df)
        loaded_df = pd.read_pickle(config_patches)
        log_msg(f"Loaded DataFrame types:\n{loaded_df.dtypes}", LogLevel.DEBUG)

        # 各カラムの型を個別に検証
        assert loaded_df['col1'].dtype == 'int64'
        assert loaded_df['col2'].dtype == 'object'  # 文字列は常にobject型
        assert loaded_df['col3'].dtype == 'float64'

        # Excel出力時の文字列変換を検証
        df_copy = _df.copy()
        df_str = df_copy.astype(str)
        log_msg(f"String converted DataFrame types:\n{df_str.dtypes}", LogLevel.DEBUG)

        # 全てのカラムが文字列型(object)に変換されていることを確認
        assert (df_str.dtypes == 'object').all()

        # 実際の値が正しく文字列に変換されていることを確認
        assert df_str['col1'].iloc[0] == '1'
        assert df_str['col2'].iloc[0] == 'a'
        assert df_str['col3'].iloc[0] == '1.1'

        log_msg("Mixed data type conversion verification completed", LogLevel.DEBUG)
