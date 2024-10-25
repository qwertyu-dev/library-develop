import pandas as pd

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.converter_utils.ibr_basic_column_editor import ColumnEditor

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config

#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

@with_config
class DataFrameEditor:
    def __init__(self, config: dict|None = None):
        # DI
        self.config = config or self.config
        self.log_msg = self.config.log_message
        self.column_editors = self.initialize_editors()

        # output_layout情報を受け取る
        self.output_columns = None

    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {}

    # 処理再編
    def edit_series(self, series: pd.Series) -> pd.Series:
        edited_series = self._prepare_output_layout(series)
        edited_series = self._apply_basic_editors(edited_series)
        #edited_series = self._apply_custom_editors(edited_series)
        return edited_series

    # 出力レイアウト準備
    def _prepare_output_layout(self, series: pd.Series) -> pd.Series:
        edited_series = pd.Series(index=self.output_columns, dtype='object')
        for col in self.output_columns:
            if col in series.index:
                edited_series[col] = series[col]
                self._log_change(col, series[col], edited_series[col])
        edited_series['debug_applied_facade_name'] = self.__class__.__name__

        return edited_series

    # 基本編集適用
    def _apply_basic_editors(self, edited_series: pd.Series) -> pd.Series:
        # 対象を絞った上で適用
        valid_editors = {
            col: editor
            for col, editor in self.column_editors.items()
            if col in edited_series.index
            }
        self.log_msg(f'valid_editors: {valid_editors}', LogLevel.INFO)

        for col, editor in valid_editors.items():
            original_value = edited_series[col]
            edited_value = editor.edit(original_value)
            edited_series[col] = edited_value
            # 前後比較でログ出力
            self._log_change(col, original_value, edited_value)

        return edited_series

    # 単なるlogヘルパー、テスト不要
    def _log_change(self, col: str, original_value: str|int, edited_value: str|int):
        self.log_msg(f"Editing column: {col}", LogLevel.INFO)
        self.log_msg(f"Original value: {original_value} -> Edited value: {edited_value}", LogLevel.INFO)
