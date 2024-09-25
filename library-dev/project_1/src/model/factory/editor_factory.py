import pandas as pd
from importlib import import_module

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_logger_helper import format_config
from src.model.facade.base_facade import DataFrameEditor

from .condition_evaluator import ConditionEvaluator

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config

#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

class NoDefaultDataFrameEditorError(Exception):
    """DecisionTableにDefaultのFadadeが定義されていない"""

@with_config
class EditorFactory:
    """データフレーム編集のためのFactory class"""
    def __init__(self, decision_table: pd.DataFrame, import_facade: str, editor_classes: dict[str, DataFrameEditor] | None=None, config: dict|None = None):
        """イニシャライザー

        Arguments:
            decision_table (pd.DataFrame): 編集方法を決定するためのディシジョンテーブル
            editor_classes (dict[str, DataFrameEditor] | None): カスタムエディタクラスの辞書 DI目的の定義
        """
        if not isinstance(decision_table, pd.DataFrame):
            err_msg = "decision_table must be a pandas DataFrame"
            raise TypeError(err_msg) from None
        if not isinstance(import_facade, str) or not import_facade:
            err_msg = "import_facade must be a string or not empty"
            raise TypeError(err_msg) from None
        if editor_classes is not None and not isinstance(editor_classes, dict):
            err_msg = "editor_classes must be a dictionary or None"
            raise TypeError(err_msg) from None

        self.decision_table = decision_table
        self.import_facade = import_facade
        # DI
        self.editor_classes = editor_classes if editor_classes is not None else {}
        self.config = config or self.config
        self.log_msg = self.config.log_message
        self.log_msg(f'\nself.decision_table: {self.decision_table}', LogLevel.DEBUG)
        self.log_msg(f'self.import_facade: {self.import_facade}', LogLevel.INFO)

        # DecisionTable評価生成
        self.condition_evaluator = ConditionEvaluator()

        # DefaultFacadeを持っていないDecisionTableが投入された場合は例外raise
        if self.decision_table.empty or 'DataFrameEditorDefault' not in self.decision_table['DecisionResult'].to_numpy():
            raise NoDefaultDataFrameEditorError from None

    def create_editor(self, row: pd.Series) -> DataFrameEditor:
        """適切なEditorインスタンスを生成する

        指定されたFacade文字列から実物を生み出すだけ
        """
        if not isinstance(row, pd.Series):
            err_msg = "row must be a pandas Series"
            raise TypeError(err_msg) from None

        if row.empty:
            err_msg = "row must not Empty Series"
            raise ValueError(err_msg) from None

        facade_name = self.condition_evaluator.evaluate_conditions(row, self.decision_table)
        # DI
        editor_class = self.editor_classes.get(facade_name) or self._load_facade(self.import_facade, facade_name)
        editor = editor_class()
        self.log_msg(f"\nCreated editor: {facade_name}, \ncolumn_editors: {format_config(editor.column_editors)}", LogLevel.INFO)
        return editor

    def _load_facade(self, import_facade: str, facade_name: str) -> type[DataFrameEditor]:
        try:
            module = import_module(import_facade)
            facade_class = getattr(module, facade_name)
            self.log_msg(f'facade class: {facade_class}', LogLevel.INFO)
        except (ImportError, AttributeError) as e:
            err_msg = f'Failed to import Facade: {import_facade}::{facade_name}'
            raise type(e)(err_msg) from e
        return facade_class

#    def _load_facade(self, import_facade: str, facade_name: str) -> type[DataFrameEditor]:
#        try:
#            module = import_module(import_facade)
#            facade_class = getattr(module, facade_name)
#            self.log_msg(f'facade class: {facade_class}', LogLevel.INFO)
#
#        except (ImportError, AttributeError) as e:
#            err_msg = f'Failed to import Facade: {import_facade}::{facade_name}'
#            raise type(e)(err_msg) from e
#        else:
#            return facade_class
