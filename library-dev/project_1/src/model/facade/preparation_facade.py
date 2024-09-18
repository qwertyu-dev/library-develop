# Facade定義
import pandas as pd

from functools import partial
from pathlib import Path
from typing import Any

from src.lib.common_utils.ibr_enums import LogLevel
from src.lib.common_utils.ibr_get_config import Config

# config共有
from src.lib.common_utils.ibr_decorator_config import with_config

#import sys
#from src.lib.common_utils.ibr_decorator_config import initialize_config
#config = initialize_config(sys.modules[__name__])

from src.lib.converter_utils.ibr_basic_column_editor import (
    ColumnEditor,
    Column1Editor,
    Column2Editor,
    Column3Editor,
    Column4Editor,
    Column5Editor,
    Column6Editor,
    Column7Editor,
    Column8Editor,
)

# 個別のColumnEditorを呼ぶ
# TODO(Suzuki): 個別編集部品をimportする



#TODO(suzuki): commonに入れるかどうかの判断
# ロギングHelper関数
def format_series_for_log(series: pd.Series) -> str:
    """Seriesオブジェクトを簡潔な文字列形式に変換します

    インデックス、dtype情報、Name情報を除去します。
    """
    return str(series.to_numpy().tolist())

@with_config
class DataFrameEditor:
    def __init__(self, config: dict|None = None):
        # DI
        self.log_msg = config or self.config.log_message
        self.column_editors = self.initialize_editors()

    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {}

    def edit_series(self, series: pd.Series) -> pd.Series:
        valid_editors = {col: editor for col, editor in self.column_editors.items() if col in series.index}

        edited_series = series.copy()
        for col, editor in valid_editors.items():
            original_value = series[col]
            edited_value = editor.edit(original_value)
            edited_series[col] = edited_value
            self.log_msg(f"Editing column: {col}", LogLevel.INFO)
            self.log_msg(f"Original value: {original_value} -> Edited value: {edited_value}", LogLevel.INFO)

        return edited_series

    def edit_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(self.edit_series, axis=1)

# どのcolumnに何の編集処理を適用するか定義している、Facadeそのもの
class DataFrameEditor1(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column1': Column1Editor(),
            'column2': Column2Editor(),
            'column3': Column3Editor(),
        }

class DataFrameEditor2(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column4': Column4Editor(),
            'column5': Column5Editor(),
            'column6': Column8Editor(),
        }

class DataFrameEditor3(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column8Editor(),
        }

class DataFrameEditor4(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column4': Column4Editor(),
            'column5': Column5Editor(),
            'column6': Column6Editor(),
            'column7': Column7Editor(),
        }

class DataFrameEditor5(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column5': Column5Editor(),
            'column6': Column6Editor(),
            'column7': Column8Editor(),
        }

class DataFrameEditor6(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column7Editor(),
        }

class DataFrameEditor7(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column7Editor(),
        }

class DataFrameEditor8(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column7Editor(),
        }

class DataFrameEditor9(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column7Editor(),
        }

class DataFrameEditor10(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column7Editor(),
        }

class DataFrameEditorDefault(DataFrameEditor):
    def initialize_editors(self) -> dict[str, ColumnEditor]:
        return {
            'column7': Column8Editor(),
        }
