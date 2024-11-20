# config共有
import sys

import pandas as pd
import pytest

from src.lib.common_utils.ibr_dataframe_helper import tabulate_dataframe
from src.lib.common_utils.ibr_decorator_config import initialize_config
from src.lib.common_utils.ibr_enums import LogLevel
from src.model.facade.base_facade import DataFrameEditor
from src.model.factory.editor_factory import EditorFactory, NoDefaultDataFrameEditorError

config = initialize_config(sys.modules[__name__])
log_msg = config.log_message
log_msg(str(config), LogLevel.DEBUG)

class TestEditorFactoryInit:
    """EditorFactoryの__init__メソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なパラメータでのインスタンス生成
    │   └── 異常系: NoDefaultDataFrameEditorErrorの発生
    ├── C1: 分岐カバレッジ
    │   ├── editor_classesがNoneの場合
    │   ├── editor_classesが辞書の場合
    │   ├── decision_tableにDataFrameEditorDefaultがある場合
    │   └── decision_tableにDataFrameEditorDefaultがない場合
    ├── C2: 条件組み合わせ
    │   ├── 有効なdecision_table, import_facade, editor_classesの組み合わせ
    │   ├── 無効なdecision_tableの型
    │   ├── 無効なimport_facadeの型
    │   └── 無効なeditor_classesの型
    ├── DT: ディシジョンテーブル
    │   ├── decision_tableの内容とeditor_classesの組み合わせ
    │   └── decision_tableの内容とNoDefaultDataFrameEditorErrorの発生条件
    └── BVT: 境界値テスト
        ├── decision_tableが空のDataFrame
        ├── import_facadeが空文字列
        ├── editor_classesが空の辞書
        └── decision_tableの列名が期待と異なる

    C1のディシジョンテーブル:
    | 条件                                   | DT1 | DT2 | DT3 | DT4 |
    |----------------------------------------|-----|-----|-----|-----|
    | editor_classesがNone                   | Y   | N   | -   | -   |
    | decision_tableにDefaultFacadeがある    | Y   | Y   | N   | -   |
    | decision_tableが有効                   | Y   | Y   | Y   | N   |
    | 結果                                   | OK  | OK  | Err | Err |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ     | テスト値                             | 期待される結果              | テストの目的/検証ポイント                    | 実装状況 | 対応するテストケース               |
    |----------|--------------------|------------------------------------|---------------------------|---------------------------------------------|----------|----------------------------------|
    | BVT_001  | decision_table     | 空のDataFrame                       | NoDefaultDataFrameEditorError | 空のDataFrameの処理を確認                    | 実装済み | test_init_BVT_empty_decision_table |
    | BVT_002  | import_facade      | 空文字列                            | TypeError                 | 空文字列の処理を確認                        | 実装済み | test_init_BVT_empty_import_facade  |
    | BVT_003  | editor_classes     | 空の辞書                            | 正常終了                  | 空の辞書の処理を確認                        | 実装済み | test_init_BVT_empty_editor_classes |
    | BVT_004  | decision_table     | 'DecisionResult'列がない            | KeyError                  | 必要な列がない場合の処理を確認              | 実装済み | test_init_BVT_invalid_decision_table_columns |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def valid_decision_table(self):
        return pd.DataFrame({
            'Condition': ['condition1', 'condition2'],
            'DecisionResult': ['DataFrameEditorDefault', 'OtherEditor'],
        })

    @pytest.fixture()
    def valid_import_facade(self):
        return "src.model.facade.data_frame_editor"

    def test_init_C0_valid_parameters(self, valid_decision_table, valid_import_facade):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なパラメータでのインスタンス生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        log_msg(f'decison_table: \n{tabulate_dataframe(valid_decision_table)}', LogLevel.INFO)
        log_msg(f'valid_import_facade: \n{valid_import_facade}', LogLevel.INFO)

        factory = EditorFactory(valid_decision_table, valid_import_facade)
        assert isinstance(factory, EditorFactory)
        log_msg(f"Created factory: {factory}", LogLevel.DEBUG)

    def test_init_C0_no_default_editor(self, valid_import_facade):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: NoDefaultDataFrameEditorErrorの発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        invalid_decision_table = pd.DataFrame({
            'Condition': ['condition1'],
            'DecisionResult': ['OtherEditor'],
        })
        log_msg(f'decison_table: \n{tabulate_dataframe(invalid_decision_table)}', LogLevel.INFO)
        log_msg(f'valid_import_facade: \n{valid_import_facade}', LogLevel.INFO)

        with pytest.raises(NoDefaultDataFrameEditorError):
            EditorFactory(invalid_decision_table, valid_import_facade)
        log_msg("NoDefaultDataFrameEditorError raised as expected", LogLevel.DEBUG)

    def test_init_C1_DT_editor_classes(self, valid_decision_table, valid_import_facade):
        test_doc = """テスト内容:
        - テストカテゴリ: C1, DT
        - テスト区分: 正常系
        - テストシナリオ: editor_classesの様々なケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # DT1: editor_classesがNone
        factory = EditorFactory(valid_decision_table, valid_import_facade, None)
        assert factory.editor_classes == {}
        log_msg("DT1: editor_classes is None", LogLevel.DEBUG)

        # DT2: editor_classesが辞書
        editor_classes = {'TestEditor': DataFrameEditor}
        factory = EditorFactory(valid_decision_table, valid_import_facade, editor_classes)
        assert factory.editor_classes == editor_classes
        log_msg("DT2: editor_classes is a dictionary", LogLevel.DEBUG)

    def test_init_C2_invalid_types(self, valid_decision_table, valid_import_facade):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 異常系
        - テストシナリオ: 無効な型のパラメータ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(TypeError):
            EditorFactory("invalid", valid_import_facade)
        log_msg("TypeError raised for invalid decision_table", LogLevel.DEBUG)

        with pytest.raises(TypeError):
            EditorFactory(valid_decision_table, 123)
        log_msg("TypeError raised for invalid import_facade", LogLevel.DEBUG)

        with pytest.raises(TypeError):
            EditorFactory(valid_decision_table, valid_import_facade, "invalid")
        log_msg("TypeError raised for invalid editor_classes", LogLevel.DEBUG)

    def test_init_BVT_edge_cases(self, valid_decision_table, valid_import_facade):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: 各パラメータの境界値ケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # BVT_001: Empty DataFrame
        with pytest.raises(NoDefaultDataFrameEditorError):
            EditorFactory(pd.DataFrame(), valid_import_facade)
        log_msg("BVT_001: NoDefaultDataFrameEditorError raised for empty DataFrame", LogLevel.DEBUG)

        # BVT_002: Empty import_facade string
        with pytest.raises(TypeError):
            EditorFactory(valid_decision_table, "")
        log_msg("BVT_002: TypeError raised for empty import_facade", LogLevel.DEBUG)

        # BVT_003: Empty editor_classes dictionary
        factory = EditorFactory(valid_decision_table, valid_import_facade, {})
        assert factory.editor_classes == {}
        log_msg("BVT_003: Empty editor_classes accepted", LogLevel.DEBUG)

        # BVT_004: Invalid decision_table columns
        invalid_decision_table = pd.DataFrame({
            'Condition': ['condition1'],
            'InvalidColumn': ['DataFrameEditorDefault'],
        })
        with pytest.raises(KeyError):
            EditorFactory(invalid_decision_table, valid_import_facade)
        log_msg("BVT_004: KeyError raised for invalid decision_table columns", LogLevel.DEBUG)

class TestEditorFactoryCreateEditor:
    """EditorFactoryのcreate_editorメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 適切なEditorインスタンスの生成
    │   └── 異常系: 不適切なrowでの例外発生
    ├── C1: 分岐カバレッジ
    │   ├── editor_classesから取得する場合
    │   └── _load_facadeを使用する場合
    ├── C2: 条件組み合わせ
    │   ├── 様々なrowの値に対するテスト
    │   ├── 異なるfacade_nameに対するテスト
    │   └── rowの型が不適切な場合
    ├── DT: ディシジョンテーブル
    │   ├── rowの内容とdecision_tableの対応関係
    │   └── 条件評価結果と生成されるEditorの対応
    └── BVT: 境界値テスト
        ├── rowが空のSeries
        ├── rowに最小限の情報しかない場合
        └── rowに余分な情報がある場合

    C1のディシジョンテーブル:
    | 条件                           | DT1 | DT2 | DT3 | DT4 |
    |--------------------------------|-----|-----|-----|-----|
    | editor_classesに存在           | Y   | N   | -   | -   |
    | _load_facadeで取得可能         | -   | Y   | N   | -   |
    | rowが有効                      | Y   | Y   | Y   | N   |
    | 結果                           | OK  | OK  | Err | Err |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                   | 期待される結果        | テストの目的/検証ポイント            | 実装状況 | 対応するテストケース               |
    |----------|----------------|----------------------------|-----------------------|--------------------------------------|----------|------------------------------------|
    | BVT_001  | row            | 空のSeries                 | ValueError            | 空のSeriesの処理を確認               | 実装済み | test_create_editor_BVT_empty_row   |
    | BVT_002  | row            | 最小限の情報のみのSeries   | 正常終了              | 最小限の情報での動作を確認           | 実装済み | test_create_editor_BVT_minimal_row |
    | BVT_003  | row            | 余分な情報を含むSeries     | KeyError              | 余分な情報がある場合の動作を確認     | 実装済み | test_create_editor_BVT_extra_info_row |
    """

    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def editor_factory(self):
        decision_table = pd.DataFrame({
            'Condition': ['condition1', 'condition2'],
            'DecisionResult': ['DataFrameEditorDefault', 'DataFrameEditor1'],
        })
        # 実在するFacadeを指定している
        # ただし本来はfavcadeの位置に置くべきだがテストローカルルールでFactory下においている
        import_facade = "tests.model.factory.dummy_editor_facade"
        return EditorFactory(decision_table, import_facade)

    @pytest.fixture()
    def mock_editor_class(self):
        class MockEditor(DataFrameEditor):
            def edit(self, df: pd.DataFrame) -> pd.DataFrame:
                return df
        return MockEditor

    def test_create_editor_C0_valid_row(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 適切なEditorインスタンスの生成
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        row = pd.Series({'Condition': 'condition1'})
        log_msg(f"row: \n{row}", LogLevel.INFO)

        editor = editor_factory.create_editor(row)
        assert isinstance(editor, DataFrameEditor)
        log_msg(f"Created editor: {editor}", LogLevel.DEBUG)

    def test_create_editor_C0_invalid_row(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: 不適切なrowでの例外発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(TypeError):
            editor_factory.create_editor("invalid_row")
        log_msg("TypeError raised as expected", LogLevel.DEBUG)

    def test_create_editor_C1_DT_editor_source(self, editor_factory, mock_editor_class):
        test_doc = """テスト内容:
        - テストカテゴリ: C1, DT
        - テスト区分: 正常系
        - テストシナリオ: editor_classesとload_facadeの使用
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)
        row = pd.Series({'Condition': 'condition2'})

        # DT1: editor_classesから取得
        # 設定との整合性に留意
        editor_factory.editor_classes['DataFrameEditor1'] = mock_editor_class
        log_msg(f'editor_factory: {editor_factory}', LogLevel.INFO)
        editor = editor_factory.create_editor(row)
        log_msg(f'editor: {editor}', LogLevel.INFO)
        log_msg(f'{type(editor)}', LogLevel.INFO)
        assert isinstance(editor, mock_editor_class)
        log_msg("DT1: Editor created from editor_classes", LogLevel.DEBUG)

        # DT2: _load_facadeを使用
        del editor_factory.editor_classes['DataFrameEditor1']
        editor = editor_factory.create_editor(row)
        assert isinstance(editor, DataFrameEditor)
        log_msg("DT2: Editor created using _load_facade", LogLevel.DEBUG)

    def test_create_editor_C2_various_rows(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系
        - テストシナリオ: 様々なrowの値に対するテスト
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        rows = [
            pd.Series({'Condition': 'condition1'}),
            pd.Series({'Condition': 'condition2'}),
            pd.Series({'Condition': 'unknown_condition'}),
        ]
        for i, row in enumerate(rows):
            editor = editor_factory.create_editor(row)
            assert isinstance(editor, DataFrameEditor)
            log_msg(f"Editor created for row {i+1}", LogLevel.DEBUG)

    def test_create_editor_BVT_edge_cases(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: rowの境界値ケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # BVT_001: Empty Series
        with pytest.raises(ValueError):
            editor_factory.create_editor(pd.Series())
        log_msg("BVT_001: ValueError raised for empty Series", LogLevel.DEBUG)

        # BVT_002: Minimal row
        minimal_row = pd.Series({'Condition': 'condition1'})
        log_msg(f"minimal_row: \n{minimal_row}", LogLevel.INFO)
        editor = editor_factory.create_editor(minimal_row)
        assert isinstance(editor, DataFrameEditor)
        log_msg("BVT_002: Editor created with minimal row", LogLevel.DEBUG)

        # BVT_003: Row with extra info
        extra_info_row = pd.Series({'Condition': 'condition1', 'extra': 'info'})
        log_msg(f"\n{extra_info_row}", LogLevel.INFO)
        editor = editor_factory.create_editor(extra_info_row)
        assert isinstance(editor, DataFrameEditor)
        log_msg("BVT_003: BVT003: Editor created with extra info row", LogLevel.DEBUG)


class TestEditorFactoryLoadFacade:
    """EditorFactoryの_load_facadeメソッドのテスト

    テスト構造:
    ├── C0: 基本機能テスト
    │   ├── 正常系: 有効なimport_facadeとfacade_nameでのクラスロード
    │   └── 異常系: ImportErrorの発生
    ├── C1: 分岐カバレッジ
    │   ├── モジュールのインポートに成功する場合
    │   ├── モジュールのインポートに失敗する場合
    │   └── 属性(クラス)が存在しない場合
    ├── C2: 条件組み合わせ
    │   ├── 異なるimport_facadeとfacade_nameの組み合わせ
    │   ├── 存在しないモジュールのテスト
    │   └── 存在しない属性のテスト
    ├── DT: ディシジョンテーブル
    │   └── import_facadeとfacade_nameの組み合わせによる結果の対応
    └── BVT: 境界値テスト
        ├── import_facadeが長い文字列の場合
        ├── facade_nameが長い文字列の場合
        └── import_facadeやfacade_nameに特殊文字が含まれる場合

    C1のディシジョンテーブル:
    | 条件                      | DT1 | DT2 | DT3 |
    |---------------------------|-----|-----|-----|
    | モジュールが存在する      | Y   | N   | Y   |
    | 属性(クラス)が存在する    | Y   | -   | N   |
    | 結果                      | OK  | Err | Err |

    境界値検証ケース一覧:
    | ケースID | 入力パラメータ | テスト値                      | 期待される結果 | テストの目的/検証ポイント                 | 実装状況 | 対応するテストケース                    |
    |----------|----------------|-------------------------------|----------------|------------------------------------------|----------|----------------------------------------|
    | BVT_001  | import_facade  | 最大長の文字列                | ImportError    | 長い import_facade の処理を確認          | 実装済み | test_load_facade_BVT_edge_cases         |
    | BVT_002  | facade_name    | 最大長の文字列                | ImportError    | 長い facade_name の処理を確認            | 実装済み | test_load_facade_BVT_edge_cases         |
    | BVT_003  | import_facade  | 特殊文字を含む文字列          | ImportError    | 特殊文字を含む import_facade の処理を確認| 実装済み | test_load_facade_BVT_edge_cases         |
    | BVT_004  | facade_name    | 特殊文字を含む文字列          | ImportError    | 特殊文字を含む facade_name の処理を確認  | 実装済み | test_load_facade_BVT_edge_cases         |
    """
    def setup_method(self):
        log_msg("test start", LogLevel.INFO)

    def teardown_method(self):
        log_msg(f"test end\n{'-'*80}\n", LogLevel.INFO)

    @pytest.fixture()
    def editor_factory(self):
        return EditorFactory(pd.DataFrame({'DecisionResult': ['DataFrameEditorDefault']}), "dummy_import_facade")

    def test_load_facade_C0_valid_parameters(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 正常系
        - テストシナリオ: 有効なimport_facadeとfacade_nameでのクラスロード
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        facade_class = editor_factory._load_facade("tests.model.factory.dummy_editor_facade", "DataFrameEditor")
        assert issubclass(facade_class, DataFrameEditor)
        log_msg(f"Loaded facade class: {facade_class}", LogLevel.DEBUG)

    def test_load_facade_C0_import_error(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C0
        - テスト区分: 異常系
        - テストシナリオ: ImportErrorの発生
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        with pytest.raises(ImportError):
            editor_factory._load_facade("non_existent_module", "SomeClass")
        log_msg("ImportError raised as expected", LogLevel.DEBUG)

    def test_load_facade_C1_DT_combinations(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C1, DT
        - テスト区分: 正常系/異常系
        - テストシナリオ: import_facadeとfacade_nameの組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # DT1: 正常系
        facade_class = editor_factory._load_facade("tests.model.factory.dummy_editor_facade", "DataFrameEditorDefault")
        assert issubclass(facade_class, DataFrameEditor)
        log_msg("DT1: Successfully loaded DataFrameEditorDefault", LogLevel.DEBUG)

        # DT2: モジュールが存在しない
        with pytest.raises(ImportError) as exc_info:
            editor_factory._load_facade("non_existent_module", "SomeClass")
        assert "Failed to import Facade" in str(exc_info.value)
        log_msg("DT2: ImportError raised for non-existent module", LogLevel.DEBUG)

        # DT3: 属性(クラス)が存在しない
        with pytest.raises(AttributeError) as exc_info:
            editor_factory._load_facade("tests.model.factory.dummy_editor_facade", "NonExistentClass")
        assert "Failed to import Facade" in str(exc_info.value)
        log_msg("DT3: ImportError raised for non-existent class", LogLevel.DEBUG)

    def test_load_facade_C2_various_combinations(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: C2
        - テスト区分: 正常系/異常系
        - テストシナリオ: 様々なimport_facadeとfacade_nameの組み合わせ
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # 正常系: 別のDataFrameEditorサブクラス
        facade_class = editor_factory._load_facade("tests.model.factory.dummy_editor_facade", "DataFrameEditor2")
        assert issubclass(facade_class, DataFrameEditor)
        log_msg("Successfully loaded AnotherDataFrameEditor", LogLevel.DEBUG)

        # 異常系: 存在しないモジュール
        with pytest.raises(ImportError):
            editor_factory._load_facade("non_existent_module", "SomeClass")
        log_msg("ImportError raised for non-existent module", LogLevel.DEBUG)

        # 異常系: 存在しない属性
        with pytest.raises(AttributeError):
            editor_factory._load_facade("tests.model.factory.dummy_editor_facade", "NonExistentClass")
        log_msg("ImportError raised for non-existent class", LogLevel.DEBUG)

    def test_load_facade_BVT_edge_cases(self, editor_factory):
        test_doc = """テスト内容:
        - テストカテゴリ: BVT
        - テスト区分: 境界値
        - テストシナリオ: import_facadeとfacade_nameの境界値ケース
        """
        log_msg(f"\n{test_doc}", LogLevel.INFO)

        # BVT_001: 長いimport_facade
        long_import_facade = "a" * 255
        with pytest.raises(ModuleNotFoundError):
            editor_factory._load_facade(long_import_facade, "SomeClass")
        log_msg("BVT_001: ImportError raised for long import_facade", LogLevel.DEBUG)

        # BVT_002: 長いfacade_name
        long_facade_name = "A" * 255
        with pytest.raises(AttributeError):
            editor_factory._load_facade("tests.model.factory.dummy_editor_facade", long_facade_name)
        log_msg("BVT_002: ImportError raised for long facade_name", LogLevel.DEBUG)

        # BVT_003, BVT_004: 特殊文字を含む文字列
        special_chars = "!@#$%^&*()"
        with pytest.raises(ModuleNotFoundError):
            editor_factory._load_facade(f"invalid{special_chars}module", "SomeClass")
        log_msg("BVT_003: ImportError raised for import_facade with special characters", LogLevel.DEBUG)

        with pytest.raises(AttributeError):
            editor_factory._load_facade("tests.model.factory.dummy_editor_facade", f"Invalid{special_chars}Class")
        log_msg("BVT_004: ImportError raised for facade_name with special characters", LogLevel.DEBUG)
