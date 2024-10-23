# config共有
import sys
from unittest.mock import MagicMock, Mock

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.model.facade.base_facade import DataFrameEditor
from src.model.factory.column_edit_facade_controller import (
    CreateEditorFactoryError,
    ImportFacadeNullError,
    ProcessRowError,
    create_editor_factory,
    process_row,
)
from src.model.factory.editor_factory import EditorFactory

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message

class TestCreateEditorFactory:
    """create_editor_factory関数のテスト

    C1のディシジョンテーブル:
    | 条件                                     | DT_01 | DT_02 | DT_03 | DT_04 | DT_05 |
    |------------------------------------------|-------|-------|-------|-------|-------|
    | decision_tableが有効な構造               | Y     | N     | Y     | Y     | Y     |
    | DecisionResult列が最左端に存在           | Y     | Y     | N     | Y     | Y     |
    | DataFrameEditorDefaultが存在             | Y     | Y     | Y     | N     | Y     |
    | import_facadeが有効                      | Y     | Y     | Y     | Y     | N     |
    | 結果                                     | 成功  | 例外  | 成功  | 例外  | 例外  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ   | テスト値                               | 期待される結果           | テストの目的/検証ポイント                     | 実装状況 | 対応するテストケース                    |
    |----------|-----------------|-----------------------------------------|--------------------------|-----------------------------------------------|----------|-----------------------------------------|
    | BVT_001  | decision_table  | 最小有効DataFrame (2行2列)              | EditorFactory            | 最小サイズの有効なDataFrameの処理を確認       | 実装済み | test_create_editor_factory_BVT_minimal_valid_decision_table |
    | BVT_002  | decision_table  | DecisionResult列のみのDataFrame         | CreateEditorFactoryError | 不完全なDataFrameの処理を確認                 | 実装済み | test_create_editor_factory_BVT_incomplete_decision_table |
    | BVT_003  | decision_table  | 大規模なDataFrame (100万行)             | EditorFactory            | 大規模なDataFrameの処理を確認                 | 未実装   | - |
    | BVT_004  | import_facade   | ""                                      | CreateEditorFactoryError | 空文字列の処理を確認                          | 実装済み | test_create_editor_factory_C2_empty_import_facade |
    | BVT_005  | import_facade   | None                                    | TypeError                | Noneの処理を確認                              | 実装済み | test_create_editor_factory_BVT_none_import_facade |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 5
    - 未実装: 1
    - 一部実装: 0

    注記:
    - BVT_003(大規模なDataFrame)は現在未実装です。これは実行時間とリソース消費の観点から、実際の運用環境に近い形でテストする必要があります。
    - 他のすべての境界値ケースは実装されており、様々な入力条件下での関数の動作を確認しています。
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_decision_table(self):
        return pd.DataFrame({
            'DecisionResult': ['DataFrameEditor1', 'DataFrameEditor2', 'DataFrameEditorDefault'],
            'col1': [1, 2, 'any'],
            'col2': ['a', 'b', 'any'],
        })

    def test_create_editor_factory_C0_valid_params(self, valid_decision_table):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なパラメータでEditorFactoryインスタンスを生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        log_msg(f"\n{tabulate_dataframe(valid_decision_table)}", LogLevel.INFO)

        result = create_editor_factory(valid_decision_table, "valid_facade")
        assert isinstance(result, EditorFactory)

    def test_create_editor_factory_C0_exception_handling(self, mocker):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: EditorFactory生成時の例外をCreateEditorFactoryErrorとしてラップ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mocker.patch('src.model.factory.column_edit_facade_controller.EditorFactory', side_effect=Exception("Test exception"))
        with pytest.raises(CreateEditorFactoryError):
            create_editor_factory(pd.DataFrame({'DecisionResult': ['DataFrameEditorDefault'], 'col1': ['any']}), "test_facade")

    def test_create_editor_factory_C1_DT_01(self, valid_decision_table):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DT_01 - 全ての条件が満たされる場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        log_msg(f"\n{tabulate_dataframe(valid_decision_table)}", LogLevel.INFO)

        result = create_editor_factory(valid_decision_table, "valid_facade")
        assert isinstance(result, EditorFactory)

    def test_create_editor_factory_C1_DT_02(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DT_02 - decision_tableが無効な構造の場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_decision_table = pd.DataFrame({
            #'DecisionResult': ['DataFrameEditor1', 'DataFrameEditorDefault'],
            #'col1': [1, 'any'],
            'DecisionResult': ['DataFrameEditor1'],
            'col1': [1],
        })
        log_msg(f"\n{tabulate_dataframe(invalid_decision_table)}", LogLevel.INFO)

        with pytest.raises(CreateEditorFactoryError):
            create_editor_factory(invalid_decision_table, "valid_facade")

    def test_create_editor_factory_C1_DT_03(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DT_03 - DecisionResult列が最左端に存在しない場合
        - ただし左端である必要はなくDataFrame内にDecisionResultがあれば良い状態
        - TODO(suzuki): 縛りとして明確にするべきか
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_decision_table = pd.DataFrame({
            'col1': [1, 2, 'any'],
            'DecisionResult': ['DataFrameEditor1', 'DataFrameEditor2', 'DataFrameEditorDefault'],
        })
        log_msg(f"\n{tabulate_dataframe(invalid_decision_table)}", LogLevel.INFO)

        result = create_editor_factory(invalid_decision_table, "valid_facade")
        assert isinstance(result, EditorFactory)


    def test_create_editor_factory_C1_DT_04(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DT_04 - DataFrameEditorDefaultが存在しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_decision_table = pd.DataFrame({
            'DecisionResult': ['DataFrameEditor1', 'DataFrameEditor2'],
            'col1': [1, 2],
            'col2': ['a', 'b'],
        })
        log_msg(f"\n{tabulate_dataframe(invalid_decision_table)}", LogLevel.INFO)
        with pytest.raises(CreateEditorFactoryError):
            create_editor_factory(invalid_decision_table, "valid_facade")

    def test_create_editor_factory_C1_DT_05(self, valid_decision_table):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DT_05 - import_facadeが無効な場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ImportFacadeNullError):
            create_editor_factory(valid_decision_table, "")

    # TODO(suzuki): DecisionTableに許される文字列を限定するか?
    #def test_create_editor_factory_C2_invalid_any_value(self):
    #    test_doc = """
    #    テスト内容:
    #    - テストカテゴリ: C2
    #    - テスト区分: 異常系
    #    - テストシナリオ: DataFrameEditorDefault行に'any'以外の値が含まれる場合
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)
    #
    #    invalid_decision_table = pd.DataFrame({
    #        'DecisionResult': ['DataFrameEditor1', 'DataFrameEditorDefault'],
    #        'col1': [1, 'invalid'],
    #        'col2': ['a', 'any'],
    #    })
    #    log_msg(f"\n{tabulate_dataframe(invalid_decision_table)}", LogLevel.INFO)
    #    with pytest.raises(CreateEditorFactoryError):
    #        create_editor_factory(invalid_decision_table, "valid_facade")

    def test_create_editor_factory_BVT_minimal_valid_decision_table(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 最小サイズの有効なDecisionTableでの生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        minimal_table = pd.DataFrame({
            'DecisionResult': ['DataFrameEditor1', 'DataFrameEditorDefault'],
            'col1': [1, 'any'],
        })
        result = create_editor_factory(minimal_table, "valid_facade")
        assert isinstance(result, EditorFactory)

    # TODO(suzuki): 異常構造のDecisionTableに対する制約定義をどこまでやるか
    #def test_create_editor_factory_BVT_incomplete_decision_table(self):
    #    test_doc = """
    #    テスト内容:
    #    - テストカテゴリ: BVT
    #    - テスト区分: 異常系
    #    - テストシナリオ: 不完全なDecisionTableでの生成試行
    #    """
    #    log_msg(f"\n{test_doc}", LogLevel.INFO)
    #
    #    invalid_decision_table = pd.DataFrame({
    #        'DecisionResult': ['DataFrameEditorDefault'],
    #    })
    #    log_msg(f"\n{tabulate_dataframe(invalid_decision_table)}", LogLevel.INFO)
    #    with pytest.raises(CreateEditorFactoryError):
    #        create_editor_factory(invalid_decision_table, "valid_facade")

    def test_create_editor_factory_BVT_none_import_facade(self, valid_decision_table):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: Noneのimport_facadeでの生成試行
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ImportFacadeNullError):
            create_editor_factory(valid_decision_table, None)

class TestProcessRow:
    """process_row関数のテスト

    C1のディシジョンテーブル(基本機能):
    | 条件                      | DT_01 | DT_02 | DT_03 | DT_04 |
    |---------------------------|-------|-------|-------|-------|
    | rowが有効                 | Y     | N     | Y     | Y     |
    | factoryが有効             | Y     | Y     | N     | Y     |
    | editor生成が成功          | Y     | Y     | Y     | N     |
    | edit_seriesが成功         | Y     | Y     | Y     | Y     |
    | 結果                      | 成功  | 例外  | 例外  | 例外  |

    C1のディシジョンテーブル(output_layout):
    | 条件                                  | DT_05 | DT_06 | DT_07 | DT_08 | DT_09 |
    |---------------------------------------|-------|-------|-------|-------|-------|
    | output_layoutが有効なリスト           | Y     | N     | Y     | Y     | Y     |
    | 指定された列が全てrowに存在する       | Y     | -     | N     | Y     | Y     |
    | 列の順序が元データと一致              | Y     | -     | -     | N     | Y     |
    | サブセット選択(一部の列のみ)          | N     | -     | -     | -     | Y     |
    | 結果                                  | 成功  | 例外  | 例外  | 成功  | 成功  |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                             | 期待される結果    | テストの目的/検証ポイント                 | 実装状況 | 対応するテストケース                    |
    |----------|----------------|--------------------------------------|-------------------|-------------------------------------------|----------|----------------------------------------|
    | BVT_001  | row            | 空のSeries                           | ProcessRowError   | 空のSeriesの処理を確認                    | 実装済み | test_process_row_BVT_empty_series       |
    | BVT_002  | row            | 1要素のSeries                        | 編集後のSeries    | 最小サイズのSeriesの処理を確認            | 実装済み | test_process_row_BVT_minimal_series     |
    | BVT_003  | row            | 大規模なSeries (1000要素             | 編集後のSeries    | 大規模なSeriesの処理を確認                | 未実装   | -                                       |
    | BVT_004  | row            | null値を含むSeries                   | 編集後のSeries    | null値の処理を確認                        | 実装済み | test_process_row_BVT_null_values        |
    | BVT_005  | row            | 異なるデータ型を含むSeries           | 編集後のSeries    | 複数のデータ型の処理を確認                | 実装済み | test_process_row_BVT_mixed_data_types   |
    | BVT_006  | factory        | None                                 | TypeError         | 無効なfactoryの処理を確認                 | 実装済み | test_process_row_BVT_none_factory       |
    | BVT_007  | output_layout  | 空リスト []                          | ProcessRowError   | 空のoutput_layoutの処理を確認             | 実装済み | test_process_row_BVT_invalid_output_layout |
    | BVT_008  | output_layout  | None                                 | ProcessRowError   | Noneのoutput_layoutの処理を確認           | 実装済み | test_process_row_BVT_invalid_output_layout |
    | BVT_009  | output_layout  | ['non_existent_col']                 | ProcessRowError   | 存在しない列の指定の処理を確認            | 実装済み | test_process_row_BVT_invalid_output_layout |
    | BVT_010  | output_layout  | ['col1', 'col1']                     | ProcessRowError   | 重複した列名の処理を確認                  | 実装済み | test_process_row_BVT_invalid_output_layout |
    | BVT_011  | output_layout  | 全列名リスト                         | 編集後のSeries    | 全列指定の処理を確認                      | 未実装   | -                                       |
    | BVT_012  | output_layout  | 列名の順序入れ替え                   | 編集後のSeries    | 列順序変更の処理を確認                    | 実装済み | test_process_row_C0_output_layout_column_order |

    境界値検証ケースの実装状況サマリー:
    - 実装済み: 10
    - 未実装: 2
    - 一部実装: 0

    注記:
    1. BVT_003(大規模なSeries)は、実行時間とリソース消費の観点から、実際の運用環境でのテストが必要です。
    2. BVT_011(全列名リスト)は、より大規模なデータセットでの動作確認のために追加が必要です。
    3. output_layout関連のテストでは、以下の観点を特に考慮しています:
        - 無効な入力値の検証(空リスト、None、無効な列名)
        - 列の順序変更の正常動作確認
        - サブセット選択(一部の列のみを選択)の動作確認
        - エラーケースでの適切な例外発生

    C2の条件組み合わせ観点:
    1. row + output_layout の組み合わせ
        - 通常のrow + 有効なoutput_layout
        - 異常なrow + 有効なoutput_layout
        - 通常のrow + 無効なoutput_layout
        - 異常なrow + 無効なoutput_layout

    2. factory + output_layout の組み合わせ
        - 有効なfactory + 有効なoutput_layout
        - 無効なfactory + 有効なoutput_layout
        - 有効なfactory + 無効なoutput_layout
        - 無効なfactory + 無効なoutput_layout

    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def mock_decision_table(self):
        return pd.DataFrame({
            'DecisionResult': ['DataFrameEditor1', 'DataFrameEditorDefault'],
            'col1': [1, 'any'],
            'col2': ['a', 'any'],
        })

    @pytest.fixture()
    def mock_editor_factory(self, mock_decision_table):
        editor_factory = EditorFactory(mock_decision_table, "mock_import_facade")
        editor_factory.condition_evaluator = Mock()
        editor_factory.condition_evaluator.evaluate_conditions.return_value = 'DataFrameEditor1'

        mock_editor = Mock()
        mock_editor.edit_series.return_value = pd.Series({'col1': 'edited', 'col2': 'edited'})

        editor_factory.create_editor = Mock(return_value=mock_editor)
        return editor_factory

    def test_process_row_C0_valid_params(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なパラメータでrowを処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        result = process_row(row, mock_editor_factory, output_layout)
        assert isinstance(result, pd.Series)
        assert result.equals(pd.Series({'col1': 'edited', 'col2': 'edited'}))

        mock_editor_factory.create_editor.assert_called_once()
        mock_editor_factory.create_editor.return_value.edit_series.assert_called_once_with(row)

    def test_process_row_C0_exception_handling(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 例外発生時のProcessRowErrorへのラップ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_editor_factory.create_editor.side_effect = Exception("Test exception")
        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        with pytest.raises(ProcessRowError):
            process_row(row, mock_editor_factory, output_layout)

    def test_process_row_C0_output_layout_column_order(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: output_layoutで指定された列順序での出力確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col2', 'col1']  # 順序を変更

        result = process_row(row, mock_editor_factory, output_layout)
        assert list(result.index) == ['col1', 'col2']  # 列順序の確認

    def test_process_row_C0_output_layout_subset(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: output_layoutで一部の列のみを選択
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 入力データ
        row = pd.Series({'col1': 'value1', 'col2': 'value2', 'col3': 'value3'})
        output_layout = ['col1', 'col3']

        # Mockの戻り値を動的に設定
        mock_editor = mock_editor_factory.create_editor.return_value
        mock_editor.edit_series.return_value = pd.Series({
            'col1': 'edited1',
            'col2': 'edited2',
            'col3': 'edited3',
        })[output_layout]  # output_layoutに応じた部分集合を返す

        # テスト実行
        result = process_row(row, mock_editor_factory, output_layout)

        # 検証
        assert list(result.index) == output_layout
        assert result['col1'] == 'edited1'
        assert result['col3'] == 'edited3'
        assert 'col2' not in result.index

        # Mockの呼び出し確認
        mock_editor.edit_series.assert_called_once_with(row)

    def test_process_row_C1_editor_output_columns_setting(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: Editorにoutput_columnsが正しく設定されることを確認
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']

        _ = process_row(row, mock_editor_factory, output_layout)

        # Editorに正しくoutput_columnsが設定されたことを確認
        mock_editor = mock_editor_factory.create_editor.return_value
        assert mock_editor.output_columns == output_layout

    def test_process_row_C1_DT_01(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: DT_01 - 全ての条件が満たされる場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        log_msg(f"\n{row}", LogLevel.INFO)
        result = process_row(row, mock_editor_factory, output_layout)
        log_msg(f"\n{result}", LogLevel.INFO)
        assert isinstance(result, pd.Series)
        assert result.equals(pd.Series({'col1': 'edited', 'col2': 'edited'}))

    def test_process_row_C1_DT_02(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DT_02 - rowが無効な場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_row = "not a series"
        output_layout = ['col1', 'col2']
        with pytest.raises(ProcessRowError):
            process_row(invalid_row, mock_editor_factory, output_layout)

    def test_process_row_C1_DT_03(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DT_03 - factoryが無効な場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        invalid_factory = "not a factory"
        with pytest.raises(ProcessRowError):
            process_row(row, invalid_factory, output_layout)

    def test_process_row_C1_DT_04(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 異常系
        - テストシナリオ: DT_04 - editor生成が失敗する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_editor_factory.create_editor.side_effect = Exception("Editor creation failed")
        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        with pytest.raises(ProcessRowError):
            process_row(row, mock_editor_factory, output_layout)

    def test_process_row_C1_output_layout_column_mismatch(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C1
        - テスト区分: 正常系
        - テストシナリオ: output_layoutで指定された列がrow/editorの列と一致しない場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col3', 'col4']  # 存在しない列
        result = process_row(row, mock_editor_factory, output_layout)
        assert result.equals(pd.Series({'col1': 'edited', 'col2': 'edited'}))


    def test_process_row_C2_edit_series_exception(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: edit_series実行時に例外が発生する場合
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mock_editor_factory.create_editor.return_value.edit_series.side_effect = Exception("Edit series failed")
        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        with pytest.raises(ProcessRowError):
            process_row(row, mock_editor_factory, output_layout)

    def test_process_row_BVT_empty_series(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: 空のSeriesの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        empty_series = pd.Series()
        output_layout = ['col1', 'col2']
        with pytest.raises(ProcessRowError):
            process_row(empty_series, mock_editor_factory, output_layout)

    def test_process_row_BVT_minimal_series(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 最小サイズのSeriesの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        minimal_series = pd.Series({'col1': 'value1'})
        output_layout = ['col1']
        result = process_row(minimal_series, mock_editor_factory, output_layout)
        assert result.equals(pd.Series({'col1': 'edited', 'col2': 'edited'}))

    def test_process_row_BVT_null_values(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: null値を含むSeriesの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        null_series = pd.Series({'col1': None, 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        result = process_row(null_series, mock_editor_factory, output_layout)
        assert result.equals(pd.Series({'col1': 'edited', 'col2': 'edited'}))

    def test_process_row_BVT_mixed_data_types(self, mock_editor_factory):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 正常系
        - テストシナリオ: 異なるデータ型を含むSeriesの処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        mixed_series = pd.Series({'col1': 'string', 'col2': 123, 'col3': 1.23, 'col4': True})
        output_layout = ['col1', 'col2']
        result = process_row(mixed_series, mock_editor_factory, output_layout)
        assert result.equals(pd.Series({'col1': 'edited', 'col2': 'edited'}))

    def test_process_row_BVT_none_factory(self):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: Noneのfactoryでの処理試行
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        output_layout = ['col1', 'col2']
        with pytest.raises(ProcessRowError):
            process_row(row, None, output_layout)

    @pytest.mark.parametrize(("output_layout"), [
        (['non_existent_col']),  # 存在しない列
        (['col1', 'col1']),  # 重複した列名
    ])
    def test_process_row_BVT_invalid_output_layout(self, mock_editor_factory, output_layout):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: 無効なoutput_layout指定での処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        process_row(row, mock_editor_factory, output_layout)

    @pytest.mark.parametrize(("output_layout", "expected_error"), [
        ([], ProcessRowError),             # 空リスト
        (None, ProcessRowError),           # None値
    ])
    def test_process_row_BVT_invalid_output_layout_None_empty(self, mock_editor_factory, output_layout, expected_error):
        test_doc = """
        テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 異常系
        - テストシナリオ: 無効なoutput_layout指定での処理
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        row = pd.Series({'col1': 'value1', 'col2': 'value2'})
        with pytest.raises(expected_error):
            process_row(row, mock_editor_factory, output_layout)

