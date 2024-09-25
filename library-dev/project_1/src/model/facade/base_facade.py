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

    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {}

    def edit_series(self, series: pd.Series) -> pd.Series:
        edited_series = series.copy()

        # 対象を絞った上で適用
        valid_editors = {col: editor for col, editor in self.column_editors.items() if col in series.index}
        self.log_msg(f'valid_editors: {valid_editors}', LogLevel.INFO)

        for col, editor in valid_editors.items():
            original_value = series[col]
            edited_value = editor.edit(original_value)
            edited_series[col] = edited_value
            # 前後比較でログ出力
            self._log_change(col, original_value, edited_value)

        return edited_series

    # 結局Seriesで廻すことになるので使用しない
    #def edit_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
    #    return df.apply(self.edit_series, axis=1)

    # 単なるlogヘルパー、テスト不要
    def _log_change(self, col: str, original_value: str|int, edited_value: str|int):
        self.log_msg(f"Editing column: {col}", LogLevel.INFO)
        self.log_msg(f"Original value: {original_value} -> Edited value: {edited_value}", LogLevel.INFO)
