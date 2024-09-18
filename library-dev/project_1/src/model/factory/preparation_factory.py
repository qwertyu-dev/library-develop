from importlib import import_module
from pathlib import Path

import pandas as pd
from src.model.facade.preparation_facade import DataFrameEditor
from src.lib.validator_utils.ibr_decision_table_validator import DT
from src.lib.common_utils.ibr_enums import LogLevel

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config

#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])


@with_config
class EditorFactory:
    """データフレーム編集のためのFactory class

    Class Overview:
        ディシジョンテーブルに基づいて適切なDataFrameEditorを生成します。
        各行のデータに応じて条件合致するFacadeを選択し適用します。

    Attributes:
        decision_table (pd.DataFrame): 編集方法を決定するためのディシジョンテーブル
        editor_classes (dict[str, DataFrameEditor]): カスタムエディタクラスの辞書

    Condition Information:
        - Condition:1
            - ID: DECISION_TABLE_MATCH
            - Type: 条件マッチング
            - Applicable Scenarios: ディシジョンテーブルの条件に一致する行の処理

    Pattern Information:
        - Pattern:1
            - ID: CUSTOM_EDITOR
            - Type: カスタム編集
            - Applicable Scenarios: 特定の編集パターンに対するカスタム処理の適用

    Methods:
        evaluate_conditions(row): 条件を評価し、適切なFacade名を返す
        check_condition(value, condition): 個別の条件をチェックする
        create_editor(row): 適切なエディタインスタンスを生成する

    Usage Example:
        >>> factory = EditorFactory(decision_table)
        >>> editor = factory.create_editor(data_row)
        >>> edited_row = editor.edit_dataframe([data_row]).squeeze()

    Notes:
        - ディシジョンテーブルの戻り値とFacade名を一致させる必要があります
        - グローバル名前空間からFacadeクラスを動的に取得します

    Dependency:
        - pandas
        - src.model.facade.preparation_facade

    ResourceLocation:
        - [本体]
            - src/model/factory/preparation_factory.py
        - [テストコード]
            - tests/model/factory/test_preparation_factory.py

    Todo:
        - エラーハンドリングの強化
        - パフォーマンス最適化

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当         |
    |------|--------------|----------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/09/08 |              |

    """
    def __init__(self, decision_table: pd.DataFrame, editor_classes: dict[str, DataFrameEditor] | None=None):
        """イニシャライザー

        Arguments:
            decision_table (pd.DataFrame): 編集方法を決定するためのディシジョンテーブル
            editor_classes (dict[str, DataFrameEditor] | None): カスタムエディタクラスの辞書 DI目的の定義
        """
        self.log_msg = self.config.log_message
        self.decision_table = decision_table
        self.editor_classes = editor_classes or {}
        # DT classで定義のある関数名dictを生成
        self.dt_functions = {func: getattr(DT, func) for func in dir(DT) if callable(getattr(DT, func)) and not func.startswith("__")}
        self.log_msg(f'self.dt_functions: {self.dt_functions}', LogLevel.DEBUG)

        if 'DataFramneEditorDefault' not in self.editor_classes:
            self.editor_classes["DataFrameEditorDefault"] = DataFrameEditor

    def evaluate_conditions(self, row: pd.Series) -> str:
        """ディシジョンテーブルによる条件を明細単位で評価し、適切なFacade名を返す

        Arguments:
            row (pd.Series): 評価対象の行データ

        Return Value:
            str: 適用するFacade名

        Algorithm:
            1. ディシジョンテーブルの各行を順に評価
            2. すべての条件が一致する行を見つけたら、その決定結果でFacade名を返す
            3. 一致する行がない場合、デフォルトのエディタ名を返す

        Usage Example:
            >>> facade_name = factory.evaluate_conditions(data_row)
            'CustomFacade1'
        """
        for _, decision_row in self.decision_table.iterrows():
            conditions_met = [self.check_condition(row[col], decision_row[col]) for col in row.index]
            if all(conditions_met):
                result = decision_row['DecisionResult']
                self.log_msg('-'*100, LogLevel.INFO)
                self.log_msg(f"All conditions met, returning DecisionResult: {result}", LogLevel.INFO)
                return result
        self.log_msg('-'*100, LogLevel.INFO)
        self.log_msg("No matching conditions found, returning DataFrameEditorDefault", LogLevel.INFO)
        return 'DataFrameEditorDefault'

    def check_condition(self, value: str | int, condition: str | int)-> bool | str:
        """ディシジョンテーブル記載の条件によりチェック結果を返す

        Arguments:
            value (str | int): チェック対象の値
            condition (str | int): 条件

        Return Value:
            bool: 条件を満たすかどうか
            str: チェック関数名

        Algorithm:
            1. 条件がNaNまたは"any"の場合、Trueを返す
            2. 文字列以外の場合、値と条件が完全に一致するかチェック
            3. 条件がチェック関数記述の場合、関数で結果チェック
            2. 条件が文字列/カンマで区切記述の場合、or条件でチェック

        Usage Example:
            >>> factory.check_condition("A", "A,B,C")
            True

        Note:
            1.DTクラスに存在するfunctionを事前にオブジェクトマッピングしているため生成時にglobals()は不要
            2.ifネストを浅くするため構造分離している
        """
        def is_any_condition(cond: str | int) -> bool:
            return pd.isna(cond) or cond == "any"

        def check_dt_function(val: str | int, cond: str) -> bool:
            if cond in self.dt_functions:
                result = self.dt_functions[cond](val)
                self.log_msg(f"DT function {cond} result: {result}", LogLevel.DEBUG)
                return result
            return False

        def check_or_condition(val: str | int, cond: str) -> bool:
            conditions = [c.strip() for c in cond.split(',')]
            return any(self.check_condition(val, c) for c in conditions)

        def check_equality(val: str | int, cond: str | int) -> bool:
            return str(val) == str(cond)

        # メイン処理フロー
        if is_any_condition(condition):
            return True

        if isinstance(condition, str):
            if condition in self.dt_functions:
                return check_dt_function(value, condition)
            if "," in condition:
                return check_or_condition(value, condition)

        return check_equality(value, condition)

    @staticmethod
    def get_facade(facade_name: str) -> type[DataFrameEditor]:
        """指定された名前のFacadeクラスを動的にインポートして返す

        Args:
            facade_name (str): インポートするFacadeクラスの名前

        Returns:
            DataFrameEditor: インポートされたFacadeクラス(DataFrameEditorのサブクラス)
            クラスオブジェクトを返す(ここではインスタンス生成はしていない)

        Raises:
            ImportError: Facadeクラスが見つからない場合
            TypeError: インポートされたクラスがDataFrameEditorのサブクラスでない場合
        """
        try:
            module = import_module('src.model.facade.preparation_facade')
            facade_class = getattr(module, facade_name)
        except (ImportError, AttributeError) as e:
            err_msg = f'Failed to import Facade: {facade_name}'
            raise ImportError(err_msg) from e
        else:
            return facade_class

    def create_editor(self, row: pd.Series) -> DataFrameEditor:
        """適切なEditorインスタンスを生成する

        指定されたFacade文字列から実物を生み出すだけ

        Arguments:
            row (pd.Series): 編集対象の行データ

        Return Value:
            DataFrameEditor: 生成されたエディタインスタンス

        Algorithm:
            1. 条件を評価してFacade名を取得
            2. カスタムエディタクラスがあればそれを使用
            3. なければグローバル名前空間からクラスを取得してインスタンス化

        Exception:
            ValueError: 不明なFacadeクラス名が指定された場合

        Usage Example:
            >>> editor = factory.create_editor(data_row)
            <CustomEditor object at 0x...>
        """
        facade_name = self.evaluate_conditions(row)
        editor_class = self.editor_classes.get(facade_name)
        if editor_class is None:
            editor_class = self.get_facade(facade_name)
        editor = editor_class()
        self.log_msg(f"Created editor: {facade_name}, column_editors: {editor.column_editors}", LogLevel.DEBUG)
        return editor

def create_editor_factory(decision_table: pd.DataFrame, editor_classes: dict[str, DataFrameEditor] | None = None) -> EditorFactory:
    """EditorFactoryインスタンスを生成するだけの役割

    実質、なにもやっていない

    Function Overview:
        指定されたdecisionテーブルを使用して、
        EditorFactoryインスタンスを生成します。

    Arguments:
        decision_table (pd.DataFrame): 編集方法を決定するためのディシジョンテーブル
        editor_classes (dict[str, DataFrameEditor] | None): カスタムエディタクラスの辞書

    Return Value:
        EditorFactory: 生成されたEditorFactoryインスタンス

    Usage Example:
        >>> factory = create_editor_factory(decision_table, custom_editors)
        <EditorFactory object at 0x...>

    Algorithm:
        1. EditorFactoryクラスのインスタンスを生成
        2. 生成したインスタンスを返す

    Notes:
        - この関数はコントローラーサポート用のヘルパー関数です

    Dependency:
        - pandas
        - src.model.facade.preparation_facade

    ResourceLocation:
        - [本体]
            - src/model/factory/preparation_factory.py
        - [テストコード]
            - tests/model/factory/test_preparation_factory.py

    Todo:
        - エラーハンドリングの追加

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当         |
    |------|--------------|----------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/09/08 |              |

    """
    # contollerサポート
    return EditorFactory(decision_table, editor_classes)

def process_row(row: pd.Series, factory: EditorFactory) -> pd.Series:
    """データ編集処理を実行する

    Function Overview:
        指定された行データに対して、適切なエディタを適用し、編集結果を返します。

    Arguments:
        row (pd.Series): 処理対象の行データ
        factory (EditorFactory): 使用するEditorFactoryインスタンス

    Return Value:
        pd.Series: 編集後の行データ

    Usage Example:
        >>> edited_row = process_row(data_row, factory)
        pd.Series([...])

    Algorithm:
        1. Factoryを使用して適切なFacadeを選択
        2. Facadeを使用して行データを編集
        3. 編集結果を返す

    Notes:
        - この関数はコントローラーサポート用のヘルパー関数です

    Dependency:
        - pandas
        - src.model.facade.preparation_facade

    ResourceLocation:
        - [本体]
            - src/model/factory/preparation_factory.py
        - [テストコード]
            - tests/model/factory/test_preparation_factory.py

    Todo:
        - 複数行の一括処理サポートの追加

    Change History:
    | No   | 修正理由     | 修正点   | 対応日     | 担当         |
    |------|--------------|----------|------------|--------------|
    | v0.1 | 初期定義作成 | 新規作成 | 2024/09/08 |              |

    """
    # contollerサポート
    editor = factory.create_editor(row)

    # Seriesに対する編集処理呼び出し
    return editor.edit_series(row)


