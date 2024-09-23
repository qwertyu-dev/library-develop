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
        self.log_msg = config or self.config.log_message
        self.column_editors = self.initialize_editors()

    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {}

    def edit_series(self, series: pd.Series) -> pd.Series:
        edited_series = series.copy()

        # 対象を絞った上で適用
        valid_editors = {col: editor for col, editor in self.column_editors.items() if col in series.index}

        for col, editor in valid_editors.items():
            original_value = series[col]
            edited_value = editor.edit(original_value)
            edited_series[col] = edited_value
            self._log_change(col, original_value, edited_value)

        return edited_series

    def edit_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(self.edit_series, axis=1)

    def _log_change(self, col: str, original_value: str|int, edited_value: str|int):
        self.log_msg(f"Editing column: {col}", LogLevel.INFO)
        self.log_msg(f"Original value: {original_value} -> Edited value: {edited_value}", LogLevel.INFO)

